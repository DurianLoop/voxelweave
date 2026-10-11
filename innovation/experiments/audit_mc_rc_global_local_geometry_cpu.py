"""Check inference geometry before looking at any validation model outputs."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[name] = '1'
import json
import sys
import traceback
from datetime import datetime, timezone
from vs_seg_task_cpu_support import resource_gate
from mc_rc_global_local_task_cpu_support import (
    ROOT, read, sha, array_sha, np, torch, physical_shape, context_plane,
    context_tiles, resize_image, starts, load_authenticated_observed, sparse_image)
from mc_rc_global_local_geometry_reference_cpu import (
    resize_reference, physical_context_reference, tile_locations, grid_context_reference)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    out = ROOT/'experiments/mc_rc_global_local_geometry_cpu'
    out.mkdir(exist_ok=False)
    path = out/'attempt_01.json'
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), resources=resource_gate(),
             complete=False, errors=[], synthetic=[], real_inputs=[], neural_forward_calls=0,
             validation_task_effects_read=False, native_hidden_MR_pixels_decoded=False,
             scientific_confirmation_patients=0, publication_claim_confirmed=False,
             script_sha256=sha(__file__), reference_sha256=sha(
                 ROOT/'experiments/mc_rc_global_local_geometry_reference_cpu.py'),
             support_sha256=sha(ROOT/'experiments/mc_rc_global_local_task_cpu_support.py'),
             float32_absolute_tolerance=0.0002, float32_relative_tolerance=0.00001,
             double_probability_absolute_tolerance=1e-12)
    def save():
        path.write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save()
    try:
        rng = np.random.default_rng(20261005)
        image = rng.normal(size=(9, 137, 173)).astype(np.float32)
        features = rng.normal(size=(1, 9, 256, 256)).astype(np.float32)
        for shape in ((137, 173), (360, 400), (128, 128)):
            axes, loc = tile_locations(shape)
            assert axes == [starts(n) for n in shape]
            coverage = np.zeros(shape, np.uint16)
            for rr, cc in loc:
                coverage[rr:rr+128, cc:cc+128] += 1
            assert coverage.min() >= 1
            chosen = [loc[0], loc[-1]]
            actual = context_tiles(torch.from_numpy(features), chosen, shape).numpy()
            expected = np.stack([grid_context_reference(features[0], at, shape) for at in chosen])
            assert np.allclose(actual, expected, rtol=1e-5, atol=2e-4)
            r['synthetic'].append(dict(shape=list(shape), tile_coverage_passed=True,
                                      coverage_min=int(coverage.min()), coverage_max=int(coverage.max()),
                                      context_grid_max_abs_difference=float(abs(actual-expected).max())))
        for spacing in (.4, .5, .7, 1.3):
            for z in (0, 4, 8):
                assert np.array_equal(context_plane(image, z, spacing),
                                      physical_context_reference(image, z, spacing))
        probabilities = rng.uniform(size=(137, 173)).astype(np.float64)
        mapped = torch.nn.functional.interpolate(torch.from_numpy(probabilities)[None, None],
                    size=(512, 384), mode='bilinear', align_corners=False)[0, 0].numpy()
        ref = resize_reference(probabilities, (512, 384))
        delta = float(abs(mapped-ref).max())
        assert delta <= 1e-12
        r['double_probability_mapping_max_abs_difference'] = delta
        r['synthetic_physical_z_checks'] = 12
        prepfile = ROOT/'experiments/mc_rc_validation_task_case_preparation/attempt_01.json'
        productionfile = ROOT/'experiments/mc_rc_validation_task_input_cpu/attempt_01.json'
        prooffile = productionfile.parent/'independent_all9_observed_inputs_and_label_axes_attempt_01.json'
        prep, production, proof = [read(p) for p in (prepfile, productionfile, prooffile)]
        assert all(x['complete'] and not x['errors'] for x in (prep, production, proof))
        assert proof['result_sha256'] == sha(productionfile)
        assert len(prep['cases']) == 9
        r['source_bindings'] = [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p))
                                for p in (prepfile, productionfile, prooffile)]
        by = {x['uid']: x for x in production['series']}
        for case in prep['cases']:
            resource_gate()
            obs = load_authenticated_observed(case, by[case['uid']])
            native, _ = sparse_image(obs, 'raw_pchip', by[case['uid']])
            shape, spacing = physical_shape(case)
            physical = resize_image(native, shape)
            errors = []
            for z in (0, native.shape[2]//2, native.shape[2]-1):
                expected = resize_reference(native[:, :, z], shape)
                maximum = float(abs(expected-physical[z]).max())
                assert np.allclose(expected, physical[z], rtol=1e-5, atol=2e-4)
                assert np.array_equal(context_plane(physical, z, spacing),
                                      physical_context_reference(physical, z, spacing))
                errors.append(dict(z=z, physical_resize_max_abs_difference=maximum))
            r['real_inputs'].append(dict(patient=case['patient'], uid=case['uid'],
                physical_shape=list(physical.shape), native_input_sha256=array_sha(native),
                physical_input_sha256=array_sha(physical), zspacing_mm=spacing,
                complete_planes_checked=errors, spatial_axes='RCZ -> ZRC, no anatomical reorientation'))
            save()
            print(json.dumps(dict(patient=case['patient'], uid=case['uid'], geometry_passed=True)), flush=True)
            del physical, native, obs
        r['gpu_initialized'] = torch.cuda.is_initialized()
        assert not r['gpu_initialized']
        r['complete'] = len(r['real_inputs']) == 9
    except Exception as error:
        r['errors'].append(type(error).__name__+': '+str(error))
        r['traceback'] = traceback.format_exc()
    r['finished_utc'] = datetime.now(timezone.utc).isoformat()
    save()
    print(json.dumps({k:r.get(k) for k in ('complete', 'errors', 'neural_forward_calls', 'gpu_initialized')}))
    return int(not r['complete'])


if __name__ == '__main__':
    raise SystemExit(main())
