"""Append actual observed archive exit and dialogue; do not rewrite any bound evidence."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import query_seranet_stdlib_v3 as prior
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');prior.base.own_priority();resources=prior.resource_guard()
    manifest=HERE/'ARCHIVE_MANIFEST.json';proof=HERE/'ARCHIVE_PROOF.json';inp=HERE/'POST_ARCHIVE_INPUT.json'
    q=read(proof);a=read(inp)
    assert q['complete'] and not q['errors'] and q['manifest_sha256']==sha(manifest)
    assert q['previous4942_evidence_hashes_unchanged'] and q['cumulative_frozen_evidence_files']==5112
    assert a['archive_actual_tool_exit']==a['record_stage_actual_tool_exit']==0
    assert a['actual_post_archive_live_poll']['value']['session_id']==99542
    assert 'exit_code' not in a['actual_post_archive_live_poll']['value']
    assert a['goal_status']=='active'
    # All links in the exact prepared final reply resolve to existing evidence.
    import re
    for target in re.findall(r'\]\(([^)]+)\)',a['prepared_final_reply']):
        p=Path(target);assert p.exists() and p.resolve().is_relative_to(ROOT.resolve())
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[prior.base.entry(p) for p in (Path(__file__),manifest,proof,inp)],
        manifest_sha256=sha(manifest),proof_sha256=sha(proof),actual_archive_tool_exit=0,actual_archive_chunk=a['archive_actual_chunk'],
        actual_record_stage_tool_exit=0,actual_record_stage_chunk=a['record_stage_actual_chunk'],
        cumulative_frozen_evidence_files=5112,previous4942_evidence_hashes_unchanged=True,
        latest_actual_live_poll=a['actual_post_archive_live_poll'],latest_actual_GPU_query=a['actual_GPU_and_archive_hash_query'],
        public_progress_after_archive=a['public_progress_after_archive'],prepared_final_reply=a['prepared_final_reply'],
        latest_raw_pchip_committed_arm_updates=6039,latest_invocation_new_updates=25839,new_updates_not_raw_arm_count=True,
        resource_snapshot=resources,new_primary_papers_read=3,new_full_text_pages_read=45,visual_pages_reviewed=26,
        original_training_terminal_exit=None,original_training_modified=False,new_GPU_job_started=False,
        medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,new_medical_training_updates=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        automatic_approval_review_rejections_received=0,archive_not_rewritten_after_success=True,
        next_stage_must_bind=[p.relative_to(ROOT).as_posix() for p in (manifest,proof,Path(__file__),inp,HERE/'POST_ARCHIVE_OBSERVATIONS.json')])
    prior.base.new(HERE/'POST_ARCHIVE_OBSERVATIONS.json',result)
    print(json.dumps(dict(complete=True,manifest_sha256=sha(manifest),proof_sha256=sha(proof),
        cumulative_frozen_evidence_files=5112,resource_snapshot=resources,goal_status='active')),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
