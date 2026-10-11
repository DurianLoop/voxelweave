"""Aggregate complete FOV scalar outcomes with equal patient weighting and full costs."""
from decimal import Decimal as D,localcontext,ROUND_CEILING
from fractions import Fraction as F
from patient_risk_cost_baseline_executor_2026_10_07 import number
COST_PHASES=('observed_load','warmup_cache','sr','candidate_exploration','feature','gate','transfer','inference','postprocess')
def amount(components):
    if set(components)!=set(COST_PHASES):raise ValueError('All nine cost phases must be explicit')
    values=[number(components[k]) for k in COST_PHASES]
    if not all(x>=0 for x in values):raise ValueError('Negative cost phase')
    return sum(values,F(0))
def packed(q):return dict(numerator=q.numerator,denominator=q.denominator)
def rounded(q):
    with localcontext() as ctx:
        ctx.prec=30;ctx.rounding=ROUND_CEILING
        return str(D(q.numerator)/D(q.denominator))
def complete_panel(records,expected_series,policy_ids,baseline_id,shared_costs,role,epsilon,rve_tau):
    if role not in ('optimization','testing'):raise ValueError('Explicit panel role required')
    patients=list(expected_series)
    if not patients or not policy_ids or len(set(policy_ids))!=len(policy_ids) or baseline_id not in policy_ids:
        raise ValueError('Complete unique cohort/policies and baseline required')
    all_uids=[u for patient in patients for u in expected_series[patient]]
    if not all(expected_series[p] for p in patients) or len(set(all_uids))!=len(all_uids):raise ValueError('Unique nonempty expected series required')
    eps=number(epsilon);tau=number(rve_tau)
    if eps<0 or tau<0:raise ValueError('Nonnegative frozen harm/RVE thresholds required')
    expected={(p,u,k) for p in patients for u in expected_series[p] for k in policy_ids};lookup={}
    for row in records:
        key=(row['patient_id'],row['uid'],row['policy_id'])
        if key not in expected or key in lookup:raise ValueError('Extra/duplicate complete series outcome')
        if row['full_fov'] is not True or row['label_used_for_inference'] is not False:
            raise ValueError('Full FOV and label-free inference declarations required')
        metrics={name:number(row[name]) for name in ('full_dice','full_recall','full_absRVE')}
        if not 0<=metrics['full_dice']<=1 or not 0<=metrics['full_recall']<=1 or metrics['full_absRVE']<0:
            raise ValueError('Invalid full-FOV scalar metric range')
        lookup[key]=dict(**metrics,cost=amount(row['cost_components']))
    if set(lookup)!=expected:raise ValueError('Missing complete series outcome: refusing to drop patient/series')
    shares={};required_shares={(p,k) for p in patients for k in policy_ids}
    for row in shared_costs:
        key=(row['patient_id'],row['policy_id'])
        if key not in required_shares or key in shares:raise ValueError('Extra/duplicate patient shared cost')
        shares[key]=amount(row['cost_components'])
    if set(shares)!=required_shares:raise ValueError('Missing explicit patient shared cost')
    summary={}
    for p in patients:
        for k in policy_ids:
            rows=[lookup[(p,u,k)] for u in expected_series[p]];n=len(rows)
            summary[(p,k)]={name:sum((row[name] for row in rows),F(0))/n for name in ('full_dice','full_recall','full_absRVE')}
            summary[(p,k)]['total_cost']=sum((row['cost'] for row in rows),F(0))+shares[(p,k)]
    names=('dice_loss','positive_dice_drop','harm_event','recall_loss','rve_tail')
    risks={name:[] for name in names};cost=[];diagnostics=[]
    for k in policy_ids:
        values={name:[] for name in names};c=[]
        for p in patients:
            v=summary[(p,k)];base=summary[(p,baseline_id)];drop=base['full_dice']-v['full_dice']
            item=dict(dice_loss=1-v['full_dice'],positive_dice_drop=max(F(0),drop),harm_event=F(int(drop>eps)),
                recall_loss=1-v['full_recall'],rve_tail=F(int(v['full_absRVE']>tau)))
            for name in names:values[name].append(rounded(item[name]))
            c.append(rounded(v['total_cost']))
            diagnostics.append(dict(patient_id=p,policy_id=k,series_uids=expected_series[p],series_count=len(expected_series[p]),
                exact_metrics={name:packed(x) for name,x in v.items()},exact_losses={name:packed(x) for name,x in item.items()},
                shared_cost=packed(shares[(p,k)])))
        for name in names:risks[name].append(values[name])
        cost.append(c)
    return dict(role=role,patient_ids=patients,policy_ids=policy_ids,risks=risks,objectives=dict(total_cost=cost),
        patient_series_weights={p:dict(series_count=len(expected_series[p]),each_series_weight=packed(F(1,len(expected_series[p])))) for p in patients},
        cohort_patient_weight=packed(F(1,len(patients))),diagnostics=diagnostics,
        loss_rounding='30 significant digits, upward; harm/tail events decided on exact fractions',
        complete_series_records=len(records),actual_MRI_risk_certificate_issued=False)
