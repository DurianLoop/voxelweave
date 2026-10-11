"""Generate a separate precision-aware verifier and preregister it before MRI loads."""
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/'experiments/verify_common_projected_observed_2026_10_08.py'
NEW = ROOT/'experiments/verify_common_projected_observed_precision_v2_2026_10_08.py'
PRE = ROOT/'experiments/common_projected_observed_precision_v2_preregistration_2026_10_08.json'
SNAP = ROOT/'experiments/common_projected_observed_backend_source_2026_10_08'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def binding(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def replace(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not NEW.exists() and not PRE.exists() and not SNAP.exists()
    prior = json.loads((ROOT/'experiments/common_projected_observed_preregistration_2026_10_08.json').read_text(encoding='utf-8'))
    for b in prior['source_bindings']:
        assert sha(ROOT/b['path']) == b['sha256'], b['path']
    failed = json.loads((ROOT/'experiments/common_projected_observed_independent_2026_10_08/attempt01.json').read_text(encoding='utf-8'))
    assert not failed['complete'] and len(failed['series']) == 3 and failed['medical_observed_packages_loaded'] == 4
    s = OLD.read_text(encoding='utf-8')
    s = replace(s, "common_projected_observed_independent_2026_10_08'", "common_projected_observed_independent_precision_v2_2026_10_08'")
    s = replace(s, "common_projected_observed_preregistration_2026_10_08.json'", "common_projected_observed_precision_v2_preregistration_2026_10_08.json'")
    s = replace(s, "ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md'", "ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PRECISION_V2_PROTOCOL_2026-10-08.md'")
    helper = '''def operator_coordinates(coords, old, target):
    # Installed UpSample.h uses scalar_t scale and opmath<float> source indices.
    old = np.asarray(old, dtype=np.int64)
    scale = old.astype(np.float32)/np.asarray(target, dtype=np.float32)
    at = scale*(coords.astype(np.float32)+np.float32(.5))-np.float32(.5)
    return np.clip(at, 0, old-1).astype(np.float32)


def precision_diagnostic(actual, ideal, coords, old, target):
    error = np.abs(actual-ideal)
    limit = ATOL+RTOL*np.abs(ideal)
    failed = error > limit
    at64 = np.clip((coords+.5)*np.asarray(old)/target-.5, 0, np.asarray(old)-1)
    at32 = operator_coordinates(coords, old, target)
    bad = np.argwhere(failed)
    worst = sorted(bad.tolist(), key=lambda ij: error[tuple(ij)]/limit[tuple(ij)], reverse=True)[:4]
    examples = [dict(target_rc=coords[i].tolist(), anchor_ordinal=int(j),
                     actual=float(actual[i,j]), ideal=float(ideal[i,j]),
                     abs_error=float(error[i,j]), original_tolerance=float(limit[i,j])) for i,j in worst]
    return dict(ideal_float64_coordinate_max_abs_error=float(error.max()),
                original_atol=ATOL, original_rtol=RTOL, original_failed_samples=int(failed.sum()),
                original_allclose_passed=not bool(failed.any()),
                worst_tolerance_ratio=float(np.max(error/limit)),
                max_coordinate_difference=float(np.max(np.abs(at32.astype(np.float64)-at64))),
                example_original_failures=examples)


'''
    s = replace(s, 'def explicit_bilinear(values_rca, coords_rc, target_rc):', helper+'def explicit_bilinear(values_rca, coords_rc, target_rc, ideal=False):')
    s = replace(s, 'at = np.clip((coords_rc+.5)*old/target_rc-.5, 0, old-1)',
                'at = (np.clip((coords_rc+.5)*old/target_rc-.5, 0, old-1) if ideal else\n          operator_coordinates(coords_rc, old, target_rc))')
    s = replace(s, "z = np.clip((coords[:, 0]+.5)*n/nz-.5, 0, n-1)",
                "z = operator_coordinates(coords[:, 0], n, nz)")
    s = replace(s, 'z = np.clip((coords[:, 0]+.5)*shape[2]/target[0]-.5, 0, shape[2]-1)',
                'z = operator_coordinates(coords[:, 0], shape[2], target[0])')
    anchor = "            n = int(shape[2])\n"
    diagnostic = '''            ideal_check = precision_diagnostic(
                anchors[rc[:, 0], rc[:, 1], :],
                explicit_bilinear(normalized, rc, target[1:], ideal=True),
                rc, shape[:2], target[1:])
            if index == 3:
                assert ideal_check['original_failed_samples'] > 0
            n = int(shape[2])
'''
    s = replace(s, anchor, diagnostic)
    s = replace(s, 'source_projection_check=projection_check, full_Hermite_check=hermite_check,',
                'source_projection_check=projection_check, ideal_coordinate_diagnostic=ideal_check,\n                                    full_Hermite_check=hermite_check,')
    s = replace(s, "z = np.clip((coords[:, 0]+.5)*n/target[0]-.5, 0, n-1)",
                "z = operator_coordinates(coords[:, 0], n, target[0])")
    s = replace(s, "             training_updates=0, validation_data_read=False, confirmation_patients_opened=False,",
                "             training_updates=0, torch_version=torch.__version__,\n             original_v1_failure_retained=True, float64_coordinate_diagnostic_retained=True,\n             validation_data_read=False, confirmation_patients_opened=False,")
    s = replace(s, "                         no_native_GT_or_neural_IO=True)",
                "                         no_native_GT_or_neural_IO=True,\n                         original_series4_failure_reproduced_and_coordinate_precision_explained=True)")
    ast.parse(s, filename=str(NEW))
    with NEW.open('x', encoding='utf-8') as f:
        f.write(s)
    SNAP.mkdir()
    snapshots = []
    for rel in ('ATen/native/UpSample.h', 'ATen/OpMathType.h'):
        original = Path('D:/conda/envs/MRI/Lib/site-packages/torch/include')/rel
        dest = SNAP/(original.name+'.source_snapshot')
        with dest.open('xb') as f:
            f.write(original.read_bytes())
        assert sha(dest) == sha(original)
        snapshots.append(dict(original_header=str(original), frozen_copy=binding(dest)))
    paths = [Path(__file__), OLD, NEW,
             ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PRECISION_V2_PROTOCOL_2026-10-08.md',
             ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md',
             ROOT/'experiments/common_projected_input_audit_2026_10_08.py',
             ROOT/'experiments/common_projected_observed_preregistration_2026_10_08.json',
             ROOT/'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json',
             ROOT/'experiments/common_projected_observed_independent_2026_10_08/attempt01.json']
    paths += [SNAP/(Path(rel).name+'.source_snapshot') for rel in ('ATen/native/UpSample.h', 'ATen/OpMathType.h')]
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
             source_bindings=[binding(p) for p in paths], frozen_backend_headers=snapshots,
             original_v1_actual_tool_exit=1, original_v1_terminal_chunk='6f11e0',
             original_v1_checked_series=3, original_v1_loaded_observed_packages=4,
             protocol_v2_frozen_before_its_array_load=True, original_input_source_and_result_unchanged=True,
             no_tolerance_widening=True, atol=3e-5, rtol=3e-5,
             medical_arrays_loaded=0, neural_forwards=0, GPU_forwards=0, training_updates=0,
             goal_status='active', publication_claim_confirmed=False)
    with PRE.open('x', encoding='utf-8') as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(dict(complete=True, source_bindings=len(paths), original_failed_attempt_retained=True,
                          medical_arrays_loaded=0, v2_preregistration_sha256=sha(PRE))), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
