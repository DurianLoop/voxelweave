"""Record inherited and directly observed evidence without editing frozen inputs."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size)


def new(p, data):
    with p.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    expected = [
        ('matched_geometry_production', 'experiments/mc_rc_matched_anchor_oracle_2026_10_08/attempt01.json', 'c4b139', 0, 'user_provided_compaction_handoff'),
        ('independent_labels_geometry', 'experiments/mc_rc_matched_anchor_oracle_2026_10_08/independent_labels_disk_fraction_attempt01.json', '339626', 0, 'user_provided_compaction_handoff'),
        ('budget_metadata_production', 'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/attempt01.json', '106be7', 0, 'user_provided_compaction_handoff'),
        ('primary_acquisition', 'literature/source_cache/shared_cost_primary_2026-10-08/acquisition_attempt01.json', 'ebb4f6', 0, 'user_provided_compaction_handoff'),
        ('primary_render', 'literature/source_cache/shared_cost_primary_2026-10-08/render_attempt01.json', '0270bd', 0, 'user_provided_compaction_handoff'),
        ('budget_independent_v1', 'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/independent_integer_rational_attempt01.json', '08b74d', 1, 'direct_live_tool_result'),
        ('budget_independent_v2', 'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/independent_integer_rational_v2_attempt01.json', 'c66c47', 0, 'direct_live_tool_result'),
    ]
    exits = [dict(key=key, **entry(ROOT/path), actual_observed_tool_chunk=chunk,
                  actual_observed_tool_exit=code, exit_observation_source=origin)
             for key, path, chunk, code, origin in expected]
    prod, verify, budget, acquired, rendered, v1, v2 = (read(ROOT/path) for key, path, chunk, code, origin in expected)
    assert all(d['complete'] and not d['errors'] for d in (prod, verify, budget, v2))
    assert not v1['complete'] and v1['errors'] == ["KeyError: 'repacking_execution_equivalence_verified'"]
    assert prod['all19_anchor_masks_saved_before_full_GT_scoring'] and len(prod['anchor_receipts']) == len(prod['series']) == 19
    assert verify['checked_series'] == verify['checked_supports'] == 19 and verify['checked_missing_plane_records'] == 1005
    assert v2['checked_series_supports'] == 76 and v2['checked_series_cost_ratios'] == 608 and v2['checked_aggregate_cost_ratios'] == 96 and v2['checked_patient_workloads'] == 44
    for doc in (prod, verify, budget, v1, v2):
        for binding in doc['source_bindings']:
            assert sha(ROOT/binding['path']) == binding['sha256'], binding['path']
    for receipt in prod['anchor_receipts']:
        assert receipt['full_GT_not_read_yet'] and receipt['annotation_oracle_not_deployment_input']
        assert sha(ROOT/receipt['file']['path']) == receipt['file']['sha256']
    for snapshot in prod['source_snapshots']:
        assert sha(ROOT/snapshot['snapshot']['path']) == snapshot['snapshot']['sha256'] == sha(ROOT/snapshot['source_path'])
    assert not prod['prohibited_access_attempts'] and not verify['prohibited_access_attempts']
    assert acquired['new_primary_papers_read'] == 0 and rendered['complete'] and not rendered['errors']
    scopes = []
    for paper in acquired['records']:
        assert paper['complete'] and not paper['errors'] and not paper['new_paper_read']
        pages = list(range(1, 9))
        images = [v for v in rendered['records'] if v['key'] == paper['key']]
        assert len(images) == 2 and all(not v['visually_reviewed'] for v in images)
        texts = [v for v in paper['page_texts'] if v['physical_page'] in pages]
        assert len(texts) == 8
        for binding in [paper['PDF'], *texts, *images]:
            assert sha(ROOT/binding['path']) == binding['sha256']
        scopes.append(dict(key=paper['key'], PDF=paper['PDF'], acquired_physical_pages=paper['physical_pages'],
            physical_pages_text_read=pages, page_texts=texts, actual_visual_image_files=images,
            visual_reviewed_pages=[v['physical_page'] for v in images],
            unread_physical_pages=[p for p in range(1, paper['physical_pages']+1) if p not in pages],
            reading_observation_source='user_provided_compaction_handoff_reports_actual_text_reads_and_view_image',
            current_continuation_reread_page01_snippets_not_added_to_unique_page_count=True))
    assert sum(s['acquired_physical_pages'] for s in scopes) == 17
    literature = ROOT/'literature/shared_cost_reading_provenance_2026-10-08.json'
    new(literature, dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        new_primary_papers_read=2, acquired_physical_pages=17, text_pages_read=16, physical_pages_visual_reviewed=4,
        source_bindings=[entry(ROOT/expected[i][1]) for i in (3, 4)], scopes=scopes,
        acquisition_and_render_receipts_not_rewritten=True, author_training_reproduced=False,
        all_supplementary_or_reference_pages_read=False))
    polls = [
        dict(tool_chunk='d20351', observation_source='user_provided_compaction_handoff', session_id=99542, returned_same_live_session=True, native_updates=13365, invocation02_new_updates=13266, cumulative_wall_seconds=30014.629973300034, full_training_observed_tool_exit=None),
        dict(tool_chunk='b589b8', observation_source='direct_live_tool_result', session_id=99542, returned_same_live_session=True, native_updates=13563, invocation02_new_updates=13464, cumulative_wall_seconds=30484.656701399945, full_training_observed_tool_exit=None),
        dict(tool_chunk='f635a9', observation_source='direct_live_tool_result', session_id=99542, returned_same_live_session=True, native_updates=13761, invocation02_new_updates=13662, cumulative_wall_seconds=30956.57806109998, full_training_observed_tool_exit=None),
    ]
    gpu = dict(actual_observed_tool_chunk='1f60b9', actual_observed_tool_exit=0, observation_source='direct_live_tool_result',
               timestamp='2026/10/08 00:18:03.095', free_MiB=1394, total_MiB=24455, utilization_percent=95, new_GPU8GB_margin_met=False)
    observations = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], actual_exits=exits,
        resumed_training_polls=polls, full_training_observed_tool_exit=None, latest_GPU=gpu,
        non_scientific_read_or_schema_issues=[
            dict(tool_chunk='904596', exit_code=1, observation_source='user_provided_compaction_handoff', reason='PowerShell literal wildcard path error123; read only'),
            dict(tool_chunk='dc2de3', exit_code=1, observation_source='user_provided_compaction_handoff', reason='rg exclusions did not prevent old inaccessible installer temp access; read only'),
            dict(tool_chunk='a4c7c5', exit_code=1, observation_source='direct_live_tool_result', reason='metadata print attempted wrong nesting for label_components; corrected explicit connectivity access in 5c2c6d; no mutation or medical arrays'),
            dict(tool_chunk='08b74d', exit_code=1, observation_source='direct_live_tool_result', reason='independent budget verifier expected optional new oracle flag in older frozen prediction schema; v1 source/receipt retained, v2 only compatibility fix')],
        reversible_source_creation=[dict(tool_chunk='3e40c5', exit_code=0, observation_source='user_provided_compaction_handoff', purpose='independent helper origin'),
                                    dict(tool_chunk='5c2c6d', exit_code=0, observation_source='direct_live_tool_result', purpose='budget verifier v2 creation, v1 unchanged')],
        training_restarted=False, training_migrated=False, user_terminal_processes_controlled=False,
        other_processes_enumerated=False, new_agents_delegated=False, automatic_approval_review_rejections_received=0)
    obsfile = ROOT/'SESSION_TOOL_OBSERVATIONS_MATCHED_ORACLE_2026-10-08.json'
    new(obsfile, observations)
    counts = {key:sum(d.get(key, 0) for d in (prod, verify)) for key in ('observed_label_arrays_loaded', 'full_development_GT_arrays_loaded', 'new_MRI_pixel_arrays_loaded', 'model_arrays_loaded', 'neural_forwards', 'GPU_forwards', 'training_updates')}
    assert counts == dict(observed_label_arrays_loaded=38, full_development_GT_arrays_loaded=38,
                          new_MRI_pixel_arrays_loaded=0, model_arrays_loaded=0, neural_forwards=0, GPU_forwards=0, training_updates=0)
    roots = []
    for path, digest in [('D:/MRI/.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                         ('D:/MRI/environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        assert sha(Path(path)) == digest
        roots.append(dict(path=path, sha256=digest, previous_sha256=digest, unchanged=True))
    oracle = prod['summaries'][0]
    assert oracle['method'] == 'ideal_observed_anchor_union_2mm_19' and oracle['ROI_gates_passed'] == 19 and oracle['coverage_boundary_ge099_and_any_saving'] == 18
    assert (oracle['N_total'], oracle['k_total']) == (572, 181)
    ledger = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        source_bindings=[entry(Path(__file__)), entry(obsfile), entry(literature)] + [entry(ROOT/path) for key, path, chunk, code, origin in expected],
        actual_exits=exits, unique_development_patients=11, unique_development_series=19,
        checked_ideal_supports=19, checked_missing_plane_records=1005, oracle_ROI_gates_passed=19,
        oracle_coverage_boundary_and_positive_conditional_saving_series=18,
        previous_real_predictors_ROI_gates_passed=0, production_and_geometry_verification_medical_array_counts=counts,
        medical_array_count_excludes_live_original_training_and_byte_hash_IO=True,
        independent_budget_checked_series_supports=76, independent_budget_checked_series_cost_ratios=608,
        independent_budget_checked_aggregate_cost_ratios=96, independent_budget_checked_patient_workloads=44,
        budget_and_archive_new_medical_arrays_loaded=0, real_latency_measured=False, clinical_benefit_measured=False,
        actual_MRI_risk_certificates_issued=0, new_primary_papers_read=2, text_pages_read=16, visual_pages_reviewed=4,
        root_files_observed=roots, failures_preserved=True, scientific_settings_not_tuned_after_scoring=True,
        annotation_oracle_not_deployment_input=True, ideal_support_not_universal_effective_repair_bound=True,
        area_gates_not_equivalent_to_actual_3D_total_budget=True, cost_flow_not_selected_by_favorable_denominator=True,
        repacking_executed=False, repacking_output_or_latency_qualified=False,
        live_training_session=99542, latest_training_poll=polls[-1], full_training_observed_tool_exit=None, latest_GPU=gpu,
        formal_final_budget_completed=False, original56FOV_evaluated=False, all6_final_capability_gates_completed=False,
        current_final_model_cache_equivalence_qualified=False, confirmation_patients_opened=False,
        validation_data_read=False, locked_IXI_opened=False, old_MIRA_MSValid84_confirmation_preserved=True,
        publication_claim_confirmed=False, goal_status='active', current_goal_turn_classification='progress')
    new(ROOT/'SESSION_EXECUTION_LEDGER_MATCHED_ORACLE_2026-10-08.json', ledger)
    print(json.dumps(dict(complete=True, checked_series=19, checked_missing_plane_records=1005,
                          actual_medical_array_counts=counts, new_primary_papers_read=2,
                          text_pages_read=16, visual_pages_reviewed=4, root_hashes_unchanged=True,
                          latest_native_updates=13761, full_training_exit=None, goal_status='active',
                          publication_claim_confirmed=False)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
