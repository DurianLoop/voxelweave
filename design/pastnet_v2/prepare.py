"""Build immutable dataset manifests and recover geometry without rewriting old data."""
from __future__ import annotations

import argparse
from pathlib import Path
import json

import nibabel as nib
import numpy as np
import pydicom

from .common import ROOT, PACKAGE, fastmri_records, read_csv, write_json


def recover_fastmri(rec):
    from processing.fastmri_brain_t2_prepare import infer_series_label
    manifests = read_csv(ROOT / 'dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_nifti_manifest.csv')
    row = next(r for r in manifests if r['case_id'] == rec['case_id'])
    directory = ROOT / 'dataset/fastMRI_brain_DICOM' / row['source_case_id']
    files = [p for p in sorted(directory.glob('*.dcm')) if infer_series_label(p) == row['series_label']]
    headers = [pydicom.dcmread(p, force=True, stop_before_pixels=True) for p in files]
    order = sorted(range(len(files)), key=lambda i: int(getattr(headers[i], 'InstanceNumber', i)))
    headers = [headers[i] for i in order]
    files = [files[i] for i in order]
    image = nib.load(rec['path'])
    if len(files) != image.shape[2]:
        raise ValueError('DICOM count differs from old NIfTI')
    # Verify the metadata order against the stored images, not just InstanceNumber.
    for i in sorted({0, len(files)//2, len(files)-1}):
        ds = pydicom.dcmread(files[i], force=True)
        if not np.allclose(ds.pixel_array, np.asarray(image.dataobj[:, :, i]), rtol=0, atol=1e-4):
            raise ValueError('DICOM/NIfTI pixel-order mismatch')
    first = headers[0]
    ps = np.asarray(first.PixelSpacing, dtype=float)
    orient = np.asarray(first.ImageOrientationPatient, dtype=float)
    positions = np.array([h.ImagePositionPatient for h in headers], dtype=float)
    if any(not np.allclose(np.array(h.ImageOrientationPatient, float), orient, atol=1e-4) for h in headers):
        raise ValueError('Nonparallel slices')
    normal = np.cross(orient[:3], orient[3:])
    z = positions @ normal
    dz = np.diff(z)
    if np.any(dz == 0) or not (np.all(dz > 0) or np.all(dz < 0)):
        raise ValueError('Nonmonotone physical positions')
    direction_z = normal * np.sign(np.median(dz))
    # Arrays are [DICOM row index, column index, slice]. RAS conversion is explicit.
    ras = np.diag([-1., -1., 1.])
    axes = ras @ np.stack([orient[3:], orient[:3], direction_z], axis=1)
    return dict(spacing=[float(ps[0]), float(ps[1]), float(np.median(np.abs(dz)))],
                axes=axes.tolist(), z_mm=(np.abs(z-z[0])).tolist(),
                spacing_known=1, orientation_known=1, source='DICOM_positions_pixel_order_verified',
                nonuniformity=float(np.std(dz)/abs(np.mean(dz))))


def geometry(rec):
    image = nib.load(rec['path'])
    if rec['dataset'] == 'fastmri':
        try:
            return recover_fastmri(rec)
        except (ValueError, AttributeError, KeyError, StopIteration, RuntimeError) as exc:
            # Synthetic affine is not a fallback measurement. Keep masks zero.
            return dict(spacing=[1., 1., 1.], axes=np.zeros((3, 3)).tolist(),
                        z_mm=list(map(float, range(image.shape[2]))), spacing_known=0,
                        orientation_known=0, source='unknown', reason=str(exc))
    affine = image.affine[:3, :3]
    spacing = np.linalg.norm(affine, axis=0)
    known = bool(np.all(spacing > 0) and not np.allclose(image.affine, np.eye(4)))
    axes = affine / spacing
    if rec['dataset'] == 'ningxia':
        # Original converter assigns direction columns in column/row order,
        # whereas stored pixel_array is row/column. Swap the in-plane vectors.
        axes = axes[:, [1, 0, 2]]
        spacing = spacing[[1, 0, 2]]
    return dict(spacing=spacing.tolist(), axes=axes.tolist() if known else np.zeros((3,3)).tolist(),
                z_mm=(np.arange(image.shape[2])*spacing[2]).tolist(), spacing_known=int(known),
                orientation_known=int(known), source='native_nifti' if known else 'unknown_identity')


def records_for(dataset, fold=0):
    if dataset == 'fastmri':
        return fastmri_records()
    if dataset == 'ixi':
        root = ROOT / 'dataset/IXI'
        rows = read_csv(root / 'metadata/ixi_cases.csv')
        paths = {r['case_id']: r['T2_path'] for r in rows if r['has_T2'] == 'True'}
        splits = {s: (root / f'splits/seed3407/{s}_cases.txt').read_text().split() for s in ('train','val','test')}
        return [dict(case_id=p, patient_id=p, path=paths[p], split=s, dataset=dataset)
                for s, ids in splits.items() for p in ids if p in paths]
    root = ROOT / f'dataset/NingXiaData/processed_saint_cv/fold_{fold:02d}'
    rows = read_csv(root / 'metadata/fastmri_brain_nifti_cases.csv')
    splits = {s: set((root / f'splits/nifti_seed3407/{s}_cases.txt').read_text().split()) for s in ('train','val','test')}
    if any(splits[a] & splits[b] for a,b in (('train','val'),('train','test'),('val','test'))):
        raise ValueError('NingXia patient leakage')
    return [dict(case_id=Path(r['nifti_path']).name.replace('.nii.gz',''), patient_id=r['case_id'],
                 path=str(ROOT / r['nifti_path']), split=s, dataset=dataset)
            for r in rows for s, ids in splits.items() if r['case_id'] in ids]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dataset', choices=['fastmri','ixi','ningxia'], default='fastmri')
    p.add_argument('--fold', type=int, choices=range(8), default=0)
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    out = a.out or PACKAGE / f'manifests/{a.dataset}' / f'fold_{a.fold:02d}.json'
    if out.exists():
        raise FileExistsError(out)
    records = records_for(a.dataset, a.fold)
    patients = {s: {r['patient_id'] for r in records if r['split']==s} for s in ('train','val','test')}
    if any(patients[x]&patients[y] for x,y in (('train','val'),('train','test'),('val','test'))):
        raise ValueError('Patient leakage')
    for i, r in enumerate(records):
        # Test images/headers are opened only by the locked external evaluator.
        if r['split'] in ('train','val'):
            r['geometry'] = geometry(r)
            r['shape'] = list(nib.load(r['path']).shape)
        print(f'prepare {a.dataset} {i+1}/{len(records)} {r["split"]}', flush=True)
    write_json(out, dict(dataset=a.dataset, fold=a.fold, records=records,
                        normalization='observed_sparse_minmax', stride=4,
                        quarantine_reason='G086 trained on another series of patient 101014598432',
                        test_pixels_opened=False))


if __name__ == '__main__':
    main()
