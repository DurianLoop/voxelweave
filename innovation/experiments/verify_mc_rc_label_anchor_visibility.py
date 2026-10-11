"""Independent slab/coordinate arithmetic; topology itself remains SciPy output."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name] = '1'
import nibabel as nib
import numpy as np
from vs_seg_task_cpu_support import resource_gate
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/mc_rc_label_anchor_visibility'
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576),b''):
            digest.update(block)
    return digest.hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resource_gate()
    result, contract = read(OUT/'attempt_01.json'), read(OUT/'run_contract.json')
    errors, records = [], []
    def check(ok, why):
        if not ok:
            errors.append(why)
    check(sha(OUT/'run_contract.json')==result['run_contract_sha256'], 'Contract hash differs')
    for item in contract['files']:
        check(sha(ROOT/item['path'])==item['sha256'], 'Input changed ' + item['path'])
    check(result['complete'] and not result['errors'] and len(result['series'])==15 and len(result['patients'])==8, 'Fixed cohort incomplete')
    check([r['uid'] for r in result['series']]==contract['selected_uids'], 'Frozen roster differs')
    for row in result['series']:
        resource_gate()
        uid = row['uid']
        check(sha(ROOT/row['component_file'])==row['component_sha256'], 'Component artifact hash differs ' + uid)
        img = nib.load(ROOT/row['label_file'])
        check(sha(ROOT/row['label_file'])==row['label_sha256'], 'Label hash differs ' + uid)
        with np.load(ROOT/row['component_file']) as pack:
            cc6, cc26 = pack['connectivity6'], pack['connectivity26']
            transform = pack['dicom_rcz_from_label_xyz']
            check(list(cc26.shape)==row['native_shape'] and cc6.shape==cc26.shape, 'Native component dimensions differ ' + uid)
            label_z_axis = int(np.flatnonzero(transform[2,:3])[0])
            plane_counts = np.zeros(img.shape[label_z_axis],dtype=np.int64)
            positive_coordinates = 0
            for start in range(0,img.shape[2],4):
                slab = np.asarray(img.dataobj[:,:,start:start+4])
                check(slab.nbytes<=32000000 and np.isfinite(slab).all() and np.isin(slab,[0,1]).all(), 'Raw label finite/binary/resource differs ' + uid)
                counts = np.count_nonzero(slab,axis=tuple(a for a in range(3) if a!=label_z_axis))
                if label_z_axis==2:
                    plane_counts[start:start+len(counts)] += counts
                else:
                    plane_counts += counts
                coords = np.array(np.nonzero(slab))
                positive_coordinates += coords.shape[1]
                coords[2] += start
                mapped = transform[:3,:3] @ coords + transform[:3,3,None]
                check(np.all(mapped>=0) and np.all(mapped<np.array(cc26.shape)[:,None]), 'Forward native coordinate out of bounds ' + uid)
                check(np.all(cc6[tuple(mapped)]>0) and np.all(cc26[tuple(mapped)]>0), 'Source label foreground absent from native components ' + uid)
            if transform[2,label_z_axis]<0:
                plane_counts = plane_counts[::-1]
            check(positive_coordinates==row['label_foreground_voxels']==np.count_nonzero(cc6)==np.count_nonzero(cc26), 'Whole foreground coverage differs ' + uid)
            check(np.array_equal(plane_counts,row['plane_foreground_voxels']) and np.array_equal(plane_counts,pack['plane_foreground']), 'Independent raw-plane counts differ ' + uid)
            # Each 6-connected class must belong wholly to one 26-connected class.
            fine_to_coarse = []
            for component in range(1,int(cc6.max())+1):
                labels = np.unique(cc26[cc6==component])
                check(len(labels)==1 and labels[0]>0, 'Connectivity refinement differs ' + uid)
                fine_to_coarse.append(int(labels[0]))
            for phase in range(4):
                anchors = list(range(phase,cc26.shape[2],4))
                missing = [z for z in range(anchors[0],anchors[-1]+1) if z not in anchors]
                raw_a, raw_m = sum(int(plane_counts[z]) for z in anchors), sum(int(plane_counts[z]) for z in missing)
                p = row['phases'][phase]
                check(p['anchor_foreground_voxels']==raw_a and p['missing_foreground_voxels']==raw_m and p['supported_foreground_voxels']==raw_a+raw_m and p['outside_support_foreground_voxels']==positive_coordinates-raw_a-raw_m, 'Independent phase support arithmetic differs ' + uid)
                expected_fraction = raw_a/(raw_a+raw_m) if raw_a+raw_m else None
                check(p['fraction_supported_on_anchors']==expected_fraction, 'Anchor fraction differs ' + uid)
                for connectivity, cc in [('6',cc6),('26',cc26)]:
                    topology = row['topology'][connectivity]
                    sizes = np.bincount(cc.ravel())[1:]
                    check(len(sizes)==topology['components'], 'Component count differs ' + uid)
                    ca = np.zeros(len(sizes),dtype=np.int64)
                    cm = np.zeros(len(sizes),dtype=np.int64)
                    for z in anchors:
                        ca += np.bincount(cc[:,:,z].ravel(),minlength=len(sizes)+1)[1:]
                    for z in missing:
                        cm += np.bincount(cc[:,:,z].ravel(),minlength=len(sizes)+1)[1:]
                    hidden = (ca==0)&(cm>0)
                    stored = topology['phases'][phase]
                    check(int(hidden.sum())==stored['anchor_absent_components'] and int(cm[hidden].sum())==stored['anchor_absent_missing_voxels'] and int((cm>0).sum())==stored['components_with_missing_foreground'], 'Independent absent-component arithmetic differs ' + uid)
                    check(stored['largest_component_anchor_absent']==bool(hidden[np.argmax(sizes)]) and topology['largest_component']==int(np.argmax(sizes)+1), 'Largest-component counterevidence differs ' + uid)
                    for i,c in enumerate(topology['component_records']):
                        cp = c['phases'][phase]
                        check(c['voxels']==int(sizes[i]) and cp['anchor_voxels']==int(ca[i]) and cp['missing_voxels']==int(cm[i]) and cp['anchor_absent']==bool(hidden[i]), 'Component size/phase differs ' + uid)
                        if phase==0:
                            coords = np.nonzero(cc==i+1)
                            bbox = [[int(v.min()),int(v.max())+1] for v in coords]
                            check(bbox==c['bbox_rcz'], 'Independent component bounding box differs ' + uid)
            records.append(dict(patient=row['patient'],uid=uid,all_foreground_coordinates_checked=positive_coordinates,native_planes=len(plane_counts),connectivity6_classes=len(fine_to_coarse),connectivity26_classes=int(cc26.max()),fine_to_coarse=fine_to_coarse))
    proof = dict(created_utc=datetime.now(timezone.utc).isoformat(), verification_script_sha256=sha(__file__), result_sha256=sha(OUT/'attempt_01.json'), run_contract_sha256=sha(OUT/'run_contract.json'), scope='all original label slabs, explicit coordinate mapping, phase/component arithmetic and topology refinement; not independent connectivity generation', counts=dict(series=len(records),patients=len({r['patient'] for r in records}),phases_per_series=4,connectivities_per_series=2,foreground_coordinates_checked=sum(r['all_foreground_coordinates_checked'] for r in records)), series=records, errors=errors, MR_pixels_decoded=False, gpu_used=False, scientific_independent_validation_patients=0, publication_claim_confirmed=False)
    with (OUT/'independent_label_phase_verification.json').open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=proof['counts'],errors=errors),ensure_ascii=False,indent=2))
    return int(bool(errors))
if __name__=='__main__':
    raise SystemExit(main())
