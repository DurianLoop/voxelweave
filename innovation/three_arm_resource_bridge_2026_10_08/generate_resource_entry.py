"""Explicit bounded transformation of the frozen gated two-arm launcher."""
import ast,hashlib,json,difflib,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE=ROOT/'experiments/run_mc_rc_3d_paired_real_resource_v2_2026_10_07.py'
DEST=HERE/'run_three_arm_real_resource.py'
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not DEST.exists()
    original=BASE.read_text(encoding='utf-8');text=original
    changes=[
        ('ROOT=Path(__file__).resolve().parents[1]',
         "HERE=Path(__file__).resolve().parent\nROOT=HERE.parent\nsys.path.insert(0,str(ROOT/'experiments'))"),
        ("PROTOCOL=ROOT/'MC_RC_3D_PAIRED_REAL_RESOURCE_ENTRY_PROTOCOL_2026-10-07.md'","PROTOCOL=HERE/'PROTOCOL.md'"),
        ("WORKER=ROOT/'experiments/mc_rc_3d_paired_resource_worker_2026_10_07.py'","WORKER=HERE/'three_arm_resource_worker.py'"),
        ("out=ROOT/('experiments/mc_rc_3d_paired_real_resource_v2_2026_10_07_'+args.device+'_attempt'+args.attempt)",
         "out=HERE/('real_resource_'+args.device+'_attempt'+args.attempt)"),
        ("cert=ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/attempt01.json'","cert=HERE/'synthetic_attempt01/receipt.json'"),
        ("receipt=ROOT/'SESSION_OBSERVED_EXITS_PAIRED_RESOURCE_WORKFLOW_2026-10-07.json'","receipt=HERE/'SYNTHETIC_OBSERVED_EXITS.json'"),
        ('import mc_rc_3d_paired_resource_worker_2026_10_07 as worker','import three_arm_resource_worker as worker'),
        ("assert r['actual_resource_updates']==68 and not denied","assert r['actual_resource_updates']==102 and not denied"),
        ("r['entry_version']=2","r['entry_version']='three_arm_v1'\n    r['representation_arms']=['legacy_dense','direct','common_projected_dense']"),
    ]
    for a,b in changes:assert text.count(a)==1,a;text=text.replace(a,b,1)
    ast.parse(text)
    with DEST.open('x',encoding='utf-8') as f:f.write(text)
    diff=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=BASE.name,tofile=DEST.name))
    with (HERE/'RESOURCE_ENTRY_DIFF.patch').open('x',encoding='utf-8') as f:f.write(diff)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(BASE),entry(HERE/'PROTOCOL.md'),entry(HERE/'three_arm_resource_worker.py')],
        output_bindings=[entry(DEST),entry(HERE/'RESOURCE_ENTRY_DIFF.patch')],explicit_text_replacements=len(changes),
        source_original_unchanged=True,original_gates_preserved=True,resource_limits_and_CUDA_telemetry_preserved=True,
        old_source_coverage_not_claimed_for_new_worker=True,real_medical_job_launched=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,goal_status='active')
    with (HERE/'RESOURCE_ENTRY_GENERATION.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,explicit_text_replacements=len(changes),new_entry=entry(DEST)),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
