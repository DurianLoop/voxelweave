"""Qualify the new common-source control on all 19 developer observed packages."""
import gc
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from mc_rc_common_projected_observed_2026_10_08 import (
    ROOT, torch, read, sha, array_sha, development_observed_cases,
    load_development_observed, lattice, shared_source, projected_pair_fields,
    branched_native, final_affines, augment_pair,
)
from common_projected_input_audit_2026_10_08 import StageAudit, entry

OUT = ROOT/'experiments/common_projected_observed_qualification_2026_10_08'
PRE = ROOT/'experiments/common_projected_observed_preregistration_2026_10_08.json'
OLD = ROOT/'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07/attempt01.json'
PROTOCOL = ROOT/'COMMON_PROJECTED_OBSERVED_INPUT_PROTOCOL_2026-10-08.md'
ATOL = RTOL = 3e-5
SEED = 20261008


def coordinates(nz, target, idx, series):
    coords = np.random.default_rng(np.random.SeedSequence([SEED, 810, series])).integers(
        0, np.asarray(target), size=(512, 3))
    special = []
    for z in idx:
        at = int(np.rint((z+.5)*target[0]/nz-.5))
        for dz in (-1, 0, 1):
            for r, c in ((0, 0), (target[1]//2, target[2]//2), (target[1]-1, target[2]-1)):
                special.append([int(np.clip(at+dz, 0, target[0]-1)), r, c])
    return np.unique(np.concatenate((coords, np.asarray(special, dtype=int))), axis=0)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    start = time.perf_counter()
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[], series=[],
             medical_observed_packages_loaded=0, model_arrays_loaded=0, neural_forwards=0, GPU_forwards=0,
             training_updates=0, task_effects_scored=False, validation_data_read=False,
             confirmation_patients_opened=False, locked_IXI_opened=False, publication_claim_confirmed=False)
    old, pre = read(OLD), read(PRE)
    assert old['complete'] and pre['complete'] and not old['errors'] and not pre['errors']
    audit = StageAudit(OUT, torch, [s['observed_package'] for s in old['series']], start)
    path = OUT/'attempt01.json'

    def save():
        path.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    save()
    try:
        for b in pre['source_bindings']:
            assert sha(ROOT/b['path']) == b['sha256'], b['path']
        r['source_bindings'] = [entry(PRE), entry(PROTOCOL), entry(Path(__file__)), entry(OLD),
                               entry(ROOT/'experiments/mc_rc_common_projected_observed_2026_10_08.py'),
                               entry(ROOT/'experiments/common_projected_input_audit_2026_10_08.py')]
        r['resources_before'] = audit.guard()
        cases = development_observed_cases()
        old_by = {s['uid']: s for s in old['series']}
        assert len(cases) == 19 and len({c['patient'] for c, row in cases}) == 11
        for index, (case, row) in enumerate(cases):
            audit.guard()
            item_start = time.perf_counter()
            obs = load_development_observed(case, row)
            r['medical_observed_packages_loaded'] += 1
            grid = lattice(case)
            source, norm_hash = shared_source(obs, grid)
            common_hash = array_sha(source.anchors_rca)
            fields, native_hashes = projected_pair_fields(source, grid)
            dense, numerator = branched_native(source)
            indices = list(source.indices)
            missing = np.ones(source.native_planes, dtype=bool)
            missing[indices] = False
            assert np.array_equal(dense[:, :, indices], source.anchors_rca)
            assert np.array_equal(numerator[:, :, indices], source.anchors_rca)
            assert np.count_nonzero(numerator[:, :, missing]) == 0
            last = source.indices[-1]
            assert np.array_equal(dense[:, :, last:],
                                  np.broadcast_to(source.anchors_rca[:, :, -1, None], dense[:, :, last:].shape))
            assert native_hashes == dict(dense=array_sha(dense), numerator=array_sha(numerator))
            assert source.observed_statistics == old_by[case['uid']]['statistics']
            assert json.loads(json.dumps(grid)) == old_by[case['uid']]['grid']
            assert array_sha(fields['availability']) == old_by[case['uid']]['physical_availability_sha256']
            assert all(np.isfinite(a).all() for a in fields.values())
            assert 0 <= fields['availability'].min() <= fields['availability'].max() <= 1
            assert all(np.count_nonzero(a[fields['valid_grid'] == 0]) == 0 for a in fields.values())
            assert np.count_nonzero(fields['numerator'][fields['availability'] == 0]) == 0
            physical_affine, padded_affine = final_affines(source, grid)
            assert np.allclose(physical_affine, grid['physical_affine_zrc_ras'], atol=1e-12, rtol=1e-12)
            assert np.allclose(padded_affine, grid['padded_affine_zrc_ras'], atol=1e-12, rtol=1e-12)
            coords = coordinates(source.native_planes, grid['unpadded_shape_zrc'], source.indices, index)
            padded = coords + np.asarray([lo for lo, hi in grid['padding']])
            z = np.clip((coords[:, 0]+.5)*source.native_planes/grid['unpadded_shape_zrc'][0]-.5,
                        0, source.native_planes-1)
            lo = np.floor(z).astype(int)
            hi = np.minimum(lo+1, source.native_planes-1)
            w = z-lo
            checks = []
            for kind, native in (('dense', dense), ('numerator', numerator)):
                expected = ((1-w)*native[coords[:, 1], coords[:, 2], lo] +
                            w*native[coords[:, 1], coords[:, 2], hi])
                actual = fields[kind][tuple(padded.T)]
                assert np.allclose(actual, expected, atol=ATOL, rtol=RTOL), kind
                checks.append(dict(field=kind, samples=len(coords),
                                   max_abs_error=float(np.max(np.abs(actual-expected))), passed=True))
            augmentation = []
            for kind, key in (('dense', 'dense'), ('direct', 'numerator')):
                augmented = augment_pair(fields[key], fields['availability'], fields['valid_grid'],
                                         1.07, -.08, kind, (True, False, True))
                unflipped = np.flip(augmented, axis=(1, 3))
                assert np.array_equal(unflipped[1], fields['availability'])
                assert np.count_nonzero(unflipped[:, fields['valid_grid'] == 0]) == 0
                if kind == 'direct':
                    assert np.count_nonzero(unflipped[0][fields['availability'] == 0]) == 0
                expected = (1.07*fields[key][tuple(padded.T)] - .08*
                            fields['availability' if kind == 'direct' else 'valid_grid'][tuple(padded.T)])
                assert np.array_equal(unflipped[0][tuple(padded.T)], expected)
                augmentation.append(dict(kind=kind, paired_input_sha256=array_sha(augmented),
                                         mask_unchanged=True, padding_zero=True, sample_values_exact=True))
                del augmented, unflipped
            assert array_sha(source.anchors_rca) == common_hash and not source.anchors_rca.flags.writeable
            rec = dict(patient=case['patient'], uid=case['uid'], observed_package=row['observed_package'],
                       observed_package_sha256=row['observed_package_sha256'],
                       observed_array_sha256=array_sha(obs.pixels), observed_indices=indices,
                       native_shape_rcz=case['native_shape'], native_affine_rcz_ras=case['affine_rcz_ras'],
                       normalized_observed_sha256=norm_hash, statistics=source.observed_statistics,
                       shared_projected_anchors_sha256=common_hash,
                       projected_anchors_shape_rca=list(source.anchors_rca.shape),
                       projected_affine_rcz_ras=source.affine_rcz_ras,
                       projected_native_dense_sha256=native_hashes['dense'],
                       projected_native_numerator_sha256=native_hashes['numerator'], grid=grid,
                       physical_dense_sha256=array_sha(fields['dense']),
                       physical_numerator_sha256=array_sha(fields['numerator']),
                       physical_availability_sha256=array_sha(fields['availability']),
                       physical_valid_grid_sha256=array_sha(fields['valid_grid']),
                       same_anchor_object_source=True, shared_source_immutable=True,
                       same_availability_object=True, old_availability_hash_equal=True,
                       native_contracts_passed=True, geometry_passed=True,
                       z_interpolation_checks=checks, augmentation_checks=augmentation,
                       padded_shape_zrc=list(fields['dense'].shape),
                       each_physical_channel_bytes=int(fields['dense'].nbytes),
                       preprocessing_and_qualification_seconds=time.perf_counter()-item_start)
            r['series'].append(rec)
            print(json.dumps(dict(index=index+1, patient=case['patient'], passed=True,
                                  max_z_error=max(c['max_abs_error'] for c in checks)), ensure_ascii=False), flush=True)
            del obs, source, fields, dense, numerator
            gc.collect()
            save()
            audit.guard()
        r['io_audit'] = audit.result()
        assert not audit.denied
        r['gate'] = dict(all19_development_series=True, all11_development_patients=True,
                         common_projected_anchors_used_for_both_branches=True,
                         original_observed_statistics_retained=True, old_availability_hashes_exact=True,
                         native_z_anchor_zero_tail_contracts=True, affine_pixel_center_contract=True,
                         fractional_mask_and_padding_contract=True, intensity_augmentation_contract=True,
                         sampled_z_math_contract=True, no_native_GT_or_neural_IO=True)
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
