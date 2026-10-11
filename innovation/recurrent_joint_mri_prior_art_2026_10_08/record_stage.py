"""Create the execution ledger after actual readings, audit exit and live observations."""
import json,sys,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_guard();tick=time.perf_counter()
    obs=read(HERE/'ACTUAL_OBSERVATIONS.json');reading=read(HERE/'READING_PROVENANCE.json')
    audit=read(HERE/'table_audit_attempt02/receipt.json')
    assert all(q['complete'] and not q['errors'] for q in [reading,audit])
    assert obs['latest_actual_live_poll']['value']['session_id']==99542
    assert 'exit_code' not in obs['latest_actual_live_poll']['value']
    assert obs['actual_goal']['value']['goal']['status']=='active'
    assert obs['latest_actual_GPU_query']['value']['exit_code']==0
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=ROOT.parent/name;got=hashlib.sha256(p.read_bytes()).hexdigest();assert got==expected
        roots.append(dict(path=str(p),sha256=got,previous_sha256=expected))
    sources=[Path(__file__),HERE/'PROTOCOL.md',HERE/'PRIMARY_READING.md',HERE/'SUPERVISION_ROUTING_AND_CHECKPOINT_PREPARATION.md',
        HERE/'READING_PROVENANCE.json',HERE/'ACTUAL_OBSERVATIONS.json',HERE/'RESULT.md',HERE/'NEXT_STAGE_HANDOFF.md',
        HERE/'VISIBLE_DIALOGUE.md',HERE/'USER_PROVIDED_HANDOFF.md',
        ROOT/'task_adaptation_compute_prior_art_2026_10_08/query_primary.py',
        ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py']
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[base.entry(p) for p in sources],new_primary_papers_read=2,new_full_text_pages_read=35,
        main_or_figure_pages_read=34,reference_only_pages_read=1,visual_pages_reviewed=23,additional_detail_images_viewed=7,
        current_unique_title_abstracts_screened=16,downloaded_extracted_pages=39,
        index_identity_audit=reading['index_identity_audit'],source_summary_inconsistencies=3,
        CPU_public_table_audit_passed=True,original_paper_printed_summaries_all_consistent=False,
        actual_execution_observations=obs['executed_stage_commands'],actual_source_arithmetic_inconsistencies=audit['source_printed_summary_inconsistencies'],
        retained_failures=['ccf0cc inline quotation exit1','fe7098 source arithmetic mismatch exit1',
            'be971c CIM query access denied within process exit0','a389b9 mistyped text file path within process exit0'],
        resource_snapshot=resources,root_files_observed=roots,original_training_latest_actual_poll=obs['latest_actual_live_poll'],
        latest_actual_GPU_query=obs['latest_actual_GPU_query'],actual_goal_observation=obs['actual_goal'],
        original_training_terminal_exit=None,original_training_modified=False,original_training_terminated_restarted_or_migrated=False,
        invocation_new_updates_not_raw_arm_steps=True,GPU_authorization_retained=True,new_GPU_job_started=False,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,
        real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,new_final_action_labels_generated=0,
        new_agents_delegated=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        author_code_read=False,author_medical_experiments_reproduced=False,formal_medical_budget_frozen=False,
        formal_medical_long_runner_qualified=False,actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,
        publication_claim_confirmed=False,goal_status='active',current_goal_turn_classification='progress',
        automatic_approval_review_rejections_received=0,elapsed_seconds=time.perf_counter()-tick)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    print(json.dumps(dict(complete=True,new_primary_papers_read=2,new_full_text_pages_read=35,visual_pages_reviewed=23,
        retained_source_summary_inconsistencies=3,root_hashes_unchanged=True,resource_snapshot=resources,
        original_training_terminal_exit=None,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
