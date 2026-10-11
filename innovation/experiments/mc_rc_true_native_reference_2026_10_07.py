"""Full native reference ONLY. No observed deployment input API or label argument."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
import nibabel as nib
import pydicom
from mc_rc_reference_resources_2026_10_07 import ROOT, resource_guard

DEVELOPERS = {'VS-MC-RC-' + x for x in ('001','002','004','005','006','007','009','010','011','012','013')}
VALIDATORS = {'VS-MC-RC-' + x for x in ('020','022','025','024')}

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for b in iter(lambda: stream.read(1048576), b''): h.update(b)
    return h.hexdigest()

def array_sha(a):
    a = np.ascontiguousarray(a)
    h = hashlib.sha256(json.dumps(dict(shape=list(a.shape), dtype=a.dtype.str), sort_keys=True).encode())
    h.update(memoryview(a).cast('B'))
    return h.hexdigest()

def require_reference_role(case):
    if case['patient'] not in DEVELOPERS | VALIDATORS:
        raise ValueError('Confirmation and unallocated native reference patients prohibited')

@dataclass(frozen=True)
class NativeReference:
    full_pixels_rcz: np.ndarray
    affine_rcz_ras: tuple
    decoded_sop_uids: tuple
    decoded_zip_members: tuple
    plane_pixel_sha256: tuple
    max_dicom_corner_affine_error_mm: float
    purpose: str = 'complete_MR_reference_not_sparse_deployment'

def read_reference(case):
    require_reference_role(case); resource_guard()
    assert sha(ROOT / case['header_file']) == case['header_sha256']
    assert sha(ROOT / case['mr_zip_file']) == case['mr_zip_sha256']
    header = read(ROOT / case['header_file'])
    by = {r['zip_member']: r for r in header['records']}
    members = case['ordered_zip_members']; shape = tuple(case['native_shape'])
    assert len(members) == shape[2] == len(by) and len(set(members)) == len(members)
    assert np.prod(shape)*4 <= 256_000_000
    full = np.empty(shape, dtype=np.float32)
    affine = np.asarray(case['affine_rcz_ras'], dtype=float)
    sops, hashes, maximum = [], [], 0.
    with zipfile.ZipFile(ROOT / case['mr_zip_file']) as archive:
        for z, member in enumerate(members):
            assert archive.getinfo(member).file_size <= 8_000_000
            with archive.open(member) as stream: d = pydicom.dcmread(stream)
            h = by[member]
            assert (str(d.PatientID), str(d.StudyInstanceUID), str(d.SeriesInstanceUID), str(d.SOPInstanceUID)) == (case['patient'], case['study_uid'], case['uid'], h['sop_uid'])
            assert str(d.FrameOfReferenceUID) == h['frame_uid'] and str(d.Modality) == 'MR'
            assert int(d.get('NumberOfFrames', 1)) == 1 and int(d.SamplesPerPixel) == 1
            assert str(d.PhotometricInterpretation) == 'MONOCHROME2'
            assert (int(d.Rows), int(d.Columns)) == shape[:2]
            iop = np.asarray(d.ImageOrientationPatient, float); ipp = np.asarray(d.ImagePositionPatient, float)
            spacing = np.asarray(d.PixelSpacing, float)
            assert np.array_equal(iop, h['iop']) and np.array_equal(ipp, h['ipp']) and np.array_equal(spacing, h['pixel_spacing'])
            assert np.isfinite(np.r_[iop, ipp, spacing]).all() and np.all(spacing > 0)
            for r, c in ((0,0), (shape[0]-1,0), (0,shape[1]-1), (shape[0]-1,shape[1]-1)):
                actual = (ipp + r*spacing[0]*iop[3:] + c*spacing[1]*iop[:3]) * np.array([-1.,-1.,1.])
                modeled = (affine @ [r,c,z,1])[:3]
                maximum = max(maximum, float(np.linalg.norm(actual-modeled)))
            assert maximum <= .05, 'Actual DICOM geometry differs from frozen RCZ affine'
            slope, offset = float(d.get('RescaleSlope',1)), float(d.get('RescaleIntercept',0))
            assert np.isfinite([slope, offset]).all()
            plane = d.pixel_array.astype(np.float32)*slope+offset
            assert plane.shape == shape[:2] and np.isfinite(plane).all()
            full[:,:,z] = plane
            sops.append(str(d.SOPInstanceUID)); hashes.append(array_sha(plane))
    full.flags.writeable = False
    return NativeReference(full, tuple(map(tuple, affine)), tuple(sops), tuple(members), tuple(hashes), maximum)

def read_reference_label(case):
    require_reference_role(case)
    assert sha(ROOT / case['label_file']) == case['label_sha256']
    image = nib.load(ROOT / case['label_file'])
    raw = np.asanyarray(image.dataobj); assert raw.nbytes <= 256_000_000
    assert np.isfinite(raw).all() and np.isin(raw, [0,1]).all()
    t = np.asarray(case['dicom_rcz_from_label_xyz'])
    assert np.array_equal(t, np.rint(t)); t = t.astype(int)
    axes = np.argmax(np.abs(t[:3,:3]), axis=1)
    assert len(set(axes)) == 3 and np.array_equal(np.sort(np.abs(t[:3,:3]).sum(axis=0)), [1,1,1])
    result = np.transpose(raw, axes)
    for axis, src in enumerate(axes):
        sign = t[axis, src]; assert sign in (-1,1)
        assert t[axis,3] == (result.shape[axis]-1 if sign == -1 else 0)
        if sign == -1: result = np.flip(result, axis)
    result = np.ascontiguousarray(result, dtype=bool)
    assert list(result.shape) == case['native_shape'] and int(result.sum()) == case['expected_label_foreground_voxels']
    return result

def fixed_cases():
    values = []
    for role, name, count, patients, observed_name in (
        ('development','mc_rc_current_development_input_preparation',19,DEVELOPERS,'mc_rc_development_training_input_cpu'),
        ('validation','mc_rc_validation_task_case_preparation',9,VALIDATORS,'mc_rc_validation_task_input_cpu')):
        prep_path = ROOT/'experiments'/name/'attempt_01.json'
        observed_path = ROOT/'experiments'/observed_name/'attempt_01.json'
        p, obs = read(prep_path), read(observed_path)
        assert p['complete'] and obs['complete'] and not p['errors'] and not obs['errors']
        assert len(p['cases']) == count and {c['patient'] for c in p['cases']} == patients
        by = {r['uid']:r for r in obs['series']}; assert len(by) == count
        for case in p['cases']: values.append((role, case, by[case['uid']]))
    assert len({case['uid'] for _,case,_ in values}) == 28
    return values
