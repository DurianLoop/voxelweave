"""Independent Fraction/120-digit entropy-form replay; never imports production selector."""
import hashlib,json,math,sys,time,traceback
from datetime import datetime,timezone
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/patient_risk_cost_baseline_executor_qualification_2026_10_07'
SOURCE=OUT/'attempt01.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def q(x):return F(D(str(x)))
def d(x):return D(x.numerator)/D(x.denominator)
def binom(n,k,a):
    terms=[F(math.factorial(n),math.factorial(j)*math.factorial(n-j))*a**j*(1-a)**(n-j) for j in range(k+1)]
    return sum(terms,F(0))
def reference_pvalue(values,spec):
    n=len(values);total=sum(map(q,values),F(0));a=q(spec['alpha']);mean=total/n
    if spec['mode']=='binary':return d(binom(n,int(total),a)),mean
    r=min(mean,a);rr=d(r);aa=d(a)
    entropy=rr*rr.ln() if r else D(0)
    if r!=1:entropy+=(1-rr)*(1-rr).ln()
    kl=entropy-rr*aa.ln()-(1-rr)*(1-aa).ln()
    threshold=math.ceil(total);p=min(D(1),(-n*kl).exp(),D(1).exp()*d(binom(n,threshold,a)))
    return p,mean
def scalar_points(panel,fields):
    return [[sum((q(v) for v in panel[group][name][i]),F(0))/len(panel['patient_ids']) for group,name in fields]
        for i in range(len(panel['policy_ids']))]
def nondominated(points,rule):
    dominated=set()
    for i,left in enumerate(points):
        for j,right in enumerate(points):
            if i==j:continue
            compare=[a-b for a,b in zip(left,right)]
            if (max(compare)<0 if rule=='all_strict' else max(compare)<=0 and min(compare)<0):dominated.add(j)
    return [j for j in range(len(points)) if j not in dominated]
def verify_selection(opt,test,specs,delta,s,checks):
    assert not set(opt['patient_ids'])&set(test['patient_ids'])
    assert opt['policy_ids']==test['policy_ids']==s['fixed_policy_ids']
    pids=opt['policy_ids'];calculated=[]
    for panel,recorded,kind in ((opt,s['optimization_risks'],'optimization'),(test,s['testing_risks'],'testing')):
        combined=[]
        for i,pid in enumerate(pids):
            row=recorded[i];assert row['policy_id']==pid
            ps=[]
            for name,spec in specs.items():
                ref,mean=reference_pvalue(panel['risks'][name][i],spec);v=row['risks'][name]
                actual=D(v['pvalue']);difference=actual-ref
                assert abs(difference)<=D('1e-58')
                assert difference>=-D('1e-110'),(kind,pid,name,str(difference))
                assert abs(D(v['mean'])-d(mean))<=D('1e-77') and v['n']==len(panel['patient_ids'])
                if spec['mode']=='binary':
                    exact=binom(v['n'],int(sum(map(q,panel['risks'][name][i]))),q(spec['alpha']))
                    assert exact==F(v['exact_numerator'],v['exact_denominator'])
                else:assert v['ceil_total_loss']==math.ceil(sum(map(q,panel['risks'][name][i])))
                checks.append(dict(panel=kind,policy_id=pid,risk=name,absolute_difference=str(abs(difference))))
                ps.append(ref)
            combined.append(max(ps));assert abs(D(row['combined_pvalue'])-max(ps))<=D('1e-58')
        calculated.append(combined)
    op,tp=calculated;method=s['method']
    fields=[('risks',name) for name in opt['risks']]+[('objectives',name) for name in opt['objectives']]
    eligible=nondominated(scalar_points(opt,fields),s['dominance_rule']) if method=='pareto' else list(range(len(pids)))
    order=sorted(eligible,key=lambda i:(op[i],pids[i]))
    assert s['frontier_policy_ids']==[pids[i] for i in eligible] and s['frozen_order']==[pids[i] for i in order]
    threshold=d(q(delta))/(len(pids) if method=='bonferroni' else 1)
    assert D(s['threshold'])<=threshold and threshold-D(s['threshold'])<=D('1e-78')
    accepted=[];tested=[];stopped=None
    for i in order:
        tested.append(pids[i]);pass_test=tp[i]<=threshold if method=='bonferroni' else tp[i]<threshold
        if pass_test:accepted.append(i)
        elif method!='bonferroni':stopped=pids[i];break
    assert s['certified_policy_ids']==[pids[i] for i in accepted]
    assert s['actual_tested_policy_ids']==tested and s['stopped_at']==stopped
    points=scalar_points(test,[('objectives',name) for name in test['objectives']])
    best=nondominated([points[i] for i in accepted],'weak') if accepted else []
    chosen=sorted([accepted[j] for j in best],key=lambda i:(tuple(points[i]),pids[i]))
    assert s['selected_policy_ids']==[pids[i] for i in chosen]
    assert s['selected_primary_policy_id']==(pids[chosen[0]] if chosen else None)
    assert not s['actual_MRI_risk_certificate_issued']
