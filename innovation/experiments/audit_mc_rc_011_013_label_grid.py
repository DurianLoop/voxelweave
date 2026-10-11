"""Five fixed official labels: streaming semantics and native-grid preflight, no MR pixels."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import csv,json,math,sys,zipfile,traceback
from pathlib import Path
from datetime import datetime,timezone
import nibabel as nib
import numpy as np
from audit_mc_rc_three_patient_label_grid import best_grid_transform,corners,sha,read,write
from vs_seg_task_cpu_support import resource_gate
ROOT=Path(__file__).resolve().parents[1]
HEADERS=ROOT/'literature/source_cache/mc_rc_011_013_headers_2026-10-03'
PRIOR=ROOT/'literature/source_cache/mc_rc_three_patient_headers_2026-10-02'
OUT=ROOT/'experiments/mc_rc_011_013_label_grid'
DATA=ROOT/'data/mc_rc_011_013_label_grid'
SELECTION=ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json'
PLAN=ROOT/'MC_RC_011_013_HEADER_AND_LABEL_PLAN_2026-10-03.md'
PREFIX='VS-MC-RC-Segmentations_with_pathname_spreadsheet-Release2023/VS-MC-RC segmentations-NIfTI-Release 2023/'
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();selected=read(SELECTION);h=read(HEADERS/'attempt_01.json')
    expected={x['series_uid'] for x in selected['next_nonpixel_qualification_series']}
    assert h['complete'] and not h['errors'] and len(expected)==5 and len(h['series'])==5
    assert {x['source']['SeriesInstanceUID'] for x in h['series']}==expected
    csvpath=PRIOR/'official_label_metadata_00_attempt_01.csv';artifact=ROOT/'experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json'
    with csvpath.open(encoding='utf-8-sig',newline='') as s:cells=list(csv.reader(s))
    a=read(artifact);assert cells==a['values'] and sha(csvpath)==a['source_sha256']
    mapping={x['series_instance_uid']:x for x in (dict(zip(cells[0],row)) for row in cells[1:])};assert len(mapping)==len(cells)-1
    prior=read(PRIOR/'attempt_01.json');zp=ROOT/prior['labels']['transfer']['file'];assert sha(zp)==prior['labels']['transfer']['sha256']
    OUT.mkdir(exist_ok=False);DATA.mkdir(exist_ok=False)
    paths=[Path(__file__),PLAN,SELECTION,HEADERS/'attempt_01.json',PRIOR/'attempt_01.json',csvpath,artifact,zp,ROOT/'experiments/audit_mc_rc_three_patient_label_grid.py',ROOT/'experiments/vs_seg_task_cpu_support.py']
    for x in h['series']:paths.append(HEADERS/x['header_file'])
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
           complete=False,errors=[],series=[],scope='Fixed five official labels and header/native-grid preflight; no MR array or model effects',
           MR_pixel_arrays_decoded=False,label_arrays_decoded=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False,
           max_zip_member_bytes=50_000_000,max_total_zip_member_bytes=150_000_000,max_label_nominal_bytes=400_000_000,max_total_nominal_bytes=2_000_000_000,max_block_bytes=32_000_000)
    write(OUT/'attempt_01.json',r);totalzip=0;totalnominal=0
    try:
        with zipfile.ZipFile(zp) as archive:
            for row in h['series']:
                resource_gate();src=row['source'];uid=src['SeriesInstanceUID'];m=mapping[uid]
                assert m['patient_id']==src['PatientID'] and m['study_instance_uid']==src['StudyInstanceUID'] and int(m['num_files'])==src['ImageCount'] and m['SegmentationPath']
                member=archive.getinfo(PREFIX+m['SegmentationPath']);assert member.file_size<=50_000_000 and totalzip+member.file_size<=150_000_000
                payload=archive.read(member);totalzip+=len(payload);dest=DATA/(src['PatientID']+'_'+uid+'_label_attempt_01.nii.gz')
                with dest.open('xb') as stream:stream.write(payload)
                img=nib.load(dest);assert len(img.shape)==3
                width=max(np.dtype(img.get_data_dtype()).itemsize,8 if img.dataobj.slope!=1 or img.dataobj.inter!=0 else 1);nominal=math.prod(img.shape)*width;totalnominal+=nominal
                assert nominal<=400_000_000 and totalnominal<=2_000_000_000
                step=min(img.shape[2],32_000_000//(img.shape[0]*img.shape[1]*width));assert step>=1
                foreground=0;values=set();actual=0
                for start in range(0,img.shape[2],step):
                    block=np.asanyarray(img.dataobj[:,:,start:min(start+step,img.shape[2])]);assert block.nbytes<=32_000_000 and np.isfinite(block).all()
                    foreground+=int(np.count_nonzero(block));values.update(np.unique(block).tolist());actual+=block.nbytes;assert len(values)<=32
                assert actual<=nominal
                qc,sc=int(img.header['qform_code']),int(img.header['sform_code']);q,s=img.get_qform(),img.get_sform();assert np.isfinite(img.affine).all() and np.isfinite(q).all() and np.isfinite(s).all()
                formerror=float(np.linalg.norm(((q-s)@corners(img.shape))[:3],axis=0).max()) if qc>0 and sc>0 else None
                consistent=formerror is None or formerror<=.05;summary=row['summary']
                grid=best_grid_transform([summary['rows'],summary['columns'],summary['planes']],np.array(summary['affine_rcz_ras']),img.shape,img.affine) if 'affine_rcz_ras' in summary else dict(same_native_grid=False,reason='Native affine pending')
                binary=values<={0,1};passed=bool(summary['header_qualified_candidate'] and grid['same_native_grid'] and binary and foreground>0 and consistent and (qc>0 or sc>0))
                entry=dict(patient=src['PatientID'],series_uid=uid,study_uid=src['StudyInstanceUID'],description=src['SeriesDescription'],
                           header_file=row['header_file'],header_sha256=row['header_sha256'],header_qualified_candidate=summary['header_qualified_candidate'],
                           header_qualification_fail_reasons=summary['qualification_fail_reasons'],label_file=dest.relative_to(ROOT).as_posix(),label_sha256=sha(dest),
                           label_zip_member=member.filename,label_member_bytes=member.file_size,zip_crc32=f'{member.CRC:08x}',label_inspection_complete=True,
                           label_shape=list(img.shape),label_dtype=str(img.get_data_dtype()),label_array_bytes=actual,label_nominal_bytes=nominal,
                           label_values=sorted(values),label_is_binary=binary,label_foreground_voxels=foreground,label_affine_xyz_ras=img.affine.tolist(),
                           qform_code=qc,sform_code=sc,qform=q.tolist(),sform=s.tolist(),max_qform_sform_corner_difference_mm=formerror,forms_consistent=consistent,
                           grid=grid,header_and_label_grid_preflight_passed=passed)
                r['series'].append(entry);r['label_arrays_decoded']=True;write(OUT/'attempt_01.json',r)
                print(json.dumps({k:entry[k] for k in ('patient','description','header_qualified_candidate','label_foreground_voxels','header_and_label_grid_preflight_passed')}),flush=True)
        r.update(complete=len(r['series'])==5,source_preflight_series_passed=sum(x['header_and_label_grid_preflight_passed'] for x in r['series']),
                 source_preflight_patient_ids=sorted({x['patient'] for x in r['series'] if x['header_and_label_grid_preflight_passed']}),label_zip_member_bytes=totalzip,label_nominal_total_bytes=totalnominal)
    except Exception as exc:r['errors'].append(type(exc).__name__+': '+str(exc));r['traceback']=traceback.format_exc()
    r['finished_utc']=datetime.now(timezone.utc).isoformat();write(OUT/'attempt_01.json',r);print(json.dumps({k:r.get(k) for k in ('complete','errors','source_preflight_series_passed','source_preflight_patient_ids','label_zip_member_bytes')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
