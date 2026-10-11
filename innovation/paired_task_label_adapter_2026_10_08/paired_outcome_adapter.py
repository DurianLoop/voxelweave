"""Complete-patient paired task labels from independently certified saved outcomes."""
from fractions import Fraction
import math

DOMAINS=('full','anchors','missing','tail')

def need(value,message):
    if not value:raise ValueError(message)

def packed(q):
    return None if q is None else dict(numerator=q.numerator,denominator=q.denominator,value=float(q))

def unpack(q):return None if q is None else Fraction(q['numerator'],q['denominator'])

def count_metrics(c):
    for k in ('tp','fp','fn','gt_foreground','pred_foreground'):
        need(type(c[k]) is int and c[k]>=0,'Nonnegative integer counts required')
    tp,fp,fn=c['tp'],c['fp'],c['fn'];gt=tp+fn;pred=tp+fp
    need(gt==c['gt_foreground'] and pred==c['pred_foreground'],'Count identities differ')
    need(c['empty_ground_truth']==(gt==0) and c['empty_prediction']==(pred==0),'Empty declarations differ')
    return dict(dice=Fraction(2*tp,gt+pred) if gt+pred else None,
        recall=Fraction(tp,gt) if gt else None,precision=Fraction(tp,pred) if pred else None,
        signed_relative_volume_error=Fraction(pred-gt,gt) if gt else None,
        absolute_relative_volume_error=Fraction(abs(pred-gt),gt) if gt else None)

def mean(values):
    return None if any(v is None for v in values) else sum(values,Fraction(0))/len(values)

