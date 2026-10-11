"""Bind actual archive completion and latest live poll, with no invented exit."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def main():
    sys.stdout.reconfigure(encoding='utf-8');manifest=ROOT/'literature/observed_roi_stage_manifest_2026-10-07.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_OBSERVED_ROI_2026-10-07.json';m=read(manifest);p=read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and sha(manifest)==p['manifest_sha256']
    assert len(m['stage_files'])==158 and len(m['evidence_files'])==1708 and m['stage_bytes']==23002490
    assert p['previous1516_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified']
    observed=ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_OBSERVED_ROI_2026-10-07.json';obs=read(observed)
    assert obs['archive']['actual_observed_tool_exit']==0 and obs['archive']['actual_observed_tool_chunk']=='0fb056'
    train=obs['training'];assert train['session_id']==99542 and train['full_training_observed_tool_exit'] is None
    latest=json.loads(train['output'].splitlines()[-1]);assert latest['updates']==11583 and latest['new_updates']==11484
    receipt=ROOT/'SESSION_CHECKPOINT_RECEIPT_OBSERVED_ROI_2026-10-07.json'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(x) for x in
        (Path(__file__),manifest,proof,observed,ROOT/'SESSION_POST_ARCHIVE_OBSERVED_ROI_UPDATE_2026-10-07.md',ROOT/'SESSION_PREPARED_FINAL_REPLY_OBSERVED_ROI_2026-10-07.md')],
        archive_actual_tool_chunk='0fb056',archive_actual_tool_exit=0,new_stage_files_frozen=158,cumulative_frozen_evidence_files=1708,
        stage_bytes=23002490,previous1516_evidence_hashes_unchanged=True,live_training_session=99542,
        latest_training_poll_tool_chunk='c13b8a',native_updates=latest['updates'],invocation02_new_updates=latest['new_updates'],
        cumulative_wall_seconds=latest['cumulative_wall_seconds'],full_training_observed_tool_exit=None,
        formal_final_budget_completed=False,original56FOV_evaluated=False,current_final_model_cache_output_equivalence_qualified=False,
        latest_GPU_query=obs['GPU'],new_GPU8GB_margin_met=False,new_primary_papers_read=2,text_pages_read=17,visual_pages_reviewed=4,
        unique_development_patients=8,unique_development_series=16,checked_cost_supports=64,checked_cost_plane_records=3456,
        checked_real_input_candidates=64,checked_literal_tile_equalities=4156,actual_observed_MRI_array_loads=33,
        new_GT_arrays_loaded=0,new_model_or_GPU_forwards=0,new_training_updates=0,actual_MRI_risk_certificates_issued=0,
        clinical_benefit_measured=False,actual_deployment_speed_benchmarked=False,publication_claim_confirmed=False,
        old_MIRA_MSValid84_confirmation_preserved=True,current_lesion_confirmation_patients=0,confirmation_patients_opened=False,
        goal_status='active',current_goal_turn_classification='progress',this_receipt_and_final_observations_are_post_manifest_appendices=True)
    with receipt.open('x',encoding='utf-8') as stream:json.dump(r,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(dict(complete=True,receipt_file=receipt.relative_to(ROOT).as_posix(),receipt_sha256=sha(receipt),
        archive_actual_tool_exit=0,live_training_session=99542,native_updates=11583,new_primary_papers_read=2,
        goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
