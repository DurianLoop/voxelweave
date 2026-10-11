"""Bind actual tool exits, failed-attempt retention, and precise primary reading scope."""
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
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def new(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    operations = [
        ('preregister', 'experiments/common_projected_observed_preregistration_2026_10_08.json', 'c4873d', 0),
        ('production', 'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json', '22b068', 0),
        ('independent_v1_retained_failure', 'experiments/common_projected_observed_independent_2026_10_08/attempt01.json', '6f11e0', 1),
        ('precision_v2_preregister', 'experiments/common_projected_observed_precision_v2_preregistration_2026_10_08.json', '00124d', 0),
        ('independent_precision_v2', 'experiments/common_projected_observed_independent_precision_v2_2026_10_08/attempt01.json', '7b8b83', 0),
        ('primary_acquisition', 'literature/source_cache/distortion_perception_primary_2026-10-08/acquisition_attempt01.json', 'c55b64', 0),
        ('primary_render', 'literature/source_cache/distortion_perception_primary_2026-10-08/render_attempt01.json', 'fa89ec', 0),
        ('scientific_summary', 'experiments/common_projected_observed_summary_2026_10_08.json', '35096d', 0)]
    exits = [dict(key=key, **entry(ROOT/path), actual_observed_tool_chunk=chunk,
                  actual_observed_tool_exit=code, observation_source='direct_live_tool_result')
             for key, path, chunk, code in operations]
    summary = read(ROOT/operations[-1][1])
    assert summary['complete'] and not summary['errors'] and summary['observed_package_load_events'] == 42
    assert summary['original_direct_full_field_bitwise_equal_series'] == 19
    assert summary['ideal_coordinate_original_tolerance_failed_series'] == 9
    assert summary['ideal_coordinate_original_tolerance_failed_samples'] == 30
    acquired, rendered = read(ROOT/operations[5][1]), read(ROOT/operations[6][1])
    assert len(acquired['records']) == 2 and all(r['complete'] and not r['errors'] for r in acquired['records'])
    assert acquired['new_primary_papers_read'] == 0 and rendered['complete'] and not rendered['errors']
    scopes = []
    for paper in acquired['records']:
        pages = [1, 2, 3, 4, 5]
        texts = [p for p in paper['page_texts'] if p['physical_page'] in pages]
        visuals = [p for p in rendered['records'] if p['key'] == paper['key']]
        assert len(texts) == 5 and len(visuals) == 2 and [v['physical_page'] for v in visuals] == [3, 5]
        assert all(not v['visually_reviewed'] for v in visuals)
        for b in [paper['PDF'], *texts, *visuals]:
            assert sha(ROOT/b['path']) == b['sha256']
        scopes.append(dict(key=paper['key'], PDF=paper['PDF'], acquired_physical_pages=paper['physical_pages'],
                           physical_pages_text_read=pages, page_texts=texts, visual_reviewed_pages=[3, 5],
                           actual_visual_image_files=visuals,
                           unread_physical_pages=list(range(6, paper['physical_pages']+1)),
                           observation_source='actual_text_tool_reads_and_four_tools.view_image_results'))
    provenance = ROOT/'literature/distortion_perception_reading_provenance_2026-10-08.json'
    new(provenance, dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        source_bindings=[entry(ROOT/operations[5][1]), entry(ROOT/operations[6][1]),
                         entry(ROOT/'literature/2026-10-08_distortion_perception_primary_protocol.md')],
        scopes=scopes, acquired_physical_pages=39, text_pages_read=10, visual_pages_reviewed=4,
        new_primary_papers_read=2, author_training_reproduced=False, all_physical_pages_read=False,
        text_read_tool_chunks=['8aea14', 'f308d8', 'ee11c2', '29b8fe', '7cf1d8', 'cdce24'],
        actual_visual_tool='functions.exec -> Promise.allSettled(four tools.view_image); returned images inspected',
        image_tool_chunk_identifier_returned=False, acquisition_and_render_receipts_not_rewritten=True,
        actual_first_paper_version='1711.06077v4, 25 Oct 2020, CVPR2018 extended version',
        actual_second_paper_version='1901.07821v4, 30 Jul 2019, Rethinking Lossy Compression subtitle'))
    roots = []
    for name, digest in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                         ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p = ROOT.parent/name
        assert sha(p) == digest
        roots.append(dict(path=str(p), sha256=digest, previous_sha256=digest, unchanged=True))
    observations = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], actual_exits=exits,
        live_launches=[dict(key='production',chunk='e3593e',session=87219,terminal_chunk='22b068',exit=0),
                       dict(key='independent_v1',chunk='f2b467',session=57025,terminal_chunk='6f11e0',exit=1),
                       dict(key='independent_v2',chunk='953e89',session=42515,terminal_chunk='7b8b83',exit=0),
                       dict(key='primary_acquisition',chunk='c526db',session=65534,terminal_chunk='c55b64',exit=0)],
        training_polls=[dict(chunk='657438',session=99542,native_updates=14850,new_updates=14751,cumulative_wall_seconds=33514.92058789998),
                        dict(chunk='819892',session=99542,native_updates=15147,new_updates=15048,cumulative_wall_seconds=34218.49690899998),
                        dict(chunk='41356e',session=99542,native_updates=15246,new_updates=15147,cumulative_wall_seconds=34447.37113049999),
                        dict(chunk='5489bb',session=99542,native_updates=15543,new_updates=15444,cumulative_wall_seconds=35133.23273809999)],
        full_training_observed_tool_exit=None, training_handle_still_live=True,
        latest_GPU=dict(actual_observed_tool_chunk='d4cf69',actual_observed_tool_exit=0,timestamp='2026/10/08 01:34:46.098',
                        free_MiB=1394,total_MiB=24455,utilization_percent=61,new_GPU8GB_margin_met=False),
        retained_scientific_failed_attempts=1, scientific_failure_resolved_with_separate_precision_protocol=True,
        metadata_tool_errors=[dict(chunk='7739d4',exit=1,kind='rg pre-existing inaccessible pip temporary directories',medical_arrays_loaded=0),
                              dict(chunk='dcd76f',exit=1,kind='PowerShell -c quoting SyntaxError, no Python body executed',medical_arrays_loaded=0),
                              dict(chunk='9de119',exit=0,kind='nonterminal Get-Content missing guessed acquisition script; actual fetch path later read',medical_arrays_loaded=0)],
        automatic_approval_review_rejections_received=0, training_restarted=False, training_migrated=False,
        user_terminal_processes_controlled=False, other_processes_enumerated=False, new_agents_delegated=False,
        earlier_incorrect_public_float32_difference_statement_corrected=True,
        used_skill='pdf:pdf', skill_path='C:/Users/user/.codex/plugins/cache/openai-primary-runtime/pdf/26.904.11930/skills/pdf/SKILL.md',
        skill_use_was_read_only_no_PDF_authoring=True)
    obsfile = ROOT/'SESSION_TOOL_OBSERVATIONS_COMMON_PROJECTED_2026-10-08.json'
    new(obsfile, observations)
    ledger = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        source_bindings=[entry(Path(__file__)),entry(obsfile),entry(provenance)]+[entry(ROOT/path) for key,path,chunk,code in operations],
        actual_exits=exits, unique_development_patients=11, unique_development_series=19,
        observed_package_load_events=42, production_observed_load_events=19, retained_failed_observed_load_events=4,
        v2_independent_observed_load_events=19, MRI_neural_forwards=0, neural_forwards=0, GPU_forwards=0, training_updates=0,
        model_arrays_loaded=0, array_counts_exclude_original_live_training_and_hash_byte_IO=True,
        original_v1_independent_passed=False, failed_original_source_and_result_retained=True,
        v2_operator_precision_independent_passed=True, no_tolerance_widening=True,
        original_ideal_coordinate_failed_series=9, original_ideal_coordinate_failed_samples=30,
        original_direct_full_field_bitwise_equal_series=19, old_availability_hashes_exact=True,
        source_projection_mathematics_is_sampled=True, independent_Hermite_covers_full_native_array=True,
        full_execution_hash_replay_is_shared_library=True, new_primary_papers_read=2,
        acquired_physical_pages=39, text_pages_read=10, visual_pages_reviewed=4, root_files_observed=roots,
        original_training_session=99542, latest_training_poll=observations['training_polls'][-1],
        full_training_observed_tool_exit=None, latest_GPU=observations['latest_GPU'],
        formal_final_budget_completed=False, original56FOV_evaluated=False, all6_final_capability_gates_completed=False,
        actual_MRI_task_benefit_measured=False, real_task_latency_measured=False, actual_MRI_risk_certificates_issued=0,
        native_GT_validation_confirmation_pixels_read=False, confirmation_patients_opened=False, validation_data_read=False,
        locked_IXI_opened=False, old_MIRA_MSValid84_confirmation_preserved=True,
        publication_claim_confirmed=False, goal_status='active', current_goal_turn_classification='progress')
    new(ROOT/'SESSION_EXECUTION_LEDGER_COMMON_PROJECTED_2026-10-08.json',ledger)
    print(json.dumps(dict(complete=True,observed_package_load_events=42,unique_series=19,original_failure_retained=True,
        full_direct_hash_equal_series=19,new_primary_papers_read=2,text_pages_read=10,visual_pages_reviewed=4,
        root_hashes_unchanged=True,latest_native_updates=15543,full_training_exit=None,goal_status='active')),flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
