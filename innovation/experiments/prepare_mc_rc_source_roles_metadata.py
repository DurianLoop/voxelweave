"""Prepare exact-UID source-role queue from stored public metadata; no patient arrays."""
import csv,hashlib,io,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_source_roles_metadata_preparation'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    src=ROOT/'literature/source_cache/mc_rc_v2_identity_2026-10-02';identity=read(src/'attempt_01.json')
    paths=[Path(__file__),ROOT/'MC_RC_SOURCE_ROLE_METADATA_PREPARATION_PLAN_2026-10-03.md',src/'attempt_01.json']
    for e in identity['responses']:
        p=src/e['raw_file'];assert sha(p)==e['raw_sha256'];paths.append(p)
    prepfile=ROOT/'experiments/mc_rc_native_t2_label_gate/labelled_native_expansion_preparation.json';prep=read(prepfile);paths.append(prepfile)
    devfile=ROOT/'experiments/mc_rc_native_competence_cpu/attempt_01.json';dev=read(devfile);assert dev['complete'] and not dev['errors'];paths.append(devfile)
    api=read(src/'series_attempt_01.response');assert sha(src/'series_attempt_01.response')==prep['api_sha256']
    byuid={x['SeriesInstanceUID']:x for x in api};assert len(byuid)==len(api)
    shared=sorted({x['PatientID'] for x in api if x['PatientID'].startswith('VS-SEG-')})
    overlap=list(csv.DictReader(io.StringIO((src/'overlap_attempt_01.response').read_text(encoding='utf-8'))))
    assert {x['Patient ID'] for x in overlap}<=set(shared)
    known=sorted({x['patient'] for x in dev['patients']});assert len(known)==8
    candidates=prep['candidate_series'];patients=sorted({x['patient'] for x in candidates})
    assert len(candidates)==159 and len(patients)==71 and patients==prep['candidate_patients']
    assert len({x['uid'] for x in candidates})==159 and not set(patients)&set(shared)
    rows=[]
    for x in candidates:
        a=byuid[x['uid']];assert a['PatientID']==x['patient'] and a['StudyInstanceUID']==x['study']
        assert x['availability']=='available' and x['segmentation_path'].startswith(x['patient']+'/')
        rows.append(dict(patient=x['patient'],study_uid=x['study'],series_uid=x['uid'],description=x['description'],
                         segmentation_path=x['segmentation_path'],api_image_count=int(a['ImageCount']),api_file_size_bytes=int(a['FileSize']),
                         source_role='already_seen_development_only' if x['patient'] in known else 'catalogue_candidate_not_yet_qualified'))
    unseen_candidates=sorted(set(patients)-set(known));nextpatients=unseen_candidates[:3];nextrows=[x for x in rows if x['patient'] in nextpatients]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),status='metadata_prepared_not_source_qualified_not_split_frozen',
                complete=True,errors=[],source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
                api_series=len(api),api_shared_vs_seg_patients_excluded=len(shared),api_shared_patient_ids=shared,
                overlap_csv_series=len(overlap),catalogue_candidate_patients=len(patients),catalogue_candidate_series=len(rows),
                already_seen_development_patients=known,already_seen_development_series=sum(x['source_role']=='already_seen_development_only' for x in rows),
                remaining_catalogue_candidate_patient_ids=unseen_candidates,remaining_catalogue_candidate_patients=len(unseen_candidates),
                remaining_catalogue_candidate_series=sum(x['source_role']=='catalogue_candidate_not_yet_qualified' for x in rows),
                next_nonpixel_qualification_patient_ids=nextpatients,next_nonpixel_qualification_series=nextrows,
                next_api_images=sum(x['api_image_count'] for x in nextrows),next_api_file_size_bytes=sum(x['api_file_size_bytes'] for x in nextrows),
                next_selection_rule='First three lexically sorted catalogue candidate patients after entire known-eight patient exclusion; all candidate series',
                complete_project_exposure_crosswalk_proven=False,mr_pixels_decoded=False,new_label_arrays_decoded=False,network_requests=0,
                new_neural_forwards=0,gpu_jobs_started=0,qualified_scientific_confirmation_patients=0,publication_claim_confirmed=False)
    csvpath=OUT/'all159_exact_uid_roles.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result.update(csv_file=csvpath.relative_to(ROOT).as_posix(),csv_sha256=sha(csvpath))
    (OUT/'attempt_01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_bindings','api_shared_patient_ids','remaining_catalogue_candidate_patient_ids','next_nonpixel_qualification_series')},ensure_ascii=False))
if __name__=='__main__':main()
