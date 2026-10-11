"""Fixed12 patients/all25 candidate series, sequential bounded public header acquisition."""
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
OUT=ROOT/'literature/source_cache/mc_rc_next12_headers_2026-10-03';DATA=ROOT/'data/mc_rc_next12_header_gate'
PLAN=ROOT/'MC_RC_NEXT12_IDENTITY_SOURCE_PLAN_2026-10-03.md';read,write,sha,now=header.read,header.write,header.sha,header.now
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=resource_gate();prep=read(ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json')
    remaining=[p for p in prep['remaining_catalogue_candidate_patient_ids'] if p not in ['VS-MC-RC-011','VS-MC-RC-012','VS-MC-RC-013']];patients=remaining[:12]
    assert patients==['VS-MC-RC-015','VS-MC-RC-019','VS-MC-RC-020','VS-MC-RC-022','VS-MC-RC-024','VS-MC-RC-025','VS-MC-RC-026','VS-MC-RC-027','VS-MC-RC-028','VS-MC-RC-029','VS-MC-RC-030','VS-MC-RC-031']
    candidates=read(ROOT/'experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json')['candidate_series'];api=read(ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response');byuid={x['SeriesInstanceUID']:x for x in api}
    sources=sorted([byuid[x['uid']] for x in candidates if x['patient'] in patients],key=lambda x:(x['PatientID'],x['StudyDate'],x['SeriesInstanceUID']))
    assert len(sources)==25 and sum(x['ImageCount'] for x in sources)==1475 and sum(x['FileSize'] for x in sources)==615515656
    OUT.mkdir(exist_ok=False);DATA.mkdir(exist_ok=False);bounded.OUT,bounded.DATA,bounded.TOTAL_CAP,bounded.budget_used=OUT,DATA,800_000_000,0;header.OUT,header.DATA,header.geometry=OUT,DATA,geometry
    bindings=[Path(__file__),PLAN,ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json',ROOT/'experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json',ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02/series_attempt_01.response',Path(bounded.__file__),Path(header.__file__),ROOT/'experiments/mc_rc_native_header_geometry_v2.py',ROOT/'experiments/vs_seg_task_cpu_support.py']
    r=dict(created_utc=now(),script_sha256=sha(__file__),source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in bindings],resources=resources,patient_roster=patients,expected_api_objects=1475,expected_series=25,expected_sources=sources,total_cap_bytes=800_000_000,max_connections=1,socket_timeout_seconds=30,series_deadline_seconds=180,automatic_retries=0,scope='Whole public MR ZIP transfer including pixel bytes; MR headers only; no model effects',MR_pixel_array_decoded=False,label_arrays_decoded=False,new_neural_forwards=0,gpu_used=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,complete=False,active_stage='fixed25_header_transfers',series=[],errors=[])
    path=OUT/'attempt_01.json';write(path,r)
    for src in sources:
        resource_gate();uid=src['SeriesInstanceUID'];cap=max(5_000_000,math.ceil(1.15*src['FileSize'])+1_000_000);transfer=bounded.download(src['PatientID']+'_'+uid,header.BASE+urllib.parse.urlencode({'SeriesInstanceUID':uid}),cap,1);row=header.inspect_series(transfer,src,1)
        r['series'].append(row);r['total_transfer_bytes']=bounded.budget_used
        if not row['headers_complete']:r['errors'].append(row.get('header_error',transfer.get('error','Unknown source failure')));r['active_stage']='failed_stop'
        write(path,r);print(json.dumps(dict(patient=src['PatientID'],description=src['SeriesDescription'],completed_series=len(r['series']),headers_complete=row['headers_complete'],header_qualified=row.get('summary',{}).get('header_qualified_candidate'),error=row.get('header_error',transfer.get('error')))),flush=True)
        if r['errors']:break
    r.update(complete=len(r['series'])==25 and not r['errors'],finished_utc=now(),header_qualified_series=sum(x.get('summary',{}).get('header_qualified_candidate',False) for x in r['series']),total_transfer_bytes=bounded.budget_used)
    if r['complete']:r['active_stage']='complete'
    write(path,r);print(json.dumps({k:r[k] for k in ('complete','active_stage','errors','header_qualified_series','total_transfer_bytes')}),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
