from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
G086 = ROOT / 'design/fastmri_brain_pastnet_2p5d/runs/full_pastnet_g086_dual_restart60/checkpoints/pastnet_epoch_best.pth'


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError('Refusing empty evidence CSV')
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fastmri_records():
    root = ROOT / 'dataset/fastMRI_brain_T2/processed'
    rows = read_csv(root / 'metadata/fastmri_brain_nifti_cases.csv')
    split_map = {}
    patient_splits = {}
    for split in ('train', 'val', 'test'):
        for case in (root / f'splits/nifti_seed3407/{split}_cases.txt').read_text().split():
            if case in split_map:
                raise ValueError(f'Duplicate split entry: {case}')
            split_map[case] = split
            patient = case.split('_')[0]
            patient_splits.setdefault(patient, set()).add(split)
    return [dict(case_id=r['case_id'], patient_id=r['case_id'].split('_')[0],
                 path=r['nifti_path'], split=('quarantine' if split_map[r['case_id']] == 'val'
                     and len(patient_splits[r['case_id'].split('_')[0]]) > 1 else split_map[r['case_id']]),
                 dataset='fastmri') for r in rows]
