"""Bind observed archive success and actual latest live poll; no future exits."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size)


def new(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest = ROOT/'literature/matched_oracle_stage_manifest_2026-10-08.json'
    proof = ROOT/'SESSION_ARCHIVE_VERIFICATION_MATCHED_ORACLE_2026-10-08.json'
    m, p = read(manifest), read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors'] and sha(manifest) == p['manifest_sha256']
    assert len(m['stage_files']) == 91 and len(m['evidence_files']) == 3201 and m['stage_bytes'] == 9179516
    assert p['newly_bound_files'] == 99 and p['new_evidence_bytes'] == 10286277
    assert p['previous3102_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified'] and p['local_links_verified']
    observed = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        archive=dict(actual_observed_tool_chunk='57f546', actual_observed_tool_exit=0,
                     stage_files=91, cumulative_frozen_files=3201, stage_bytes=9179516,
                     newly_bound_files=99, new_evidence_bytes=10286277),
        metadata_record=dict(actual_observed_tool_chunk='57f95e', actual_observed_tool_exit=0),
        independent_budget_verification=dict(actual_observed_tool_chunk='c66c47', actual_observed_tool_exit=0),
        training=dict(actual_observed_tool_chunk='8393e7', session_id=99542, returned_same_live_session=True,
                      native_updates=13959, invocation02_new_updates=13860, cumulative_wall_seconds=31415.690081799985,
                      full_training_observed_tool_exit=None, training_restarted=False, training_migrated=False),
        latest_GPU=dict(actual_observed_tool_chunk='0dbb13', actual_observed_tool_exit=0,
                        timestamp='2026/10/08 00:30:42.520', free_MiB=1394, total_MiB=24455,
                        utilization_percent=88, new_GPU8GB_margin_met=False),
        routine_direct_read_tool_chunks=[dict(chunk=c, exit_code=code) for c, code in (
            ('06ad70',0),('66dfcd',0),('509a41',0),('80b6d2',0),('faeb9c',0),
            ('085229',0),('91dc8f',0),('3c84dd',0),('23a5e5',0),('e78f1f',0),('a4c7c5',1))],
        unsuccessful_budget_verification=dict(actual_observed_tool_chunk='08b74d', actual_observed_tool_exit=1,
            reason='optional schema key absent in old frozen predictions; v1 retained; compatible v2 passed'),
        automatic_approval_review_rejections_received=0, publication_claim_confirmed=False, goal_status='active')
    obsfile = ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_MATCHED_ORACLE_2026-10-08.json'
    new(obsfile, observed)
    ledger = read(ROOT/'SESSION_EXECUTION_LEDGER_MATCHED_ORACLE_2026-10-08.json')
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        source_bindings=[entry(x) for x in (Path(__file__), manifest, proof, obsfile,
            ROOT/'SESSION_POST_ARCHIVE_MATCHED_ORACLE_UPDATE_2026-10-08.md',
            ROOT/'SESSION_PREPARED_FINAL_REPLY_MATCHED_ORACLE_2026-10-08.md')],
        archive_actual_tool_exit=0, archive_actual_tool_chunk='57f546', new_stage_files_frozen=91,
        cumulative_frozen_evidence_files=3201, stage_bytes=9179516, new_evidence_bytes=10286277,
        previous3102_evidence_hashes_unchanged=True, diagnostic_actual_tool_exit=0,
        independent_geometry_actual_tool_exit=0, independent_budget_actual_tool_exit=0,
        unique_development_patients=11, unique_development_series=19,
        checked_ideal_supports=19, checked_missing_plane_records=1005,
        independent_budget_series_supports=76, independent_budget_series_cost_ratios=608,
        independent_budget_aggregate_cost_ratios=96, independent_budget_patient_workloads=44,
        actual_medical_array_counts=ledger['production_and_geometry_verification_medical_array_counts'],
        new_primary_papers_read=2, text_pages_read=16, visual_pages_reviewed=4,
        live_training=observed['training'], latest_GPU=observed['latest_GPU'],
        formal_final_budget_completed=False, original56FOV_evaluated=False,
        all6_final_capability_gates_completed=False, current_final_model_cache_equivalence_qualified=False,
        actual_MRI_risk_certificates_issued=0, clinical_benefit_measured=False, real_latency_measured=False,
        repacking_executed=False, repacking_output_or_latency_qualified=False,
        confirmation_patients_opened=False, validation_data_read=False, locked_IXI_opened=False,
        publication_claim_confirmed=False, old_MIRA_MSValid84_confirmation_preserved=True,
        goal_status='active', current_goal_turn_classification='progress',
        this_receipt_is_post_manifest_appendix=True)
    dest = ROOT/'SESSION_CHECKPOINT_RECEIPT_MATCHED_ORACLE_2026-10-08.json'
    new(dest, r)
    print(json.dumps(dict(complete=True, receipt=entry(dest), archive_actual_tool_exit=0,
        stage_files=91, cumulative_frozen_files=3201, native_updates=13959,
        full_training_exit=None, goal_status='active', publication_claim_confirmed=False)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
