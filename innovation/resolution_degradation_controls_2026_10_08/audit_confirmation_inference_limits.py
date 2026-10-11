"""Exact patient-count inference limits; no unseen data or model evaluation."""
import sys,time,math,itertools
from fractions import Fraction
from pathlib import Path
from scipy.stats import binomtest,beta
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import entry,dump,resource_guard


def exact_sign(wins,n):
    if n==0:return Fraction(1)
    tail=sum(math.comb(n,j) for j in range(min(wins,n-wins)+1))
    return min(Fraction(1),Fraction(2*tail,2**n))


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    journal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    assert size+max(0,1_500_000-journal.stat().st_size)+150_000+100_000+10_000<5_000_000
    out=HERE/'confirmation_inference_limits_attempt01';out.mkdir(exist_ok=False)
    rows=[];max_error=0.
    for n in range(13):
        for wins in range(n+1):
            p=exact_sign(wins,n);reference=float(binomtest(wins,n,.5).pvalue) if n else 1.
            max_error=max(max_error,abs(float(p)-reference));assert abs(float(p)-reference)<=1e-14
            # Every binary vector is independently enumerated for n<=8, a separate check of the tails.
            if 0<n<=8:
                probability=sum(abs(sum(bits)-n/2)>=abs(wins-n/2) for bits in itertools.product([0,1],repeat=n))/2**n
                assert probability==float(p)
            rows.append(dict(n=n,wins=wins,p_numerator=p.numerator,p_denominator=p.denominator,p=float(p)))
    summaries=[]
    for n,label in [(8,'locked_confirmation_patients'),(11,'development_patients_not_confirmation'),(12,'series_miscount_illustration_only')]:
        lower=float(beta.ppf(.025,n,1))
        # For n successes the exact binomial upper-tail probability is lower**n=.025.
        assert abs(lower**n-.025)<=1e-14
        p=exact_sign(n,n)
        summaries.append(dict(n=n,role=label,all_positive_two_sided_sign_p=float(p),
             all_positive95percent_two_sided_CP_lower=lower,
             Bonferroni_minimum_p_by_family_size={str(m):float(min(Fraction(1),m*p)) for m in range(1,9)}))
    ties=[dict(confirmation_patients=8,ties=t,effective_nonzero_patients=8-t,
               all_remaining_positive_two_sided_sign_p=float(exact_sign(8-t,8-t))) for t in range(9)]
    selected=[v for v in rows if v['n']==8 and v['wins']>=6]
    result=dict(complete=True,errors=[],all91_exact_sign_cases_verified=True,
          exact_sign_cases=len(rows),max_scipy_error=max_error,
          summaries=summaries,n8_six_to_eight_wins=selected,confirmation_ties=ties,
          all_patient_binary_vectors_enumerated_n1_to8=True,
          confirmatory_family_and_endpoint_not_selected=True,
          sign_assumption_not_automatically_met_by_MRI=True,
          CP_direction_frequency_not_effect_size_or_no_harm_certificate=True,
          n12_not_an_authorized_independent_denominator=True,
          MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
          confirmation_patients_opened=False,lockedIXI_opened=False,new_medical_effects=0,
          publication_claim_confirmed=False,goal_status='active',
          elapsed_seconds=time.perf_counter()-started,
          source_bindings=[entry(p) for p in [Path(__file__),HERE/'CONFIRMATION_INFERENCE_LIMITS_PROTOCOL_TURN29.md',
              ROOT/'spatial_adaptation_matched_2026_10_08/EVALUATION_PROTOCOL.md',
              ROOT/'literature/2026-10-07_learn_then_test_primary_reading.md',
              ROOT/'literature/2026-10-07_calibration_selection_primary_reading.md']])
    assert len(rows)==91 and result['elapsed_seconds']<120
    dump(out/'receipt.json',result)
    print({k:v for k,v in result.items() if k not in ['source_bindings','confirmation_ties']},flush=True)


if __name__=='__main__':main()
