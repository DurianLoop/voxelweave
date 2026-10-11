"""Only the 28 already-opened series: official CSV, label path and two DICOM headers."""
import csv,json,sys,time,zipfile,traceback,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
import pydicom
import hashlib
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
def iso_short(s):
    m,d,y=map(int,s.split('/'));return f'{1900+y if y>=70 else 2000+y:04d}-{m:02d}-{d:02d}'
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();dest=HERE/'ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT.json'
    assert not dest.exists();r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],series=[],
        medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    try:
        resources=resource_guard();sources=[Path(__file__)];cases=[]
        for role,n,count in [('development','mc_rc_current_development_input_preparation',19),('validation','mc_rc_validation_task_case_preparation',9)]:
            p=ROOT/'experiments'/n/'attempt_01.json';q=read(p);assert q['complete'] and not q['errors'] and len(q['cases'])==count
            sources.append(p);cases.extend((role,c) for c in q['cases'])
        allowed={c['uid'] for _,c in cases};assert len(allowed)==28
        csvpath=ROOT/'literature/source_cache/mc_rc_three_patient_headers_2026-10-02/official_label_metadata_00_attempt_01.csv'
        artifact=ROOT/'experiments/mc_rc_native_t2_label_gate/official_pathnames_artifact_read.json'
        assert sha(csvpath)==read(artifact)['source_sha256']=='f9d8d2b2ecab74824d02c95fdccd42f60c82f5e17746b830e3c67f73f9a372eb'
        with csvpath.open(encoding='utf-8-sig',newline='') as f:rows=[x for x in csv.DictReader(f) if x['series_instance_uid'] in allowed]
        assert len(rows)==28;mapping={x['series_instance_uid']:x for x in rows};assert len(mapping)==28;sources.extend([csvpath,artifact])
        auditpath=HERE/'PHYSICAL_VOLUME_METADATA_AUDIT.json';audit=read(auditpath);sources.append(auditpath)
        volumes={s['uid']:s for s in audit['series']};assert set(volumes)==allowed
        cache={}
        tags=['PatientID','StudyInstanceUID','SeriesInstanceUID','SOPInstanceUID','StudyDate','SeriesDate',
            'AcquisitionDate','StudyDescription','SeriesDescription','Modality','Rows','Columns']
        for role,c in cases:
            assert time.perf_counter()-started<300;resource_guard();uid=c['uid'];m=mapping[uid]
            assert m['patient_id']==c['patient'] and m['study_instance_uid']==c['study_uid'] and int(m['num_files'])==c['native_shape'][2]
            resultpath=ROOT/c['source_result'];sources.append(resultpath)
            if str(resultpath) not in cache:
                q=read(resultpath);cache[str(resultpath)]=[s for s in q['series'] if s.get('series_uid') in allowed]
            s=next(s for s in cache[str(resultpath)] if s['series_uid']==uid)
            assert s['label_file']==c['label_file'] and s['label_sha256']==c['label_sha256']
            assert s['label_zip_member'].endswith('/'+m['SegmentationPath']) and s['grid']['same_native_grid']
            labeldate=m['SegmentationPath'].split('/')[-2];csvdate=iso_short(m['study_date']);assert csvdate==labeldate
            zp=ROOT/c['mr_zip_file'];hp=ROOT/c['header_file'];assert sha(zp)==c['mr_zip_sha256'] and sha(hp)==c['header_sha256'];sources.extend([zp,hp])
            hd=read(hp);hby={h['zip_member']:h for h in hd['records']};headers=[]
            members=[c['ordered_zip_members'][0],c['ordered_zip_members'][-1]]
            with zipfile.ZipFile(zp) as z:
                for member in members:
                    with z.open(member) as stream:d=pydicom.dcmread(stream,stop_before_pixels=True,specific_tags=tags)
                    assert str(d.PatientID)==c['patient'] and str(d.StudyInstanceUID)==c['study_uid'] and str(d.SeriesInstanceUID)==uid
                    assert str(d.SOPInstanceUID)==hby[member]['sop_uid'] and str(d.Modality)=='MR'
                    assert 'PixelData' not in d
                    date=str(d.get('StudyDate',''));assert date==labeldate.replace('-','')
                    headers.append(dict(zip_member=member,study_date=date,series_date=str(d.get('SeriesDate','')),
                        acquisition_date=str(d.get('AcquisitionDate','')),study_description=str(d.get('StudyDescription','')),
                        series_description=str(d.get('SeriesDescription','')),PixelData_present=False))
            r['series'].append(dict(role=role,patient=c['patient'],uid=uid,study_uid=c['study_uid'],
                official_study_date=csvdate,official_series_date=iso_short(m['series_date']),
                official_study_description=m['study_description'],description=c['description'],
                label_zip_member=s['label_zip_member'],label_path_date=labeldate,official_patient_UID_path_link_verified=True,
                native_grid_corner_max_error_mm=s['grid']['max_corner_world_error_mm'],
                GT_volume_ml=volumes[uid]['label_volume_ml'],dicom_headers=headers))
        groups=[]
        for patient in sorted({s['patient'] for s in r['series']}):
            rr=sorted([s for s in r['series'] if s['patient']==patient],key=lambda s:s['official_study_date'])
            groups.append(dict(patient=patient,role=rr[0]['role'],series=len(rr),distinct_studies=len({s['study_uid'] for s in rr}),
                distinct_dates=len({s['official_study_date'] for s in rr}),timepoints=[dict(uid=s['uid'],date=s['official_study_date'],
                    study_description=s['official_study_description'],volume_ml=s['GT_volume_ml']) for s in rr],
                max_to_min_volume_ratio=max(s['GT_volume_ml'] for s in rr)/min(s['GT_volume_ml'] for s in rr)))
        r.update(complete=True,patients=groups,allowed_series_count=28,headers_read=56,
            source_bindings=[entry(p) for p in sorted(set(sources))],resources_before=resources,resources_after=resource_guard(),
            all_official_CSV_label_path_and_first_last_DICOM_dates_match=True,
            distinct_timepoints_do_not_identify_treatment_or_prove_label_correctness=True,
            same_patient_series_not_qualified_as_same_time_repeatability_pairs=True)
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    with dest.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=r['complete'],errors=r['errors'],headers_read=r.get('headers_read'),
        key_patients=[p for p in r.get('patients',[]) if p['patient'] in ['VS-MC-RC-010','VS-MC-RC-022','VS-MC-RC-025']],
        elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
