"""Known LTT/SplitFST/Pareto baselines on complete patient panels; no MRI/model IO."""
from decimal import Decimal as D,localcontext,InvalidOperation,ROUND_CEILING,ROUND_FLOOR
from fractions import Fraction as F
import math
NUMERICAL_MARGIN=D('1e-60')
def number(x):
    s=str(x)
    if len(s)>80:raise ValueError('Numeric input too long')
    try:d=D(s)
    except InvalidOperation as e:raise ValueError('Finite numeric input required') from e
    if not d.is_finite() or len(d.as_tuple().digits)>30:raise ValueError('Finite numeric precision <=30 required')
    if d and abs(d.adjusted())>30:raise ValueError('Numeric magnitude outside declared range')
    return F(d)
def dec(x):return D(x.numerator)/D(x.denominator)
def probability(x):
    q=number(x)
    if not 0<q<1:raise ValueError('Probability must be in (0,1)')
    return q
def cdf(n,k,alpha):
    return sum((math.comb(n,j)*alpha**j*(1-alpha)**(n-j) for j in range(k+1)),F(0))
def pvalue(losses,alpha,mode):
    if not 1<=len(losses)<=256:raise ValueError('Patient count must be 1..256')
    a=probability(alpha);v=[number(x) for x in losses]
    if not all(0<=x<=1 for x in v):raise ValueError('Bounded risk loss must lie in [0,1]')
    if mode not in ('binary','bounded'):raise ValueError('Unknown risk mode')
    n=len(v);total=sum(v,F(0));mean=total/n
    with localcontext() as context:
        context.prec=80
        if mode=='binary':
            if not all(x in (0,1) for x in v):raise ValueError('Binary risk requires 0/1 losses')
            exact=cdf(n,int(total),a)
            context.rounding=ROUND_CEILING
            return dict(pvalue=str(dec(exact)),mean=str(dec(mean)),mode=mode,n=n,
                exact_numerator=exact.numerator,exact_denominator=exact.denominator)
        r=min(mean,a);rr=dec(r);aa=dec(a)
        h=(rr*(rr/aa).ln() if r>0 else D(0))+(1-rr)*((1-rr)/(1-aa)).ln()
        hoeffding=(-D(n)*h).exp()
        k=(total.numerator+total.denominator-1)//total.denominator
        bentkus=D(1).exp()*dec(cdf(n,k,a))
        value=min(D(1),min(hoeffding,bentkus)+NUMERICAL_MARGIN)
        return dict(pvalue=str(value),mean=str(dec(mean)),mode=mode,n=n,
            hoeffding_KL_term=str(hoeffding),bentkus_term=str(bentkus),
            ceil_total_loss=k,numerical_margin=str(NUMERICAL_MARGIN))
def validate_panel(panel):
    ids=panel['patient_ids'];policies=panel['policy_ids']
    if not 1<=len(ids)<=256 or len(set(ids))!=len(ids) or not all(isinstance(x,str) and x for x in ids):
        raise ValueError('Unique complete patient IDs required')
    if not 1<=len(policies)<=128 or len(set(policies))!=len(policies) or not all(isinstance(x,str) and x for x in policies):
        raise ValueError('Unique policy IDs required')
    if set(panel['risks'])&set(panel['objectives']):raise ValueError('Risk/objective names must be distinct')
    for field in ('risks','objectives'):
        if not 1<=len(panel[field])<=8:raise ValueError('Risk/objective count must be 1..8')
        for name,rows in panel[field].items():
            if len(rows)!=len(policies) or any(len(row)!=len(ids) for row in rows):
                raise ValueError('Every policy must cover the entire identical patient panel')
            values=[number(x) for row in rows for x in row]
            if field=='risks' and not all(0<=v<=1 for v in values):raise ValueError('Risk outside [0,1]')
            if name=='total_cost' and not all(v>=0 for v in values):raise ValueError('Total cost must be nonnegative')
    return panel
def means(panel):
    fields=list(panel['risks'])+list(panel['objectives']);n=len(panel['patient_ids'])
    return [[sum((number(x) for x in (panel['risks']|panel['objectives'])[field][i]),F(0))/n for field in fields]
        for i in range(len(panel['policy_ids']))]
