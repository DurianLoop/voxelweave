"""Five fixed public MR archives, bounded sequential transfers, header reads only."""
import os,sys,json,math,urllib.parse
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'experiments'))
from vs_seg_task_cpu_support import resource_gate
from mc_rc_native_header_geometry_v2 import geometry
import download_mc_rc_004_006_native_headers_2026_10_02 as bounded
import download_mc_rc_three_patient_headers_2026_10_02 as header
os.environ['CUDA_VISIBLE_DEVICES']='-1'
OUT=ROOT/'literature/source_cache/mc_rc_011_013_headers_2026-10-03'
DATA=ROOT/'data/mc_rc_011_013_header_gate'
SELECTION=ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json'
PLAN=ROOT/'MC_RC_011_013_HEADER_AND_LABEL_PLAN_2026-10-03.md'
read,write,sha,now=header.read,header.write,header.sha,header.now
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();selected=read(SELECTION)
    assert selected['next_nonpixel_qualification_patient_ids']==['VS-MC-RC-011','VS-MC-RC-012','VS-MC-RC-013']
    assert len(selected['next_nonpixel_qualification_series'])==5 and selected['next_api_images']==230
    api=read(ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response');byuid={x['SeriesInstanceUID']:x for x in api}
    sources=sorted([byuid[x['series_uid']] for x in selected['next_nonpixel_qualification_series']],key=lambda x:(x['PatientID'],x['StudyDate'],x['SeriesInstanceUID']))
    OUT.mkdir(exist_ok=False);DATA.mkdir(exist_ok=False)
    bounded.OUT,bounded.DATA,bounded.TOTAL_CAP,bounded.budget_used=OUT,DATA,150_000_000,0
    header.OUT,header.DATA,header.geometry=OUT,DATA,geometry
    r=dict(attempt=1,created_utc=now(),script_sha256=sha(__file__),plan_sha256=sha(PLAN),selection_sha256=sha(SELECTION),
           helper_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (Path(header.__file__),Path(bounded.__file__),ROOT/'experiments/mc_rc_native_header_geometry_v2.py',ROOT/'experiments/vs_seg_task_cpu_support.py')],
           resources=resources,total_cap_bytes=150_000_000,max_connections=1,socket_timeout_seconds=30,series_deadline_seconds=180,automatic_retries=0,
           scope='Whole public MR ZIP transfer includes pixel bytes; classic DICOM header arrays only',MR_pixel_array_decoded=False,label_arrays_decoded=False,
           patient_performance_statistics_computed=False,complete=False,active_stage='fixed_five_header_transfers',series=[],errors=[],
           new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    path=OUT/'attempt_01.json';write(path,r)
    for source in sources:
        resource_gate();uid=source['SeriesInstanceUID'];cap=max(5_000_000,math.ceil(1.15*source['FileSize'])+1_000_000)
        transfer=bounded.download(source['PatientID']+'_'+uid,header.BASE+urllib.parse.urlencode({'SeriesInstanceUID':uid}),cap,1)
        row=header.inspect_series(transfer,source,1);r['series'].append(row);r['total_transfer_bytes']=bounded.budget_used
        if not row['headers_complete']:r['errors'].append(row.get('header_error',transfer.get('error','Unknown header failure')));r['active_stage']='failed_stop'
        write(path,r);print(json.dumps(dict(patient=source['PatientID'],uid=uid,headers_complete=row['headers_complete'],header_qualified_candidate=row.get('summary',{}).get('header_qualified_candidate'),completed_series=len(r['series']),error=row.get('header_error',transfer.get('error')))),flush=True)
        if r['errors']:break
    r.update(complete=len(r['series'])==5 and not r['errors'],finished_utc=now(),header_qualified_series=sum(x.get('summary',{}).get('header_qualified_candidate',False) for x in r['series']),total_transfer_bytes=bounded.budget_used)
    if r['complete']:r['active_stage']='complete'
    write(path,r);print(json.dumps({k:r[k] for k in ('complete','active_stage','errors','header_qualified_series','total_transfer_bytes')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
