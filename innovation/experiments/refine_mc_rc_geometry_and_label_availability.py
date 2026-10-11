"""Keep first-run failures; classify public availability and fit all IPPs."""
from __future__ import annotations
import csv
import hashlib
import itertools
import json
import os
import sqlite3
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path

os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
import numpy as np
from audit_mc_rc_three_patient_label_grid import best_grid_transform

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
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')

def availability(ledger):
    db=sqlite3.connect(':memory:');db.executescript('CREATE TABLE api(uid TEXT PRIMARY KEY,p TEXT,st TEXT,des TEXT,n INT,release TEXT); CREATE TABLE mapping(uid TEXT PRIMARY KEY,p TEXT,st TEXT,n INT,path TEXT); CREATE TABLE labels(path TEXT PRIMARY KEY);')
    for r in read(ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response'):db.execute('INSERT INTO api VALUES(?,?,?,?,?,?)',(r['SeriesInstanceUID'],r['PatientID'],r['StudyInstanceUID'],r['SeriesDescription'],r['ImageCount'],r['DateReleased']))
    with (B/'official_label_metadata_00_attempt_01.csv').open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):db.execute('INSERT INTO mapping VALUES(?,?,?,?,?)',(r['series_instance_uid'],r['patient_id'],r['study_instance_uid'],int(r['num_files']),r['SegmentationPath']))
    prefix='VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023/VS-MC-RC segmentations-NIfTI-Release 2023/'
    with zipfile.ZipFile(ROOT/ledger['labels']['transfer']['file']) as z:
        for m in z.infolist():
            if not m.is_dir() and m.filename.startswith(prefix) and m.filename.endswith('.nii.gz'):db.execute('INSERT INTO labels VALUES(?)',(m.filename[len(prefix):],))
    status="CASE WHEN m.path='' THEN 'blank_path' WHEN l.path IS NULL THEN 'specified_path_absent' ELSE 'available' END"
    sql='SELECT a.uid,a.p,a.st,a.des,a.release,m.path,'+status+' FROM api a JOIN mapping m ON a.uid=m.uid LEFT JOIN labels l ON m.path=l.path ORDER BY a.p,a.st,a.uid'
    rows=[dict(zip(['uid','patient','study','description','release','segmentation_path','availability'],v)) for v in db.execute(sql)]
    groups=[]
    for group,filter in [('all','1=1'),('official_nonoverlap_candidates',"substr(a.p,1,9)='VS-MC-RC-'"),('shared_VS_SEG_excluded',"substr(a.p,1,7)='VS-SEG-'")]:
        query='SELECT substr(a.des,1,4),a.release,'+status+',COUNT(*),COUNT(DISTINCT a.p) FROM api a JOIN mapping m ON a.uid=m.uid LEFT JOIN labels l ON m.path=l.path WHERE '+filter+' GROUP BY 1,2,3 ORDER BY 1,2,3'
        for v in db.execute(query):groups.append(dict(zip(['description_prefix','release','availability','series','patients'],v))|{'group':group})
    qa={'api_rows':db.execute('SELECT COUNT(*) FROM api').fetchone()[0],'mapping_rows':db.execute('SELECT COUNT(*) FROM mapping').fetchone()[0],'label_members':db.execute('SELECT COUNT(*) FROM labels').fetchone()[0],'identity_count_disagreements':db.execute('SELECT COUNT(*) FROM api a JOIN mapping m ON a.uid=m.uid WHERE a.p!=m.p OR a.st!=m.st OR a.n!=m.n').fetchone()[0],'available_rows':sum(r['availability']=='available' for r in rows),'blank_paths':sum(r['availability']=='blank_path' for r in rows),'specified_paths_absent':sum(r['availability']=='specified_path_absent' for r in rows),'nonoverlap_T2_patients_with_actual_label':len({r['patient'] for r in rows if r['patient'].startswith('VS-MC-RC-') and r['description'].startswith('_T2_') and r['availability']=='available'}),'nonoverlap_T2_series_with_actual_label':sum(r['patient'].startswith('VS-MC-RC-') and r['description'].startswith('_T2_') and r['availability']=='available' for r in rows)}
    return {'qa':qa,'groups':groups,'rows':rows}

