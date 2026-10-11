"""Scalar replay of all frozen completed-cohort estimates; never neural inference."""
from __future__ import annotations
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np
from vs_seg_selection_sensitivity import completion_gate, load_verified_records, sha

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/vs_seg_complete_analysis_cpu'
COHORT = ROOT / 'experiments/vs_seg_full_volume_cohort'
QUEUE = ROOT / 'experiments/vs_seg_full_volume_queue'
SEED, DRAWS = 20261012, 5000


def mean(values):
    return math.fsum(values) / len(values)


def quantile(values, p):
    ordered = sorted(values)
    at = (len(ordered) - 1) * p
    lower, upper = math.floor(at), math.ceil(at)
    return ordered[lower] + (at - lower) * (ordered[upper] - ordered[lower])


def replay(values):
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError('Replay requires finite nonempty patient differences')
    draws = np.random.default_rng(SEED).integers(0, len(values), size=(DRAWS, len(values)))
    sampled = [mean([values[int(i)] for i in draw]) for draw in draws]
    return dict(n=len(values), mean_difference=mean(values),
                ci95_percentile=[quantile(sampled, .025), quantile(sampled, .975)],
                seed=SEED, draws=DRAWS, negative_patients=sum(v < 0 for v in values),
                zero_patients=sum(v == 0 for v in values))


def same(actual, expected, where, errors):
    if isinstance(actual, dict) and isinstance(expected, dict):
        if actual.keys() != expected.keys():
            errors.append(where + ': keys differ')
        for k in actual.keys() & expected.keys():
            same(actual[k], expected[k], where + '/' + k, errors)
    elif isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            errors.append(where + ': length differs')
        for i, (a, b) in enumerate(zip(actual, expected)):
            same(a, b, where + '/' + str(i), errors)
    elif isinstance(actual, float) or isinstance(expected, float):
        if not isinstance(actual, (float, int)) or not isinstance(expected, (float, int)) or not math.isclose(actual, expected, rel_tol=1e-11, abs_tol=1e-14):
            errors.append(where + ': numerical value differs')
    elif actual != expected:
        errors.append(where + ': value differs')


