"""Independent observed-mask replay: physical disk, rational support, exact costs.

Reads frozen prediction arrays and metadata only, never MRI/GT/checkpoints.
Does not import production, EDT, torch, or its grid/tile/cost routines.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
import hashlib, itertools, json, math, sys, time, traceback
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.ndimage import binary_dilation
from mc_rc_reference_resources_2026_10_07 import resource_guard

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07'
METHODS = ('joint_QDA', 'appearance_QDA', 'coordinates_QDA', 'joint_LDA')
PATCH = (64, 128, 128)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def array_hash(value):
    value = np.ascontiguousarray(value)
    h = hashlib.sha256(json.dumps(dict(shape=list(value.shape), dtype=value.dtype.str), sort_keys=True).encode())
    h.update(memoryview(value).cast('B'))
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def binding(path):
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=sha(path), bytes=path.stat().st_size)

def compare(actual, expected, context=''):
    if isinstance(expected, float):
        assert math.isclose(actual, expected, rel_tol=0, abs_tol=1e-14), (context, actual, expected)
    elif isinstance(expected, dict):
        assert set(actual) == set(expected), (context, set(actual), set(expected))
        for key in expected:
            compare(actual[key], expected[key], context+'/'+key)
    else:
        assert actual == expected, (context, actual, expected)

def neighbors(native_length, target_length):
    lo, hi = [], []
    for index in range(target_length):
        q = Fraction((2*index+1)*native_length-target_length, 2*target_length)
        q = min(max(q, Fraction(0)), Fraction(native_length-1))
        lo.append(q.numerator//q.denominator)
        hi.append(-((-q.numerator)//q.denominator))
    return np.array(lo), np.array(hi)

def positive_support(native, dims, padding):
    value = native.transpose(2, 0, 1).copy()
    for axis, (old, new) in enumerate(zip(value.shape, dims)):
        low, high = neighbors(old, new)
        value = np.take(value, low, axis=axis) | np.take(value, high, axis=axis)
    return np.pad(value, padding, mode='constant', constant_values=False)

def cost(support, locations):
    touched = []
    for index, start in enumerate(locations):
        window = support[tuple(slice(s, s+p) for s, p in zip(start, PATCH))]
        if window.any():
            touched.append(index)
    pair_ids = sorted(set(i//2 for i in touched))
    n, k = (len(locations)+1)//2, len(pair_ids)
    return dict(affected_tile_ids=touched, recomputed_batch_pair_ids=pair_ids,
        affected_tiles=len(touched), recomputed_tiles=sum(i//2 in pair_ids for i in range(len(locations))),
        recomputed_batch_pairs=k, saved_forward_calls=n-k, saved_forward_fraction=float(Fraction(n-k, n)),
        five_same_support_actions_with_initialization_count_ratio=float(Fraction(n+5*k, 5*n)),
        minimum_same_support_actions_for_strict_count_saving=n//(n-k)+1 if k<n else None)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    dest = OUT/'independent_disk_rational_attempt01.json'
    assert not dest.exists()
    started = time.perf_counter()
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[],
        cached_prediction_arrays_loaded=0, checked_series=0, checked_method_supports=0, checked_plane_records=0,
        new_MRI_pixel_arrays_loaded=0, new_GT_arrays_loaded=0, model_or_classification_calls=0,
        GPU_forwards=0, training_updates=0, confirmation_patients_opened=False, validation_data_read=False,
        coverage_metrics_sourced_not_newly_scored=True, publication_claim_confirmed=False,
        implementation_independence='explicit physical disk + binary_dilation; Fraction centers + Boolean OR; independent tile/cost/summary',
        workspace_read_paths=[], prohibited_access_attempts=[])
    allowed = {Path(__file__).resolve(), (OUT/'attempt01.json').resolve()}
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if not path.is_relative_to(ROOT.parent.resolve()) or path.is_relative_to(OUT.resolve()):
            return
        if path not in allowed:
            result['prohibited_access_attempts'].append(str(path))
            raise PermissionError('Unlisted workspace access: '+str(path))
        key = path.relative_to(ROOT).as_posix()
        if key not in result['workspace_read_paths']:
            result['workspace_read_paths'].append(key)
    def save():
        dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    def guard():
        assert time.perf_counter()-started < 900
        assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()) < 5_000_000
        return resource_guard()
    save()
    try:
        result['resources_before'] = guard()
        sys.addaudithook(audit)
        production = read(OUT/'attempt01.json')
        assert production['complete'] and not production['errors'] and not production['prohibited_access_attempts']
        allowed.update((ROOT/v['path']).resolve() for v in production['source_bindings'])
        for v in production['source_bindings']:
            assert sha(ROOT/v['path']) == v['sha256']
        for snap in production['source_snapshots']:
            assert sha(ROOT/snap['snapshot']['path']) == snap['snapshot']['sha256'] == sha(ROOT/snap['source_path'])
        assert len({s['snapshot']['path'] for s in production['source_snapshots']}) == 9
        oldfile = ROOT/'experiments/mc_rc_anchor_qda_cpu/attempt_01.json'
        contractfile = ROOT/'experiments/mc_rc_anchor_qda_cpu/run_contract.json'
        old = read(oldfile)
        cases = {c['uid']: c for c in read(contractfile)['cases']}
        original = {s['uid']: s for s in old['series']}
        assert set(cases) == set(original) == {s['uid'] for s in production['series']} and len(cases) == 16
        result['source_bindings'] = [binding(p) for p in (Path(__file__), OUT/'attempt01.json', oldfile, contractfile)]
        snapshot = OUT/(Path(__file__).name+'.source_snapshot')
        snapshot.write_bytes(Path(__file__).read_bytes())
        exact = []
        for row in production['series']:
            guard()
            c = cases[row['uid']]
            native_shape = c['native_shape']
            old_shape = [native_shape[2], native_shape[0], native_shape[1]]
            affine = np.array(c['affine_rcz_ras'], dtype=np.float64)
            spacings = np.sqrt((affine[:3,:3]**2).sum(axis=0))[[2,0,1]]
            dims = np.maximum(1, np.rint(np.array(old_shape)*spacings/0.5).astype(int)).tolist()
            padding = [(max(0,p-n)//2, (max(0,p-n)+1)//2) for p,n in zip(PATCH,dims)]
            grid = row['physical_grid']
            assert dims == grid['unpadded_shape_zrc'] and old_shape == grid['native_shape_zrc']
            assert [list(x) for x in padding] == grid['padding']
            scale = np.array(old_shape)/np.array(dims)
            assert np.array_equal(scale, grid['native_coordinate_scale_zrc'])
            independent_affine = np.eye(4)
            independent_affine[:3,:3] = affine[:3,[2,0,1]]*scale
            independent_affine[:3,3] = affine[:3,3]+affine[:3,[2,0,1]]@(scale/2-0.5)
            assert np.allclose(independent_affine, grid['physical_affine_zrc_ras'], rtol=0, atol=1e-12)
            independent_affine[:3,3] -= independent_affine[:3,:3]@np.array([x[0] for x in padding])
            assert np.allclose(independent_affine, grid['padded_affine_zrc_ras'], rtol=0, atol=1e-12)
            assert np.array_equal(spacings*scale, grid['realized_spacing_zrc_mm'])
            shape = [n+sum(p) for n,p in zip(dims,padding)]
            starts = [sorted({i for i in range(n-p+1) if i%(p//2)==0}|{n-p}) for n,p in zip(shape,PATCH)]
            locations = list(itertools.product(*starts))
            assert shape == row['physical_shape_zrc'] and [list(x) for x in locations] == row['tile_locations_zrc']
            assert (len(locations)+1)//2 == row['full_forward_calls']
            oldrow = original[c['uid']]
            predfile = ROOT/oldrow['prediction_file']
            assert sha(predfile) == oldrow['prediction_sha256']
            target_z = [i for i in range(1, (native_shape[2]-1)//4*4) if i%4]
            spacing_r, spacing_c = c['native_spacing_rcz_mm'][:2]
            rmax, cmax = math.ceil((2.+1e-12)/spacing_r), math.ceil((2.+1e-12)/spacing_c)
            offsets_r = np.arange(-rmax,rmax+1)*spacing_r
            offsets_c = np.arange(-cmax,cmax+1)*spacing_c
            disk = np.hypot(offsets_r[:,None], offsets_c[None,:]) <= 2.+1e-12
            assert disk[rmax,cmax] and np.array_equal(disk,disk[::-1,::-1])
            with np.load(predfile, allow_pickle=False) as pack:
                assert set(pack.files) == set(METHODS)
                for method in METHODS:
                    pred = pack[method]
                    result['cached_prediction_arrays_loaded'] += 1
                    assert pred.dtype == np.bool_ and pred.shape == (*native_shape[:2], len(range(0,native_shape[2],4)))
                    m = row['methods'][method]
                    assert array_hash(pred) == oldrow['prediction_array_sha256'][method] == m['anchor_prediction_array_sha256']
                    assert int(pred.sum()) == m['anchor_prediction_foreground']
                    native = np.zeros(native_shape, dtype=bool)
                    planes = []
                    for z in target_z:
                        union = pred[:,:,z//4] | pred[:,:,z//4+1]
                        plane = binary_dilation(union, structure=disk, border_value=0)
                        native[:,:,z] = plane
                        planes.append(dict(z=z, roi_voxels=int(plane.sum()), roi_array_sha256=array_hash(plane)))
                    assert planes == m['plane_records']
                    assert int(native.sum()) == m['native_ROI_voxels'] and array_hash(native) == m['native_ROI_sha256']
                    assert bool(not native.any()) == m['empty_ROI_no_proposed_edit']
                    physical = positive_support(native,dims,padding)
                    assert int(physical.sum()) == m['physical_support_voxels'] and array_hash(physical) == m['physical_support_sha256']
                    compare(m['cost'],cost(physical,locations),c['uid']+'/'+method)
                    sourced = oldrow['methods'][method]['roi']
                    assert sourced['metrics'] == m['sourced_original_roi_metrics'] and sourced['gate_passed'] == m['sourced_original_roi_gate_passed']
                    by_z = {v['z']:v['counts']['roi_voxels'] for v in sourced['target_records']}
                    assert {v['z']:v['roi_voxels'] for v in planes} == by_z
                    result['checked_plane_records'] += len(planes)
                    result['checked_method_supports'] += 1
            result['checked_series'] += 1
            save()
        patients = sorted({s['patient'] for s in production['series']})
        assert len(patients) == production['development_patients'] == 8
        for summary in production['summaries']:
            method = summary['method']
            pairs = [(s,s['methods'][method]) for s in production['series']]
            n = sum(s['full_forward_calls'] for s,m in pairs)
            k = sum(m['cost']['recomputed_batch_pairs'] for s,m in pairs)
            patient_means = {}
            exact_savings = []
            for p in patients:
                rows = [(s,m) for s,m in pairs if s['patient']==p]
                saving = sum(Fraction(s['full_forward_calls']-m['cost']['recomputed_batch_pairs'],s['full_forward_calls']) for s,m in rows)/len(rows)
                exact_savings.append(saving)
                patient_means[p] = dict(saved_forward_fraction=float(saving),
                    sourced_foreground_recall=float(sum(Fraction(str(m['sourced_original_roi_metrics']['foreground_recall'])) for s,m in rows)/len(rows)),
                    sourced_boundary_recall=float(sum(Fraction(str(m['sourced_original_roi_metrics']['boundary_recall'])) for s,m in rows)/len(rows)))
            expected = dict(method=method,series=16,patients=8,full_forward_calls_total=n,recomputed_batch_pairs_total=k,
                empty_ROI_series=sum(m['native_ROI_voxels']==0 for s,m in pairs),
                nonempty_series_with_any_forward_saving=sum(m['native_ROI_voxels']>0 and m['cost']['saved_forward_calls']>0 for s,m in pairs),
                nonempty_series_with_all_batches_affected=[s['uid'] for s,m in pairs if m['native_ROI_voxels']>0 and not m['cost']['saved_forward_calls']],
                all_series_with_five_count_ratio_strictly_below1=sum(s['full_forward_calls']+5*m['cost']['recomputed_batch_pairs']<5*s['full_forward_calls'] for s,m in pairs),
                series_with_coverage_boundary_ge099_and_forward_saving=sum(m['sourced_original_roi_metrics']['foreground_recall']>=.99 and m['sourced_original_roi_metrics']['boundary_recall']>=.99 and m['cost']['saved_forward_calls']>0 for s,m in pairs),
                sourced_original_ROI_gates_passed=sum(m['sourced_original_roi_gate_passed'] for s,m in pairs),
                patient_means=patient_means,patient_first_mean_saved_forward_fraction=float(sum(exact_savings)/len(patients)),
                patient_first_mean_sourced_foreground_recall=sum(v['sourced_foreground_recall'] for v in patient_means.values())/len(patients),
                patient_first_mean_sourced_boundary_recall=sum(v['sourced_boundary_recall'] for v in patient_means.values())/len(patients),
                five_same_support_actions_with_initialization_total_count_ratio=float(Fraction(n+5*k,5*n)))
            compare(summary,expected,method+'/summary')
            nonempty=[(s,m) for s,m in pairs if m['native_ROI_voxels']>0]
            exact.append(dict(method=method,patient_first_saving_fraction=str(sum(exact_savings)/len(patients)),
                nonempty_series=len(nonempty),nonempty_series_with_five_strict_saving=sum(s['full_forward_calls']+5*m['cost']['recomputed_batch_pairs']<5*s['full_forward_calls'] for s,m in nonempty),
                sourced_coverage_ge099_and_saving=expected['series_with_coverage_boundary_ge099_and_forward_saving']))
        assert result['cached_prediction_arrays_loaded'] == result['checked_method_supports'] == 64
        result.update(complete=True, exact_fraction_summaries=exact, resources_after=guard())
    except Exception as error:
        result['errors'].append(type(error).__name__+': '+str(error))
        result['traceback'] = traceback.format_exc()
    result.update(elapsed_seconds=time.perf_counter()-started, finished_utc=datetime.now(timezone.utc).isoformat())
    save()
    print(json.dumps({k:result.get(k) for k in ('complete','errors','checked_series','checked_method_supports','checked_plane_records','exact_fraction_summaries','elapsed_seconds')},ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__ == '__main__':
    raise SystemExit(main())
