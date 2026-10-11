"""Record observed archive exit and confirmed-live handle; do not predict a future exit."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=ROOT/'literature/common_projected_stage_manifest_2026-10-08.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_COMMON_PROJECTED_2026-10-08.json'
    m,p=read(manifest),read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors']
    assert sha(manifest)==p['manifest_sha256'] and len(m['stage_files'])==82 and len(m['evidence_files'])==3409
    assert m['stage_bytes']==9591642 and p['new_evidence_bytes']==10426993 and p['newly_bound_files']==90
    assert p['previous3319_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified'] and p['local_links_verified']
    observed=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive=dict(actual_observed_tool_chunk='68577f',actual_observed_tool_exit=0,stage_files=82,
                     cumulative_frozen_files=3409,stage_bytes=9591642,newly_bound_files=90,new_evidence_bytes=10426993),
        metadata_record=dict(actual_observed_tool_chunk='62da79',actual_observed_tool_exit=0),
        training=dict(actual_observed_tool_chunk='e54794',session_id=99542,returned_same_live_session=True,
                      native_updates=15741,invocation02_new_updates=15642,cumulative_wall_seconds=35607.11290119996,
                      full_training_observed_tool_exit=None,training_restarted=False,training_migrated=False),
        latest_GPU=dict(actual_observed_tool_chunk='9b03af',actual_observed_tool_exit=0,timestamp='2026/10/08 01:40:12.775',
                        free_MiB=1394,total_MiB=24455,utilization_percent=96,new_GPU8GB_margin_met=False),
        automatic_approval_review_rejections_received=0,goal_status='active',publication_claim_confirmed=False)
    obsfile=ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_COMMON_PROJECTED_2026-10-08.json'
    new(obsfile,observed)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(x) for x in (Path(__file__),manifest,proof,obsfile,
            ROOT/'SESSION_POST_ARCHIVE_COMMON_PROJECTED_UPDATE_2026-10-08.md',
            ROOT/'SESSION_PREPARED_FINAL_REPLY_COMMON_PROJECTED_2026-10-08.md')],
        archive_actual_tool_exit=0,archive_actual_tool_chunk='68577f',new_stage_files_frozen=82,
        cumulative_frozen_evidence_files=3409,stage_bytes=9591642,new_evidence_bytes=10426993,
        previous3319_evidence_hashes_unchanged=True,production_actual_tool_exit=0,
        original_independent_actual_tool_exit=1,original_failed_attempt_retained=True,
        v2_independent_actual_tool_exit=0,unique_development_patients=11,unique_development_series=19,
        observed_package_load_events=42,new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        original_direct_bitwise_equivalent_series=19,old_availability_hash_equal_series=19,
        original_ideal_coordinate_failed_series=9,original_ideal_coordinate_failed_samples=30,
        no_tolerance_widening=True,new_primary_papers_read=2,text_pages_read=10,visual_pages_reviewed=4,
        live_training=observed['training'],latest_GPU=observed['latest_GPU'],formal_final_budget_completed=False,
        original56FOV_evaluated=False,all6_final_capability_gates_completed=False,
        current_final_model_cache_equivalence_qualified=False,actual_MRI_risk_certificates_issued=0,
        actual_MRI_task_benefit_measured=False,real_task_latency_measured=False,
        confirmation_patients_opened=False,validation_data_read=False,locked_IXI_opened=False,
        old_MIRA_MSValid84_confirmation_preserved=True,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',this_receipt_is_post_manifest_appendix=True)
    dest=ROOT/'SESSION_CHECKPOINT_RECEIPT_COMMON_PROJECTED_2026-10-08.json'
    new(dest,receipt)
    print(json.dumps(dict(complete=True,receipt=entry(dest),archive_actual_tool_exit=0,stage_files=82,
                         cumulative_frozen_files=3409,native_updates=15741,full_training_exit=None,
                         goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