def paired_labels(rows,contract):
    people=contract['patient_series'];methods=(contract['baseline_action'],contract['candidate_action'])
    need(people and len(set(methods))==2,'Nonempty cohort and distinct actions required')
    alluids=[uid for uu in people.values() for uid in uu]
    need(all(uu and len(set(uu))==len(uu) for uu in people.values()) and len(set(alluids))==len(alluids),
         'Unique nonempty complete patient series required')
    expected={(p,uid,m) for p,uu in people.items() for uid in uu for m in methods};lookup={}
    for row in rows:
        key=(row['patient'],row['uid'],row['action'])
        need(key in expected and key not in lookup,'Extra/duplicate/wrong patient action outcome')
        metadata=contract['series_metadata'][row['uid']]
        need(metadata['patient']==row['patient'],'Wrong patient ownership')
        need(row['task_checkpoint_sha256']==contract['task_checkpoint_sha256'],'Task checkpoint differs')
        need(row['observed_package_sha256']==metadata['observed_package_sha256'],'Observed package binding differs')
        need(row['observed_array_sha256']==metadata['observed_array_sha256'],'Observed array binding differs')
        need(row['label_array_sha256']==metadata['label_array_sha256'],'Gold label binding differs')
        need(row['input_sha256']==metadata['input_sha256_by_action'][row['action']],'Action input binding differs')
        need(row['observed_statistics']==metadata['observed_statistics'],'Shared observed statistics differ')
        need(row['label_used_for_inference'] is False,'Gold label must not enter inference')
        need(row['full_fov'] is True and row['native_planes']==list(range(metadata['native_shape'][2])),
             'Complete original native FOV required')
        need(type(row['coverage_min']) in (int,float) and math.isfinite(row['coverage_min']) and row['coverage_min']>=1,
             'Complete coverage required')
        need(row['status'] in ('completed','failed','deferred'),'Explicit action execution status required')
        need(row['full_action_cost'] is None,'This qualification source has no full action cost; do not invent one')
        if row['status']=='completed':
            need(row['independently_verified_counts'] is True,'Certified source counts required')
            metric={}
            for domain in DOMAINS:
                values=count_metrics(row['counts'][domain]);metric[domain]=values
                for name,q in values.items():
                    scalar=row['counts'][domain][name]
                    need((scalar is None) if q is None else
                         type(scalar) in (int,float) and math.isfinite(scalar) and abs(scalar-float(q))<=1e-15,
                         'Saved scalar/count metric mismatch')
            for name in ('tp','fp','fn','gt_foreground','pred_foreground'):
                need(row['counts']['full'][name]==sum(row['counts'][d][name] for d in DOMAINS[1:]),'Full/domain count partition differs')
            interval=row['saved_infer_native_interval_seconds']
            need(type(interval) in (int,float) and math.isfinite(interval) and interval>=0,'Finite saved inference interval required')
        else:
            need(row['counts'] is None,'Failed action must not masquerade as an observed zero score')
            metric=None
        lookup[key]=(row,metric)
    need(set(lookup)==expected,'Missing complete series action outcome; refusing to shrink cohort')
    series=[];patients=[]
    for p in sorted(people):
        pp=[]
        for uid in people[p]:
            before,mb=lookup[p,uid,methods[0]];after,ma=lookup[p,uid,methods[1]]
            q0=mb['full']['dice'] if mb is not None else None;q1=ma['full']['dice'] if ma is not None else None
            g=q1-q0 if q0 is not None and q1 is not None else None
            item=dict(patient=p,uid=uid,baseline_status=before['status'],candidate_status=after['status'],
                Q_before=packed(q0),Q_after=packed(q1),delta_Q=packed(g),
                quality_cost_before=packed(1-q0) if q0 is not None else None,
                quality_cost_after=packed(1-q1) if q1 is not None else None,
                utility_defined=g is not None,full_action_cost=None,
                saved_infer_native_interval_before=before['saved_infer_native_interval_seconds'],
                saved_infer_native_interval_after=after['saved_infer_native_interval_seconds'],
                source_bindings={k:before[k] for k in ('observed_package_sha256','observed_array_sha256','label_array_sha256','task_checkpoint_sha256')},
                before_input_sha256=before['input_sha256'],after_input_sha256=after['input_sha256'],
                before_prediction_sha256=before['prediction_file_sha256'],after_prediction_sha256=after['prediction_file_sha256'])
            series.append(item);pp.append(item)
        qb=mean([unpack(v['Q_before']) for v in pp]);qa=mean([unpack(v['Q_after']) for v in pp]);gg=qa-qb if qa is not None and qb is not None else None
        patients.append(dict(patient=p,series_uids=people[p],series_count=len(pp),Q_before=packed(qb),Q_after=packed(qa),delta_Q=packed(gg),
            utility_defined=gg is not None,full_action_cost=None,
            saved_inference_interval_sum_before=sum(v['saved_infer_native_interval_before'] for v in pp) if all(v['saved_infer_native_interval_before'] is not None for v in pp) else None,
            saved_inference_interval_sum_after=sum(v['saved_infer_native_interval_after'] for v in pp) if all(v['saved_infer_native_interval_after'] is not None for v in pp) else None,
            task_model_training_exposed=p in set(contract['task_training_patient_ids']),
            cohort_role=contract['cohort_role'],head_fitting_allowed=False))
    q0=mean([unpack(v['Q_before']) for v in patients]);q1=mean([unpack(v['Q_after']) for v in patients])
    delta=q1-q0 if q0 is not None and q1 is not None else None
    return dict(schema_version=1,complete=True,baseline_action=methods[0],candidate_action=methods[1],
        endpoint='full_dice',higher_is_better=True,delta_direction='candidate_minus_baseline',
        source_cohort_role=contract['cohort_role'],series=series,patients=patients,
        patient_first_means=dict(Q_before=packed(q0),Q_after=packed(q1),delta_Q=packed(delta)),
        all_negative_and_zero_outcomes_retained=True,failed_or_undefined_series_retained=True,
        original_task_capability_gate_passed=contract['task_capability_gate_passed'],
        independently_certified_saved_outcomes=True,new_MRI_inference_executed=False,
        full_action_costs_available=False,training_readiness=False,publication_claim_confirmed=False)

def require_fit_ready(bundle):
    reasons=[]
    if bundle['source_cohort_role']!='development':reasons.append('Cohort is already-seen validation, not authorized training labels')
    if not bundle['original_task_capability_gate_passed']:reasons.append('Source task capability gate failed')
    if not bundle['full_action_costs_available']:reasons.append('Full measured costs are unavailable')
    if not all(v['utility_defined'] for v in bundle['patients']):reasons.append('Incomplete/undefined whole-patient utility')
    raise ValueError('Qualified label extraction does not authorize a head fit: '+'; '.join(reasons))
