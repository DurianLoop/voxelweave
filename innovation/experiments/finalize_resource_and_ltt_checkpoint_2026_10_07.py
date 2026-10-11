"""Post-manifest receipt binds the actual successful archive and latest live observations."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=ROOT/'literature/resource_and_ltt_stage_manifest_2026-10-07.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_RESOURCE_AND_LTT_2026-10-07.json'
    m=json.loads(manifest.read_text(encoding='utf-8'));p=json.loads(proof.read_text(encoding='utf-8'))
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and p['manifest_sha256']==sha(manifest)
    assert len(m['stage_files'])==140 and len(m['evidence_files'])==1386 and m['stage_bytes']==12634128
    assert p['previous1240_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified']
    reply=ROOT/'SESSION_FINAL_REPLY_RESOURCE_AND_LTT_ACTUAL_2026-10-07.md'
    update=ROOT/'SESSION_POST_ARCHIVE_RESOURCE_AND_LTT_UPDATE_2026-10-07.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive_observed_tool_chunk='46625f',archive_observed_tool_exit=0,
        manifest_file=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha(manifest),
        archive_file=proof.relative_to(ROOT).as_posix(),archive_sha256=sha(proof),
        new_stage_files_frozen=140,cumulative_frozen_evidence_files=1386,stage_bytes=12634128,
        previous1240_evidence_hashes_unchanged=True,
        metadata_record_observed_tool_chunk='6e2c64',metadata_record_observed_tool_exit=0,
        actual_final_reply_file=reply.relative_to(ROOT).as_posix(),actual_final_reply_sha256=sha(reply),
        post_archive_update_file=update.relative_to(ROOT).as_posix(),post_archive_update_sha256=sha(update),
        live_training_session=99542,
        latest_actual_training_poll=dict(chunk='b89051',native_updates=8712,invocation02_new_updates=8613,
            cumulative_wall_seconds=19124.343475600006,returned_session=99542),
        latest_GPU_query=dict(chunk='15d1ae',timestamp_local='2026/10/07 21:07:27.097',free_MiB=1394,total_MiB=24455,utilization_percent=50),
        PCHIP99_is_historical_not_realtime=True,full_training_observed_tool_exit=None,
        formal_final_budget_completed=False,final_models_evaluated=False,real19series_resource_qualification_completed=False,
        primary_papers_selected_read=2,successful_PDF_pages=58,complete_selected_unique_pages_read=27,actual_visual_pages_reviewed=10,
        stage_synthetic_workflow_updates=8,new_MRI_data_reads=0,new_MRI_forwards=0,new_GPU_forwards=0,
        publication_claim_confirmed=False,current_lesion_confirmation_patients=0,old_MIRA_MSValid84_confirmation_preserved=True,
        this_receipt_and_final_reply_are_post_manifest_appendices=True,goal_status='active',finalize_script_sha256=sha(__file__))
    path=ROOT/'SESSION_CHECKPOINT_RECEIPT_RESOURCE_AND_LTT_2026-10-07.json'
    with path.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,new_stage_files_frozen=140,cumulative_frozen_evidence_files=1386,
        archive_actual_exit=0,goal_status='active',publication_claim_confirmed=False)));return 0
if __name__=='__main__':raise SystemExit(main())