def fit(r,original):
    hdr=read(B/r['header_file']);records=hdr['records'];iop=np.asarray([x['iop'] for x in records]);ps=np.asarray([x['pixel_spacing'] for x in records]);pos=np.asarray([x['ipp'] for x in records]);normal=np.cross(iop[0,:3],iop[0,3:]);order=np.argsort(pos@normal);pos=pos[order];n=len(pos);z=np.arange(n,dtype=float);center=z-z.mean();step=(center[:,None]*(pos-pos.mean(axis=0))).sum(axis=0)/(center@center);origin=pos.mean(axis=0)-z.mean()*step;pred=origin+z[:,None]*step;maxres=float(np.linalg.norm(pos-pred,axis=1).max());gaps=np.diff(pos@normal);deviation=float(np.max(abs(gaps-np.median(gaps))))
    affine=np.eye(4);affine[:3,0]=iop[0,3:]*ps[0,0];affine[:3,1]=iop[0,:3]*ps[0,1];affine[:3,2]=step;affine[:3,3]=origin;ras=np.diag([-1.,-1.,1.,1.])@affine
    immutable_issues=[x for x in hdr['summary']['issues'] if x!='Nonuniform/non-affine slice geometry'];geom=not immutable_issues and maxres<=.02 and deviation<=.02
    types=hdr['summary']['mr_acquisition_types'];pending=any(not t for t in types);acq=types==['3D'];native_spacing=[float(ps[0,0]),float(ps[0,1]),float(np.linalg.norm(step))];thin=max(native_spacing)<=1.5 and max(x['slice_thickness'] for x in records)<=1.5
    native=geom and acq and hdr['summary']['original_no_derived'] and not hdr['summary']['derivative_evidence'] and thin
    grid=None;source_pass=False
    if original.get('label_inspection_complete'):
        grid=best_grid_transform([hdr['summary']['rows'],hdr['summary']['columns'],n],ras,original['label_shape'],np.asarray(original['label_affine_xyz_ras']))
        source_pass=native and grid['same_native_grid'] and original['label_is_binary'] and original['forms_consistent'] and (original['qform_code']>0 or original['sform_code']>0)
    return {'patient':r['source']['PatientID'],'uid':r['source']['SeriesInstanceUID'],'description':r['source']['SeriesDescription'],'header_file':r['header_file'],'header_sha256':r['header_sha256'],'first_run_header_qualified':hdr['summary']['header_qualified_candidate'],'first_run_max_affine_residual_mm':hdr['summary']['max_affine_position_residual_mm'],'fit_method':'centered linear regression of all ordered IPPs','fitted_affine_rcz_lps':affine.tolist(),'fitted_affine_rcz_ras':ras.tolist(),'native_spacing_rcz_mm':native_spacing,'nominal_thicknesses_mm':hdr['summary']['slice_thicknesses_mm'],'max_fitted_position_residual_mm':maxres,'max_gap_deviation_mm':deviation,'unchanged_other_header_issues':immutable_issues,'missing_acquisition_type_pending':pending,'geometry_passed':geom,'refined_header_qualified':bool(native),'prior_label_inspection_complete':original.get('label_inspection_complete',False),'grid_with_fitted_affine':grid,'refined_header_and_label_grid_passed':bool(source_pass),'label_foreground_voxels':original.get('label_foreground_voxels'),'first_run_source_preflight_passed':original['header_and_label_grid_preflight_passed']}

def main():
    sys.stdout.reconfigure(encoding='utf-8');attempt=len(list(OUT.glob('geometry_availability_attempt_*.json')))+1
    ledger=read(B/'attempt_01.json');old=read(OUT/'label_grid_attempt_01.json');original={r['series_uid']:r for r in old['series']}
    audit=availability(ledger);rows=[fit(r,original[r['source']['SeriesInstanceUID']]) for r in ledger['series']]
    result={'attempt':attempt,'created_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),'grid_helper_sha256':sha(ROOT/'experiments/audit_mc_rc_three_patient_label_grid.py'),'plan_sha256':sha(PLAN),'header_attempt_sha256':sha(B/'attempt_01.json'),'first_label_grid_attempt_sha256':sha(OUT/'label_grid_attempt_01.json'),'scope':'post-result geometry-estimator correction and availability diagnosis; all original failures retained','availability':audit,'series':rows,'refined_header_qualified_series':sum(r['refined_header_qualified'] for r in rows),'refined_source_preflight_series':sum(r['refined_header_and_label_grid_passed'] for r in rows),'refined_source_preflight_patients':len({r['patient'] for r in rows if r['refined_header_and_label_grid_passed']}),'full_public_label_coverage_certified':False,'MR_pixel_arrays_decoded':False,'scientific_independent_validation_patients':0}
    write(OUT/f'geometry_availability_attempt_{attempt:02d}.json',result)
    print(json.dumps({'availability_qa':audit['qa'],'refined_header_qualified_series':result['refined_header_qualified_series'],'refined_source_preflight_series':result['refined_source_preflight_series'],'refined_source_preflight_patients':result['refined_source_preflight_patients']},ensure_ascii=False,indent=2))
    for r in rows:print(json.dumps({k:r[k] for k in ('patient','description','max_fitted_position_residual_mm','refined_header_qualified','refined_header_and_label_grid_passed','missing_acquisition_type_pending')},ensure_ascii=False))
    return 0

if __name__=='__main__':raise SystemExit(main())
