"""Resolve actually indexed title/author identities before fetching any preprint."""
import sys,time,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_attempt04'
base=prior.base;resource_guard=prior.resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();assert shutil.disk_usage(ROOT).free>8_050_000_000
    OUT.mkdir(exist_ok=False);prior.OUT=OUT;tick=time.perf_counter()
    cutoff=' AND submittedDate:[199101010000 TO 202610082359]'
    jobs=[('acar_segmentation_aware','arxiv','au:Acar AND ti:reconstruction AND (all:MRI OR all:"magnetic resonance")'+cutoff),
        ('xu_oksuz_subsampling','arxiv','au:Xu AND au:Oksuz AND (all:subsampling OR all:"sub-sampling") AND (all:MRI OR all:"magnetic resonance")'+cutoff)]
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(prior.fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),
        errors=[e for r in rows for e in r['errors']],records=rows,source_bindings=[base.entry(p) for p in
        (Path(__file__),HERE/'PROTOCOL.md',HERE/'INDEX_SELECTION_FOLLOWUP.md',HERE/'query_seranet_stdlib_v3.py',HERE/'index_attempt03/receipt.json')],
        public_GET_only=True,TLS_verification_disabled=False,automatic_retries=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_primary_papers_read=0,elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],errors=result['errors'],records=[dict(key=r['key'],
        total_results=r.get('total_results'),entries=r.get('entries',[]),errors=r['errors']) for r in rows]),ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
