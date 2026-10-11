"""Independently re-read all seven raw sources and labels; no MR pixels."""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import nibabel as nib
import numpy as np
import pydicom
from vs_seg_task_cpu_support import resource_gate
ROOT = Path(__file__).resolve().parents[1]
HEADERS = ROOT / 'literature/source_cache/mc_rc_007_010_native_headers_2026-10-02'
OUT = ROOT / 'experiments/mc_rc_007_010_native_label_gate'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def sha(p):
    digest = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()

def corners(shape):
    return np.array([[*v, 1] for v in itertools.product(*[(0, n - 1) for n in shape])], dtype=float).T

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resources = resource_gate()
    ledger, labels = read(HEADERS / 'attempt_01.json'), read(OUT / 'attempt_01.json')
    selection_path = ROOT / 'experiments/mc_rc_visible_joint_development_diagnostic/next_developer_source_preparation.json'
    selection = read(selection_path)
    prior = read(ROOT / 'literature/source_cache/mc_rc_three_patient_headers_2026-10-02/attempt_01.json')
    csv_path = ROOT / 'literature/source_cache/mc_rc_three_patient_headers_2026-10-02/official_label_metadata_00_attempt_01.csv'
    artifact_path = ROOT / 'experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json'
    artifact = read(artifact_path)
    with csv_path.open(encoding='utf-8-sig', newline='') as stream:
        cells = list(csv.reader(stream))
    mappings = [dict(zip(cells[0], row)) for row in cells[1:]]
    metadata = {r['series_instance_uid']: r for r in mappings}
    official_zip = ROOT / prior['labels']['transfer']['file']
    errors, records, objects = [], [], 0
    def check(ok, reason):
        if not ok:
            errors.append(reason)
    check(cells == artifact['values'] and sha(csv_path) == artifact['source_sha256'], 'CSV/artifact provenance differs')
    check(len(metadata) == len(mappings), 'Duplicate official metadata UID')
    check(sha(official_zip) == prior['labels']['transfer']['sha256'] == labels['official_label_zip_sha256'], 'Official ZIP hash differs')
    check(sha(selection_path) == labels['selection_sha256'] == ledger['selection_sha256'], 'Selection hash differs')
    check(sha(HEADERS / 'attempt_01.json') == labels['header_result_sha256'], 'Label/header lineage differs')
    check(sha(ROOT / 'experiments/audit_mc_rc_007_010_label_grid.py') == labels['script_sha256'], 'Label producer hash differs')
    check(sha(ROOT / 'literature/download_mc_rc_007_010_native_headers_2026_10_02.py') == ledger['script_sha256'], 'Header producer hash differs')
    expected = {r['source']['SeriesInstanceUID']: r['source'] for r in selection['next_batch_series']}
    check(len(expected) == 7 and ledger['complete'] and labels['complete'], 'Fixed-seven completeness differs')
    check({r['source']['SeriesInstanceUID']: r['source'] for r in ledger['series']} == expected, 'Frozen API roster differs')
    by_uid = {r['series_uid']: r for r in labels['series']}
    check(set(by_uid) == set(expected), 'Label roster differs')
    destination = OUT / 'independent_raw_geometry_grid_verification.json'
    if destination.exists():
        raise ValueError('Preserve completed verification; no blind overwrite')
    with zipfile.ZipFile(official_zip) as official:
        for row in ledger['series']:
            resource_gate()
            src, summary = row['source'], row['summary']
            uid, label = src['SeriesInstanceUID'], by_uid[src['SeriesInstanceUID']]
            raw_zip, header_path = ROOT / row['transfer']['file'], HEADERS / row['header_file']
            check(sha(raw_zip) == row['transfer']['sha256'] and sha(header_path) == row['header_sha256'], 'Raw ZIP/header hash differs ' + uid)
            saved = {r['sop_uid']: r for r in read(header_path)['records']}
            datasets = []
            with zipfile.ZipFile(raw_zip) as archive:
                for member in archive.infolist():
                    if member.is_dir() or not member.filename.lower().endswith('.dcm'):
                        continue
                    with archive.open(member) as stream:
                        ds = pydicom.dcmread(stream, stop_before_pixels=True)
                    datasets.append(ds)
                    objects += 1
                    check(str(ds.PatientID) == src['PatientID'] and str(ds.StudyInstanceUID) == src['StudyInstanceUID'] and str(ds.SeriesInstanceUID) == uid and str(ds.Modality) == 'MR', 'Raw identity differs ' + uid)
                    s = saved.get(str(ds.SOPInstanceUID))
                    check(s is not None, 'Raw SOP absent from saved header ' + uid)
                    if s is None:
                        continue
                    for tag, field in [('PixelSpacing', 'pixel_spacing'), ('ImageOrientationPatient', 'iop'), ('ImagePositionPatient', 'ipp')]:
                        check(np.array_equal(np.asarray(ds.get(tag), dtype=float), s[field]), 'Raw vector differs ' + uid + ' ' + tag)
                    for tag, field in [('Rows', 'rows'), ('Columns', 'columns'), ('SliceThickness', 'slice_thickness')]:
                        check(float(ds.get(tag)) == s[field], 'Raw scalar differs ' + uid + ' ' + tag)
                    check(str(ds.get('MRAcquisitionType', '')) == s['mr_acquisition_type'] and list(ds.get('ImageType', [])) == s['image_type'] and str(ds.FrameOfReferenceUID) == s['frame_uid'], 'Raw acquisition/frame differs ' + uid)
            n = len(datasets)
            check(n == src['ImageCount'] == len(saved) and len({str(d.SOPInstanceUID) for d in datasets}) == n, 'Object count/uniqueness differs ' + uid)
            orient = np.asarray(datasets[0].ImageOrientationPatient, dtype=float)
            normal = np.cross(orient[:3], orient[3:])
            positions = np.array([d.ImagePositionPatient for d in datasets], dtype=float)
            positions = positions[np.argsort(positions @ normal)]
            origin, step = np.linalg.lstsq(np.column_stack((np.ones(n), np.arange(n))), positions, rcond=None)[0]
            residual = float(np.linalg.norm(positions - origin - np.arange(n)[:, None] * step, axis=1).max())
            affine = np.eye(4)
            affine[:3, 0] = orient[3:] * float(datasets[0].PixelSpacing[0])
            affine[:3, 1] = orient[:3] * float(datasets[0].PixelSpacing[1])
            affine[:3, 2], affine[:3, 3] = step, origin
            ras = np.diag([-1., -1., 1., 1.]) @ affine
            check(np.allclose(ras, summary['affine_rcz_ras'], rtol=0, atol=1e-9) and abs(residual - summary['max_affine_position_residual_mm']) <= 1e-9, 'Full-matrix least-squares geometry differs ' + uid)
            gaps = np.diff(positions @ normal)
            consistent = len({(int(d.Rows), int(d.Columns), str(d.FrameOfReferenceUID)) for d in datasets}) == 1
            consistent = consistent and all(np.max(abs(np.asarray(d.ImageOrientationPatient, dtype=float) - orient)) <= 1e-6 and np.max(abs(np.asarray(d.PixelSpacing, dtype=float) - np.asarray(datasets[0].PixelSpacing, dtype=float))) <= 1e-6 for d in datasets)
            ortho = max(abs(np.linalg.norm(orient[:3]) - 1), abs(np.linalg.norm(orient[3:]) - 1), abs(orient[:3] @ orient[3:])) <= 1e-4
            geometry = consistent and ortho and all(int(d.get('NumberOfFrames', 1)) == 1 for d in datasets) and residual <= .02 and gaps.min() > 1e-4 and abs(gaps - np.median(gaps)).max() <= .02
            original = all('ORIGINAL' in [str(v).upper() for v in d.get('ImageType', [])] and 'DERIVED' not in [str(v).upper() for v in d.get('ImageType', [])] for d in datasets)
            derivative = any(any(token in (' '.join(str(v) for v in d.get('ImageType', [])) + ' ' + str(d.get('SeriesDescription', '')) + ' ' + str(d.get('DerivationDescription', ''))).upper() for token in ('MPR', 'REFORMAT', 'LOCALIZER')) for d in datasets)
            spacing = [float(datasets[0].PixelSpacing[0]), float(datasets[0].PixelSpacing[1]), float(np.linalg.norm(step))]
            thin = max(spacing) <= 1.5 and max(float(d.SliceThickness) for d in datasets) <= 1.5
            acquired3d = all(str(d.get('MRAcquisitionType', '')) == '3D' for d in datasets)
            qualified = bool(geometry and original and not derivative and thin and acquired3d)
            check(qualified == summary['header_qualified_candidate'], 'Independent header gate differs ' + uid)
            m = metadata[uid]
            check(m['patient_id'] == src['PatientID'] and m['study_instance_uid'] == src['StudyInstanceUID'] and int(m['num_files']) == n and label['label_zip_member'].endswith('/' + m['SegmentationPath']), 'Official UID/path linkage differs ' + uid)
            payload = official.read(label['label_zip_member'])
            label_path = ROOT / label['label_file']
            check(hashlib.sha256(payload).hexdigest() == label['label_sha256'] == sha(label_path) and len(payload) == label['label_member_bytes'], 'Original label member/extraction differs ' + uid)
            img = nib.load(label_path)
            foreground, values, finite = 0, set(), True
            for start in range(0, img.shape[2], 4):
                slab = np.asarray(img.dataobj[:, :, start:start + 4])
                check(slab.nbytes <= 32000000, 'Four-plane slab budget exceeded ' + uid)
                finite = finite and bool(np.isfinite(slab).all())
                foreground += int((slab != 0).sum())
                values.update(np.unique(slab).tolist())
            check(foreground == label['label_foreground_voxels'] and sorted(values) == label['label_values'] and list(img.shape) == label['label_shape'] and finite, 'All-label contents differ ' + uid)
            integer = np.rint(np.linalg.solve(ras, img.affine)).astype(int)
            matrix = integer[:3, :3]
            signed = np.all(np.sum(abs(matrix), axis=0) == 1) and np.all(np.sum(abs(matrix), axis=1) == 1) and np.array_equal(integer[-1], [0, 0, 0, 1])
            points = corners(img.shape)
            mapped = integer @ points
            shape = np.array([int(datasets[0].Rows), int(datasets[0].Columns), n])
            extent = np.array_equal(mapped[:3].min(axis=1), [0, 0, 0]) and np.array_equal(mapped[:3].max(axis=1), shape - 1)
            corner_error = float(np.linalg.norm(((ras @ integer - img.affine) @ points)[:3], axis=0).max())
            grid = bool(signed and extent and corner_error <= .05)
            qc, sc = int(img.header['qform_code']), int(img.header['sform_code'])
            forms_finite = np.isfinite(img.affine).all() and (qc <= 0 or np.isfinite(img.get_qform()).all()) and (sc <= 0 or np.isfinite(img.get_sform()).all())
            form_error = float(np.linalg.norm(((img.get_qform() - img.get_sform()) @ points)[:3], axis=0).max()) if qc > 0 and sc > 0 else None
            passed = bool(qualified and grid and finite and forms_finite and values <= {0, 1} and (qc > 0 or sc > 0) and (form_error is None or form_error <= .05))
            check(grid == label['grid']['same_native_grid'] and abs(corner_error - label['grid']['max_corner_world_error_mm']) <= 1e-8 and passed == label['header_and_label_grid_preflight_passed'], 'Inverse-grid/source gate differs ' + uid)
            records.append(dict(patient=src['PatientID'], uid=uid, description=src['SeriesDescription'], raw_objects=n, header_qualified=qualified, derivative_evidence=derivative, native_spacing_rcz_mm=spacing, nominal_thicknesses_mm=sorted({float(d.SliceThickness) for d in datasets}), least_squares_max_residual_mm=residual, grid_max_corner_error_mm=corner_error, inverse_integer_grid_matrix=integer.tolist(), label_foreground_voxels=foreground, source_preflight_passed=passed))
    counts = dict(raw_DICOM_objects_checked=objects, series=len(records), label_arrays_checked=len(records), header_qualified_series=sum(r['header_qualified'] for r in records), source_preflight_series=sum(r['source_preflight_passed'] for r in records), source_preflight_patients=len({r['patient'] for r in records if r['source_preflight_passed']}))
    check(objects == 527 and len(records) == 7 and counts['source_preflight_series'] == labels['source_preflight_series_passed'] == 6 and counts['source_preflight_patients'] == 3, 'Fixed-seven final scope differs')
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), verification_script_sha256=sha(__file__), header_result_sha256=sha(HEADERS / 'attempt_01.json'), label_result_sha256=sha(OUT / 'attempt_01.json'), selection_sha256=sha(selection_path), official_zip_sha256=sha(official_zip), source_csv_sha256=sha(csv_path), artifact_read_sha256=sha(artifact_path), resources=resources, counts=counts, series=records, errors=errors, MR_pixel_arrays_decoded=False, reconstruction_or_task_models_executed=0, scientific_independent_validation_patients=0, publication_claim_confirmed=False)
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(counts=counts, errors=errors), ensure_ascii=False, indent=2))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
