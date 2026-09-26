import csv,hashlib,json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import nibabel as nib
import pydicom
from processing.fastmri_brain_t2_prepare import infer_series_label
from pastnet_v2.common import ROOT as WORKSPACE,PACKAGE,sha256,write_json

ROOT=Path(__file__).resolve().parent
SOURCE=PACKAGE/'manifests/fastmri/fold_00.json'

def uid_hash(x):return hashlib.sha256(str(x).encode()).hexdigest()
def main():
    source=json.loads(SOURCE.read_text(encoding='utf-8'))
    catalog={r['case_id']:r for r in csv.DictReader((WORKSPACE/'dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_nifti_manifest.csv').open(encoding='utf-8-sig'))}
    records=[r for r in source['records'] if r['split'] in ('train','val')]
    def scan(rec):
        row=catalog[rec['case_id']];directory=WORKSPACE/'dataset/fastMRI_brain_DICOM'/row['source_case_id']
        groups=defaultdict(list)
        for f in sorted(directory.glob('*.dcm')):
            if infer_series_label(f)!=row['series_label']:continue
            h=pydicom.dcmread(f,force=True,stop_before_pixels=True)
            groups[str(h.SeriesInstanceUID)].append(f)
        return rec,groups
    scans=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(rec,groups) in enumerate(pool.map(scan,records)):
            scans.append((rec,groups))
            if (i+1)%20==0:print(f'headers {i+1}/{len(records)} train/val series',flush=True)
    header_rows=[dict(case_id=r['case_id'],split=r['split'],patient_id=r['patient_id'],
        stored_depth=r['shape'][2],uid_count=len(g),groups={uid_hash(u):len(v) for u,v in g.items()}) for r,g in scans]
    mixed=[(r,g) for r,g in scans if len(g)>1]
    write_json(ROOT/'results/header_audit.json',dict(records=header_rows,mixed_cases=[r['case_id'] for r,g in mixed],
        source_manifest_sha256=sha256(SOURCE),test_headers_read=False))
    # Scope fixed by the previously documented anomaly. Additional anomalies
    # must be reviewed; never silently modify validation or another patient.
    assert len(mixed)==1 and mixed[0][0]['case_id']=='113452254821_ax_t2'
    rec,groups=mixed[0];assert rec['split']=='train'
    old=nib.load(rec['path']).get_fdata(dtype=np.float32)
    pixels={hashlib.sha256(old[:,:,i].tobytes()).hexdigest():i for i in range(old.shape[2])}
    assert len(pixels)==32 and len(groups)==2
    details=[]
    for uid,files in sorted(groups.items()):
        rows=[];images=[]
        for f in files:
            h=pydicom.dcmread(f,force=True);v=h.pixel_array.astype(np.float32)
            idx=pixels[hashlib.sha256(v.tobytes()).hexdigest()]
            assert np.array_equal(v,old[:,:,idx])
            orient=np.array(h.ImageOrientationPatient,float);pos=np.array(h.ImagePositionPatient,float)
            z=float(pos@np.cross(orient[:3],orient[3:]))
            rows.append(dict(source=str(f),source_sha256=sha256(f),old_index=idx,instance=int(h.InstanceNumber),
                position=pos.tolist(),orientation=orient.tolist(),pixel_spacing=list(map(float,h.PixelSpacing)),projected_z=z))
        rows.sort(key=lambda x:x['projected_z']);z=np.array([r['projected_z'] for r in rows]);d=np.diff(z)
        assert len(rows)==16 and np.all(d>0) and np.allclose(d,d.mean(),atol=1e-4)
        assert all(np.allclose(x['orientation'],rows[0]['orientation'],atol=1e-6) for x in rows)
        details.append(dict(uid_sha256=uid_hash(uid),slice_count=16,spacing_z=float(d.mean()),slices=rows))
    assert sorted(x['old_index'] for d in details for x in d['slices'])==list(range(32))
    a=old[:,:,[r['old_index'] for r in details[0]['slices']]];b=old[:,:,[r['old_index'] for r in details[1]['slices']]]
    grid=[]
    index_to_z={x['old_index']:x['projected_z'] for d in details for x in d['slices']}
    index_to_uid={x['old_index']:i for i,d in enumerate(details) for x in d['slices']}
    for start in range(28):
        phases=[(index_to_z[start+j]-index_to_z[start])/(index_to_z[start+4]-index_to_z[start]) for j in (1,2,3)]
        grid.append(dict(z=start,actual_phase=phases,nominal_phase=[.25,.5,.75],
            uid_indices=[index_to_uid[start+j] for j in range(5)]))
    write_json(ROOT/'results/repair_mapping.json',dict(case_id=rec['case_id'],patient_id=rec['patient_id'],
        original_nifti=rec['path'],original_sha256=sha256(rec['path']),groups=details,
        arrays_identical=bool(np.array_equal(a,b)),between_uid_raw_mse=float(np.mean((a-b).astype(np.float64)**2)),
        old_intervals=grid,all_32_pixels_exactly_mapped=True,old_volume_modified=False))
    print(json.dumps(dict(mixed_cases=[r['case_id'] for r,g in mixed],groups=2,all_pixels_matched=True,
        arrays_identical=bool(np.array_equal(a,b)),old_phase_examples=grid[:2]),indent=2))
if __name__=='__main__':main()
