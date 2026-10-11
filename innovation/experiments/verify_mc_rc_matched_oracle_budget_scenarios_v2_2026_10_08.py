"""Metadata-only independent integer-rational verification; no medical arrays."""
import hashlib
import json
import math
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experiments/mc_rc_matched_anchor_oracle_2026_10_08/attempt01.json'
GEOMETRY_PROOF = SOURCE.parent / 'independent_labels_disk_fraction_attempt01.json'
TARGET = ROOT / 'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/attempt01.json'
OUT = TARGET.parent / 'independent_integer_rational_v2_attempt01.json'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def rational(a, b=1):
    assert b > 0
    g = math.gcd(a, b)
    return a // g, b // g


def add(x, y):
    return rational(x[0]*y[1] + y[0]*x[1], x[1]*y[1])


def mean(values):
    values = list(values)
    total = (0, 1)
    for value in values:
        total = add(total, value)
    return rational(total[0], total[1]*len(values))


def check(value, expected):
    parts = value['exact'].split('/')
    actual = rational(int(parts[0]), int(parts[1]) if len(parts) == 2 else 1)
    assert actual == expected, (value, expected)
    assert math.isclose(value['value'], expected[0]/expected[1], rel_tol=0, abs_tol=1e-14)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not OUT.exists()
    started = time.perf_counter()
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False,
                  errors=[], source_bindings=[entry(p) for p in (Path(__file__), SOURCE, GEOMETRY_PROOF, TARGET)],
                  medical_arrays_loaded=0, model_arrays_loaded=0, neural_forwards=0,
                  GPU_forwards=0, training_updates=0, latency_measured=False,
                  confirmation_patients_opened=False, validation_data_read=False,
                  production_code_imported=False, fractions_module_used=False,
                  packing_executed=False, publication_claim_confirmed=False)
    try:
        source, proof, target = (read(p) for p in (SOURCE, GEOMETRY_PROOF, TARGET))
        assert all(d['complete'] and not d['errors'] for d in (source, proof, target))
        assert proof['checked_series'] == 19 and proof['checked_missing_plane_records'] == 1005
        patients = sorted({s['patient'] for s in source['series']})
        assert len(source['series']) == 19 and len(patients) == 11
        assert target['hypothetical_repacking_not_executed_or_output_qualified']
        assert target['medical_arrays_loaded'] == target['GPU_forwards'] == 0
        aggregate_checks = series_checks = packing_checks = workload_checks = 0
        methods = []
        for model in target['models']:
            name = model['method']
            rows = {}
            for series in source['series']:
                support = series['oracle'] if name == 'ideal_observed_anchor_union_2mm_19' else series['frozen_predictions'][name]
                geo = support['geometry_cost']
                n = (len(geo['tile_locations_zrc']) + 1)//2
                batch_ids = {int(t)//2 for t in geo['affected_tile_ids']}
                k = len(batch_ids)
                packed = (len(geo['affected_tile_ids']) + 1)//2
                assert n == geo['full_forward_calls'] and k == geo['recomputed_batch_pairs']
                assert batch_ids == set(geo['recomputed_batch_pair_ids'])
                assert packed <= k <= n
                assert geo.get('repacking_execution_equivalence_verified', False) is False
                rows[(series['patient'], series['uid'])] = (n, k, packed, support['roi']['gate_passed'])
                packing_checks += 1
            assert len(rows) == 19 and len(model['series']) == 19
            for row in model['series']:
                n, k, packed, gate = rows[(row['patient'], row['uid'])]
                assert (row['N'], row['k'], row['hypothetical_repacked_k'], row['ROI_gates_passed']) == (n, k, packed, gate)
                assert row['affected_tiles'] == next((len((s['oracle'] if name == 'ideal_observed_anchor_union_2mm_19' else s['frozen_predictions'][name])['geometry_cost']['affected_tile_ids']) for s in source['series'] if (s['patient'], s['uid']) == (row['patient'], row['uid'])))
                first = row['strict_break_even_actions_scenario_A']
                if k == n:
                    assert first is None
                else:
                    assert isinstance(first, int) and first >= 1
                    assert n < first*(n-k) and n >= (first-1)*(n-k)
                for m in (1, 2, 5, 10):
                    check(row['scenario_A_ratios'][str(m)], rational(n + m*k, m*n))
                    check(row['scenario_B_ratios'][str(m)], rational(n + m*k, (m+1)*n))
                    series_checks += 2
            grouped = {}
            for p in patients:
                selected = [v for (person, uid), v in rows.items() if person == p]
                grouped[p] = tuple(sum(v[i] for v in selected) for i in range(3))
            assert len(model['patient_workloads']) == 11
            for workload in model['patient_workloads']:
                assert (workload['N'], workload['k'], workload['repacked_k']) == grouped[workload['patient']]
                workload_checks += 1
            total_n, total_k, total_packed = (sum(v[i] for v in rows.values()) for i in range(3))
            assert (model['N_total'], model['k_total'], model['hypothetical_repacked_k_total']) == (total_n, total_k, total_packed)
            check(model['hypothetical_original_pair_packing_call_reduction'], rational(total_k-total_packed, total_k))
            check(model['hypothetical_patient_workload_equal_repacked_conditional_saving'], mean(rational(n-packed, n) for n, k, packed in grouped.values()))
            for flow in ('A', 'B'):
                for m in (1, 2, 5, 10):
                    denominator = m if flow == 'A' else m+1
                    legacy = mean(mean(rational(n+m*k, denominator*n) for (person, uid), (n, k, packed, gate) in rows.items() if person == p) for p in patients)
                    patient = mean(rational(n+m*k, denominator*n) for n, k, packed in grouped.values())
                    pooled = rational(total_n+m*total_k, denominator*total_n)
                    aggregate = model['aggregate_cost_scenarios'][flow][str(m)]
                    for key, expected in zip(('legacy_patient_series_equal', 'complete_patient_workload_equal', 'pooled_workload'), (legacy, patient, pooled)):
                        check(aggregate[key], expected)
                        aggregate_checks += 1
            methods.append(dict(method=name, N=total_n, k=total_k, hypothetical_repacked_k=total_packed))
            assert time.perf_counter()-started < 60
        totals = {}
        for connectivity in ('6', '26'):
            groups = [s['label_components']['connectivity'][connectivity] for s in source['series']]
            components = [c for g in groups for c in g['components']]
            for component in components:
                assert component['missing_component_without_observed_contact'] == (component['missing_voxels'] > 0 and component['observed_voxels'] == 0)
                assert component['voxels'] == component['observed_voxels'] + component['missing_voxels'] + component['tail_voxels']
            totals[connectivity] = dict(full_GT_components=len(components),
                components_with_missing=sum(c['missing_voxels'] > 0 for c in components),
                missing_components_without_observed_contact=sum(c['missing_component_without_observed_contact'] for c in components),
                foreground_voxels=sum(c['voxels'] for c in components))
        assert totals == target['component_counts']
        result.update(complete=True, checked_methods=len(methods), checked_series_supports=packing_checks,
                      checked_series_cost_ratios=series_checks, checked_aggregate_cost_ratios=aggregate_checks,
                      checked_patient_workloads=workload_checks, methods=methods, component_counts=totals)
    except Exception as error:
        result['errors'].append(type(error).__name__ + ': ' + str(error))
        result['traceback'] = traceback.format_exc()
    result['elapsed_seconds'] = time.perf_counter()-started
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    with OUT.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_bindings', 'traceback')}, ensure_ascii=False), flush=True)
    return 0 if result['complete'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
