"""Read-only CSV reconciliation and fixed-nine-label native-grid checks."""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
import os
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path

os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import nibabel as nib
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'literature/source_cache/mc_rc_three_patient_headers_2026-10-02'
OUT=ROOT/'experiments/mc_rc_native_t2_label_gate'
DATA=ROOT/'data/mc_rc_three_patient_label_grid'
PLAN=ROOT/'MC_RC_THREE_PATIENT_LABEL_GRID_PLAN_2026-10-02.md'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
def corners(shape):return np.array([[*x,1.] for x in itertools.product(*[(0,n-1) for n in shape])]).T

def mapping_audit():
    errors=[];csvpath=B/'official_label_metadata_00_attempt_01.csv'
    with csvpath.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.reader(f);cells=list(reader)
    artifact=read(OUT/'official_pathnames_artifact_read.json')
    if artifact['source_sha256']!=sha(csvpath) or artifact['values']!=cells:errors.append('Artifact read and independent CSV cells differ')
    fields=cells[0];rows=[dict(zip(fields,r)) for r in cells[1:]];byuid={r['series_instance_uid']:r for r in rows}
    api=read(ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response');apid={r['SeriesInstanceUID']:r for r in api}
    if len(byuid)!=len(rows) or len(apid)!=len(api) or set(byuid)!=set(apid):errors.append('Full UID sets/uniqueness differ')
    ledger=read(B/'attempt_01.json');zipfile_path=ROOT/ledger['labels']['transfer']['file']
    if sha(zipfile_path)!=ledger['labels']['transfer']['sha256']:errors.append('Official label ZIP hash differs')
    prefix='VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023/VS-MC-RC segmentations-NIfTI-Release 2023/'
    with zipfile.ZipFile(zipfile_path) as z:
        actual={m.filename for m in z.infolist() if not m.is_dir() and not m.filename.startswith('__MACOSX/') and m.filename.endswith('.nii.gz')}
    matches=[]
    for uid,r in byuid.items():
        other=apid[uid]
        issues=[]
        for left,right in [('collection','Collection'),('patient_id','PatientID'),('study_instance_uid','StudyInstanceUID'),('modality','Modality')]:
            if r[left]!=str(other[right]):issues.append(left+' differs')
        if int(r['num_files'])!=int(other['ImageCount']):issues.append('Object count differs')
        expected=prefix+r['SegmentationPath']
        if expected not in actual:issues.append('Exact official label path absent')
        if issues:errors.append(uid+': '+', '.join(issues))
        matches.append({'uid':uid,'patient':r['patient_id'],'label_zip_member':expected,'metadata_issues':issues})
    return ledger,byuid,{r['uid']:r for r in matches},zipfile_path,{'rows':len(rows),'patients':len({r['patient_id'] for r in rows}),'series':len(byuid),'unique_segmentation_paths':len({r['SegmentationPath'] for r in rows}),'actual_nonmacos_nifti_members':len(actual),'matched_rows':sum(not r['metadata_issues'] for r in matches),'artifact_cells_exact_match':artifact['values']==cells,'source_csv_sha256':sha(csvpath),'artifact_read_sha256':sha(OUT/'official_pathnames_artifact_read.json'),'errors':errors}

def best_grid_transform(dicom_shape,dicom_affine,label_shape,label_affine):
    candidates=[]
    for perm in itertools.permutations(range(3)):
        if any(dicom_shape[i]!=label_shape[perm[i]] for i in range(3)):continue
        for signs in itertools.product((-1,1),repeat=3):
            t=np.zeros((4,4));t[3,3]=1
            for i,j in enumerate(perm):
                t[i,j]=signs[i]
                if signs[i]<0:t[i,3]=dicom_shape[i]-1
            delta=(dicom_affine@t-label_affine)@corners(label_shape)
            error=float(np.linalg.norm(delta[:3],axis=0).max())
            candidates.append((error,t,perm,signs))
    if not candidates:return {'same_native_grid':False,'reason':'Shape cannot match by axis permutation','signed_permutations_considered':0}
    error,t,perm,signs=min(candidates,key=lambda r:r[0])
    return {'same_native_grid':error<=.05,'max_corner_world_error_mm':error,'dicom_rcz_from_label_xyz':t.tolist(),'axis_permutation':list(perm),'axis_signs':list(signs),'signed_permutations_considered':len(candidates)}

def one(r,mapping,byuid,zip_path,attempt,total):
    source=r['source'];uid=source['SeriesInstanceUID'];match=mapping[uid];entry={'patient':source['PatientID'],'series_uid':uid,'study_uid':source['StudyInstanceUID'],'description':source['SeriesDescription'],'header_qualified_candidate':r['summary']['header_qualified_candidate'],'header_pending_acquisition_type':any(not x for x in r['summary']['mr_acquisition_types']),'label_zip_member':match['label_zip_member'],'metadata_issues':match['metadata_issues']}
    try:
        if match['metadata_issues']:raise ValueError('Metadata join did not pass')
        with zipfile.ZipFile(zip_path) as z:
            m=z.getinfo(match['label_zip_member'])
            if m.file_size>100_000_000 or total[0]+m.file_size>300_000_000:raise ValueError('Fixed label decompression budget exceeded')
            raw=z.read(m);total[0]+=len(raw)
        dest=DATA/f'{source["PatientID"]}_{uid}_label_attempt_{attempt:02d}.nii.gz';dest.write_bytes(raw)
        img=nib.load(dest);shape=list(img.shape)
        if len(shape)!=3:raise ValueError('Label is not 3D')
        data=np.asanyarray(img.dataobj)
        if not np.isfinite(data).all():raise ValueError('Non-finite label')
        unique=np.unique(data).tolist();binary=set(unique)<={0,1}
        nonzero=int(np.count_nonzero(data));spacing=list(map(float,img.header.get_zooms()[:3]));voxel=float(abs(np.linalg.det(img.affine[:3,:3])))
        qc=int(img.header['qform_code']);sc=int(img.header['sform_code']);q=img.get_qform();s=img.get_sform()
        form_error=float(np.linalg.norm(((q-s)@corners(shape))[:3],axis=0).max()) if qc>0 and sc>0 else None
        form_consistent=form_error is None or form_error<=.05
        summary=r['summary'];dicom_affine=np.asarray(summary['affine_rcz_ras'])
        dicom_shape=[summary['rows'],summary['columns'],summary['planes']]
        grid=best_grid_transform(dicom_shape,dicom_affine,shape,img.affine)
        source_geometry_uniform=not any('Nonuniform' in x or 'Duplicate' in x or 'Orientation' in x or 'Rows/columns' in x for x in summary['issues'])
        qualified=bool(r['summary']['header_qualified_candidate'] and source_geometry_uniform and grid['same_native_grid'] and binary and form_consistent and (qc>0 or sc>0))
        entry.update(label_file=dest.relative_to(ROOT).as_posix(),label_sha256=sha(dest),label_compressed_bytes=len(raw),label_zip_uncompressed_bytes=m.file_size,zip_crc32_verified=True,label_shape=shape,label_dtype=str(data.dtype),label_values=unique,label_is_binary=binary,label_foreground_voxels=nonzero,label_voxel_volume_mm3=voxel,label_foreground_volume_mm3=nonzero*voxel,label_spacing_xyz_mm=spacing,label_affine_xyz_ras=img.affine.tolist(),qform_code=qc,sform_code=sc,qform=q.tolist(),sform=s.tolist(),max_qform_sform_corner_difference_mm=form_error,forms_consistent=form_consistent,dicom_shape_rcz=dicom_shape,dicom_affine_rcz_ras=dicom_affine.tolist(),source_geometry_uniform=source_geometry_uniform,grid=grid,header_and_label_grid_preflight_passed=qualified,label_inspection_complete=True)
    except Exception as exc:entry.update(label_inspection_complete=False,error=f'{type(exc).__name__}: {exc}',header_and_label_grid_preflight_passed=False)
    return entry

def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True);attempt=len(list(OUT.glob('label_grid_attempt_*.json')))+1
    ledger,byuid,mapping,zip_path,audit=mapping_audit()
    if not ledger['complete']:raise ValueError('Full fixed-nine header retrieval incomplete')
    total=[0];rows=[]
    for r in ledger['series']:
        entry=one(r,mapping,byuid,zip_path,attempt,total);rows.append(entry)
        print(json.dumps({k:entry.get(k) for k in ('patient','description','header_qualified_candidate','header_pending_acquisition_type','label_shape','label_foreground_voxels','grid','header_and_label_grid_preflight_passed','error')},ensure_ascii=False),flush=True)
    result={'attempt':attempt,'created_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'source_header_attempt_sha256':sha(B/'attempt_01.json'),'official_label_zip_sha256':sha(zip_path),'scope':'full public metadata join and fixed-nine source label/native-grid checks; no reconstruction/segmentation performance','full_metadata_audit':audit,'series':rows,'complete':not audit['errors'] and all(r['label_inspection_complete'] for r in rows),'label_decompressed_file_bytes':total[0],'MR_pixel_arrays_decoded':False,'label_arrays_decoded':True,'source_preflight_series_passed':sum(r['header_and_label_grid_preflight_passed'] for r in rows),'source_preflight_patients_with_a_passing_series':len({r['patient'] for r in rows if r['header_and_label_grid_preflight_passed']}),'scientific_independent_validation_patients':0}
    write(OUT/f'label_grid_attempt_{attempt:02d}.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('series','script_sha256','plan_sha256')},ensure_ascii=False),flush=True)
    return int(not result['complete'])

if __name__=='__main__':raise SystemExit(main())
