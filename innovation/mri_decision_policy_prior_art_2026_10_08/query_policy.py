"""New bounded policy queries using the existing verified public GET helper."""
import json,sys,shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
OUT=HERE/'index_attempt01'

def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();assert shutil.disk_usage(ROOT).free>8_050_000_000
    OUT.mkdir(exist_ok=False);base.OUT=OUT
    cutoff=' AND submittedDate:[199101010000 TO 202610082359]'
    jobs=[('mri_RL_state','arxiv','(all:MRI OR all:"magnetic resonance") AND (all:"reinforcement learning" OR all:"policy network") AND (all:reconstruction OR all:"super-resolution")'+cutoff),
        ('downstream_selection','arxiv','(ti:restoration OR ti:reconstruction OR ti:"super-resolution") AND (all:downstream OR all:"task-aware") AND (all:selection OR all:adaptive OR all:reinforcement)'+cutoff),
        ('mri_task_decision','arxiv','(all:MRI OR all:"magnetic resonance") AND (all:reconstruction OR all:"super-resolution") AND (all:"decision-focused" OR all:"task-specific" OR all:"task-driven")'+cutoff)]
    # The reused helper takes at most8rows. Query excludes future submissions;
    # its order is provider-default, not claimed as sorted search.
    with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(base.fetch,jobs))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=all(v['complete'] for v in rows),errors=[],records=rows,
        source_bindings=[base.entry(Path(__file__)),base.entry(HERE/'PROTOCOL.md'),
            base.entry(ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py')],
        public_GET_only=True,TLS_verification_disabled=False,source_helper_outputs_redirected_to_new_stage=True,
        new_primary_papers_read=0,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,training_updates=0,goal_status='active')
    base.new(OUT/'receipt.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
