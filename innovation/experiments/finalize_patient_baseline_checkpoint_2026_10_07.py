"""Bind successful archive and final actual observations; no goal-completion assertion."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=ROOT/'literature/patient_baseline_stage_manifest_2026-10-07.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_PATIENT_BASELINE_2026-10-07.json'
    m=json.loads(manifest.read_text(encoding='utf-8'));p=json.loads(proof.read_text(encoding='utf-8'))
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and p['manifest_sha256']==sha(manifest)
    assert len(m['stage_files'])==39 and len(m['evidence_files'])==1431 and m['stage_bytes']==380708
    assert p['previous1386_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified']
    reply=ROOT/'SESSION_FINAL_REPLY_PATIENT_BASELINE_ACTUAL_2026-10-07.md'
    update=ROOT/'SESSION_POST_ARCHIVE_PATIENT_BASELINE_UPDATE_2026-10-07.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive_observed_tool_chunk='87369e',archive_observed_tool_exit=0,
        manifest_file=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha(manifest),
        archive_file=proof.relative_to(ROOT).as_posix(),archive_sha256=sha(proof),
        new_stage_files_frozen=39,cumulative_frozen_evidence_files=1431,stage_bytes=380708,
        previous1386_evidence_hashes_unchanged=True,metadata_record_observed_tool_chunk='20138e',metadata_record_observed_tool_exit=0,
        actual_final_reply_file=reply.relative_to(ROOT).as_posix(),actual_final_reply_sha256=sha(reply),
        post_archive_update_file=update.relative_to(ROOT).as_posix(),post_archive_update_sha256=sha(update),
        live_training_session=99542,latest_actual_training_poll=dict(chunk='0bc35c',native_updates=9504,
            invocation02_new_updates=9405,cumulative_wall_seconds=20966.394249100005,returned_session=99542),
        latest_GPU_query=dict(chunk='29e341',timestamp_local='2026/10/07 21:37:16.708',free_MiB=1394,total_MiB=24455,utilization_percent=91),
        PCHIP99_is_historical_not_realtime=True,full_training_observed_tool_exit=None,formal_final_budget_completed=False,
        original_56FOV_evaluated=False,real19series_resource_qualification_completed=False,
        synthetic_qualifications=3,independent_verifiers=2,independent_selections=9,independent_risk_pvalues=104,
        independent_patient_panels=3,independent_patient_policy_rows=8,new_primary_papers_read=0,
        new_MRI_pixels_or_GT_reads=0,new_model_or_GPU_forwards=0,new_training_updates=0,
        actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False,
        current_lesion_confirmation_patients=0,old_MIRA_MSValid84_confirmation_preserved=True,
        previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
        this_receipt_and_actual_reply_are_post_manifest_appendices=True,goal_status='active',
        finalize_script_sha256=sha(__file__))
    path=ROOT/'SESSION_CHECKPOINT_RECEIPT_PATIENT_BASELINE_2026-10-07.json'
    with path.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,new_stage_files_frozen=39,cumulative_frozen_evidence_files=1431,
        archive_actual_exit=0,goal_status='active',publication_claim_confirmed=False)));return 0
if __name__=='__main__':raise SystemExit(main())
