"""Follow title wording after the acronym query returned zero."""
import sys,json,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'index_followup_attempt01'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard()
    prior=json.loads((HERE/'index_attempt01/receipt.json').read_text(encoding='utf-8'))
    assert prior['complete'] and prior['records'][1]['total_results']=='0'
    OUT.mkdir(exist_ok=False);base.OUT=OUT
    query='ti:Joint AND (ti:MRI OR ti:"Magnetic Resonance") AND ti:Segmentation AND submittedDate:[199101010000 TO 202610082359]'
    tick=time.perf_counter();row=base.fetch(('joint_title','arxiv',query))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=row['complete'],errors=[],records=[row],
       source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'index_attempt01/receipt.json',
       ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py')],public_GET_only=True,
       TLS_verification_disabled=False,new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,
       GPU_forwards=0,new_agents_delegated=0,elapsed_seconds=time.perf_counter()-tick)
    base.new(OUT/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
