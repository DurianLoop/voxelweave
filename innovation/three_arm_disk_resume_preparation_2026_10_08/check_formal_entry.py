"""Preparation/defer entry only: no torch/numpy imports or medical training."""
import argparse,subprocess,sys,time,traceback
from pathlib import Path
import disk_resume_core as core

def main():
    sys.stdout.reconfigure(encoding='utf-8'); ap=argparse.ArgumentParser()
    ap.add_argument('--device',choices=('cpu','gpu'),required=True); ap.add_argument('--attempt',required=True); a=ap.parse_args()
    assert a.attempt.isdigit() and len(a.attempt)==2
    out=core.HERE/('formal_entry_'+a.device+'_attempt'+a.attempt); out.mkdir(exist_ok=False); tick=time.perf_counter()
    r=dict(created_utc=core.now(),complete=False,status='checking_prerequisites',errors=[],requested_device=a.device,
           medical_arrays_loaded=0,model_checkpoint_arrays_loaded=0,neural_forwards=0,actual_training_updates=0,
           neural_modules_imported=False,CUDA_initialized=False,formal_training_budget_frozen=False,
           formal_long_training_entry_implemented=False,publication_claim_confirmed=False,goal_status='active')
    code=1
    try:
        r['resources_before_neural_import']=core.guard(tick,120)
        checker=core.ROOT/'experiments/check_mc_rc_3d_paired_resource_readiness_2026_10_07.py'
        readiness=out/'original_readiness.json'
        p=subprocess.run([sys.executable,'-X','utf8','-B',str(checker),'--output',readiness.relative_to(core.ROOT).as_posix()],capture_output=True,timeout=60)
        core.new_bytes(out/'readiness_stdout.txt',p.stdout); core.new_bytes(out/'readiness_stderr.txt',p.stderr)
        q=core.read(readiness)
        r.update(readiness_process_exit=p.returncode,missing_prerequisites=q['missing_files'],failed_prerequisite_conditions=q['failed_conditions'],
                 mutable_training_read_observations_not_frozen=q.get('mutable_read_observations_not_frozen',[]),
                 source_bindings=[core.entry(Path(__file__)),core.entry(core.HERE/'PROTOCOL.md'),core.entry(checker),core.entry(readiness)])
        assert q['complete'] and not q['errors'] and p.returncode in (0,3)
        pending=[core.HERE/'QUALIFICATION_OBSERVED_EXITS.json',core.ROOT/'three_arm_resource_bridge_2026_10_08/REAL_RESOURCE_OBSERVED_EXITS.json',
                 core.HERE/'FORMAL_TRAINING_CONFIG.json']
        r['later_stage_required_files_missing']=[v.relative_to(core.ROOT).as_posix() for v in pending if not v.is_file()]
        if not q['ready']:
            r.update(complete=True,status='original_capability_prerequisite_deferred'); code=3
        elif r['later_stage_required_files_missing']:
            r.update(complete=True,status='formal_resource_and_budget_preparation_deferred'); code=3
        else:
            # Presence alone cannot qualify future contracts or authorize an invented budget.
            r.update(complete=True,status='future_formal_contract_independent_audit_required'); code=3
        r.update(torch_in_sys_modules='torch' in sys.modules,numpy_in_sys_modules='numpy' in sys.modules)
        assert not r['torch_in_sys_modules'] and not r['numpy_in_sys_modules']
    except Exception as e:
        r['errors'].append(f'{type(e).__name__}: {e}'); r['traceback']=traceback.format_exc()
    r.update(finished_utc=core.now(),elapsed_seconds=time.perf_counter()-tick)
    core.new_json(out/'receipt.json',r)
    print(core.json.dumps({k:r.get(k) for k in ('complete','status','errors','readiness_process_exit','neural_modules_imported','actual_training_updates','elapsed_seconds')}),flush=True)
    return code
if __name__=='__main__': raise SystemExit(main())
