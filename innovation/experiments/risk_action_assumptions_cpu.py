"""Fixed synthetic assumption checks, not patient evidence or a new theorem."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT / 'experiments/risk_action_assumptions_cpu'
PLAN=ROOT / 'RISK_ACTION_ASSUMPTION_CPU_PLAN_2026-10-02.md'
N=200_000
SEED=20261002

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def moments(values):
    return {'mean':float(np.mean(values)), 'standard_error':float(np.std(values,ddof=1)/np.sqrt(values.size)), 'n_synthetic_draws':int(values.size)}

def compare(values,expected):
    m=moments(values)
    m.update(exact_expectation=float(expected), discrepancy=float(m['mean']-expected),
             within_fixed_six_se=bool(abs(m['mean']-expected)<=6*m['standard_error']+1e-12))
    return m

def fixed_mask():
    b=np.zeros(16)
    observed=np.arange(0,16,4)
    delta=np.ones(16)
    delta[observed]=0
    r=b+delta
    pairs=[]
    for sign in (1,-1):
        x=b+sign*delta
        pairs.append({'truth_sign':sign, 'observation':x[observed].tolist(),
                      'base_full_mse':float(np.mean((b-x)**2)), 'candidate_full_mse':float(np.mean((r-x)**2)),
                      'full_gain_mse':float(np.mean((b-x)**2-(r-x)**2)),
                      'base_projected_sse':float(np.sum((b[observed]-x[observed])**2)),
                      'candidate_projected_sse':float(np.sum((r[observed]-x[observed])**2))})
    phases=[]
    fixed_error=np.arange(1,17,dtype=float)/16
    for phase in range(4):
        mask=np.arange(16)%4==phase
        dependent_error=(~mask).astype(float)
        phases.append({'phase':phase, 'projection_diagonal':mask.astype(int).tolist(),
                       'fixed_error_full_mse':float(np.mean(fixed_error**2)),
                       'fixed_error_inverse_probability_projected_mse':float(np.sum(fixed_error[mask]**2)/(.25*16)),
                       'dependent_error_full_mse':float(np.mean(dependent_error**2)),
                       'dependent_error_inverse_probability_projected_mse':float(np.sum(dependent_error[mask]**2)/(.25*16))})
    return {'dimension':16,'observed_indices':observed.tolist(),'base':b.tolist(),'candidate':r.tolist(),
            'two_truths':pairs,'four_phase_enumeration':phases,
            'note':'Inverse weighting of a fixed error is a control; the mask-dependent example is not a reproduction or refutation of the complete ENSURE theorem.'}

def run():
    rng=np.random.default_rng(SEED)
    sigma=.4
    swap=np.zeros((8,8))
    for i in range(0,8,2):
        swap[i,i+1]=swap[i+1,i]=1
    lb=.5*np.eye(8)
    lr=lb+.25*swap
    controls=[]
    errors=[]
    for rho in (-.6,0.,.6):
        cov=sigma*sigma*(np.eye(8)+rho*swap)
        diag=np.diag(np.diag(cov))
        chol=np.linalg.cholesky(cov)
        true_gain=[]
        full_sure=[]
        diag_sure=[]
        for start in range(0,N,4096):
            y=rng.standard_normal((min(4096,N-start),8))@chol.T
            b,r=y@lb.T,y@lr.T
            actual=np.sum(b*b-r*r,axis=1)
            residual=np.sum((b-y)**2-(r-y)**2,axis=1)
            true_gain.append(actual)
            full_sure.append(residual+2*np.trace(cov@(lb-lr)))
            diag_sure.append(residual+2*np.trace(diag@(lb-lr)))
        actual=np.concatenate(true_gain)
        full=np.concatenate(full_sure)
        naive=np.concatenate(diag_sure)
        exact=float(np.trace((lb.T@lb-lr.T@lr)@cov))
        bias=float(2*np.trace((diag-cov)@(lb-lr)))
        row={'rho':rho,'sigma':sigma,'covariance':cov.tolist(),'base_linear':lb.tolist(),'candidate_linear':lr.tolist(),
             'gain_unit':'sum squared error, base minus candidate',
             'true_gain':compare(actual,exact),'full_covariance_sure_gain':compare(full,exact),
             'diagonal_covariance_sure_gain':compare(naive,exact+bias),
             'full_sure_minus_actual':compare(full-actual,0.),
             'diagonal_sure_minus_actual':compare(naive-actual,bias),
             'exact_diagonal_sure_bias':bias,
             'exact_expected_gain_sign_reversal':bool(exact*(exact+bias)<0)}
        controls.append(row)
    repetitions=[]
    rho=.6
    cov=sigma*sigma*(np.eye(8)+rho*swap)
    chol=np.linalg.cholesky(cov)
    exact=float(np.trace((lb.T@lb-lr.T@lr)@cov))
    for gamma in (0.,.5,1.):
        true_gain=[]
        target_gain=[]
        for start in range(0,N,4096):
            k=min(4096,N-start)
            e1=rng.standard_normal((k,8))@chol.T
            ei=rng.standard_normal((k,8))@chol.T
            e2=gamma*e1+np.sqrt(1-gamma*gamma)*ei
            b,r=e1@lb.T,e1@lr.T
            true_gain.append(np.sum(b*b-r*r,axis=1))
            target_gain.append(np.sum((b-e2)**2-(r-e2)**2,axis=1))
        actual=np.concatenate(true_gain)
        noisy=np.concatenate(target_gain)
        bias=float(2*gamma*np.trace((lr-lb)@cov))
        repetitions.append({'rho':rho,'gamma':gamma,'cross_repetition_covariance':(gamma*cov).tolist(),
                            'true_gain':compare(actual,exact),'noisy_target_gain':compare(noisy,exact+bias),
                            'noisy_target_minus_actual':compare(noisy-actual,bias),
                            'exact_target_gain_bias':bias,
                            'exact_expected_gain_sign_reversal':bool(exact*(exact+bias)<0)})
    for group in (controls,repetitions):
        for row in group:
            for key,value in row.items():
                if isinstance(value,dict) and 'within_fixed_six_se' in value and not value['within_fixed_six_se']:
                    errors.append(f'Monte Carlo expectation discrepancy: {row.get("rho")} {row.get("gamma")} {key}')
    return {'complete':not errors,'errors':errors,'independent_patient_evidence':False,'new_theorem':False,
            'seed':SEED,'draws_per_condition':N,'cuda_devices_hidden':True,'x':np.zeros(8).tolist(),
            'fixed_mask':fixed_mask(),'sure_conditions':controls,'repetition_conditions':repetitions}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    started=datetime.now(timezone.utc).isoformat()
    contract={'created_utc':started,'scope':'synthetic-only assumption audit',
              'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (PLAN,Path(__file__))]}
    (OUT / f'run_contract_attempt_{attempt:02d}.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    result=run()
    result.update(attempt=attempt,started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
                  plan_sha256=sha(PLAN),script_sha256=sha(__file__),contract_sha256=sha(OUT / f'run_contract_attempt_{attempt:02d}.json'))
    (OUT / f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'complete':result['complete'],'errors':result['errors'],
                     'fixed_mask_gains':[x['full_gain_mse'] for x in result['fixed_mask']['two_truths']],
                     'sure':[{'rho':r['rho'],'true_gain':r['true_gain']['exact_expectation'],'diagonal_gain':r['diagonal_covariance_sure_gain']['exact_expectation']} for r in result['sure_conditions']],
                     'repetitions':[{'gamma':r['gamma'],'true_gain':r['true_gain']['exact_expectation'],'noisy_target_gain':r['noisy_target_gain']['exact_expectation']} for r in result['repetition_conditions']]},indent=2))
    return int(bool(result['errors']))

if __name__=='__main__':
    raise SystemExit(main())
