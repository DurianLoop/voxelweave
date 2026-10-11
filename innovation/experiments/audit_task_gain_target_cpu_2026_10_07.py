"""Exact finite decision-target qualification, not a new theorem or MRI experiment."""
import hashlib,itertools,json,sys,time
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/task_gain_target_cpu_2026_10_07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def serial(f):return dict(numerator=f.numerator,denominator=f.denominator,value=float(f))
def positions(mask):return [j for j in range(4) if (mask>>j)&1]
def main():
    sys.stdout.reconfigure(encoding='utf-8');OUT.mkdir(exist_ok=False);started=time.perf_counter()
    table={};verified=0
    for gt,pred in itertools.product(range(1,16),range(16)):
        bit_dice=Fraction(2*(gt&pred).bit_count(),gt.bit_count()+pred.bit_count())
        g,p=set(positions(gt)),set(positions(pred));set_dice=Fraction(2*len(g.intersection(p)),len(g)+len(p))
        assert bit_dice==set_dice;table[gt,pred]=bit_dice;verified+=1
    mismatch=0;strict_regrets=0;examples=[];regret_sum=Fraction(0);max_regret=Fraction(0);visited=0
    for gt0,gt1,a0,a1 in itertools.product(range(1,16),range(1,16),range(16),range(16)):
        g0=table[gt0,a1]-table[gt0,a0];g1=table[gt1,a1]-table[gt1,a0]
        gain=(3*g0+g1)/4;probability=(3*int(g0>0)+int(g1>0))/Fraction(4)
        cost0=(3*(1-table[gt0,a0])+(1-table[gt1,a0]))/4
        cost1=(3*(1-table[gt0,a1])+(1-table[gt1,a1]))/4
        decision_gain=int(gain>0);decision_cost=int(cost1<cost0);decision_probability=int(probability>Fraction(1,2))
        assert decision_gain==decision_cost and gain==cost0-cost1
        regret=(cost1 if decision_probability else cost0)-min(cost0,cost1);assert regret>=0
        visited+=1;regret_sum+=regret;max_regret=max(max_regret,regret)
        if decision_gain!=decision_probability:
            mismatch+=1;strict_regrets+=int(regret>0)
            if len(examples)<10:examples.append(dict(gt_majority=positions(gt0),gt_minority=positions(gt1),
                baseline_prediction=positions(a0),action_prediction=positions(a1),gain_majority=serial(g0),gain_minority=serial(g1),
                expected_gain=serial(gain),probability_positive_gain=serial(probability),
                expected_cost_baseline=serial(cost0),expected_cost_action=serial(cost1),probability_policy_action=decision_probability,
                expected_gain_policy_action=decision_gain,regret=serial(regret)))
        if visited%1024==0:assert time.perf_counter()-started<=60
    assert visited==57_600 and verified==240
    protocol=ROOT/'TASK_GAIN_TARGET_CPU_AUDIT_PROTOCOL_2026-10-07.md'
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        source_bindings=[dict(path=protocol.relative_to(ROOT).as_posix(),sha256=sha(protocol))],
        toy_binary_positions=4,independent_set_and_bit_dice_pairs_verified=verified,configurations_enumerated=visited,
        state_probabilities=[serial(Fraction(3,4)),serial(Fraction(1,4))],expected_gain_and_cost_decision_disagreements=0,
        positive_gain_probability_policy_target_disagreements=mismatch,positive_gain_probability_policy_strict_regret_cases=strict_regrets,
        mean_exact_regret_over_enumeration=serial(regret_sum/visited),max_exact_regret=serial(max_regret),first_ten_counterexamples=examples,
        enumeration_uniform_average_not_patient_population_effect=True,thresholds_selected_from_results=False,
        real_MRI_or_GT_files_loaded=0,neural_forwards=0,actual_training_updates=0,actual_gpu_updates=0,
        novelty_claimed=False,publication_claim_confirmed=False,elapsed_seconds=time.perf_counter()-started)
    path=OUT/'attempt01.json'
    with path.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    assert path.stat().st_size<5_000_000
    print(json.dumps({k:r[k] for k in ['complete','configurations_enumerated','expected_gain_and_cost_decision_disagreements',
        'positive_gain_probability_policy_target_disagreements','positive_gain_probability_policy_strict_regret_cases','elapsed_seconds']}))
    print(json.dumps(examples[:2],ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
