"""Exact rational enumeration, no model/MRI imports."""
import hashlib,json,math,sys
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'LTT_ORDERING_COUNTEREXAMPLE_CPU_PROTOCOL_2026-10-07.md'
OUT=ROOT/'experiments/ltt_ordering_counterexample_cpu_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atom(k,n,q):return math.comb(n,k)*q**k*(1-q)**(n-k)
def pack(x):return dict(numerator=x.numerator,denominator=x.denominator,value=float(x))
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False)
    n=8;alpha=F(3,10);delta=F(1,10);q=F(31,100)
    ps=[sum((atom(k,n,alpha) for k in range(j+1)),F(0)) for j in range(n+1)]
    mass=F(0);fixed=F(0);adaptive=F(0);bonf=F(0);rows=[]
    for a in range(n+1):
        for b in range(n+1):
            probability=atom(a,n,q)*atom(b,n,q);mass+=probability
            first=ps[a]<=delta;sortedfirst=min(ps[a],ps[b])<=delta
            corrected=min(ps[a],ps[b])<=delta/2
            if first:fixed+=probability
            if sortedfirst:adaptive+=probability
            if corrected:bonf+=probability
            rows.append(dict(counts=[a,b],probability=pack(probability),fixed_any_false_rejection=first,
                calibration_sorted_any_false_rejection=sortedfirst,bonferroni_any_false_rejection=corrected))
    p0=(1-alpha)**n;f0=(1-q)**n
    assert mass==1 and fixed==f0 and adaptive==1-(1-f0)**2 and bonf==0
    assert fixed<=delta<adaptive and delta/2<p0<=delta and ps[1]>delta
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_bindings=[dict(path=PROTOCOL.relative_to(ROOT).as_posix(),sha256=sha(PROTOCOL))],
        n=n,alpha=pack(alpha),delta=pack(delta),true_error_rate_each=pack(q),hypotheses=2,
        pvalue_zero_errors=pack(p0),fixed_sequence_FWER=pack(fixed),calibration_sorted_FWER=pack(adaptive),
        bonferroni_FWER=pack(bonf),four_patient_zero_error_pvalue=pack((1-alpha)**4),
        assumptions=dict(patient_binary_losses=True,independent_patients=True,independent_two_policies_for_this_example=True,
            policies_frozen_before_calibration=True),joint_count_states=rows,
        known_multiplicity_counterexample=True,MRI_data_reads=0,model_forwards=0,training_updates=0,
        fresh_MRI_calibration_patients=0,publication_claim_confirmed=False)
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as s:json.dump(r,s,indent=2);s.write('\n')
    print(json.dumps({k:r[k] for k in ('complete','pvalue_zero_errors','fixed_sequence_FWER','calibration_sorted_FWER','bonferroni_FWER')}))
    return 0
if __name__=='__main__':raise SystemExit(main())
