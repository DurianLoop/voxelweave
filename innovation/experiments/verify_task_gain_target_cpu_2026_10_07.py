"""Independent boolean-list cost replay for all exact toy configurations."""
import hashlib,itertools,json,sys,time
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/task_gain_target_cpu_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sf(v):return dict(numerator=v.numerator,denominator=v.denominator,value=float(v))
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();source=OUT/'attempt01.json';q=json.loads(source.read_text(encoding='utf-8'))
    path=OUT/'independent_boolean_cost_replay_attempt01.json';assert not path.exists()
    masks=list(itertools.product((False,True),repeat=4));truths=[m for m in masks if any(m)]
    def cost(g,p):return 1-Fraction(2*sum(x and y for x,y in zip(g,p)),sum(g)+sum(p))
    table={(g,p):cost(g,p) for g in truths for p in masks}
    counts=dict(target_disagreements=0,strict_regret_cases=0,accept_despite_negative_expected_gain=0,
                reject_despite_positive_expected_gain=0,accept_at_zero_expected_gain=0)
    regret_sum=Fraction(0);max_regret=Fraction(0);examples={};n=0
    for g0,g1,p0,p1 in itertools.product(truths,truths,masks,masks):
        c00,c01,c10,c11=table[g0,p0],table[g0,p1],table[g1,p0],table[g1,p1]
        expected0=Fraction(3,4)*c00+Fraction(1,4)*c10
        expected1=Fraction(3,4)*c01+Fraction(1,4)*c11
        probability=Fraction(3*int(c01<c00)+int(c11<c10),4)
        binary=probability>Fraction(1,2);optimal=expected1<expected0
        regret=(expected1 if binary else expected0)-min(expected0,expected1)
        n+=1;counts['target_disagreements']+=int(binary!=optimal);counts['strict_regret_cases']+=int(regret>0)
        regret_sum+=regret;max_regret=max(max_regret,regret)
        name=None
        if binary and expected1>expected0:name='accept_despite_negative_expected_gain'
        elif not binary and optimal:name='reject_despite_positive_expected_gain'
        elif binary and expected1==expected0:name='accept_at_zero_expected_gain'
        if name:
            counts[name]+=1
            if name not in examples:examples[name]=dict(majority_GT=list(g0),minority_GT=list(g1),
                baseline=list(p0),action=list(p1),majority_gain=sf(c00-c01),minority_gain=sf(c10-c11),
                probability_positive_gain=sf(probability),expected_gain=sf(expected0-expected1),expected_regret=sf(regret))
        if n%1024==0:assert time.perf_counter()-started<=60
    assert n==q['configurations_enumerated']==57_600
    assert counts['target_disagreements']==q['positive_gain_probability_policy_target_disagreements']
    assert counts['strict_regret_cases']==q['positive_gain_probability_policy_strict_regret_cases']
    assert sf(regret_sum/n)==q['mean_exact_regret_over_enumeration'] and sf(max_regret)==q['max_exact_regret']
    assert counts['target_disagreements']==sum(counts[k] for k in ['accept_despite_negative_expected_gain',
        'reject_despite_positive_expected_gain','accept_at_zero_expected_gain'])
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_file=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),configurations_replayed=n,
        counts=counts,representative_counterexamples_by_type=examples,mean_exact_regret=sf(regret_sum/n),max_exact_regret=sf(max_regret),
        whole_enumeration_not_real_patient_sample=True,real_MRI_or_GT_files_loaded=0,actual_training_updates=0,
        actual_gpu_updates=0,publication_claim_confirmed=False,elapsed_seconds=time.perf_counter()-started)
    with path.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(counts));print(json.dumps(examples,ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
