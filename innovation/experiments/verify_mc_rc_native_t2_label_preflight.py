"""Independent raw-DICOM reread, least-squares fit and inverse-grid checks."""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
import os
import sys
import zipfile
from pathlib import Path

os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import numpy as np
import pydicom
import nibabel as nib

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'literature/source_cache/mc_rc_three_patient_headers_2026-10-02'
OUT=ROOT/'experiments/mc_rc_native_t2_label_gate'
PLAN=ROOT/'MC_RC_GEOMETRY_AND_LABEL_AVAILABILITY_FOLLOWUP_PLAN_2026-10-02.md'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def points(shape):return np.array([[*v,1] for v in itertools.product(*[(0,n-1) for n in shape])],dtype=float).T

def main():
    sys.stdout.reconfigure(encoding='utf-8');errors=[];records=[];objects_checked=0;labels_checked=0
    ledger=read(B/'attempt_01.json');first=read(OUT/'label_grid_attempt_01.json');refined=read(OUT/'geometry_availability_attempt_01.json')
    first_by_uid={r['series_uid']:r for r in first['series']};new_by_uid={r['uid']:r for r in refined['series']}
    if not ledger['complete'] or first['complete'] or refined['full_public_label_coverage_certified']:errors.append('Original result/failure scopes differ')
    for r in ledger['series']:
        src=r['source'];uid=src['SeriesInstanceUID'];saved=read(B/r['header_file']);saved_by_sop={v['sop_uid']:v for v in saved['records']}
        zip_path=ROOT/r['transfer']['file']
        if sha(zip_path)!=r['transfer']['sha256'] or sha(B/r['header_file'])!=r['header_sha256']:errors.append('ZIP/header hash differs '+uid)
        datasets=[]
        with zipfile.ZipFile(zip_path) as z:
            for m in z.infolist():
                if m.is_dir() or not m.filename.lower().endswith('.dcm'):continue
                with z.open(m) as f:ds=pydicom.dcmread(f,stop_before_pixels=True)
                datasets.append(ds);objects_checked+=1;sop=str(ds.SOPInstanceUID)
                if sop not in saved_by_sop:errors.append('Raw SOP absent from saved header '+uid);continue
                other=saved_by_sop[sop]
                if str(ds.PatientID)!=src['PatientID'] or str(ds.SeriesInstanceUID)!=uid or str(ds.StudyInstanceUID)!=src['StudyInstanceUID']:errors.append('Raw identity differs '+uid)
                for attr,field in [('Rows','rows'),('Columns','columns'),('SliceThickness','slice_thickness')]:
                    if float(ds.get(attr))!=float(other[field]):errors.append('Raw scalar differs '+uid+' '+field)
                for attr,field in [('PixelSpacing','pixel_spacing'),('ImagePositionPatient','ipp'),('ImageOrientationPatient','iop')]:
                    if not np.array_equal(np.array(ds.get(attr),dtype=float),np.asarray(other[field])):errors.append('Raw vector differs '+uid+' '+field)
                if str(ds.get('MRAcquisitionType',''))!=other['mr_acquisition_type'] or [str(v) for v in ds.get('ImageType',[])]!=other['image_type']:errors.append('Raw acquisition tags differ '+uid)
        if len(datasets)!=int(src['ImageCount']) or len({str(d.SOPInstanceUID) for d in datasets})!=len(datasets):errors.append('Raw object count/uniqueness differs '+uid)
        orient=np.asarray(datasets[0].ImageOrientationPatient,dtype=float);normal=np.cross(orient[:3],orient[3:]);pos=np.array([d.ImagePositionPatient for d in datasets],dtype=float);pos=pos[np.argsort(pos@normal)];n=len(pos)
        coefficients=np.linalg.lstsq(np.column_stack((np.ones(n),np.arange(n))),pos,rcond=None)[0];origin=coefficients[0];step=coefficients[1]
        residual=float(np.linalg.norm(pos-(origin+np.arange(n)[:,None]*step),axis=1).max());endpoint=(pos[-1]-pos[0])/(n-1);eres=float(np.linalg.norm(pos-(pos[0]+np.arange(n)[:,None]*endpoint),axis=1).max())
        affine=np.eye(4);affine[:3,0]=orient[3:]*float(datasets[0].PixelSpacing[0]);affine[:3,1]=orient[:3]*float(datasets[0].PixelSpacing[1]);affine[:3,2]=step;affine[:3,3]=origin;ras=np.diag([-1.,-1.,1.,1.])@affine
        ref=new_by_uid[uid]
        if not np.allclose(ras,np.asarray(ref['fitted_affine_rcz_ras']),rtol=0,atol=1e-9) or abs(residual-ref['max_fitted_position_residual_mm'])>1e-9:errors.append('Independent fit differs '+uid)
        raw_spacing=[float(datasets[0].PixelSpacing[0]),float(datasets[0].PixelSpacing[1]),float(np.linalg.norm(step))]
        acq=all(str(d.get('MRAcquisitionType',''))=='3D' for d in datasets)
        missing=any(not str(d.get('MRAcquisitionType','')) for d in datasets)
        orig=all('ORIGINAL' in [str(v).upper() for v in d.get('ImageType',[])] and 'DERIVED' not in [str(v).upper() for v in d.get('ImageType',[])] for d in datasets)
        derivative=any(any(token in (' '.join(str(v) for v in d.get('ImageType',[]))+' '+str(d.get('SeriesDescription',''))+' '+str(d.get('DerivationDescription',''))).upper() for token in ('MPR','REFORMAT','LOCALIZER')) for d in datasets)
        gap=np.diff(pos@normal);consistent=True
        for ds in datasets:
            if ds.Rows!=datasets[0].Rows or ds.Columns!=datasets[0].Columns or str(ds.FrameOfReferenceUID)!=str(datasets[0].FrameOfReferenceUID):consistent=False
            if np.max(abs(np.asarray(ds.PixelSpacing,dtype=float)-np.asarray(datasets[0].PixelSpacing,dtype=float)))>1e-6 or np.max(abs(np.asarray(ds.ImageOrientationPatient,dtype=float)-orient))>1e-6:consistent=False
        orthonormal=max(abs(np.linalg.norm(orient[:3])-1),abs(np.linalg.norm(orient[3:])-1),abs(orient[:3]@orient[3:]))<=1e-4
        geometry_ok=consistent and orthonormal and residual<=.02 and min(gap)>1e-4 and max(abs(gap-np.median(gap)))<=.02
        thin=max(raw_spacing)<=1.5 and max(float(d.SliceThickness) for d in datasets)<=1.5
        header_qualified=bool(geometry_ok and acq and orig and not derivative and thin)
        if header_qualified!=ref['refined_header_qualified'] or missing!=ref['missing_acquisition_type_pending']:errors.append('Independent header eligibility differs '+uid)
        old=first_by_uid[uid];grid_pass=False;corner_error=None;integer_matrix=None;source_pass=False
        if old['label_inspection_complete']:
            label=ROOT/old['label_file']
            if sha(label)!=old['label_sha256']:errors.append('Saved label hash differs '+uid)
            img=nib.load(label);data=np.asarray(img.dataobj);labels_checked+=1
            if list(img.shape)!=old['label_shape'] or int((data!=0).sum())!=old['label_foreground_voxels'] or sorted(np.unique(data).tolist())!=old['label_values']:errors.append('Raw label contents differ '+uid)
            transform=np.linalg.solve(ras,img.affine);integer=np.rint(transform).astype(int)
            matrix=integer[:3,:3];signed=np.all(np.sum(abs(matrix),axis=0)==1) and np.all(np.sum(abs(matrix),axis=1)==1) and np.array_equal(integer[3],[0,0,0,1])
            mapped=integer@points(img.shape);shape=[int(datasets[0].Rows),int(datasets[0].Columns),n]
            extent=np.array_equal(mapped[:3].min(axis=1),[0,0,0]) and np.array_equal(mapped[:3].max(axis=1),np.array(shape)-1)
            corner_error=float(np.linalg.norm(((ras@integer-img.affine)@points(img.shape))[:3],axis=0).max());grid_pass=bool(signed and extent and corner_error<=.05);integer_matrix=integer.tolist()
            if grid_pass!=ref['grid_with_fitted_affine']['same_native_grid'] or abs(corner_error-ref['grid_with_fitted_affine']['max_corner_world_error_mm'])>1e-8:errors.append('Independent inverse-grid check differs '+uid)
            qc=int(img.header['qform_code']);sc=int(img.header['sform_code']);form_error=float(np.linalg.norm(((img.get_qform()-img.get_sform())@points(img.shape))[:3],axis=0).max()) if qc>0 and sc>0 else None
            binary=np.all((data==0)|(data==1));source_pass=bool(header_qualified and grid_pass and binary and (qc>0 or sc>0) and (form_error is None or form_error<=.05))
        if source_pass!=ref['refined_header_and_label_grid_passed']:errors.append('Independent complete source preflight differs '+uid)
        records.append({'patient':src['PatientID'],'uid':uid,'raw_objects':n,'header_qualified':header_qualified,'missing_acquisition_type_pending':missing,'least_squares_max_residual_mm':residual,'endpoint_max_residual_mm':eres,'grid_passed':grid_pass,'grid_max_corner_error_mm':corner_error,'integer_inverse_grid_matrix':integer_matrix,'source_preflight_passed':source_pass})
    counts={'raw_DICOM_objects_checked':objects_checked,'series':len(records),'label_arrays_checked':labels_checked,'header_qualified_series':sum(r['header_qualified'] for r in records),'source_preflight_series':sum(r['source_preflight_passed'] for r in records),'source_preflight_patients':len({r['patient'] for r in records if r['source_preflight_passed']})}
    if counts!={'raw_DICOM_objects_checked':473,'series':9,'label_arrays_checked':6,'header_qualified_series':6,'source_preflight_series':4,'source_preflight_patients':2}:errors.append('Fixed-nine source scope/count differs')
    proof={'verification_script_sha256':sha(__file__),'plan_sha256':sha(PLAN),'header_result_sha256':sha(B/'attempt_01.json'),'first_label_result_sha256':sha(OUT/'label_grid_attempt_01.json'),'refined_result_sha256':sha(OUT/'geometry_availability_attempt_01.json'),'scope':'raw source headers, independent geometry fits and inverse integer-grid verification; not reconstruction performance','counts':counts,'series':records,'MR_pixel_arrays_decoded':False,'original_full_label_gate_complete':first['complete'],'full_public_label_coverage_certified':False,'scientific_independent_validation_patients':0,'errors':errors}
    (OUT/'independent_raw_geometry_grid_verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'counts':counts,'errors':errors,'original_full_label_gate_complete':first['complete']},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':raise SystemExit(main())
