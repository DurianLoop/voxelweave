"""Independent package reload, library hash replay, and separate NumPy mathematics.

Does not import production input functions or the original reconstruct function.
Torch/SciPy replay is explicitly distinct from independent coordinate/Hermite checks.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
import gc
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from scipy.interpolate import PchipInterpolator
from common_projected_input_audit_2026_10_08 import ROOT, StageAudit, entry, read, sha, arrsha

torch.set_num_threads(1)
torch.set_num_interop_threads(1)
OUT = ROOT/'experiments/common_projected_observed_independent_precision_v2_2026_10_08'
SOURCE = ROOT/'experiments/common_projected_observed_qualification_2026_10_08/attempt01.json'
PRE = ROOT/'experiments/common_projected_observed_precision_v2_preregistration_2026_10_08.json'
ATOL = RTOL = 3e-5
SEED = 20261008


def own_grid(shape_rcz, affine):
    old = np.asarray(shape_rcz)[[2, 0, 1]]
    spacing = np.sqrt(np.sum(np.asarray(affine)[:3, :3]**2, axis=0))[[2, 0, 1]]
    target = np.maximum(1, np.rint(old*spacing/.5).astype(int))
    scale = old/target
    permutation = np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float)
    center = np.eye(4)
    center[:3, :3] = np.diag(scale)
    center[:3, 3] = scale/2-.5
    physical = np.asarray(affine)@permutation@center
    padding = [[max(0, p-int(n))//2, (max(0, p-int(n))+1)//2]
               for n, p in zip(target, (64, 128, 128))]
    pad_map = np.eye(4)
    pad_map[:3, 3] = -np.asarray([p[0] for p in padding])
    return target, padding, physical, physical@pad_map


def operator_coordinates(coords, old, target):
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


def explicit_bilinear(values_rca, coords_rc, target_rc, ideal=False):
    old = np.asarray(values_rca.shape[:2])
    at = (np.clip((coords_rc+.5)*old/target_rc-.5, 0, old-1) if ideal else
          operator_coordinates(coords_rc, old, target_rc))
    lo = np.floor(at).astype(int)
    hi = np.minimum(lo+1, old-1)
    frac = at-lo
    result = np.zeros((len(at), values_rca.shape[2]), dtype=np.float64)
    for r in range(2):
        for c in range(2):
            rr = hi[:, 0] if r else lo[:, 0]
            cc = hi[:, 1] if c else lo[:, 1]
            weight = (frac[:, 0] if r else 1-frac[:, 0])*(frac[:, 1] if c else 1-frac[:, 1])
            result += weight[:, None]*values_rca[rr, cc, :]
    return result


def scipy_replay(anchors, n, indices):
    result = np.zeros((*anchors.shape[:2], n), dtype=np.float32)
    result[:, :, indices] = anchors
    last = indices[-1]
    for z in range(1, last):
        if z % 4 == 0:
            continue
        i, t = z//4, (z % 4)/4
        if i >= 1 and i+2 < anchors.shape[2]:
            knots = np.arange(i-1, i+3)
            result[:, :, z] = PchipInterpolator(knots*4, anchors[:, :, knots], axis=2)(z)
        else:
            result[:, :, z] = (1-t)*anchors[:, :, i] + t*anchors[:, :, i+1]
    result[:, :, last+1:] = anchors[:, :, -1, None]
    return result


def harmonic_slope(left, right):
    result = np.zeros_like(left)
    same = (left*right > 0)
    result[same] = 2/(1/left[same]+1/right[same])
    return result


def hermite_math(anchors, n, indices):
    # Same *mathematical* piecewise contract, without calling SciPy.
    a = anchors.astype(np.float64)
    result = np.zeros((*a.shape[:2], n), dtype=np.float64)
    result[:, :, indices] = a
    last = indices[-1]
    for z in range(1, last):
        if z % 4 == 0:
            continue
        i, t = z//4, (z % 4)/4
        if i >= 1 and i+2 < a.shape[2]:
            d0 = (a[:, :, i]-a[:, :, i-1])/4
            d1 = (a[:, :, i+1]-a[:, :, i])/4
            d2 = (a[:, :, i+2]-a[:, :, i+1])/4
            m0, m1 = harmonic_slope(d0, d1), harmonic_slope(d1, d2)
            result[:, :, z] = ((2*t**3-3*t**2+1)*a[:, :, i] +
                               (t**3-2*t**2+t)*4*m0 +
                               (-2*t**3+3*t**2)*a[:, :, i+1] + (t**3-t**2)*4*m1)
        else:
            result[:, :, z] = (1-t)*a[:, :, i]+t*a[:, :, i+1]
    result[:, :, last+1:] = a[:, :, -1, None]
    return result


def torch_physical(field, target, padding):
    x = torch.from_numpy(np.ascontiguousarray(field.transpose(2, 0, 1)))[None, None]
    with torch.no_grad():
        core = F.interpolate(x, size=target.tolist(), mode='trilinear', align_corners=False)[0, 0].numpy()
    return np.pad(core, padding, mode='constant').astype(np.float32, copy=False)


def physical_coordinates(n, target, indices, series):
    coords = np.random.default_rng(np.random.SeedSequence([SEED, 810, series])).integers(
        0, target, size=(512, 3))
    special = []
    for z in indices:
        at = int(np.rint((z+.5)*target[0]/n-.5))
        for dz in (-1, 0, 1):
            for r, c in ((0, 0), (target[1]//2, target[2]//2), (target[1]-1, target[2]-1)):
                special.append([int(np.clip(at+dz, 0, target[0]-1)), r, c])
    return np.unique(np.concatenate((coords, np.asarray(special, dtype=int))), axis=0)


def explicit_z(field, coords, n, nz):
    z = operator_coordinates(coords[:, 0], n, nz)
    lo = np.floor(z).astype(int)
    hi = np.minimum(lo+1, n-1)
    frac = z-lo
    return ((1-frac)*field[coords[:, 1], coords[:, 2], lo] +
            frac*field[coords[:, 1], coords[:, 2], hi])


def math_direct_from_raw(normalized, indices, coords, shape, target):
    # Explicit separable form of the original 8-corner trilinear map.
    projected = explicit_bilinear(normalized, coords[:, 1:], target[1:])
    z = operator_coordinates(coords[:, 0], shape[2], target[0])
    lo = np.floor(z).astype(int)
    hi = np.minimum(lo+1, shape[2]-1)
    frac = z-lo
    lookup = {int(z): i for i, z in enumerate(indices)}
    result = np.zeros(len(coords), dtype=np.float64)
    for j, (a, b, w) in enumerate(zip(lo, hi, frac)):
        if int(a) in lookup:
            result[j] += (1-w)*projected[j, lookup[int(a)]]
        if int(b) in lookup:
            result[j] += w*projected[j, lookup[int(b)]]
    return result


def check(actual, expected, name):
    maximum = float(np.max(np.abs(actual-expected)))
    assert np.allclose(actual, expected, atol=ATOL, rtol=RTOL), (name, maximum)
    return dict(name=name, elements=int(actual.size), max_abs_error=maximum, passed=True,
                atol=ATOL, rtol=RTOL)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    start = time.perf_counter()
    q, pre = read(SOURCE), read(PRE)
    assert q['complete'] and pre['complete'] and not q['errors'] and all(q['gate'].values())
    audit = StageAudit(OUT, torch, [s['observed_package'] for s in q['series']], start)
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[], series=[],
             medical_observed_packages_loaded=0, model_arrays_loaded=0, neural_forwards=0, GPU_forwards=0,
             training_updates=0, torch_version=torch.__version__,
             original_v1_failure_retained=True, float64_coordinate_diagnostic_retained=True,
             validation_data_read=False, confirmation_patients_opened=False,
             locked_IXI_opened=False, task_effects_scored=False, publication_claim_confirmed=False)
    path = OUT/'attempt01.json'

    def save():
        path.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    save()
    try:
        for b in pre['source_bindings']:
            assert sha(ROOT/b['path']) == b['sha256'], b['path']
        r['source_bindings'] = [entry(SOURCE), entry(PRE), entry(Path(__file__)),
                               entry(ROOT/'experiments/common_projected_input_audit_2026_10_08.py'),
                               entry(ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PRECISION_V2_PROTOCOL_2026-10-08.md')]
        r['resources_before'] = audit.guard()
        for index, rec in enumerate(q['series']):
            audit.guard()
            p = ROOT/rec['observed_package']
            assert sha(p) == rec['observed_package_sha256']
            with np.load(p, allow_pickle=False) as package:
                a = package['observed_rcz'].copy()
                r['medical_observed_packages_loaded'] += 1
                idx = package['observed_indices'].astype(int).tolist()
                shape = package['native_shape'].astype(int)
                affine = package['affine_rcz_ras'].copy()
            assert arrsha(a) == rec['observed_array_sha256']
            assert idx == rec['observed_indices'] == list(range(0, int(shape[2]), 4))
            assert shape.tolist() == rec['native_shape_rcz'] and np.array_equal(affine, rec['native_affine_rcz_ras'])
            mean, std = float(np.mean(a, dtype=np.float64)), float(np.std(a, dtype=np.float64))
            st = dict(mean=mean, population_std=std, divisor=std if std > 0 else 1.,
                      elements=int(a.size), zero_std=std == 0)
            assert st == rec['statistics']
            normalized = ((a.astype(np.float64)-mean)/st['divisor']).astype(np.float32)
            assert arrsha(normalized) == rec['normalized_observed_sha256']
            target, padding, physical_affine, padded_affine = own_grid(shape, affine)
            assert target.tolist() == rec['grid']['unpadded_shape_zrc'] and padding == rec['grid']['padding']
            assert np.allclose(physical_affine, rec['grid']['physical_affine_zrc_ras'], atol=1e-12, rtol=1e-12)
            assert np.allclose(padded_affine, rec['grid']['padded_affine_zrc_ras'], atol=1e-12, rtol=1e-12)
            intermediate = np.eye(4)
            scale = shape[:2]/target[1:]
            intermediate[0, 0], intermediate[1, 1] = scale
            intermediate[:2, 3] = scale/2-.5
            assert np.allclose(affine@intermediate, rec['projected_affine_rcz_ras'], atol=1e-12, rtol=1e-12)
            x = torch.from_numpy(np.ascontiguousarray(normalized.transpose(2, 0, 1)))[:, None]
            with torch.no_grad():
                core = F.interpolate(x, size=target[1:].tolist(), mode='bilinear', align_corners=False)[:, 0].numpy()
            anchors = np.ascontiguousarray(core.transpose(1, 2, 0))
            assert arrsha(anchors) == rec['shared_projected_anchors_sha256']
            rc = np.random.default_rng(np.random.SeedSequence([SEED, 810, index])).integers(
                0, target[1:], size=(512, 2))
            rc = np.unique(np.concatenate((rc, [[0, 0], target[1:]//2, target[1:]-1])), axis=0)
            projection_check = check(anchors[rc[:, 0], rc[:, 1], :],
                                     explicit_bilinear(normalized, rc, target[1:]), 'sampled_bilinear_all_anchors')
            ideal_check = precision_diagnostic(
                anchors[rc[:, 0], rc[:, 1], :],
                explicit_bilinear(normalized, rc, target[1:], ideal=True),
                rc, shape[:2], target[1:])
            if index == 3:
                assert ideal_check['original_failed_samples'] > 0
            n = int(shape[2])
            dense = scipy_replay(anchors, n, idx)
            numerator = np.zeros_like(dense)
            numerator[:, :, idx] = anchors
            assert arrsha(dense) == rec['projected_native_dense_sha256']
            assert arrsha(numerator) == rec['projected_native_numerator_sha256']
            mathematical_dense = hermite_math(anchors, n, idx)
            hermite_check = check(dense, mathematical_dense, 'full_native_z_Hermite_linear_tail')
            del mathematical_dense
            physical_dense = torch_physical(dense, target, padding)
            physical_num = torch_physical(numerator, target, padding)
            mask = np.zeros(tuple(shape), dtype=np.float32)
            mask[:, :, idx] = 1
            physical_mask = torch_physical(mask, target, padding)
            valid = np.pad(np.ones(target, dtype=np.float32), padding, mode='constant')
            for key, data in (('dense', physical_dense), ('numerator', physical_num),
                              ('availability', physical_mask), ('valid_grid', valid)):
                assert arrsha(data) == rec[f'physical_{key}_sha256'], key
            coords = physical_coordinates(n, target, idx, index)
            padded = coords+np.asarray([lo for lo, hi in padding])
            z_checks = [check(data[tuple(padded.T)], explicit_z(native, coords, n, target[0]), 'sampled_z_'+key)
                        for key, data, native in (('dense', physical_dense, dense),
                                                  ('numerator', physical_num, numerator))]
            original_math = math_direct_from_raw(normalized, idx, coords, shape, target)
            direct_math = check(physical_num[tuple(padded.T)], original_math, 'sampled_original_raw_direct_math')
            z = operator_coordinates(coords[:, 0], n, target[0])
            lo = np.floor(z).astype(int)
            hi = np.minimum(lo+1, n-1)
            weight = z-lo
            expected_mask = (1-weight)*np.isin(lo, idx)+weight*np.isin(hi, idx)
            mask_check = check(physical_mask[tuple(padded.T)], expected_mask, 'sampled_fractional_availability')
            # An exact whole-field difference is diagnostic only, with no pass threshold.
            original_num = np.zeros(tuple(shape), dtype=np.float32)
            original_num[:, :, idx] = normalized
            original_physical = torch_physical(original_num, target, padding)
            difference = np.abs(physical_num.astype(np.float64)-original_physical)
            original_diagnostic = dict(whole_field_bitwise_equal=np.array_equal(physical_num, original_physical),
                                       max_abs_difference=float(difference.max()),
                                       mean_abs_difference=float(difference.mean()),
                                       mathematical_equivalence_sample_gate_passed=True,
                                       whole_field_float32_equivalence_certified=False)
            for kind, data in (('dense', physical_dense), ('direct', physical_num)):
                transformed = 1.07*data+(-.08)*(physical_mask if kind == 'direct' else valid)
                transformed = np.where(valid > 0, transformed, np.float32(0)).astype(np.float32)
                paired = np.stack((np.flip(transformed, axis=(0, 2)), np.flip(physical_mask, axis=(0, 2))))
                expected = next(a for a in rec['augmentation_checks'] if a['kind'] == kind)
                assert arrsha(paired) == expected['paired_input_sha256'], kind
                del transformed, paired
            r['series'].append(dict(patient=rec['patient'], uid=rec['uid'], observed_source_hashes_equal=True,
                                    full_library_execution_hash_replay_exact=True,
                                    source_projection_check=projection_check, ideal_coordinate_diagnostic=ideal_check,
                                    full_Hermite_check=hermite_check,
                                    sampled_z_checks=z_checks, original_direct_math_check=direct_math,
                                    mask_check=mask_check, geometry_independently_equal=True,
                                    augmentation_hashes_equal=True, original_direct_float32_diagnostic=original_diagnostic))
            print(json.dumps(dict(index=index+1, patient=rec['patient'], passed=True,
                                  projection_max_error=projection_check['max_abs_error'],
                                  Hermite_max_error=hermite_check['max_abs_error']), ensure_ascii=False), flush=True)
            del a, normalized, x, core, anchors, dense, numerator, mask, valid
            del physical_dense, physical_num, physical_mask, original_num, original_physical, difference
            gc.collect()
            save()
            audit.guard()
        assert len(r['series']) == 19 and len({s['patient'] for s in r['series']}) == 11
        assert not audit.denied
        r['io_audit'] = audit.result()
        r['gate'] = dict(all19_observed_package_reloads=True, full_execution_hashes_exact=True,
                         independent_sampled_bilinear=True, independent_full_Hermite_linear_tail=True,
                         independent_sampled_z_interpolation=True, independent_sampled_original_direct_math=True,
                         independent_availability_and_geometry=True, augmentation_exact=True,
                         no_native_GT_or_neural_IO=True,
                         original_series4_failure_reproduced_and_coordinate_precision_explained=True)
        r['resources_after'] = audit.guard()
        r['complete'] = True
    except Exception as exc:
        r['errors'].append(f'{type(exc).__name__}: {exc}')
        r['traceback'] = traceback.format_exc()
        r['io_audit'] = audit.result()
    r['elapsed_seconds'] = time.perf_counter()-start
    r['finished_utc'] = datetime.now(timezone.utc).isoformat()
    save()
    print(json.dumps(dict(complete=r['complete'], errors=r['errors'], checked_series=len(r['series']),
                          observed_packages_loaded=r['medical_observed_packages_loaded'],
                          elapsed_seconds=r['elapsed_seconds']), ensure_ascii=False), flush=True)
    return int(not r['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
