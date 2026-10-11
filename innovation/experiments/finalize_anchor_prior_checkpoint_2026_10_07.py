"""Bind actual archive exit and final live poll to a new checkpoint receipt."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=ROOT/'literature/anchor_prior_stage_manifest_2026-10-07.json';proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_ANCHOR_PRIOR_2026-10-07.json'
    m=read(manifest);p=read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and sha(manifest)==p['manifest_sha256']
    assert len(m['stage_files'])==1383 and len(m['evidence_files'])==3102 and m['stage_bytes']==87966671
    assert p['previous1708_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified']
    observed=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive=dict(actual_observed_tool_chunk='cf7387',actual_observed_tool_exit=0,stage_files=1383,cumulative_frozen_files=3102,stage_bytes=87966671),
        metadata_record=dict(actual_observed_tool_chunk='420b8a',actual_observed_tool_exit=0),
        training=dict(actual_observed_tool_chunk='565710',session_id=99542,returned_same_live_session=True,native_updates=12969,invocation02_new_updates=12870,cumulative_wall_seconds=29075.616771399975,full_training_observed_tool_exit=None),
        latest_GPU=dict(actual_observed_tool_chunk='3a79c6',actual_observed_tool_exit=0,timestamp='2026/10/07 23:48:48.906',free_MiB=1394,total_MiB=24455,utilization_percent=85,new_GPU8GB_margin_met=False),
        publication_claim_confirmed=False,goal_status='active')
    obsfile=ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_ANCHOR_PRIOR_2026-10-07.json';new(obsfile,observed)
    ledger=read(ROOT/'SESSION_EXECUTION_LEDGER_ANCHOR_PRIOR_2026-10-07.json')
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],source_bindings=[entry(x) for x in (Path(__file__),manifest,proof,obsfile,ROOT/'SESSION_POST_ARCHIVE_ANCHOR_PRIOR_UPDATE_2026-10-07.md',ROOT/'SESSION_PREPARED_FINAL_REPLY_ANCHOR_PRIOR_2026-10-07.md')],
        archive_actual_tool_exit=0,archive_actual_tool_chunk='cf7387',new_stage_files_frozen=1383,cumulative_frozen_evidence_files=3102,stage_bytes=87966671,previous1708_evidence_hashes_unchanged=True,
        diagnostic_actual_tool_exit=0,independent_actual_tool_exit=0,unique_development_patients=11,unique_development_series=19,checked_supports=57,checked_missing_plane_records=3015,forest_trees_compared=704,
        actual_medical_array_counts=ledger['actual_medical_array_counts_including_failed_preparation'],new_primary_papers_read=2,text_pages_read=21,visual_pages_reviewed=4,
        live_training=observed['training'],latest_GPU=observed['latest_GPU'],formal_final_budget_completed=False,original56FOV_evaluated=False,all6_final_capability_gates_completed=False,current_final_model_cache_equivalence_qualified=False,
        new_GPU_forwards=0,new_neural_training_updates=0,actual_MRI_risk_certificates_issued=0,clinical_benefit_measured=False,real_latency_measured=False,confirmation_patients_opened=False,validation_data_read=False,publication_claim_confirmed=False,
        old_MIRA_MSValid84_confirmation_preserved=True,goal_status='active',current_goal_turn_classification='progress',this_receipt_is_post_manifest_appendix=True)
    dest=ROOT/'SESSION_CHECKPOINT_RECEIPT_ANCHOR_PRIOR_2026-10-07.json';new(dest,r)
    print(json.dumps(dict(complete=True,receipt=entry(dest),archive_actual_tool_exit=0,stage_files=1383,cumulative_frozen_files=3102,native_updates=12969,full_training_exit=None,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
