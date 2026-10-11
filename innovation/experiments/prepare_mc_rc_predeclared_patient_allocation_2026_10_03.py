"""Prepare all159 exact-UID roles before outcomes; activation remains explicitly pending."""
import csv,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'experiments/mc_rc_predeclared_patient_allocation'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    prior=ROOT/'experiments/mc_rc_source_roles_metadata_preparation/attempt_01.json';p=read(prior)
    auditp=ROOT/'experiments/mc_rc_local_identity_audit/attempt_02.json';audit=read(auditp)
    streamp=ROOT/'experiments/mc_rc_local_identity_audit/gap_stream_attempt_01.json';stream=read(streamp)
    assert audit['complete'] and stream['complete'] and not audit['errors'] and not stream['errors']
    assert all(not x['patients'] for x in stream['streamed_texts'])
    reviewed={
      'innovation/MC_RC_011_013_SOURCE_PREFLIGHT_RESULT_2026-10-03.md':'Source qualification report: MR headers/label grids only; zero task model outcomes',
      'innovation/experiments/mc_rc_v2_nonpixel_identity/patient_roster_attempt_01.csv':'API identity and acquisition-description counts; not model predictions',
      'innovation/experiments/mc_rc_v2_nonpixel_identity/attempt_01.json':'Nonpixel identity/version crosswalk; its first incomplete attempt retained, zero model outcomes'
    }
    assert set(reviewed)=={x['path'] for x in audit['focused_requires_review']}
    known=p['already_seen_development_patients'];newtrain=['VS-MC-RC-011','VS-MC-RC-012','VS-MC-RC-013']
    h=read(ROOT/'literature/source_cache/mc_rc_next12_headers_2026-10-03/attempt_01.json');next12=h['patient_roster']
    salt='MRI-MCRC-adaptation-v1|';order=sorted(next12,key=lambda x:hashlib.sha256((salt+x).encode()).hexdigest());validation=order[:4];confirmation=order[4:]
    assert len(known)==8 and len(validation)==4 and len(confirmation)==8 and not set(known+newtrain)&set(next12)
    labels=read(ROOT/'experiments/mc_rc_label_anchor_visibility/attempt_01.json');assert labels['complete'] and len(labels['series'])==15
    qualified={x['uid']:dict(patient=x['patient'],status='source_qualified_in_prior_development',source_result=x['source_result']) for x in labels['series']}
    rejected={x['uid']:dict(patient=x['patient'],status='source_rejected_in_prior_preflight',source_result=x['source_result']) for x in labels['excluded_sources']}
    for folder in ('mc_rc_011_013_label_grid','mc_rc_next12_label_grid'):
        path=ROOT/'experiments'/folder/'attempt_01.json';src=read(path);assert src['complete'] and not src['errors']
        for x in src['series']:
            q=dict(patient=x['patient'],status='source_qualified_new_no_model_outcomes' if x['header_and_label_grid_preflight_passed'] else 'source_rejected_new_preflight',source_result=path.relative_to(ROOT).as_posix())
            (qualified if x['header_and_label_grid_preflight_passed'] else rejected)[x['series_uid']]=q
    rows=[]
    with (ROOT/p['csv_file']).open(encoding='utf-8',newline='') as f:base=list(csv.DictReader(f))
    for row in base:
        patient=row['patient'];uid=row['series_uid']
        role='development_training_candidate' if patient in known+newtrain else 'validation_candidate' if patient in validation else 'confirmation_reserved_candidate' if patient in confirmation else 'not_allocated_catalogue_candidate'
        qc=qualified.get(uid,rejected.get(uid,dict(patient=patient,status='not_source_preflighted',source_result='')));assert qc['patient']==patient
        rows.append(dict(patient=patient,study_uid=row['study_uid'],series_uid=uid,description=row['description'],patient_role=role,source_status=qc['status'],source_result=qc['source_result'],training_queue_active=False,scientific_confirmation_effect_computed=False))
    counts={role:dict(patients=len({x['patient'] for x in rows if x['patient_role']==role}),series=sum(x['patient_role']==role for x in rows),qualified_series=sum(x['patient_role']==role and x['series_uid'] in qualified for x in rows)) for role in sorted({x['patient_role'] for x in rows})}
    cp=OUT/'all159_predeclared_patient_roles.csv'
    with cp.open('x',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    reviews=[dict(path=x['path'],sha256=x['content_sha256'],classification_after_review='source_or_identity_metadata_not_model_effect',rationale=reviewed[x['path']]) for x in audit['focused_requires_review']]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),status='allocation_predeclared_provisional_training_inactive_not_clean_split_proof',
           source_bindings=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in (prior,auditp,streamp,ROOT/'MC_RC_LOCAL_IDENTITY_AUDIT_PLAN_2026-10-03.md',ROOT/'MC_RC_IDENTITY_GAP_STREAM_ADDENDUM_2026-10-03.md')],
           allocation_rule='Old eight plus fixed011/012/013 development; fixednext12 sorted by SHA256(salt+exact PatientID), first4 validation, remaining8 reserved confirmation',hash_salt=salt,hashed_order=[dict(patient=x,hash=hashlib.sha256((salt+x).encode()).hexdigest()) for x in order],
           development_training_candidate_patient_ids=sorted(known+newtrain),validation_candidate_patient_ids=validation,confirmation_reserved_candidate_patient_ids=confirmation,counts=counts,manual_reviews=reviews,
           shared_vs_seg_patient_ids_excluded=p['api_shared_patient_ids'],patient_all_times_same_role=True,selection_used_outcomes=False,
           local_documented_new15_model_outcome_exposure_found=False,local_evidence_scope='503812 file names,23432 whole text files plus14 streaming CSV gaps; explicit binary/excluded/unknown-alias limitations',
           external_pretraining_identity_verified=False,cross_dataset_identity_linkage_proven=False,complete_project_exposure_crosswalk_proven=False,final_scientific_split_activated=False,
           task_model_policy='Train from scratch, or use only a fully verified patient training roster; MC-RC/mixed author models cannot serve as unseen confirmation evaluators',
           activation_pending=['Verify complete model initialization/training identity and cross-source identity policy','Implement and audit actual sparse input/augmentation/labels without hidden-reference conditioning','Freeze task competence criterion,optimizer,threshold,checkpoint rule and equal budgets','GPU availability without interference with current user training','Use confirmation only after method and thresholds fixed; no selecting favorable patients'],
           csv_file=cp.relative_to(ROOT).as_posix(),csv_sha256=sha(cp),complete=True,errors=[],new_neural_forwards=0,gpu_jobs_started=0,scientific_confirmation_patients=0,publication_claim_confirmed=False)
    (OUT/'attempt_01.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('status','development_training_candidate_patient_ids','validation_candidate_patient_ids','confirmation_reserved_candidate_patient_ids','counts')},ensure_ascii=False))
if __name__=='__main__':main()
