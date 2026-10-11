"""Bind completed archive and actual latest live observations; no invented training exit."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def main():
    sys.stdout.reconfigure(encoding='utf-8');manifest=ROOT/'literature/real_support_stage_manifest_2026-10-07.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_REAL_SUPPORT_2026-10-07.json';m=read(manifest);p=read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and sha(manifest)==p['manifest_sha256']
    assert len(m['stage_files'])==79 and len(m['evidence_files'])==1516 and m['stage_bytes']==9484187
    assert p['previous1431_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified']
    observed=ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_REAL_SUPPORT_2026-10-07.json';obs=read(observed)
    assert obs['archive']['observed_tool_exit']==0 and obs['archive']['observed_tool_chunk']=='cfd61d'
    train=obs['training'];assert train['session_id']==99542 and 'exit_code' not in train
    last=json.loads(train['output'].splitlines()[-1]);assert last['kind']=='native_reference' and last['updates']==10395 and last['new_updates']==10296
    receipt=ROOT/'SESSION_CHECKPOINT_RECEIPT_REAL_SUPPORT_2026-10-07.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(x) for x in
        (Path(__file__),manifest,proof,observed,ROOT/'SESSION_POST_ARCHIVE_REAL_SUPPORT_UPDATE_2026-10-07.md',ROOT/'SESSION_FINAL_REPLY_REAL_SUPPORT_ACTUAL_2026-10-07.md')],
        archive_actual_observed_tool_chunk='cfd61d',archive_actual_observed_tool_exit=0,new_stage_files_frozen=79,
        cumulative_frozen_evidence_files=1516,stage_bytes=9484187,previous1431_evidence_hashes_unchanged=True,
        live_training_session=99542,latest_training_poll_tool_chunk=train['chunk_id'],native_updates=last['updates'],
        invocation02_new_updates=last['new_updates'],cumulative_wall_seconds=last['cumulative_wall_seconds'],
        full_training_observed_tool_exit=None,formal_final_budget_completed=False,original_56FOV_evaluated=False,
        real19series_resource_qualification_completed=False,PCHIP99_is_historical=True,
        latest_GPU_query=obs['gpu'],new_GPU8GB_margin_met=False,new_primary_papers_read=3,
        main_text_pages_read=24,visual_pages_reviewed=7,developer_label_reads=38,checked_series=19,checked_supports=38,checked_single_plane_actions=806,
        new_MRI_pixel_arrays_loaded=0,new_model_or_GPU_forwards=0,new_training_updates=0,
        actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False,old_MIRA_MSValid84_confirmation_preserved=True,
        current_lesion_confirmation_patients=0,confirmation_patients_opened=False,goal_status='active',current_goal_turn_classification='progress',
        this_receipt_and_new_final_observations_are_post_manifest_appendices=True)
    with receipt.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,receipt_file=receipt.relative_to(ROOT).as_posix(),receipt_sha256=sha(receipt),archive_observed_tool_exit=0,
        live_training_session=99542,native_updates=10395,new_primary_papers_read=3,goal_status='active',publication_claim_confirmed=False)));return 0
if __name__=='__main__':raise SystemExit(main())