def frontier_indices(points,rule='weak'):
    if rule not in ('weak','all_strict'):raise ValueError('Unknown Pareto dominance rule')
    def dominates(a,b):
        return all(x<y for x,y in zip(a,b)) if rule=='all_strict' else all(x<=y for x,y in zip(a,b)) and any(x<y for x,y in zip(a,b))
    return [j for j,b in enumerate(points) if not any(i!=j and dominates(a,b) for i,a in enumerate(points))]
def risk_values(panel,specs):
    if set(panel['risks'])!=set(specs):raise ValueError('Frozen risk names must match')
    details=[]
    for i,pid in enumerate(panel['policy_ids']):
        risk={name:pvalue(panel['risks'][name][i],spec['alpha'],spec['mode']) for name,spec in specs.items()}
        details.append(dict(policy_id=pid,risks=risk,combined_pvalue=str(max(D(v['pvalue']) for v in risk.values()))))
    return details
def select(optimization,testing,specs,delta,method,forbidden_testing_ids=(),dominance_rule='weak'):
    with localcontext() as context:
        context.prec=80
        opt=validate_panel(optimization);test=validate_panel(testing);level=dec(probability(delta))
        if opt['role']!='optimization' or test['role']!='testing':raise ValueError('Frozen panel roles required')
        if set(opt['patient_ids'])&set(test['patient_ids']):raise ValueError('Optimization/testing patient overlap')
        if set(test['patient_ids'])&set(forbidden_testing_ids):raise ValueError('Testing patient belongs to forbidden seen/confirmation cohort')
        if opt['policy_ids']!=test['policy_ids'] or list(opt['risks'])!=list(test['risks']) or list(opt['objectives'])!=list(test['objectives']):
            raise ValueError('Fixed candidate/objective order must match across panels')
        if method not in ('bonferroni','split_fst','pareto'):raise ValueError('Unknown baseline method')
        op=risk_values(opt,specs);tp=risk_values(test,specs);pids=opt['policy_ids']
        allowed=frontier_indices(means(opt),dominance_rule) if method=='pareto' else list(range(len(pids)))
        order=sorted(allowed,key=lambda j:(D(op[j]['combined_pvalue']),pids[j]))
        certified=[];stopped=None;tested=[]
        if method=='bonferroni':
            context.rounding=ROUND_FLOOR
            threshold=level/len(pids)
            context.rounding=ROUND_CEILING
            for j in order:
                tested.append(pids[j])
                if D(tp[j]['combined_pvalue'])<=threshold:certified.append(j)
        else:
            threshold=level
            for j in order:
                tested.append(pids[j])
                if D(tp[j]['combined_pvalue'])<threshold:certified.append(j)
                else:stopped=pids[j];break
        objective_points=[[sum((number(x) for x in test['objectives'][name][j]),F(0))/len(test['patient_ids'])
            for name in test['objectives']] for j in certified]
        best=frontier_indices(objective_points,'weak') if certified else []
        chosen=[certified[j] for j in best]
        chosen=sorted(chosen,key=lambda j:(tuple(sum((number(x) for x in test['objectives'][name][j]),F(0))
            for name in test['objectives']),pids[j]))
        return dict(method=method,dominance_rule=dominance_rule,fixed_policy_ids=pids,
            optimization_patient_ids=opt['patient_ids'],testing_patient_ids=test['patient_ids'],
            optimization_risks=op,testing_risks=tp,
            frontier_policy_ids=[pids[j] for j in allowed],frozen_order=[pids[j] for j in order],
            actual_tested_policy_ids=tested,stopped_at=stopped,threshold=str(threshold),
            certified_policy_ids=[pids[j] for j in certified],selected_policy_ids=[pids[j] for j in chosen],
            selected_primary_policy_id=pids[chosen[0]] if chosen else None,
            complete=True,actual_MRI_risk_certificate_issued=False,
            guarantee_conditions='Requires independent i.i.d. fresh patient testing and candidates/losses frozen before testing; not proved by IDs alone.')