def main():
    sys.stdout.reconfigure(encoding='utf-8');at=time.perf_counter();dest=OUT/'independent_attempt01.json';assert not dest.exists()
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],script_sha256=sha(__file__),
        source_file=SOURCE.relative_to(ROOT).as_posix(),source_sha256=sha(SOURCE),
        source_bindings=[dict(path='PATIENT_RISK_COST_BASELINE_NUMERICAL_AMENDMENT_2026-10-07.md',
            sha256=sha(ROOT/'PATIENT_RISK_COST_BASELINE_NUMERICAL_AMENDMENT_2026-10-07.md'))],
        production_executor_imported=False,MRI_data_reads=0,model_forwards=0,GPU_forwards=0,
        actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False)
    try:
        c=json.loads(SOURCE.read_text(encoding='utf-8'));assert c['complete'] and not c['errors'] and c['synthetic_only']
        for b in c['source_bindings']:
            p=ROOT/b['path'];snap=OUT/(p.name+'.source_snapshot');assert sha(p)==sha(snap)==b['sha256']
        checks=[];count=0
        with localcontext() as ctx:
            ctx.prec=120
            for s in c['selections']+[c['all_strict_variant']]:
                verify_selection(c['fixture_optimization'],c['fixture_testing'],c['risk_specs'],'0.1',s,checks);count+=1
            verify_selection(c['fixture_optimization'],c['halt_fixture_testing'],c['risk_specs'],'0.1',c['halt_selection'],checks);count+=1
            for s in c['tie_checks'].values():
                verify_selection(c['tie_fixture_optimization'],c['tie_fixture_testing'],c['tie_specs'],'0.1',s,checks);count+=1
            verify_selection(c['max_risk_fixture_optimization'],c['max_risk_fixture_testing'],c['max_risk_specs'],'0.2',c['max_risk_selection'],checks);count+=1
            verify_selection(c['multi_objective_fixture_optimization'],c['multi_objective_fixture_testing'],c['risk_specs'],'0.1',c['multi_objective_selection'],checks);count+=1
        assert count==9 and len(c['invalid_inputs_rejected'])==12 and all(x['rejected'] and x['error'] for x in c['invalid_inputs_rejected'])
        assert 'patient_risk_cost_baseline_executor_2026_10_07' not in sys.modules and 'torch' not in sys.modules
        r.update(complete=True,independent_selections_replayed=count,independent_risk_values_checked=len(checks),
            pvalue_checks=checks,all_frontier_order_certification_utility_choices_match=True,
            invalid_input_rejections_only_record_consistency_checked=True,
            statistical_iid_MRI_guarantee_not_demonstrated_by_fixtures=True)
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-at
    with dest.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
    print(json.dumps({k:r.get(k) for k in ('complete','errors','independent_selections_replayed','independent_risk_values_checked','elapsed_seconds')}))
    return 0 if r['complete'] and not r['errors'] else 1
if __name__=='__main__':raise SystemExit(main())
