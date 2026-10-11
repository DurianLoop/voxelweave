"""Bind the two observed process exits and existing input qualifications."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    production=HERE/'synthetic_attempt01/receipt.json';verification=HERE/'independent_attempt01/receipt.json'
    q,v=read(production),read(verification)
    assert q['complete'] and v['complete'] and not q['errors'] and not v['errors'] and all(q['gate'].values())
    assert q['actual_resource_updates']==12 and q['completed_model_forward_calls']==36 and v['independent_batch_count']==9
    assert v['new_worker_imported'] is False and v['neural_forwards']==v['training_updates']==0
    foundations=[ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json',
        ROOT/'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json',
        ROOT/'experiments/common_projected_observed_independent_precision_v2_2026_10_08/attempt01.json']
    for p in foundations:
        f=read(p);assert f['complete'] and not f['errors']
    for doc in (q,v):
        for b in doc['source_bindings']:assert entry(ROOT/b['path'])['sha256']==b['sha256']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(production),entry(verification),entry(HERE/'run_three_arm_real_resource.py')]+[entry(p) for p in foundations],
        synthetic_observed_tool_exit=0,synthetic_observed_chunk='84810c',synthetic_session_id=64443,
        synthetic_result_file=production.relative_to(ROOT).as_posix(),synthetic_result_sha256=entry(production)['sha256'],
        verifier_observed_tool_exit=0,verifier_observed_chunk='6c8fd2',
        verifier_result_file=verification.relative_to(ROOT).as_posix(),verifier_result_sha256=entry(verification)['sha256'],
        three_arm_dispatch_qualified=True,synthetic_updates=12,synthetic_neural_forwards=36,independent_batch_checks=9,
        real_medical_resource_qualification_completed=False,real_medical_formal_training_started=False,
        medical_arrays_loaded=0,GPU_forwards=0,task_effects_scored=False,publication_claim_confirmed=False,goal_status='active')
    with (HERE/'SYNTHETIC_OBSERVED_EXITS.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,synthetic_observed_tool_exit=0,verifier_observed_tool_exit=0,independent_batch_checks=9)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
