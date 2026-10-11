"""Two named public MRI joint-task index searches; never write outside this stage."""
import sys,json,time,shutil
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard()
    assert shutil.disk_usage(ROOT).free>8_050_000_000
    OUT.mkdir(exist_ok=False);base.OUT=OUT
    cutoff=' AND submittedDate:[199101010000 TO 202610082359]'
    jobs=[('segnetmri','arxiv','all:SegNetMRI'+cutoff),('seranet','arxiv','all:SERANet'+cutoff)]
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(base.fetch,jobs))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[],records=rows,source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',
        ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py')],
        public_GET_only=True,TLS_verification_disabled=False,new_primary_papers_read=0,
        medical_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        original_training_modified=False,new_agents_delegated=0,elapsed_seconds=time.perf_counter()-start)
    base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],records=rows),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())

