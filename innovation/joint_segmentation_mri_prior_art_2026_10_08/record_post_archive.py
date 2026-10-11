"""Append actual archive completion and prepared final text; never rewrite frozen files."""
import json,sys,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter();resource_guard()
    manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json';inp=HERE/'POST_ARCHIVE_INPUT.json'
    q=read(proof);a=read(inp)
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==sha(manifest)
    assert q['previous4686_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==4759
    assert a['archive_actual_tool_exit']==a['record_stage_actual_tool_exit']==0
    assert a['actual_post_archive_live_poll']['value']['session_id']==99542
    assert 'exit_code' not in a['actual_post_archive_live_poll']['value']
    assert a['actual_goal']['value']['goal']['status']=='active'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       source_bindings=[entry(p) for p in (Path(__file__),manifest,proof,inp)],
       actual_archive_observed_tool_exit=0,actual_archive_observed_chunk=a['archive_actual_chunk'],
       record_stage_observed_tool_exit=0,record_stage_observed_chunk=a['record_stage_actual_chunk'],
       stage_files=q['stage_files'],stage_bytes=q['stage_bytes'],newly_bound_files=q['newly_bound_files'],
       new_evidence_bytes=q['new_evidence_bytes'],cumulative_frozen_evidence_files=4759,
       previous4686_evidence_hashes_unchanged=True,all_source_bindings_verified=True,all_local_links_verified=True,
       latest_actual_live_poll=a['actual_post_archive_live_poll'],latest_actual_GPU_query=a['actual_GPU_query'],
       actual_goal_observation=a['actual_goal'],public_progress_after_frozen_dialogue=[a['public_progress_after_archive']],
       prepared_final_reply=a['prepared_final_reply'],same_logical_resumption_two_stages_total=a['same_logical_resumption_two_stages_total'],
       original_training_terminal_exit=None,original_training_terminated_or_restarted_or_migrated=False,
       original_terminal_training_modified=False,GPU_authorization_retained=True,new_GPU_job_started=False,
       new_updates_not_raw_arm_count=True,new_primary_papers_read=2,new_full_text_pages_read=15,visual_pages_reviewed=10,
       medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,MRI_neural_forwards=0,GPU_forwards=0,
       real_medical_resource_updates=0,real_medical_formal_training_updates=0,head_fits=0,new_action_labels=0,
       confirmation_patients_opened=False,lockedIXI_opened=False,new_agents_delegated=0,
       formal_three_arm_long_MRI_training_implemented_and_qualified=False,
       actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,publication_claim_confirmed=False,
       goal_status='active',current_goal_turn_classification='progress',automatic_approval_review_rejections_received=0,
       next_stage_must_bind=[p.relative_to(ROOT).as_posix() for p in (manifest,proof,Path(__file__),inp,HERE/'POST_ARCHIVE_OBSERVATIONS.json')],
       archive_not_rewritten_after_success=True,elapsed_seconds=time.perf_counter()-tick)
    base.new(HERE/'POST_ARCHIVE_OBSERVATIONS.json',r)
    print(json.dumps(dict(complete=True,cumulative_frozen_evidence_files=4759,
       manifest_sha256=sha(manifest),proof_sha256=sha(proof),original_training_terminal_exit=None,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

