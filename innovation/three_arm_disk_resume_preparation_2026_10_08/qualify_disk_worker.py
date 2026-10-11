"""One genuine synthetic training process; preflight restore metadata before torch."""
import argparse, os, sys, time, traceback
from pathlib import Path
import disk_resume_core as core

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=('continuous','restarted'),required=True); ap.add_argument('--attempt',required=True); a=ap.parse_args()
    assert len(a.attempt)==2 and a.attempt.isdigit()
    attempt=core.HERE/('attempt'+a.attempt); directory=attempt/a.mode; directory.mkdir(exist_ok=False)
    plan_path=attempt/'qualification_plan.json'; start=time.perf_counter()
    r=dict(created_utc=core.now(),complete=False,errors=[],mode=a.mode,own_pid=os.getpid(),
           synthetic_only=True,synthetic_checkpoint_arrays_loaded_from_disk=0,medical_arrays_loaded=0,
           actual_resource_updates=0,attempted_model_forward_calls=0,completed_model_forward_calls=0,
           MRI_forwards=0,GPU_forwards=0,real_medical_training_updates=0,CUDA_initialized=False,arms=[])
    report=directory/'receipt.json'
    def save(): core.atomic_json(report,r)
    save()
    try:
        plan=core.verify_plan(plan_path); r['resources_before_neural_import']=core.guard(start,240)
        restore={}
        if a.mode=='restarted':
            previous=core.read(attempt/'continuous/receipt.json')
            assert previous['complete'] and not previous['errors'] and previous['mode']=='continuous'
            for arm in core.ARMS:
                record=next(x for x in previous['arms'] if x['arm']==arm)
                b=next(x for x in record['commits'] if x['step']==plan['resume_from_step'])['metadata']
                restore[arm]=core.verify_resume(core.ROOT/b['path'],b['sha256'],arm,plan_path)
        r.update(all_restore_bindings_checked_before_neural_import=True,torch_imported_at_restore_check='torch' in sys.modules,
                 numpy_imported_at_restore_check='numpy' in sys.modules)
        assert not r['torch_imported_at_restore_check'] and not r['numpy_imported_at_restore_check']
        read_paths=set(); weight_paths=[]; denied=[]
        def audit(event,args):
            if event!='open' or not args or not isinstance(args[0],(str,bytes)): return
            try: p=Path(args[0]).resolve()
            except (TypeError,ValueError,OSError): return
            mode=args[1] if len(args)>1 else None
            if isinstance(mode,str) and 'r' not in mode and '+' not in mode: return
            if not p.is_relative_to(core.ROOT.parent): return
            rel=p.relative_to(core.ROOT.parent).as_posix()
            if p.name.endswith('.pt') and p.is_relative_to(attempt/'continuous'):
                assert a.mode=='restarted' and p.name in {arm+'_step001.pt' for arm in core.ARMS}
                weight_paths.append(p.relative_to(core.ROOT).as_posix()); return
            if rel.startswith('data/') or p.name.endswith(('.pt','.nii','.nii.gz','.zip','.npz','.npy')) or 'confirmation' in rel or 'mc_rc_validation' in rel:
                denied.append(rel); raise PermissionError('Medical/old weight IO forbidden: '+rel)
            read_paths.add(rel)
        sys.addaudithook(audit)
        sys.path.insert(0,str(core.ROOT/'experiments')); sys.path.insert(0,str(core.ROOT/'three_arm_resource_bridge_2026_10_08'))
        import training_engine as engine
        from synthetic_case import fixture
        w=engine.w; w.torch.set_num_threads(4)
        def guard(extra=0):
            v=core.guard(start,240,extra)
            assert w.torch.get_num_threads()==4 and w.torch.get_num_interop_threads()==1 and not w.torch.cuda.is_initialized()
            return dict(v,cpu_threads=4,cpu_interop_threads=1,CUDA_initialized=False)
        cache={}; factory=[]
        for which in (1,2):
            observed,grid,target=fixture(which); fields,stats,meta=w.three_fields(observed,grid)
            uid='SYNTHETIC_UID_'+str(which); cache[uid]=dict(**fields,target=target)
            factory.append(dict(uid=uid,array_sha256={k:w.array_sha(cache[uid][k]) for k in w.FIELDS},metadata=meta))
        _,initial=w.old.canonical_states(); r.update(factory_records=factory,parameter_count=1_401_795,
            initial_weights_sha256=w.old.statehash(initial),source_bindings=[core.entry(plan_path)]+plan['source_bindings'])
        def progress(arm,step):
            save(); print(core.json.dumps(dict(mode=a.mode,arm=arm,step=step,new_updates=r['actual_resource_updates'])),flush=True)
        for arm in core.ARMS:
            r['arms'].append(engine.execute_arm(arm,cache,plan,plan_path,initial,directory,guard,r,restore.get(arm),progress))
            save()
        assert r['actual_resource_updates']==r['completed_model_forward_calls']==(9 if a.mode=='continuous' else 6)
        assert all({k:w.array_sha(cache[f['uid']][k]) for k in w.FIELDS}==f['array_sha256'] for f in factory)
        assert not denied
        r.update(complete=True,status='completed',resources_after=guard(),io_audit=dict(workspace_read_paths=sorted(read_paths),
                 synthetic_weight_read_paths=weight_paths,denied_paths=denied),input_arrays_not_mutated=True,
                 output_bindings=[core.entry(core.ROOT/c[k]['path']) for arm in r['arms'] for c in arm['commits'] for k in ('checkpoint','journal','metadata')])
    except Exception as e:
        r.update(status='failed'); r['errors'].append(f'{type(e).__name__}: {e}'); r['traceback']=traceback.format_exc()
    r['finished_utc']=core.now(); r['elapsed_seconds']=time.perf_counter()-start; save()
    print(core.json.dumps({k:r.get(k) for k in ('complete','status','errors','actual_resource_updates','completed_model_forward_calls','elapsed_seconds')}),flush=True)
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__': raise SystemExit(main())
