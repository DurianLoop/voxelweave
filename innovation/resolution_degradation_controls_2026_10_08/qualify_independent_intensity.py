"""Check an independent intensity reference on full synthetic fields and primitive metadata."""
import os
for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[key] = '1'
import sys, time, itertools, traceback
from pathlib import Path
import numpy as np
import torch
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / 'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read, entry, bind, dump, resource_guard
sys.path.insert(0, str(ROOT / 'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import array_sha
sys.path.insert(0, str(ROOT / 'adaptation_paired_pilot_2026_10_08'))
import augmentation as production
from independent_intensity import apply_reference


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    torch.set_num_threads(1)
    assert torch.get_num_interop_threads() == 1
    resource_guard()
    started = time.perf_counter()
    terminal = read(HERE / 'ACTUAL_INTENSITY_COMPOSITION_TERMINAL_TOOL.json')
    assert terminal['exit_code'] == 0 and 'session_id' not in terminal
    assert terminal['observed_unified_exec_session'] == 31866
    parent = read(HERE / 'intensity_composition_attempt01/receipt.json')
    assert parent['complete'] and not parent['errors']
    for binding in parent['source_bindings']:
        bind(binding)
    out = HERE / 'independent_intensity_attempt01'
    out.mkdir(exist_ok=False)
    sources = [Path(__file__), HERE / 'independent_intensity.py', Path(production.__file__),
               HERE / 'INDEPENDENT_INTENSITY_PROTOCOL.md',
               HERE / 'ACTUAL_INTENSITY_COMPOSITION_TERMINAL_TOOL.json',
               HERE / 'intensity_composition_attempt01/receipt.json']
    dump(out / 'frozen_config.json', dict(image_gate=3e-6, wall_seconds=180,
         expected_full_fields=40, primitive_metadata_records=5984,
         source_bindings=[entry(p) for p in sources]))
    result = dict(complete=False, errors=[], fields=[], MRI_arrays_loaded=0,
                  GT_arrays_loaded=0, model_arrays_loaded=0, training_updates=0,
                  confirmation_patients_opened=False, publication_claim_confirmed=False,
                  goal_status='active', shared_numpy_seeded_normal_convention=True)
    try:
        fixtures = [np.full((7,11,13), 2.5, np.float32), np.array([[[3.]]], np.float32)]
        rng = np.random.default_rng(2026100828)
        fixtures.append(rng.normal(size=(9,17,23)).astype(np.float32))
        fixtures.append(rng.normal(size=(64,128,128)).astype(np.float32))
        padded = np.zeros((64,128,128), np.float32)
        padded[12:52] = rng.normal(size=(40,128,128)).astype(np.float32)
        padded[32,50,50] = 12.
        padded[32,50,51] = -5.
        fixtures.append(padded)
        maximum = 0.
        for fixture, image in enumerate(fixtures):
            before = array_sha(image)
            for gamma, bias, noise in itertools.product([False,True], repeat=3):
                resource_guard()
                assert time.perf_counter()-started < 180 and not torch.cuda.is_initialized()
                primitive = dict(gamma_enabled=gamma, gamma=.7 if fixture%2 else 1.5,
                                 bias_enabled=bias, bias_coefficients=[-.3,.21,.3],
                                 noise_enabled=noise, noise_std=.08, noise_seed=1701+fixture)
                actual = production.apply(image[None,None], [primitive])[0,0]
                reference = apply_reference(image, primitive)
                error = float(np.max(np.abs(actual-reference)))
                result['fields'].append(dict(fixture=fixture, primitive=primitive,
                     full_target_voxels=int(image.size), max_error=error,
                     source_unchanged=array_sha(image)==before))
                maximum = max(maximum,error)
                assert error <= 3e-6, f'Independent intensity error {error} exceeds 3e-6'
                assert array_sha(image)==before
        records = 0
        for step in range(1,2993):
            for primitive in production.primitives(step):
                assert .7 <= primitive['gamma'] <= 1.5
                assert len(primitive['bias_coefficients'])==3
                assert all(-.3<=x<=.3 for x in primitive['bias_coefficients'])
                assert 0<=primitive['noise_std']<=.08 and 0<=primitive['noise_seed']<2**32
                records += 1
        assert len(result['fields'])==40 and records==5984
        result.update(complete=True, all40_full_synthetic_fields_verified=True,
                      all5984_primitive_metadata_records_verified=True, max_image_error=maximum)
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc))
        result['traceback']=traceback.format_exc()
        traceback.print_exc()
    result.update(elapsed_seconds=time.perf_counter()-started,
                  CUDA_initialized=torch.cuda.is_initialized(),
                  source_bindings=[entry(p) for p in sources])
    dump(out/'receipt.json',result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print({k:v for k,v in result.items() if k not in ('fields','source_bindings','traceback')},flush=True)
    return int(not result['complete'])


if __name__=='__main__':
    raise SystemExit(main())
