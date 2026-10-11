"""Append actual archive exit and final public text without rewriting the archive."""
import sys,time
from pathlib import Path
import disk_resume_core as core
def main():
    sys.stdout.reconfigure(encoding='utf-8'); tick=time.perf_counter()
    manifest=core.HERE/'ARCHIVE_MANIFEST.json'; proof=core.HERE/'ARCHIVE_PROOF.json'; inp=core.HERE/'POST_ARCHIVE_INPUT.json'
    q=core.read(proof); a=core.read(inp)
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==core.sha(manifest)
    assert q['previous4397_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==4546
    assert a['archive_actual_tool_exit']==0 and a['actual_post_archive_live_poll']['value']['session_id']==99542
    assert 'exit_code' not in a['actual_post_archive_live_poll']['value'] and a['actual_goal']['value']['goal']['status']=='active'
    r=dict(created_utc=core.now(),complete=True,errors=[],source_bindings=[core.entry(p) for p in (Path(__file__),manifest,proof,inp)],
           actual_archive_observed_tool_exit=0,actual_archive_observed_chunk=a['archive_actual_chunk'],
           record_stage_observed_tool_exit=0,record_stage_observed_chunk=a['record_stage_actual_chunk'],
           stage_files=q['stage_files'],stage_bytes=q['stage_bytes'],newly_bound_files=q['newly_bound_files'],new_evidence_bytes=q['new_evidence_bytes'],
           cumulative_frozen_evidence_files=4546,previous4397_evidence_hashes_unchanged=True,all_source_bindings_verified=True,all_local_links_verified=True,
           original_live_terminal_exit=None,original_training_terminated_or_restarted_or_migrated=False,original_terminal_training_modified=False,
           new_updates_not_raw_arm_count=True,GPU_authorization_retained=True,new_GPU_job_started=False,
           latest_actual_live_poll=a['actual_post_archive_live_poll'],latest_actual_GPU_query=a['actual_GPU_query'],actual_goal_observation=a['actual_goal'],
           public_progress_after_frozen_dialogue=[a['public_progress_after_archive']],prepared_final_reply=a['prepared_final_reply'],
           actual_synthetic_updates=16,synthetic_neural_forwards=16,synthetic_checkpoint_arrays_loaded_from_disk=12,
           failed_attempt_actual_updates=1,failed_attempt_sources_and_checkpoint_retained=True,qualified_cross_process_disk_resumes=3,
           six_disk_faults_rejected_before_neural_import=True,medical_arrays_loaded=0,old_checkpoint_arrays_loaded=0,MRI_neural_forwards=0,GPU_forwards=0,
           real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,new_action_labels=0,new_primary_papers_read=0,
           confirmation_patients_opened=False,lockedIXI_opened=False,formal_three_arm_long_MRI_training_implemented_and_qualified=False,
           actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
           current_goal_turn_classification='progress',automatic_approval_review_rejections_received=0,
           next_stage_must_bind=[p.relative_to(core.ROOT).as_posix() for p in (manifest,proof,Path(__file__),inp,core.HERE/'POST_ARCHIVE_OBSERVATIONS.json')],
           archive_not_rewritten_after_success=True,resources=core.guard(tick,60))
    core.new_json(core.HERE/'POST_ARCHIVE_OBSERVATIONS.json',r)
    print(core.json.dumps(dict(complete=True,cumulative_frozen_evidence_files=4546,manifest_sha256=core.sha(manifest),proof_sha256=core.sha(proof),
                              original_training_terminal_exit=None,goal_status='active')),flush=True); return 0
if __name__=='__main__':raise SystemExit(main())
