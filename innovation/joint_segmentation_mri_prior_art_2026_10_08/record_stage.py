"""Freeze the measured stage ledger before archiving; do not touch live files."""
import json,sys,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();resource_guard();tick=time.perf_counter()
    a=read(HERE/'ACTUAL_OBSERVATIONS.json');r=read(HERE/'READING_PROVENANCE.json')
    assert r['complete'] and not r['errors'] and r['new_primary_papers_read']==2
    assert r['new_full_text_pages_read']==15 and r['visual_pages_reviewed']==10
    assert a['actual_reading_record']['value']['exit_code']==0
    assert a['actual_CPU_table_audit']['value']['exit_code']==0
    assert a['actual_live_poll']['value']['session_id']==99542 and 'exit_code' not in a['actual_live_poll']['value']
    assert a['actual_goal']['value']['goal']['status']=='active'
    roots=[]
    for p,expected in [(Path('D:/MRI/.gitignore'),'7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        (Path('D:/MRI/environment.yml'),'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==expected
        roots.append(dict(path=str(p),sha256=h,previous_sha256=expected))
    stage=[p for p in HERE.rglob('*') if p.is_file()]
    assert not any(p.suffix=='.pyc' for p in stage)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       source_bindings=[base.entry(p) for p in (Path(__file__),HERE/'ACTUAL_OBSERVATIONS.json',HERE/'READING_PROVENANCE.json',
       HERE/'PROTOCOL.md',HERE/'RESULT.md',HERE/'VISIBLE_DIALOGUE.md',HERE/'NEXT_STAGE_HANDOFF.md')],
       root_files_observed=roots,stage_bytes_before_ledger=sum(p.stat().st_size for p in stage),
       new_primary_papers_read=2,new_full_text_pages_read=15,visual_pages_reviewed=10,index_requests=3,
       index_unique_titles_abstracts_screened=8,new_public_table_audits_completed=1,
       medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,
       MRI_neural_forwards=0,GPU_forwards=0,real_medical_resource_updates=0,real_medical_formal_training_updates=0,
       head_fits=0,new_final_action_labels_generated=0,new_agents_delegated=0,
       confirmation_patients_opened=False,lockedIXI_opened=False,GPU_authorization_retained=True,new_GPU_job_started=False,
       original_terminal_training_not_modified=True,original_training_terminal_exit=None,
       original_live_observation=a['actual_live_poll'],actual_GPU_observation=a['actual_GPU_and_root_hash_query'],
       formal_three_arm_long_MRI_training_implemented_and_qualified=False,
       actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,
       publication_claim_confirmed=False,goal_status='active',current_goal_turn_classification='progress',
       automatic_approval_review_rejections_received=0,elapsed_seconds=time.perf_counter()-tick)
    base.new(HERE/'EXECUTION_LEDGER.json',result)
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,new_full_text_pages_read=15,
       visual_pages_reviewed=10,stage_bytes_before_ledger=result['stage_bytes_before_ledger'],
       medical_arrays_loaded=0,goal_status='active')),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())

