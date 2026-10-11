"""Assemble fixed 4/9 validation source contract before new outcome evaluation."""
import json,sys,csv
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_task_roles_input_cpu import ROOT,read,sha,VALIDATORS
OUT=ROOT/'experiments/mc_rc_validation_task_case_preparation'
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);headerdir=ROOT/'literature/source_cache/mc_rc_next12_headers_2026-10-03';hp=headerdir/'attempt_01.json';lp=ROOT/'experiments/mc_rc_next12_label_grid/attempt_01.json';qp=lp.parent/'independent_all1475_headers_and_25_labels_attempt_01.json';rolesp=ROOT/'experiments/mc_rc_predeclared_patient_allocation/attempt_01.json';currentp=ROOT/'experiments/mc_rc_current_development_input_preparation/attempt_01.json';h,labels,proof,roles,current=map(read,(hp,lp,qp,rolesp,currentp));assert all(x['complete'] and not x['errors'] for x in (h,labels,proof,current));assert set(roles['validation_candidate_patient_ids'])==VALIDATORS;by={x['source']['SeriesInstanceUID']:x for x in h['series']};cases=[]
    for x in labels['series']:
        if x['patient'] not in VALIDATORS:continue
        assert x['header_and_label_grid_preflight_passed'];y=by[x['series_uid']];g=y['summary'];cases.append(dict(patient=x['patient'],uid=x['series_uid'],description=x['description'],study_uid=x['study_uid'],native_shape=[g['rows'],g['columns'],g['planes']],native_spacing_rcz_mm=g['native_spacing_rcz_mm'],affine_rcz_ras=g['affine_rcz_ras'],ordered_zip_members=g['ordered_zip_members'],header_file=(headerdir/y['header_file']).relative_to(ROOT).as_posix(),header_sha256=y['header_sha256'],mr_zip_file=y['transfer']['file'],mr_zip_sha256=y['transfer']['sha256'],label_file=x['label_file'],label_sha256=x['label_sha256'],dicom_rcz_from_label_xyz=x['grid']['dicom_rcz_from_label_xyz'],expected_label_foreground_voxels=x['label_foreground_voxels'],source_result=lp.relative_to(ROOT).as_posix(),role='validation_candidate'))
    cases.sort(key=lambda c:(c['patient'],c['uid']));assert len(cases)==9 and {c['patient'] for c in cases}==VALIDATORS;assert not VALIDATORS&set(roles['confirmation_reserved_candidate_patient_ids'])
    with (ROOT/current['csv_file']).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    for c in cases:
        row=next(x for x in rows if x['series_uid']==c['uid']);assert row['patient']==c['patient'] and row['patient_role']=='validation_candidate' and row['source_status'].startswith('source_qualified');assert all(sha(ROOT/c[k])==c[k.replace('_file','_sha256')] for k in ('header_file','mr_zip_file','label_file'))
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),cases=cases,validation_patient_ids=sorted(VALIDATORS),validation_series=9,selection_used_new_outcomes=False,source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in (hp,lp,qp,rolesp,currentp,ROOT/current['csv_file'])],MR_pixel_arrays_decoded=False,new_neural_forwards=0,final_scientific_split_activated=False,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    (OUT/'attempt_01.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(validation_patients=4,validation_series=9,complete=True)))
if __name__=='__main__':main()
