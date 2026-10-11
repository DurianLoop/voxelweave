"""Post-manifest appendix binds actual archive exit and public final wording only."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    archive=ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_OBSERVED_2026-10-07.json'
    manifest=ROOT/'literature/direct_observed_stage_manifest_2026-10-07.json'
    a=json.loads(archive.read_text(encoding='utf-8'))
    assert a['complete'] and not a['errors'] and a['manifest_sha256']==sha(manifest)
    assert a['previous_frozen_evidence_files_verified']==1032 and a['stage_files']==94 and a['evidence_files']==1130
    draft=ROOT/'SESSION_FINAL_REPLY_DIRECT_OBSERVED_2026-10-07.md'
    actual=ROOT/'SESSION_FINAL_REPLY_DIRECT_OBSERVED_ACTUAL_2026-10-07.md';assert not actual.exists()
    actual.write_bytes(draft.read_bytes())
    receipt=dict(archive_observed_tool_chunk='c5b1db',archive_observed_tool_exit=0,
        archive_file=archive.relative_to(ROOT).as_posix(),archive_sha256=sha(archive),
        manifest_file=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha(manifest),
        new_stage_files_frozen=94,cumulative_frozen_evidence_files=1130,stage_bytes=40858779,
        previous1032_evidence_hashes_unchanged=True,own_live_training_session=99542,
        latest_actual_training_poll_at_stage_checkpoint='42bef7',native_committed_update_observed_at_checkpoint=5940,
        full_training_observed_tool_exit=None,formal_final_budget_completed=False,final_models_evaluated=False,
        current_3D_lesion_confirmation_patients=0,whole_project_confirmation_zero_not_claimed=True,
        publication_claim_confirmed=False,goal_status='active',
        actual_final_reply_file=actual.relative_to(ROOT).as_posix(),actual_final_reply_sha256=sha(actual),
        this_receipt_and_actual_reply_are_post_manifest_appendices=True)
    with (ROOT/'SESSION_CHECKPOINT_RECEIPT_DIRECT_OBSERVED_2026-10-07.json').open('x',encoding='utf-8') as f:
        json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,archive_tool_exit=0,new_stage_files=94,frozen_evidence_files=1130,goal_status='active')))
    return 0
if __name__=='__main__':raise SystemExit(main())
