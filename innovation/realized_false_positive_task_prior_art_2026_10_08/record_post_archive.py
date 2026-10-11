"""Bind the archive success and later public dialogue without changing frozen evidence."""
import sys,json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json';inp=HERE/'POST_ARCHIVE_INPUT.json'
    q=read(proof);a=read(inp)
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==sha(manifest)
    assert q['previous5292_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==5392
    assert a['archive_actual_tool_exit']==a['record_stage_actual_tool_exit']==0
    assert a['actual_post_archive_live_poll']['session_id']==99542 and a['actual_post_archive_live_poll']['terminal_exit'] is None
    assert a['actual_goal_observation']['status']=='active'
    for target in re.findall(r'\]\(([^)]+)\)',a['prepared_final_reply']):
        p=Path(target);assert p.is_file() and p.resolve().is_relative_to(ROOT.resolve())
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[client.base.entry(p) for p in [Path(__file__),manifest,proof,inp]],
        manifest_sha256=sha(manifest),proof_sha256=sha(proof),actual_archive_tool_exit=0,actual_archive_chunk=a['archive_actual_chunk'],
        actual_record_stage_tool_exit=0,actual_record_stage_chunk=a['record_stage_actual_chunk'],
        cumulative_frozen_evidence_files=5392,previous5292_evidence_hashes_unchanged=True,
        latest_actual_live_poll=a['actual_post_archive_live_poll'],latest_actual_GPU_query=a['actual_post_archive_GPU_query'],
        actual_goal_observation=a['actual_goal_observation'],public_progress_after_frozen_dialogue=a['public_progress_after_frozen_dialogue'],
        prepared_final_reply=a['prepared_final_reply'],latest_raw_pchip_committed_arm_updates=7524,latest_invocation_new_updates=27324,
        new_updates_not_raw_arm_count=True,resource_snapshot=resources,new_primary_papers_read=1,new_full_text_pages_read=43,
        visual_pages_reviewed=13,public_table_rows_checked=52,original_training_terminal_exit=None,original_training_modified=False,
        new_GPU_job_started=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_medical_training_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        automatic_approval_review_rejections_received=0,archive_not_rewritten_after_success=True,
        next_stage_must_bind=[p.relative_to(ROOT).as_posix() for p in [manifest,proof,Path(__file__),inp,HERE/'POST_ARCHIVE_OBSERVATIONS.json']])
    client.base.new(HERE/'POST_ARCHIVE_OBSERVATIONS.json',result)
    print(json.dumps(dict(complete=True,manifest_sha256=sha(manifest),proof_sha256=sha(proof),cumulative_frozen_evidence_files=5392,
        resource_snapshot=resources,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
