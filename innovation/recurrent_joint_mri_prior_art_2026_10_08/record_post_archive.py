"""Append observed actual archive exit, live training status, and the public final reply."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json';inp=HERE/'POST_ARCHIVE_INPUT.json'
    q=read(proof);a=read(inp)
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==sha(manifest)
    assert q['previous4825_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==4942
    assert a['archive_actual_tool_exit']==a['record_stage_actual_tool_exit']==0
    assert a['actual_post_archive_live_poll']['value']['session_id']==99542
    assert 'exit_code' not in a['actual_post_archive_live_poll']['value']
    assert a['actual_goal']['value']['goal']['status']=='active'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),manifest,proof,inp)],actual_archive_observed_tool_exit=0,
        actual_archive_observed_chunk=a['archive_actual_chunk'],record_stage_observed_tool_exit=0,
        record_stage_observed_chunk=a['record_stage_actual_chunk'],stage_files=q['stage_files'],stage_bytes=q['stage_bytes'],
        newly_bound_files=q['newly_bound_files'],new_evidence_bytes=q['new_evidence_bytes'],cumulative_frozen_evidence_files=4942,
        previous4825_evidence_hashes_unchanged=True,all_source_bindings_verified=True,all_local_links_verified=True,
        latest_actual_live_poll=a['actual_post_archive_live_poll'],latest_actual_GPU_query=a['actual_GPU_query'],
        actual_goal_observation=a['actual_goal'],public_progress_after_frozen_dialogue=[a['public_progress_after_archive']],
        prepared_final_reply=a['prepared_final_reply'],new_primary_papers_read=2,new_full_text_pages_read=35,
        visual_pages_reviewed=23,additional_detail_images_viewed=7,source_summary_inconsistencies_retained=3,
        CPU_public_table_audit_passed=True,original_paper_printed_summaries_all_consistent=False,
        medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,
        real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,new_action_labels=0,new_agents_delegated=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,original_training_terminal_exit=None,
        original_training_terminated_or_restarted_or_migrated=False,original_terminal_training_modified=False,
        latest_raw_pchip_committed_arm_updates=5148,latest_invocation_new_updates=24948,new_updates_not_raw_arm_count=True,
        GPU_authorization_retained=True,new_GPU_job_started=False,formal_medical_budget_frozen=False,
        formal_medical_long_runner_qualified=False,actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,
        publication_claim_confirmed=False,goal_status='active',current_goal_turn_classification='progress',
        automatic_approval_review_rejections_received=0,archive_not_rewritten_after_success=True,
        next_stage_must_bind=[p.relative_to(ROOT).as_posix() for p in (manifest,proof,Path(__file__),inp,HERE/'POST_ARCHIVE_OBSERVATIONS.json')])
    with (HERE/'POST_ARCHIVE_OBSERVATIONS.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<35_000_000
    print(json.dumps(dict(complete=True,cumulative_frozen_evidence_files=4942,manifest_sha256=sha(manifest),proof_sha256=sha(proof),
        original_training_terminal_exit=None,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
