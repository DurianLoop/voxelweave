"""Finite synthetic calibration/routing audit; no torch, MRI data, or training."""
import hashlib, itertools, json, sys, time
from fractions import Fraction as Q
from pathlib import Path
from datetime import datetime, timezone
from mc_rc_reference_resources_2026_10_07 import resource_guard
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/calibrated_risk_vs_action_gain_2026_10_07'
TABLE=((0,10,5,85),(30,10,50,10),(60,0,30,10),(90,0,10,0))
EXPECTED0=(Q(9,10),Q(3,5),Q(2,5),Q(1,10))
EXPECTED1=(Q(19,20),Q(1,5),Q(1,10),Q(0))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fraction(q):return dict(numerator=q.numerator,denominator=q.denominator,value=float(q))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);start=time.perf_counter()
    protocol=ROOT/'CALIBRATED_RISK_VS_ACTION_GAIN_CPU_PROTOCOL_2026-10-07.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=False,errors=[],
        source_bindings=[dict(path=protocol.relative_to(ROOT).as_posix(),sha256=sha(protocol)),
        dict(path=Path(__file__).relative_to(ROOT).as_posix(),sha256=sha(__file__)),
        dict(path='experiments/mc_rc_reference_resources_2026_10_07.py',sha256=sha(ROOT/'experiments/mc_rc_reference_resources_2026_10_07.py'))],
        MRI_arrays_loaded=0,MRI_model_forwards=0,training_updates=0,GPU_initialized=False,confirmation_opened=False,
        new_theorem_claimed=False,publication_claim_confirmed=False,goal_status='active')
    try:
        r['resources_before']=resource_guard();groups=[];truth=[];base=[];alternative=[]
        for g,counts in enumerate(TABLE):
            e0,e1=[],[]
            for (a,b),n in zip(((0,0),(0,1),(1,0),(1,1)),counts):e0.extend([a]*n);e1.extend([b]*n)
            y=np.array(e0,dtype=np.uint8);p0=np.zeros(100,dtype=np.uint8);p1=np.bitwise_xor(y,np.array(e1,dtype=np.uint8))
            assert int((p0!=y).sum())==int(100*EXPECTED0[g]) and int((p1!=y).sum())==int(100*EXPECTED1[g])
            # Independent count arithmetic, not recomputed from array outcome functions.
            q0=Q(counts[2]+counts[3],sum(counts));q1=Q(counts[1]+counts[3],sum(counts))
            assert q0==EXPECTED0[g] and q1==EXPECTED1[g]
            groups.append(dict(group=chr(65+g),four_cell_counts=list(counts),baseline_risk=fraction(q0),action_risk=fraction(q1),
                gain=fraction(q0-q1),baseline_calibration_error=0,action_calibration_error=0))
            truth.append(y);base.append(p0);alternative.append(p1)
        y=np.concatenate(truth);p0=np.concatenate(base);p1=np.concatenate(alternative)
        baseline_errors=int((p0!=y).sum());r['groups']=groups;r['total_samples']=len(y)
        policies=[]
        def policy(name,selected):
            out=p0.copy()
            for i in selected:out[i*100:(i+1)*100]=p1[i*100:(i+1)*100]
            errors=int((out!=y).sum());expected=Q(baseline_errors,1)-100*sum((EXPECTED0[i]-EXPECTED1[i] for i in selected),Q(0))
            assert expected==errors
            row=dict(name=name,selected_groups=[chr(65+i) for i in selected],action_calls=100*len(selected),
                total_errors=errors,system_error=fraction(Q(errors,len(y))),net_error_reduction=baseline_errors-errors)
            policies.append(row);return row
        risk=policy('highest_baseline_risk_equal_budget',[max(range(4),key=lambda i:EXPECTED0[i])])
        gain=policy('known_two_path_cost_sensitive_equal_budget',[max(range(4),key=lambda i:EXPECTED0[i]-EXPECTED1[i])])
        assert risk['net_error_reduction']==-5 and gain['net_error_reduction']==40
        random_results=[policy('random_one_group_outcome_'+chr(65+i),[i]) for i in range(4)]
        random_improvement=Q(sum(x['net_error_reduction'] for x in random_results),4);assert random_improvement==Q(75,4)
        policy('never_call',[]);policy('always_call_different_budget',list(range(4)))
        equivalence=[]
        for perm in itertools.permutations(range(4)):
            a=max(perm,key=lambda i:EXPECTED0[i]-EXPECTED1[i]);b=min(perm,key=lambda i:EXPECTED1[i]-EXPECTED0[i]);assert a==b
            equivalence.append(list(perm))
        order=sorted(range(4),key=lambda i:EXPECTED0[i],reverse=True)
        curve=[policy('nested_high_risk_acceptance_'+str(k),order[:k]) for k in range(5)]
        assert any(b['total_errors']>a['total_errors'] for a,b in zip(curve,curve[1:]))
        crc=[]
        for n in (4,8,11,19,59,99):
            for alpha in (Q(1,20),Q(1,10),Q(3,10)):
                lower=Q(1,n+1);max_emp=(alpha*(n+1)-1)/n
                crc.append(dict(n=n,alpha=fraction(alpha),bounded_loss_B=1,zero_empirical_corrected=fraction(lower),
                    zero_empirical_satisfies_corrected_inequality=lower<=alpha,maximum_empirical_risk_for_corrected_inequality=fraction(max_emp),
                    real_MRI_calibration_authorized=False))
        r.update(policies=policies,random_one_group_expected_net_error_reduction=fraction(random_improvement),
            gain_and_cost_routing_equivalent_permutations=len(equivalence),nested_acceptance_error_curve=curve,
            nested_action_support_does_not_imply_monotone_system_loss=True,CRC_finite_n_arithmetic=crc,
            gates=dict(per_group_exact_calibration=True,independent_fraction_counts=True,
                perfect_baseline_risk_can_choose_harmful_action=True,paired_risk_is_known_cost_sensitive_baseline=True,
                nonmonotone_correction_loss=True),complete=True)
        r['resources_after']=resource_guard();assert time.perf_counter()-start<60
    except Exception as e:r['errors'].append(f'{type(e).__name__}: {e}');r['complete']=False
    r['elapsed_seconds']=time.perf_counter()-start
    p=OUT/'attempt01.json'
    with p.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    assert p.stat().st_size<2_000_000
    print(json.dumps({k:r.get(k) for k in ('complete','errors','gates','random_one_group_expected_net_error_reduction','elapsed_seconds')},ensure_ascii=False))
    return 0 if r['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
