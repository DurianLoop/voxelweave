"""Independent exact disk trees and journal reconciliation; no update/model import."""
import gc, os, sys, time, traceback
from pathlib import Path
import disk_resume_core as core

def main():
    sys.stdout.reconfigure(encoding='utf-8'); tick=time.perf_counter()
    for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[k]='1'
    os.environ['CUDA_VISIBLE_DEVICES']=''
    out=core.HERE/'independent_attempt01'; out.mkdir(exist_ok=False)
    r=dict(created_utc=core.now(),complete=False,errors=[],medical_arrays_loaded=0,synthetic_checkpoint_arrays_loaded_from_disk=0,
           neural_forwards=0,MRI_forwards=0,GPU_forwards=0,real_medical_training_updates=0,arm_checks=[],
           publication_claim_confirmed=False,goal_status='active')
    seen=[]; denied=[]
    try:
        r['resources_before']=core.guard(tick,120)
        plan_path=core.HERE/'attempt01/qualification_plan.json'; plan=core.verify_plan(plan_path)
        receipt=core.read(core.HERE/'attempt01/receipt.json')
        assert receipt['complete'] and not receipt['errors'] and receipt['actual_synthetic_updates']==15
        reports={m:core.read(core.HERE/'attempt01'/m/'receipt.json') for m in ('continuous','restarted')}
        for v in reports.values():
            assert v['complete'] and not v['errors']; core.verify_bindings(v['source_bindings']); core.verify_bindings(v['output_bindings'])
        allowed={ (core.ROOT/c['checkpoint']['path']).resolve() for v in reports.values() for a in v['arms'] for c in a['commits'] }
        assert len(allowed)==9
        def audit(event,args):
            if event!='open' or not args or not isinstance(args[0],(str,bytes)): return
            try: p=Path(args[0]).resolve()
            except (TypeError,ValueError,OSError): return
            mode=args[1] if len(args)>1 else None
            if isinstance(mode,str) and 'r' not in mode and '+' not in mode: return
            if p.is_relative_to(core.ROOT.parent) and p.name.endswith(('.pt','.npz','.npy','.nii','.nii.gz','.zip')):
                if p not in allowed: denied.append(str(p)); raise PermissionError('Only new artificial checkpoints allowed')
                seen.append(p.relative_to(core.ROOT).as_posix())
        sys.addaudithook(audit)
        import torch
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        assert torch.get_num_interop_threads()==1 and not torch.cuda.is_initialized()
        def exact(a,b):
            if isinstance(a,torch.Tensor): return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
            if isinstance(a,dict): return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
            if isinstance(a,(list,tuple)): return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
            return type(a)==type(b) and a==b
        stable=('arm','step','patient','uid','draws','selected_field','augmentation_semantic','selected_full_field_sha256',
                'loss','input_batch_sha256','label_batch_sha256','label_foreground','gradient_groups','mask_gradient_max')
        supervision=('step','patient','uid','draws','label_batch_sha256','label_foreground')
        allrows={}
        bindings=[core.entry(Path(__file__)),core.entry(plan_path),core.entry(core.HERE/'attempt01/receipt.json')]
        for arm in core.ARMS:
            core.guard(tick,120)
            c=next(a for a in reports['continuous']['arms'] if a['arm']==arm)
            s=next(a for a in reports['restarted']['arms'] if a['arm']==arm)
            assert c['starting_step']==0 and s['starting_step']==1 and c['ending_step']==s['ending_step']==3
            assert c['actual_new_updates']==3 and s['actual_new_updates']==2 and c['parameter_count']==s['parameter_count']==1_401_795
            assert c['initial_weights_sha256']==s['initial_weights_sha256']==reports['continuous']['initial_weights_sha256']
            assert [{k:h[k] for k in stable} for h in c['history']]==[{k:h[k] for k in stable} for h in s['history']]
            allrows[arm]=[{k:h[k] for k in supervision} for h in c['history']]
            checkpoints=[]
            for v in (c['commits'][0],c['commits'][-1],s['commits'][-1]):
                bindings.extend(v[k] for k in ('metadata','journal','checkpoint'))
                q=core.read(core.ROOT/v['metadata']['path']); core.verify_bindings(q['source_bindings'])
                cp=torch.load(core.ROOT/v['checkpoint']['path'],map_location='cpu',weights_only=True)
                r['synthetic_checkpoint_arrays_loaded_from_disk']+=1; checkpoints.append(cp)
                rows=[core.json.loads(line) for line in (core.ROOT/v['journal']['path']).read_text(encoding='utf-8').splitlines()]
                assert len(rows)==cp['step']==q['step']==v['step'] and cp['arm']==q['arm']==arm
                assert rows==c['history'][:cp['step']] or rows==s['history'][:cp['step']]
                assert cp['initial_weights_sha256']==c['initial_weights_sha256'] and cp['plan_sha256']==core.sha(plan_path)
                assert len(cp['optimizer']['state'])==len(cp['model'])
                assert all(int(st['step'].item())==cp['step'] for st in cp['optimizer']['state'].values())
                assert all(torch.isfinite(t).all() for t in cp['model'].values())
            split,continuous,restarted=checkpoints
            assert split['step']==1 and continuous['step']==restarted['step']==3
            assert exact(continuous,restarted) and not exact(split['model'],continuous['model'])
            assert c['final_weights_sha256']==s['final_weights_sha256']!=c['initial_weights_sha256']
            r['arm_checks'].append(dict(arm=arm,complete_model_optimizer_RNG_and_config_exact=True,
                 journal_losses_inputs_labels_gradients_and_draws_exact=True,optimizer_steps_1_to_3_verified=True,
                 actual_new_updates_continuous=3,actual_new_updates_restarted=2,final_weights_changed=True))
            del checkpoints,split,continuous,restarted,cp; gc.collect()
        assert allrows[core.ARMS[0]]==allrows[core.ARMS[1]]==allrows[core.ARMS[2]]
        for i in range(3):
            inputs=[reports['continuous']['arms'][j]['history'][i]['input_batch_sha256'] for j in range(3)]
            assert len(set(inputs))==3
        assert receipt['distinct_training_processes'] and len(receipt['probes'])==7
        assert all(v['expected_acceptance']==v['actual_acceptance'] and v['observed_child_exit']==(0 if v['actual_acceptance'] else 3) for v in receipt['probes'])
        for v in receipt['probes']:
            q=core.read(core.ROOT/v['result']['path']); assert not q['torch_in_sys_modules'] and not q['numpy_in_sys_modules']; bindings.append(v['result'])
        assert not denied and len(set(seen))==9 and r['synthetic_checkpoint_arrays_loaded_from_disk']==9
        r.update(complete=True,source_bindings=bindings,resources_after=core.guard(tick,120),CUDA_initialized=False,
             gate=dict(three_cross_process_full_disk_resumes_exact=True,shared_supervision_and_draws=True,
                  all_three_inputs_distinct=True,all_six_disk_faults_rejected_before_neural_import=True,
                  correct_metadata_accepted_before_neural_import=True,exact_update_and_optimizer_counters=True),
             io_audit=dict(allowed_synthetic_checkpoint_reads=sorted(set(seen)),denied_read_attempts=denied),
             all19series_real_resource_qualification_not_claimed=True,formal_long_MRI_training_not_qualified=True)
    except Exception as e:
        r['errors'].append(f'{type(e).__name__}: {e}'); r['traceback']=traceback.format_exc()
    r.update(finished_utc=core.now(),elapsed_seconds=time.perf_counter()-tick)
    core.new_json(out/'receipt.json',r)
    print(core.json.dumps({k:r.get(k) for k in ('complete','errors','synthetic_checkpoint_arrays_loaded_from_disk','neural_forwards','gate','elapsed_seconds')}),flush=True)
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__': raise SystemExit(main())
