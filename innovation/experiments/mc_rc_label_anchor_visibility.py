"""Developer-only geometry diagnostic of true labels under fixed x4 anchors."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import nibabel as nib
import numpy as np
from scipy import ndimage
from vs_seg_task_cpu_support import resource_gate
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/mc_rc_label_anchor_visibility'
PLAN = ROOT / 'MC_RC_LABEL_ANCHOR_VISIBILITY_PLAN_2026-10-03.md'
SOURCES = [
 ('experiments/mc_rc_native_t2_label_gate/label_grid_attempt_01.json', 'experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json'),
 ('experiments/mc_rc_004_006_native_label_gate/resource_followup_attempt_01.json', 'experiments/mc_rc_004_006_native_label_gate/independent_raw_geometry_grid_verification.json'),
 ('experiments/mc_rc_007_010_native_label_gate/attempt_01.json', 'experiments/mc_rc_007_010_native_label_gate/independent_raw_geometry_grid_verification.json'),
]
def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            digest.update(chunk)
    return digest.hexdigest()
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resources = resource_gate()
    accepted, excluded, inputs = [], [], [PLAN, Path(__file__)]
    for source, proof in SOURCES:
        src, verification = read(ROOT / source), read(ROOT / proof)
        if verification['errors']:
            raise ValueError('Source independent verification has errors ' + proof)
        inputs += [ROOT / source, ROOT / proof]
        for row in src['series']:
            item = dict(row, source_result=source, independent_source_proof=proof)
            (accepted if row['header_and_label_grid_preflight_passed'] else excluded).append(item)
    accepted.sort(key=lambda r: (r['patient'], r['series_uid']))
    if len(accepted) != 15 or len(excluded) != 9 or len({r['patient'] for r in accepted}) != 8 or len({r['series_uid'] for r in accepted}) != 15:
        raise ValueError('Fixed 15-series / 8-developer roster differs')
    for row in accepted:
        p = ROOT / row['label_file']
        if sha(p) != row['label_sha256']:
            raise ValueError('Label hash differs ' + str(p))
        inputs.append(p)
    OUT.mkdir(exist_ok=False)
    contract = dict(created_utc=datetime.now(timezone.utc).isoformat(), selected_uids=[r['series_uid'] for r in accepted], patients=sorted({r['patient'] for r in accepted}), source_series=24, accepted_series=15, excluded_series=9, phase_primary=0, phases=[0,1,2,3], factor=4, connectivity_primary=26, connectivity_sensitivity=6, clinical_lesion_identity_assumed=False, MR_pixels_decoded=False, files=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in inputs])
    write(OUT / 'run_contract.json', contract)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), run_contract_sha256=sha(OUT / 'run_contract.json'), resources=resources, excluded_sources=[dict(patient=r['patient'], uid=r['series_uid'], source_result=r['source_result']) for r in excluded], series=[], errors=[], complete=False, gpu_used=False, MR_pixels_decoded=False, neural_networks_executed=0, scientific_independent_validation_patients=0, publication_claim_confirmed=False)
    for row in accepted:
        resource_gate()
        uid, patient = row['series_uid'], row['patient']
        img = nib.load(ROOT / row['label_file'])
        binary = np.empty(img.shape, dtype=bool)
        for start in range(0, img.shape[2], 4):
            slab = np.asarray(img.dataobj[:, :, start:start+4])
            if slab.nbytes > 32000000 or not np.isfinite(slab).all() or not np.isin(slab, [0,1]).all():
                raise ValueError('Label resource/value gate violated ' + uid)
            binary[:, :, start:start+4] = slab != 0
        matrix = np.array(row['grid']['dicom_rcz_from_label_xyz'], dtype=int)
        axes = [int(np.flatnonzero(matrix[i,:3])[0]) for i in range(3)]
        native = binary.transpose(axes)
        for axis in range(3):
            if matrix[axis, axes[axis]] < 0:
                native = np.flip(native, axis=axis)
        native = np.ascontiguousarray(native)
        del binary
        foreground = int(native.sum())
        if foreground != row['label_foreground_voxels']:
            raise ValueError('Native mapping lost foreground ' + uid)
        plane_counts = native.sum(axis=(0,1)).astype(np.int64)
        voxel_mm3 = float(abs(np.linalg.det(img.affine[:3,:3])))
        count6, n6 = ndimage.label(native, structure=ndimage.generate_binary_structure(3,1))
        count26, n26 = ndimage.label(native, structure=np.ones((3,3,3), dtype=bool))
        path = OUT / (patient + '_' + uid + '_native_components.npz')
        np.savez_compressed(path, connectivity6=count6, connectivity26=count26, plane_foreground=plane_counts, dicom_rcz_from_label_xyz=matrix)
        record = dict(patient=patient, uid=uid, description=row['description'], label_file=row['label_file'], label_sha256=row['label_sha256'], source_result=row['source_result'], component_file=path.relative_to(ROOT).as_posix(), component_sha256=sha(path), native_shape=list(native.shape), label_foreground_voxels=foreground, voxel_mm3=voxel_mm3, plane_foreground_voxels=plane_counts.tolist(), phases=[], topology={})
        z = np.arange(native.shape[2])
        for phase in range(4):
            anchors = np.flatnonzero(z % 4 == phase)
            support = (z >= anchors[0]) & (z <= anchors[-1])
            missing = support & (z % 4 != phase)
            a, m, s = int(plane_counts[anchors].sum()), int(plane_counts[missing].sum()), int(plane_counts[support].sum())
            record['phases'].append(dict(phase=phase, first_anchor=int(anchors[0]), last_anchor=int(anchors[-1]), anchor_foreground_voxels=a, missing_foreground_voxels=m, supported_foreground_voxels=s, outside_support_foreground_voxels=foreground-s, fraction_supported_on_anchors=a/s if s else None))
        for connectivity, components, n in [(26, count26, n26), (6, count6, n6)]:
            sizes = np.bincount(components.ravel(), minlength=n+1)[1:]
            boxes = ndimage.find_objects(components)
            comp_records, phase_records = [], []
            for index, (size, box) in enumerate(zip(sizes, boxes), 1):
                comp_records.append(dict(component=index, voxels=int(size), volume_mm3=float(size*voxel_mm3), bbox_rcz=[[int(b.start), int(b.stop)] for b in box]))
            for phase in range(4):
                anchors = np.flatnonzero(z % 4 == phase)
                support = (z >= anchors[0]) & (z <= anchors[-1])
                missing = support & (z % 4 != phase)
                ca = np.bincount(components[:,:,anchors].ravel(), minlength=n+1)[1:]
                cm = np.bincount(components[:,:,missing].ravel(), minlength=n+1)[1:]
                hidden = (ca == 0) & (cm > 0)
                phase_records.append(dict(phase=phase, components_with_missing_foreground=int((cm>0).sum()), anchor_absent_components=int(hidden.sum()), anchor_absent_missing_voxels=int(cm[hidden].sum()), largest_component_anchor_absent=bool(hidden[np.argmax(sizes)]) if n else None))
                for i, c in enumerate(comp_records):
                    c.setdefault('phases', []).append(dict(phase=phase, anchor_voxels=int(ca[i]), missing_voxels=int(cm[i]), anchor_absent=bool(hidden[i])))
            record['topology'][str(connectivity)] = dict(components=n, largest_component=int(np.argmax(sizes)+1) if n else None, size_bin_edges_voxels=[1,8,64,512,4096,None], size_bin_counts=[int(((sizes>=a)&(sizes<b)).sum()) for a,b in zip([1,8,64,512,4096],[8,64,512,4096,np.inf])], phases=phase_records, component_records=comp_records)
        result['series'].append(record)
        write(OUT / 'attempt_01.json', result)
        print(json.dumps(dict(patient=patient, uid=uid, components26=n26, phase0=record['topology']['26']['phases'][0])), flush=True)
        del native, count6, count26
    result['patients'] = []
    for patient in contract['patients']:
        rows = [r for r in result['series'] if r['patient'] == patient]
        result['patients'].append(dict(patient=patient, development_only=True, qualified_series=len(rows), phase0_series_with_anchor_absent_components=sum(r['topology']['26']['phases'][0]['anchor_absent_components']>0 for r in rows), phase0_series_with_anchor_absent_largest_component=sum(r['topology']['26']['phases'][0]['largest_component_anchor_absent'] is True for r in rows)))
    result.update(complete=len(result['series'])==15, finished_utc=datetime.now(timezone.utc).isoformat())
    write(OUT / 'attempt_01.json', result)
    print(json.dumps(dict(complete=result['complete'], series=len(result['series']), patients=result['patients'])), flush=True)
if __name__ == '__main__':
    main()
