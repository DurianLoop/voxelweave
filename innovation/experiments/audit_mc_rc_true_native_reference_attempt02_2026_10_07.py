"""Native-source production certificate, no MR copy is stored or neural model imported."""
import sys
import traceback
from datetime import datetime, timezone
import json
import numpy as np
from mc_rc_true_native_reference_v2_2026_10_07 import ROOT, resource_guard, sha, array_sha, read_reference, read_reference_label, fixed_cases
OUT = ROOT/'experiments/mc_rc_true_native_reference_attempt02_2026_10_07'

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    sys.stdout.reconfigure(encoding='utf-8'); OUT.mkdir(exist_ok=False)
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=False, errors=[], series=[],
             confirmation_patients_opened=False, scientific_confirmation_patients=0, publication_claim_confirmed=False,
             neural_updates=0, native_mr_copies_saved=0, full_native_read_is_reference_only=True,
             script_sha256=sha(__file__), source_bindings=[])
    source_paths = ['MC_RC_NATIVE_REFERENCE_PROTOCOL_2026-10-07.md','MC_RC_NATIVE_REFERENCE_ATTEMPT02_ADDENDUM_2026-10-07.md','experiments/mc_rc_true_native_reference_v2_2026_10_07.py','experiments/mc_rc_true_native_reference_2026_10_07/attempt_01.json',
                    'experiments/mc_rc_true_native_reference_2026_10_07.py','experiments/mc_rc_reference_resources_2026_10_07.py',
                    'experiments/mc_rc_current_development_input_preparation/attempt_01.json',
                    'experiments/mc_rc_validation_task_case_preparation/attempt_01.json',
                    'experiments/mc_rc_development_training_input_cpu/attempt_01.json',
                    'experiments/mc_rc_validation_task_input_cpu/attempt_01.json']
    r['source_bindings'] = [dict(path=p, sha256=sha(ROOT/p)) for p in source_paths]
    path = OUT/'attempt_01.json'; write(path,r)
    try:
        r['resources_before'] = resource_guard()
        for role, case, observed in fixed_cases():
            resource_guard(); native = read_reference(case)
            indices = list(range(0, case['native_shape'][2], 4))
            acquired = np.ascontiguousarray(native.full_pixels_rcz[:,:,indices])
            assert array_sha(acquired) == observed['observed_array_sha256']
            assert indices == observed['observed_indices']
            assert list(native.decoded_sop_uids[::4]) == observed['decoded_sop_uids']
            assert list(native.decoded_zip_members[::4]) == observed['decoded_zip_members']
            package_path = ROOT/observed['observed_package']
            assert sha(package_path) == observed['observed_package_sha256']
            with np.load(package_path, allow_pickle=False) as q:
                assert np.array_equal(acquired, q['observed_rcz'])
                assert np.array_equal(native.affine_rcz_ras, q['affine_rcz_ras'])
                assert np.array_equal(case['native_shape'], q['native_shape'])
            label = read_reference_label(case)
            assert array_sha(label) == observed['label_array_sha256']
            item = dict(role=role, patient=case['patient'], uid=case['uid'], native_shape=case['native_shape'],
                        native_array_sha256=array_sha(native.full_pixels_rcz), native_array_bytes=native.full_pixels_rcz.nbytes,
                        plane_pixel_sha256=list(native.plane_pixel_sha256),
                        all_native_sop_uids=list(native.decoded_sop_uids),
                        ordered_zip_members=list(native.decoded_zip_members),
                        affine_rcz_ras=case['affine_rcz_ras'],
                        max_dicom_corner_affine_error_mm=native.max_dicom_corner_affine_error_mm,
                        observed_array_sha256=array_sha(acquired), observed_package_sha256=sha(package_path),
                        observed_extract_equal=True, label_array_sha256=array_sha(label),
                        label_foreground=int(label.sum()), complete=True)
            r['series'].append(item); write(path,r)
            print(json.dumps(dict(role=role,patient=case['patient'],uid=case['uid'],native_planes=case['native_shape'][2],
                                  max_affine_error_mm=item['max_dicom_corner_affine_error_mm'],observed_extract_equal=True)),flush=True)
            del native, acquired, label
        r['complete'] = len(r['series']) == 28 and 'torch' not in sys.modules
        r['torch_imported'] = 'torch' in sys.modules
        r['resources_after'] = resource_guard()
        r['saved_bytes'] = sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())
        assert r['saved_bytes'] < 5_000_000
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e)); r['traceback'] = traceback.format_exc()
    r['finished_utc'] = datetime.now(timezone.utc).isoformat(); write(path,r)
    print(json.dumps({k:r.get(k) for k in ('complete','errors','native_mr_copies_saved','saved_bytes')},ensure_ascii=False),flush=True)
    return int(not r['complete'])

if __name__ == '__main__': raise SystemExit(main())
