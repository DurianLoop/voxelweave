"""Freeze production measurement source and record cold child end-to-end wall time."""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/deployment_observed_feature_cost_launch_2026_10_08'


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def new(p,data):
    with p.open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    sources=['DEPLOYMENT_FEATURE_COST_AND_DOWNSTREAM_PROTOCOL_2026-10-08.md',
        'experiments/measure_deployment_observed_feature_cost_2026_10_08.py',
        'experiments/observed_holdout_feature_2026_10_08.py',
        'experiments/common_projected_input_audit_2026_10_08.py',
        'experiments/mc_rc_reference_resources_2026_10_07.py',
        'experiments/observed_holdout_feature_qualification_2026_10_08/attempt01.json',
        'experiments/observed_holdout_feature_independent_layout_v2_2026_10_08/attempt01.json',
        'experiments/observed_holdout_feature_table_2026_10_08.json']
    pre=ROOT/'experiments/deployment_observed_feature_cost_preregistration_2026_10_08.json'
    new(pre,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__))]+[entry(ROOT/p) for p in sources],
        repeats=1,warmups=0,expected_observed_packages=19,expected_real_folds=38,
        expected_neural_forwards=0,expected_GPU_forwards=0,expected_training_updates=0))
    env=os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES='-1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    start=time.perf_counter()
    proc=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'experiments/measure_deployment_observed_feature_cost_2026_10_08.py')],
        capture_output=True,env=env,timeout=1200)
    elapsed=time.perf_counter()-start
    (OUT/'child_stdout.txt').write_bytes(proc.stdout)
    (OUT/'child_stderr.txt').write_bytes(proc.stderr)
    body=ROOT/'experiments/deployment_observed_feature_cost_2026_10_08/attempt01.json'
    data=json.loads(body.read_text(encoding='utf-8')) if body.exists() else None
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=proc.returncode==0 and bool(data and data['complete']),
        errors=[] if proc.returncode==0 else [proc.stderr.decode('utf-8',errors='replace')],
        source_bindings=[entry(Path(__file__)),entry(pre)]+([entry(body)] if body.exists() else []),
        child_actual_subprocess_exit=proc.returncode,cold_child_end_to_end_wall_seconds=elapsed,
        timing_includes_process_start_imports_all_child_output_and_exit=True,
        timing_excludes_launcher_before_child_and_parent_receipt_write=True,
        child_body_complete=bool(data and data['complete']),child_body_errors=data['errors'] if data else None,
        cold_cache_state_controlled=False,original_live_training_excluded_from_medical_load_counts=True,
        publication_claim_confirmed=False,goal_status='active')
    new(OUT/'launch_attempt01.json',r)
    print(proc.stdout.decode('utf-8',errors='replace'),end='')
    print(json.dumps(dict(complete=r['complete'],child_actual_subprocess_exit=proc.returncode,
        cold_child_end_to_end_wall_seconds=elapsed,errors=r['errors']),ensure_ascii=False),flush=True)
    return int(not r['complete'])


if __name__=='__main__':raise SystemExit(main())