def main():
    gate, contract = completion_gate()
    if not gate['allowed']:
        print(json.dumps(gate))
        return
    OUT.mkdir(exist_ok=True)
    proof_path = OUT / 'independent_all_frozen_estimates_replay.json'
    if proof_path.exists():
        raise FileExistsError('Existing evidence must not be overwritten')
    coverage = json.loads((ROOT / 'experiments/vs_seg_full_volume_coverage/attempt_01.json').read_text(encoding='utf-8'))
    roster = contract['main_roster']
    records, provenance = load_verified_records(roster, {r['patient']: r for r in coverage['patients']})
    completed_path = QUEUE / 'completed_analysis.json'
    status_path = COHORT / 'status.json'
    completed = json.loads(completed_path.read_text(encoding='utf-8'))
    status = json.loads(status_path.read_text(encoding='utf-8'))
    errors, endpoints, summaries = [], [], []
    same(completed['primary_analysis'], status['analysis'], 'completed/status analysis', errors)

    def check(key, patients, values, expected):
        actual = replay(values) if values else None
        same(actual, expected, key, errors)
        endpoints.append(dict(key=key, included_patients=patients, patient_differences=values, replay=actual))
        return actual

    def image(model, baseline, patients):
        return [records[p][model]['image_metrics']['support']['target_equal_nmse'] - records[p][baseline]['image_metrics']['support']['target_equal_nmse'] for p in patients]

    def task(model, baseline, ref, domain, patients):
        return [records[p][model]['task_metrics'][ref][domain]['dice'] - records[p][baseline]['task_metrics'][ref][domain]['dice'] for p in patients]

    analysis = completed['primary_analysis']
    primary_image = check('primary_image_difference', roster, image('hat', 'pipeline_pchip', roster), analysis['primary_image_difference'])
    primary_task = check('primary_task_difference', roster, task('hat', 'pipeline_pchip', 'original_json', 'full', roster), analysis['primary_task_difference'])
    actual_joint = all(r['ci95_percentile'][1] < 0 for r in (primary_image, primary_task))
    same(actual_joint, completed['fixed_joint_direction_supported'], 'completed primary gate', errors)
    same(actual_joint, status['fixed_primary_joint_direction_supported'], 'status primary gate', errors)
    expected_pairs = {(m, b) for m in ('hat', 'swinir') for b in ('raw_linear', 'raw_pchip', 'pipeline_linear', 'pipeline_pchip')}
    actual_pairs = [(r['model'], r['baseline']) for r in analysis['descriptive_secondary_pairs']]
    if len(actual_pairs) != 8 or set(actual_pairs) != expected_pairs:
        errors.append('Fixed secondary family differs')
    for entry in analysis['descriptive_secondary_pairs']:
        model, baseline = entry['model'], entry['baseline']
        prefix = model + '-' + baseline
        check(prefix + '/support_nmse', roster, image(model, baseline, roster), entry['support_nmse'])
        expected_keys = {ref + '/' + domain for ref in ('original_json', 'rtstruct') for domain in ('full', 'observed_anchor_slab', 'exclude_reference_boundary_1mm')}
        if set(entry['task_sensitivity']) != expected_keys:
            errors.append(prefix + ': sensitivity family differs')
        same(entry['formal_significance_claim'], False, prefix + '/formal_significance_claim', errors)
        for key, sensitivity in entry['task_sensitivity'].items():
            ref, domain = key.split('/')
            finite = [p for p in roster if records[p][model]['task_metrics'][ref][domain]['dice'] is not None and records[p][baseline]['task_metrics'][ref][domain]['dice'] is not None]
            same(finite, sensitivity['included_patients'], prefix + '/' + key + '/included', errors)
            same(len(roster) - len(finite), sensitivity['undefined_count'], prefix + '/' + key + '/undefined', errors)
            check(prefix + '/' + key, finite, task(model, baseline, ref, domain, finite), sensitivity['estimate'])
    same(analysis['secondary_intervals_are_descriptive_without_familywise_claim'], True, 'secondary descriptive status', errors)
    for condition in contract['conditions']:
        for ref in ('original_json', 'rtstruct'):
            rows = [records[p][condition]['task_metrics'][ref]['full'] for p in roster]
            row = dict(condition=condition, reference=ref, patients=len(rows),
                       mean_dice=mean([r['dice'] for r in rows]), median_dice=quantile([r['dice'] for r in rows], .5),
                       mean_absolute_relative_volume_error=mean([r['absolute_relative_volume_error'] for r in rows]),
                       empty_predictions=sum(r['prediction_voxels'] == 0 for r in rows),
                       boundary_infinite_or_undefined_patients=sum(r['boundary']['status'] != 'finite' for r in rows),
                       mean_support_nmse=mean([records[p][condition]['image_metrics']['support']['target_equal_nmse'] for p in roster]))
            expected = [r for r in completed['condition_summaries'] if r['condition'] == condition and r['reference'] == ref]
            if len(expected) != 1:
                errors.append(condition + '/' + ref + ': summary absent/duplicate')
            else:
                same(row, expected[0], condition + '/' + ref + '/summary', errors)
            summaries.append(row)
    if len(endpoints) != 58 or len(completed['condition_summaries']) != 14:
        errors.append('Frozen endpoint or summary count differs')
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=not errors,
                  script_sha256=sha(__file__), plan_sha256=sha(ROOT / 'VS_SEG_COMPLETE_ANALYSIS_REPLAY_PLAN_2026-10-03.md'),
                  contract_sha256=sha(COHORT / 'run_contract.json'), completed_analysis_sha256=sha(completed_path),
                  status_sha256=sha(status_path), gate=gate, record_provenance=provenance,
                  patients=45, replayed_endpoints=len(endpoints), draws_per_endpoint=DRAWS,
                  endpoints=endpoints, condition_summaries=summaries, fixed_joint_direction_supported=actual_joint,
                  errors=errors, gpu_used=False, publication_claim_confirmed=False,
                  independence='Shared completion/hash-loader and NumPy RNG; independently coded scalar fsum aggregation, per-draw mean and manual linear quantile; no neural inference or new patients')
    proof_path.write_text(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('complete', 'patients', 'replayed_endpoints', 'errors', 'fixed_joint_direction_supported')}))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
