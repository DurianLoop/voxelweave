"""Descriptive temporal endpoint from already-scored counts; no new MRI/GT/model arrays."""
import json,sys,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sign(x):return int(x>0)-int(x<0)
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    ep=ROOT/'lossless_final_evaluation_entry_2026_10_08/medical_attempt03/evaluation_attempt01.json'
    tp=HERE/'ALLOWED_LABEL_TIMEPOINT_SOURCE_AUDIT_V2.json';vp=HERE/'PHYSICAL_VOLUME_METADATA_AUDIT.json'
    q=read(ep);t=read(tp);v=read(vp);assert all(x['complete'] and not x['errors'] for x in [q,t,v])
    by={s['uid']:s for s in v['series']};assert len(by)==28
    patients=[]
    for p in t['patients']:
        times=p['timepoints'];assert len(times)==p['series'];rr=[]
        for i in range(len(times)-1):
            a,b=times[i:i+2];assert a['date']<b['date'],'Same-date pairs not allowed in this temporal diagnostic'
            u,w=by[a['uid']],by[b['uid']];dg=w['label_volume_ml']-u['label_volume_ml'];arms={}
            for kind in ['native_reference','raw_pchip']:
                pa=u['model_metrics'][kind]['predicted_volume_ml'];pb=w['model_metrics'][kind]['predicted_volume_ml'];dp=pb-pa
                arms[kind]=dict(prediction_volume_earlier_ml=pa,prediction_volume_later_ml=pb,predicted_change_ml=dp,
                    label_change_ml=dg,absolute_change_error_ml=abs(dp-dg),label_direction=sign(dg),prediction_direction=sign(dp),
                    direction_disagrees=sign(dg)!=sign(dp),relative_change_not_computed_when_prediction_zero=pa==0)
            rr.append(dict(earlier_uid=a['uid'],later_uid=b['uid'],earlier_date=a['date'],later_date=b['date'],
                elapsed_deidentified_days=(datetime.fromisoformat(b['date'])-datetime.fromisoformat(a['date'])).days,
                ground_truth_volume_earlier_ml=u['label_volume_ml'],ground_truth_volume_later_ml=w['label_volume_ml'],arms=arms))
        patients.append(dict(patient=p['patient'],role=p['role'],adjacent_intervals=len(rr),intervals=rr))
    summary=[]
    for role in ['development','validation']:
        ps=[p for p in patients if p['role']==role and p['adjacent_intervals']>0]
        for kind in ['native_reference','raw_pchip']:
            per=[sum(s['arms'][kind]['direction_disagrees'] for s in p['intervals'])/len(p['intervals']) for p in ps]
            summary.append(dict(role=role,kind=kind,patients_with_intervals=len(ps),adjacent_intervals=sum(p['adjacent_intervals'] for p in ps),
                patients_with_any_direction_disagreement=sum(any(s['arms'][kind]['direction_disagrees'] for s in p['intervals']) for p in ps),
                patient_first_mean_direction_disagreement_fraction=sum(per)/len(per) if per else None,
                direction_disagreements=sum(s['arms'][kind]['direction_disagrees'] for p in ps for s in p['intervals'])))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],patients=patients,summary=summary,
        scope='Post-hoc descriptive endpoint on already-opened patients; not clinical growth/recurrence classification',
        same_patient_intervals_are_dependent=True,patients_without_temporal_pairs_excluded_from_this_endpoint_only=True,
        main_segmentation_denominators_unchanged=True,clinical_treatment_status_unavailable=True,
        probability_thresholds_not_changed=True,endpoint_threshold='mathematical sign only; no clinical growth cutoff',
        independence_or_publication_claim_established=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,new_training_updates=0,confirmation_patients_opened=False,lockedIXI_opened=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),ep,tp,vp]],
        resource_snapshot=resource_guard(),elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
    dest=HERE/'LONGITUDINAL_VOLUME_DIRECTION_DIAGNOSTIC.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,summary=summary,elapsed_seconds=r['elapsed_seconds']),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
