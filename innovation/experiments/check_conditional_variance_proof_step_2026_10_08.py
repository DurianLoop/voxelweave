"""Exact finite-moment check of a marginal-to-conditional variance implication."""
import hashlib,json,sys,time
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
from mc_rc_reference_resources_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/conditional_variance_proof_step_2026_10_08'


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def encode(x):return dict(fraction=str(x),value=float(x))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    start=time.perf_counter();before=resource_guard()
    p=F(1,20);states=[dict(probability=1-p,y=F(0),noise_mean=F(0),noise_variance=F(0)),
        dict(probability=p,y=F(1),noise_mean=F(0),noise_variance=F(381,20))]
    mean_y=sum(s['probability']*s['y'] for s in states)
    ex=sum(s['probability']*(s['y']-mean_y+s['noise_mean']) for s in states)
    ex2=sum(s['probability']*((s['y']-mean_y)**2+s['noise_variance']) for s in states)
    marginal=ex2-ex*ex
    conditional_mean_variance=sum(s['probability']*(s['y']-mean_y)**2 for s in states)
    average_conditional=sum(s['probability']*s['noise_variance'] for s in states)
    assert ex==0 and marginal==1 and marginal==average_conditional+conditional_mean_variance
    assert average_conditional==F(381,400) and conditional_mean_variance==F(19,400)
    assert max(s['noise_variance'] for s in states)==F(381,20)>marginal
    assert all(s['noise_mean']==0 for s in states)
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(ROOT/'CONDITIONAL_VARIANCE_PROOF_CHECK_PROTOCOL_2026-10-08.md'),
            entry(ROOT/'literature/source_cache/downstream_feature_cost_primary_2026-10-08/noise2same_supplement_page01.txt')],
        exact_moments=dict(mean_X=encode(ex),marginal_variance_X=encode(marginal),
            average_conditional_variance=encode(average_conditional),variance_of_conditional_mean=encode(conditional_mean_variance),
            conditional_variance_at_Y1=encode(states[1]['noise_variance'])),
        marginal_to_pointwise_conditional_variance_implication_disproved=True,
        total_variance_identity_checked_two_paths=True,complete_Noise2Same_theorem1_disproved=False,
        all_paper_mask_and_normalization_assumptions_verified=False,MRI_noise_conditions_verified=False,
        new_statistical_theorem_claimed=False,medical_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,resources_before=before,
        resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-start,
        publication_claim_confirmed=False,goal_status='active')
    assert r['elapsed_seconds']<60
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,exact_moments=r['exact_moments'],complete_theorem1_disproved=False,medical_arrays_loaded=0),ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
