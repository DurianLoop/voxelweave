"""Three bounded identity searches after an arXiv acronym search returned zero."""
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
    OUT.mkdir(exist_ok=False);base.OUT=OUT;tick=time.perf_counter()
    jobs=[('seranet_crossref','crossref','SERANet'),
        ('segmentation_aware_crossref','crossref','Segmentation-aware MRI reconstruction'),
        ('segmentation_aware_arxiv','arxiv','all:"segmentation-aware" AND (all:MRI OR all:"magnetic resonance") AND submittedDate:[199101010000 TO 202610082359]')]
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(base.fetch,jobs))
    q=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[base.entry(p) for p in
        (Path(__file__),HERE/'PROTOCOL.md',ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py',
         ROOT/'joint_segmentation_mri_prior_art_2026_10_08/index_attempt01/receipt.json')],
        public_GET_only=True,TLS_verification_disabled=False,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_agents_delegated=0,
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',q)
    print(json.dumps(dict(complete=q['complete'],errors=q['errors'],records=[dict(key=r['key'],
        complete=r['complete'],total_results=r.get('total_results'),entries=r.get('entries',[]),errors=r['errors']) for r in rows]),ensure_ascii=False),flush=True)
    return int(not q['complete'])
if __name__=='__main__':raise SystemExit(main())
