"""Seek a primary static-control article after thesis exceeds the PDF bound."""
import sys,json,shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();assert shutil.disk_usage(ROOT).free>8_050_000_000
    out=HERE/'static_index_attempt01';out.mkdir(exist_ok=False);base.OUT=out
    cut=' AND submittedDate:[199101010000 TO 202610082359]'
    jobs=[('stochastic_LBCS','arxiv','all:"stochastic LBCS"'+cut),
        ('Sanchez_RL_MRI','arxiv','au:Sanchez AND (all:MRI OR all:"magnetic resonance") AND (all:reinforcement OR all:LBCS)'+cut)]
    with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(base.fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(r['complete'] for r in rows),errors=[],records=rows,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'PROTOCOL.md'),
            base.entry(HERE/'primary_attempt01/receipt.json'),base.entry(ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py')],
        provider_default_order=True,max_rows_per_query=8,new_primary_papers_read=0,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,goal_status='active')
    base.new(out/'receipt.json',result)
    print(json.dumps(dict(complete=result['complete'],groups=[dict(key=r['key'],total=r.get('total_results'),
        entries=[{k:e.get(k) for k in ('id','title','authors','summary')} for e in r.get('entries',[])],errors=r['errors']) for r in rows]),
        ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
