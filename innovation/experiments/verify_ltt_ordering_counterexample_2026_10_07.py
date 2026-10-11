"""Independent integer-weight enumeration of all 65,536 binary data outcomes."""
import hashlib,json,math,sys
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/ltt_ordering_counterexample_cpu_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frac(v):return Fraction(v['numerator'],v['denominator'])
def main():
    sys.stdout.reconfigure(encoding='utf-8');p=OUT/'attempt01.json';dest=OUT/'independent_attempt01.json';assert not dest.exists()
    c=json.loads(p.read_text(encoding='utf-8'));assert c['complete'] and not c['errors'] and c['n']==8
    # All true nulls: q=.31>.30. All admissible calibration count states checked by integer CDF.
    cdf=[sum(math.comb(8,k)*3**k*7**(8-k) for k in range(j+1)) for j in range(9)]
    total=fixed=adaptive=bonferroni=0
    for bits in range(65536):
        left=(bits&255).bit_count();right=(bits>>8).bit_count();ones=left+right
        weight=31**ones*69**(16-ones);total+=weight
        if cdf[left]*10<=10**8:fixed+=weight
        if min(cdf[left],cdf[right])*10<=10**8:adaptive+=weight
        if min(cdf[left],cdf[right])*20<=10**8:bonferroni+=weight
    assert total==100**16
    expected={'fixed_sequence_FWER':Fraction(fixed,total),'calibration_sorted_FWER':Fraction(adaptive,total),
        'bonferroni_FWER':Fraction(bonferroni,total),'pvalue_zero_errors':Fraction(7**8,10**8),
        'four_patient_zero_error_pvalue':Fraction(7**4,10**4)}
    assert all(frac(c[k])==v and float(v)==c[k]['value'] for k,v in expected.items())
    assert len(c['joint_count_states'])==81
    for row in c['joint_count_states']:
        a,b=row['counts'];num=math.comb(8,a)*math.comb(8,b)*31**(a+b)*69**(16-a-b)
        assert frac(row['probability'])==Fraction(num,total)
        assert row['fixed_any_false_rejection']==(cdf[a]*10<=10**8)
        assert row['calibration_sorted_any_false_rejection']==(min(cdf[a],cdf[b])*10<=10**8)
        assert row['bonferroni_any_false_rejection']==(min(cdf[a],cdf[b])*20<=10**8)
    for b in c['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_file=p.relative_to(ROOT).as_posix(),source_sha256=sha(p),independent_binary_outcomes_enumerated=65536,
        integer_denominator=total,exact_rational_results_match=True,model_forwards=0,MRI_data_reads=0,
        publication_claim_confirmed=False)
    with dest.open('x',encoding='utf-8') as s:json.dump(r,s,indent=2);s.write('\n')
    print(json.dumps(dict(complete=True,exact_rational_results_match=True,outcomes=65536)));return 0
if __name__=='__main__':raise SystemExit(main())
