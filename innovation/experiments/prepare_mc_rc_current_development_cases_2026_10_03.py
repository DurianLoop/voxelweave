"""Correct stale source eligibility and assemble current19 developer cases, no pixel reads."""
import csv,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_current_development_input_preparation'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    rp=ROOT/'experiments/mc_rc_predeclared_patient_allocation/attempt_01.json';roles=read(rp)
    cp=ROOT/'experiments/mc_rc_source_denominator_correction/attempt_01.json';current=read(cp)
    assert current['complete'] and not current['errors'] and current['counts']['qualified_series']==16
    native=read(ROOT/'experiments/mc_rc_native_competence_cpu/run_contract.json');assert {x['uid'] for x in native['cases']}=={x['uid'] for x in current['cases']}
    proofs=['experiments/mc_rc_native_t2_label_gate/independent_raw_geometry_grid_verification.json','experiments/mc_rc_004_006_native_label_gate/independent_raw_geometry_grid_verification.json','experiments/mc_rc_007_010_native_label_gate/independent_raw_geometry_grid_verification.json']
    verified={}
    for p in proofs:
        q=read(ROOT/p);assert not q['errors']
        for x in q['series']:verified[x['uid']]=x
    assert all(verified[x['uid']]['source_preflight_passed'] for x in current['cases'])
    development=set(roles['development_training_candidate_patient_ids']);assert len(development)==11
    cases=[dict(x) for x in current['cases']]
    hs=ROOT/'literature/source_cache/mc_rc_011_013_headers_2026-10-03';h=read(hs/'attempt_01.json');labpath=ROOT/'experiments/mc_rc_011_013_label_grid/attempt_01.json';lab=read(labpath)
    byuid={x['source']['SeriesInstanceUID']:x for x in h['series']}
    for x in lab['series']:
        if not x['header_and_label_grid_preflight_passed']:continue
        y=byuid[x['series_uid']];g=y['summary'];s=y['source']
        cases.append(dict(patient=x['patient'],uid=x['series_uid'],description=x['description'],study_uid=x['study_uid'],native_shape=[g['rows'],g['columns'],g['planes']],native_spacing_rcz_mm=g['native_spacing_rcz_mm'],affine_rcz_ras=g['affine_rcz_ras'],ordered_zip_members=g['ordered_zip_members'],header_file=(hs/y['header_file']).relative_to(ROOT).as_posix(),header_sha256=y['header_sha256'],mr_zip_file=y['transfer']['file'],mr_zip_sha256=y['transfer']['sha256'],label_file=x['label_file'],label_sha256=x['label_sha256'],dicom_rcz_from_label_xyz=x['grid']['dicom_rcz_from_label_xyz'],expected_label_foreground_voxels=x['label_foreground_voxels'],source_result=labpath.relative_to(ROOT).as_posix()))
    cases.sort(key=lambda x:(x['patient'],x['uid']));assert len(cases)==19 and {x['patient'] for x in cases}==development
    with (ROOT/roles['csv_file']).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    before=[dict(x) for x in rows];case_by={x['uid']:x for x in cases};changes=[]
    for x in rows:
        if x['series_uid'] in case_by:
            c=case_by[x['series_uid']];assert c['patient']==x['patient'] and x['patient_role']=='development_training_candidate'
            status='source_qualified_current_development_no_new_model_outcomes'
            if not x['source_status'].startswith('source_qualified'):changes.append(dict(patient=x['patient'],series_uid=x['series_uid'],old_status=x['source_status'],corrected_status=status,source_result=c['source_result']))
            x['source_status']=status;x['source_result']=c['source_result']
    assert len(changes)==1 and changes[0]['series_uid']=='1.3.6.1.4.1.14519.5.2.1.213711595575218613093188251544325434833'
    counts={role:dict(patients=len({x['patient'] for x in rows if x['patient_role']==role}),series=sum(x['patient_role']==role for x in rows),qualified_series=sum(x['patient_role']==role and x['source_status'].startswith('source_qualified') for x in rows)) for role in roles['counts']}
    assert sum(x['qualified_series'] for x in counts.values())==40 and counts['development_training_candidate']['qualified_series']==19
    csvpath=OUT/'all159_current_patient_roles.csv'
    with csvpath.open('x',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    paths=[Path(__file__),ROOT/'MC_RC_DEVELOPMENT_INPUT_CPU_PLAN_2026-10-03.md',rp,ROOT/roles['csv_file'],cp,ROOT/'experiments/mc_rc_native_competence_cpu/run_contract.json',labpath,hs/'attempt_01.json']+[ROOT/x for x in proofs]
    for c in cases:
        assert sha(ROOT/c['header_file'])==c['header_sha256'] and sha(ROOT/c['mr_zip_file'])==c['mr_zip_sha256'] and sha(ROOT/c['label_file'])==c['label_sha256']
        paths.extend(ROOT/c[k] for k in ('header_file','mr_zip_file','label_file'))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),cases=cases,source_changes=changes,counts=counts,csv_file=csvpath.relative_to(ROOT).as_posix(),csv_sha256=sha(csvpath),
                source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in sorted(set(paths))],
                patient_roles_unchanged=True,qualification_updated_from_authoritative_current_proofs=True,final_scientific_split_activated=False,MR_pixels_decoded=False,new_neural_forwards=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    write(OUT/'attempt_01.json',result);print(json.dumps(dict(cases=len(cases),patients=len(development),source_changes=changes,counts=counts),ensure_ascii=False))
if __name__=='__main__':main()
