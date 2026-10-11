"""Independent raw PixelData decoding and affine-coordinate label replay, all 28 cases."""
import itertools
import json
import sys
import traceback
import zipfile
from datetime import datetime, timezone
import nibabel as nib
import numpy as np
import pydicom
from mc_rc_true_native_reference_v2_2026_10_07 import ROOT, read, sha, array_sha, fixed_cases, read_reference, read_reference_label, require_reference_role, resource_guard
OUT = ROOT/'experiments/mc_rc_true_native_reference_attempt02_2026_10_07'

def manual_plane(d):
    ts = str(d.file_meta.TransferSyntaxUID)
    assert ts in ('1.2.840.10008.1.2', '1.2.840.10008.1.2.1', '1.2.840.10008.1.2.2'), 'Independent decoder supports classic uncompressed only'
    assert int(d.BitsAllocated) in (8,16,32) and int(d.PixelRepresentation) in (0,1)
    little = ts != '1.2.840.10008.1.2.2'
    dtype = np.dtype(('<' if little else '>') + ('i' if int(d.PixelRepresentation) else 'u') + str(int(d.BitsAllocated)//8))
    n = int(d.Rows)*int(d.Columns); nominal = n*dtype.itemsize
    assert len(d.PixelData) in (nominal, nominal+nominal%2)
    raw = np.frombuffer(d.PixelData,dtype=dtype,count=n).reshape(int(d.Rows),int(d.Columns))
    # Classic sources here use low bits; handle stored-bit masking/sign extension explicitly.
    bits = int(d.BitsStored); high = int(d.HighBit)
    assert 0 < bits <= int(d.BitsAllocated) and high == bits-1
    values = raw.astype(np.int64) & ((1 << bits)-1)
    if int(d.PixelRepresentation): values = np.where(values >= (1 << (bits-1)), values-(1 << bits), values)
    result = values.astype(np.float32)*float(d.get('RescaleSlope',1))+float(d.get('RescaleIntercept',0))
    assert np.isfinite(result).all()
    return result

def label_coordinate_replay(case, production):
    source = nib.load(ROOT/case['label_file'])
    source_from_rcz = np.linalg.solve(source.affine, np.asarray(case['affine_rcz_ras']))
    integer = np.rint(source_from_rcz).astype(int)
    assert np.allclose(source_from_rcz,integer,atol=.01)
    assert np.array_equal(np.linalg.inv(np.asarray(case['dicom_rcz_from_label_xyz'])),integer)
    max_error = 0.
    for p in itertools.product(*[(0,n-1) for n in production.shape]):
        v = np.asarray([*p,1]); max_error = max(max_error,float(np.linalg.norm((source.affine@integer@v-np.asarray(case['affine_rcz_ras'])@v)[:3])))
    assert max_error <= .05
    # Build source bool slabs independently. Replay every RCZ voxel using affine-derived integer coordinates.
    raw = np.empty(source.shape,bool)
    for z in range(0,source.shape[2],2):
        slab = np.asanyarray(source.dataobj[:,:,z:z+2]); assert np.isin(slab,[0,1]).all() and slab.nbytes <= 32_000_000
        raw[:,:,z:z+2] = slab
    rr,cc = np.indices(production.shape[:2]); checked = 0
    for z in range(production.shape[2]):
        base = np.stack((rr.ravel(),cc.ravel(),np.full(rr.size,z,dtype=int)))
        xyz = integer[:3,:3]@base+integer[:3,3,None]
        assert (xyz>=0).all() and (xyz<np.asarray(source.shape)[:,None]).all()
        plane = raw[tuple(xyz)].reshape(production.shape[:2])
        assert np.array_equal(plane, production[:,:,z]); checked += plane.size
    return dict(voxels_replayed=checked, max_label_corner_error_mm=max_error, affine_derived_integer_transform=integer.tolist())

def main():
    sys.stdout.reconfigure(encoding='utf-8'); path = OUT/'independent_all28_pixels_and_labels_2026_10_07.json'
    assert not path.exists()
    result_path = OUT/'attempt_01.json'; prod = read(result_path)
    assert prod['complete'] and not prod['errors'] and len(prod['series']) == 28
    r = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],
             script_sha256=sha(__file__), result_sha256=sha(result_path),
             confirmation_patients_opened=False, scientific_confirmation_patients=0,
             raw_pixels_checked=0, label_voxels_replayed=0, actual_native_planes_checked=0,
             raw_decoder_used_pydicom_pixel_array=False, source_bindings=prod['source_bindings'])
    def save(): path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        for b in prod['source_bindings']: assert sha(ROOT/b['path']) == b['sha256']
        assert sha(ROOT/'experiments/audit_mc_rc_true_native_reference_attempt02_2026_10_07.py') == prod['script_sha256']
        # Denial happens before filesystem access, including missing-path cases.
        for patient in ('030','029','019','028','031','026','027','015'):
            try: require_reference_role({'patient':'VS-MC-RC-'+patient})
            except ValueError: pass
            else: raise AssertionError('Confirmation role was accepted')
        r['all8_confirmation_roles_rejected_before_io'] = True
        by = {v['uid']:v for v in prod['series']}
        for role,case,observed in fixed_cases():
            resource_guard(); native = read_reference(case); row = by[case['uid']]
            assert array_sha(native.full_pixels_rcz) == row['native_array_sha256']
            with zipfile.ZipFile(ROOT/case['mr_zip_file']) as archive:
                for z,member in enumerate(case['ordered_zip_members']):
                    with archive.open(member) as stream: d = pydicom.dcmread(stream)
                    plane = manual_plane(d)
                    assert np.array_equal(plane,native.full_pixels_rcz[:,:,z]) and array_sha(plane) == row['plane_pixel_sha256'][z]
                    r['raw_pixels_checked'] += plane.size; r['actual_native_planes_checked'] += 1
            label = read_reference_label(case); replay = label_coordinate_replay(case,label)
            assert array_sha(label) == row['label_array_sha256']; r['label_voxels_replayed'] += replay['voxels_replayed']
            indices = list(range(0,case['native_shape'][2],4))
            assert array_sha(native.full_pixels_rcz[:,:,indices]) == observed['observed_array_sha256']
            r['series'].append(dict(role=role,patient=case['patient'],uid=case['uid'],manual_pixel_planes=case['native_shape'][2],**replay,complete=True))
            save(); print(json.dumps(dict(role=role,patient=case['patient'],planes=case['native_shape'][2],complete=True)),flush=True)
            del native,label
        r['complete'] = len(r['series']) == 28 and 'torch' not in sys.modules
        r['resources_after'] = resource_guard()
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e)); r['traceback'] = traceback.format_exc()
    r['finished_utc'] = datetime.now(timezone.utc).isoformat(); save()
    print(json.dumps({k:r.get(k) for k in ('complete','errors','raw_pixels_checked','label_voxels_replayed','actual_native_planes_checked')}),flush=True)
    return int(not r['complete'])

if __name__ == '__main__': raise SystemExit(main())
