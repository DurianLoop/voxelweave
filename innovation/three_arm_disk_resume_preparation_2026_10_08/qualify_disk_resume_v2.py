"""Bounded cross-process disk resume qualification; never controls user training."""
import copy, json, os, subprocess, sys, time, traceback
from pathlib import Path
import disk_resume_core as core

def main():
    sys.stdout.reconfigure(encoding='utf-8'); start=time.perf_counter()
    out=core.HERE/'attempt02'; out.mkdir(exist_ok=False); plan_path=out/'qualification_plan.json'
    r=dict(created_utc=core.now(),complete=False,status='preparing',errors=[],synthetic_only=True,
           medical_arrays_loaded=0,MRI_forwards=0,GPU_forwards=0,actual_synthetic_updates=0,
           synthetic_neural_forwards=0,synthetic_checkpoint_arrays_loaded_from_disk=0,
           real_medical_formal_training_updates=0,publication_claim_confirmed=False,goal_status='active',children=[],probes=[])
    report=out/'receipt.json'
    def save(): core.atomic_json(report,r)
    env=os.environ.copy(); env.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
    def run(command,label,limit):
        core.guard(start,600)
        p=subprocess.run([sys.executable,'-X','utf8','-B']+command,capture_output=True,timeout=min(limit,max(1,int(600-(time.perf_counter()-start)))),env=env)
        core.new_bytes(out/(label+'_stdout.txt'),p.stdout); core.new_bytes(out/(label+'_stderr.txt'),p.stderr)
        v=dict(label=label,exit_code=p.returncode,stdout=core.entry(out/(label+'_stdout.txt')),stderr=core.entry(out/(label+'_stderr.txt')))
        r['children'].append(v); save(); print(json.dumps(dict(child=label,exit_code=p.returncode)),flush=True); return p.returncode
    save()
    try:
        # Reserve worst-case stage writes before the first neural child is launched.
        r['resources_before']=core.guard(start,600,200_000_000-core.saved_bytes())
        failed=core.read(core.HERE/'attempt01/receipt.json')
        assert time.perf_counter()-start+failed['elapsed_seconds']<600
        paths=[core.HERE/name for name in ('ATTEMPT02_AMENDMENT.md','generate_attempt02.py','PROTOCOL.md','disk_resume_core.py','training_engine.py',
             'qualify_disk_worker_v2.py','qualify_disk_resume_v2.py','probe_resume.py','verify_disk_resume_v2.py','check_formal_entry.py')]
        paths += [core.ROOT/'three_arm_resource_bridge_2026_10_08'/name for name in ('three_arm_resource_worker.py','synthetic_case.py')]
        paths += [core.ROOT/'experiments'/name for name in ('mc_rc_3d_paired_resource_worker_2026_10_07.py',
             'mc_rc_3d_paired_sampling_fov_2026_10_07.py','mc_rc_3d_direct_observed_2026_10_07.py',
             'mc_rc_common_projected_observed_2026_10_08.py','mc_rc_observed_only_training_input.py',
             'mc_rc_3d_baseline_v2_2026_10_07.py','mc_rc_3d_baseline_2026_10_07.py','mc_rc_reference_resources_2026_10_07.py')]
        plan=dict(created_utc=core.now(),synthetic_only=True,arms=list(core.ARMS),updates_per_arm=3,resume_from_step=1,
                  patch=[64,128,128],batch_size=2,parameter_count=1_401_795,optimizer='AdamW',lr=.0001,weight_decay=.0001,
                  stream=[dict(step=i+1,uid=uid,patient='SYNTHETIC_PATIENT') for i,uid in enumerate(('SYNTHETIC_UID_1','SYNTHETIC_UID_2','SYNTHETIC_UID_1'))],
                  source_bindings=[core.entry(p) for p in paths])
        core.new_json(plan_path,plan); r['source_bindings']=[core.entry(plan_path)]+plan['source_bindings']
        snapshots=out/'source_snapshots'; snapshots.mkdir()
        for i,p in enumerate(paths): core.new_bytes(snapshots/(f'{i:02d}_'+p.name+'.source_snapshot'),p.read_bytes())
        assert run([str(core.HERE/'qualify_disk_worker_v2.py'),'--mode','continuous','--attempt','02'],'continuous',240)==0
        continuous=core.read(out/'continuous/receipt.json')
        r.update(actual_synthetic_updates=continuous['actual_resource_updates'],synthetic_neural_forwards=continuous['completed_model_forward_calls'])
        arm=core.ARMS[0]; binding=continuous['arms'][0]['commits'][0]['metadata']
        realmeta=core.ROOT/binding['path']; metadata=core.read(realmeta)
        faults=out/'fault_fixtures'; faults.mkdir()
        journal=(core.ROOT/metadata['journal']['path']).read_bytes()
        specs=[('missing_row',b'',None),('extra_row',journal+journal,None),('truncated_row',journal[:-2],None),
               ('checkpoint_sha',None,lambda q:q['checkpoint'].update(sha256='0'*64)),
               ('metadata_step',None,lambda q:q.update(step=2)),('arm_mismatch',None,lambda q:q.update(arm=core.ARMS[1]))]
        candidates=[('valid',realmeta,binding['sha256'],True)]
        for label,payload,mutator in specs:
            q=copy.deepcopy(metadata)
            if payload is not None:
                p=faults/(label+'.jsonl'); core.new_bytes(p,payload)
                # Keep the original expected byte/hash binding to expose actual disk corruption.
                q['journal']['path']=p.relative_to(core.ROOT).as_posix()
            if mutator: mutator(q)
            p=faults/(label+'_binding.json'); core.new_json(p,q); candidates.append((label,p,core.sha(p),False))
        for label,p,hashvalue,accepted in candidates:
            destination=faults/(label+'_probe.json')
            code=run([str(core.HERE/'probe_resume.py'),'--metadata',str(p),'--metadata-sha',hashvalue,
                 '--arm',arm,'--plan',str(plan_path),'--output',str(destination)],'probe_'+label,60)
            q=core.read(destination)
            assert code==(0 if accepted else 3) and q['complete'] and not q['errors'] and q['accepted']==accepted
            assert not q['torch_in_sys_modules'] and not q['numpy_in_sys_modules']
            r['probes'].append(dict(label=label,expected_acceptance=accepted,actual_acceptance=q['accepted'],
                     observed_child_exit=code,result=core.entry(destination),rejection_reason=q.get('rejection_reason'))); save()
        assert run([str(core.HERE/'qualify_disk_worker_v2.py'),'--mode','restarted','--attempt','02'],'restarted',240)==0
        restarted=core.read(out/'restarted/receipt.json')
        assert continuous['own_pid']!=restarted['own_pid'] and restarted['complete'] and not restarted['errors']
        r.update(actual_synthetic_updates=continuous['actual_resource_updates']+restarted['actual_resource_updates'],
                 synthetic_neural_forwards=continuous['completed_model_forward_calls']+restarted['completed_model_forward_calls'],
                 synthetic_checkpoint_arrays_loaded_from_disk=restarted['synthetic_checkpoint_arrays_loaded_from_disk'],
                 continuous_own_pid=continuous['own_pid'],restarted_own_pid=restarted['own_pid'],distinct_training_processes=True,
                 independent_verification_not_yet_run=True,output_bindings=[core.entry(out/mode/'receipt.json') for mode in ('continuous','restarted')],
                 resources_after=core.guard(start),complete=True,status='workers_and_fault_probes_completed')
        assert r['actual_synthetic_updates']==r['synthetic_neural_forwards']==15
        assert r['synthetic_checkpoint_arrays_loaded_from_disk']==3
    except Exception as e:
        r['status']='failed'; r['errors'].append(f'{type(e).__name__}: {e}'); r['traceback']=traceback.format_exc()
    r['combined_qualification_wall_seconds']=time.perf_counter()-start+core.read(core.HERE/'attempt01/receipt.json')['elapsed_seconds']
    assert r['combined_qualification_wall_seconds']<600
    r.update(finished_utc=core.now(),elapsed_seconds=time.perf_counter()-start,stage_saved_bytes=core.saved_bytes()); save()
    print(json.dumps({k:r[k] for k in ('complete','status','errors','actual_synthetic_updates','synthetic_neural_forwards','elapsed_seconds','stage_saved_bytes')}),flush=True)
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__': raise SystemExit(main())
