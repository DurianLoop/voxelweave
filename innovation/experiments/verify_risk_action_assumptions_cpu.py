"""Independent scalar Gaussian quadrature for the synthetic risk checks."""
from __future__ import annotations
import hashlib
import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT / 'experiments/risk_action_assumptions_cpu'
SOURCE=OUT / 'attempt_01.json'
NODE=(-math.sqrt(3),0.,math.sqrt(3))
WEIGHT=(1/6,2/3,1/6)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def pair(z1,z2,rho,sigma=.4):
    return sigma*z1, sigma*(rho*z1+math.sqrt(1-rho*rho)*z2)

def outputs(u,v):
    return (.5*u,.5*v),(.5*u+.25*v,.5*v+.25*u)

def squared_to(out,target):
    return sum((a-t)**2 for a,t in zip(out,target))

def quadrature_sure(rho):
    actual=full=diagonal=0.
    for i,j in itertools.product(range(3),repeat=2):
        u,v=pair(NODE[i],NODE[j],rho)
        b,r=outputs(u,v)
        w=WEIGHT[i]*WEIGHT[j]
        actual+=w*(squared_to(b,(0.,0.))-squared_to(r,(0.,0.)))
        residual=squared_to(b,(u,v))-squared_to(r,(u,v))
        diagonal+=w*residual
        full+=w*(residual-rho*.4*.4)
    return {'true_gain':4*actual, 'full_covariance_sure_gain':4*full,
            'diagonal_covariance_sure_gain':4*diagonal,
            'full_sure_minus_actual':4*(full-actual),
            'diagonal_sure_minus_actual':4*(diagonal-actual)}

def quadrature_repetition(gamma):
    actual=noisy=0.
    for indices in itertools.product(range(3),repeat=4):
        u,v=pair(NODE[indices[0]],NODE[indices[1]],.6)
        c,d=pair(NODE[indices[2]],NODE[indices[3]],.6)
        target=(gamma*u+math.sqrt(1-gamma*gamma)*c,
                gamma*v+math.sqrt(1-gamma*gamma)*d)
        b,r=outputs(u,v)
        w=math.prod(WEIGHT[i] for i in indices)
        actual+=w*(squared_to(b,(0.,0.))-squared_to(r,(0.,0.)))
        noisy+=w*(squared_to(b,target)-squared_to(r,target))
    return {'true_gain':4*actual,'noisy_target_gain':4*noisy,'noisy_target_minus_actual':4*(noisy-actual)}

def main():
    result=json.loads(SOURCE.read_text(encoding='utf-8'))
    errors=[]
    exact_checks=[]
    contract=OUT / 'run_contract_attempt_01.json'
    if sha(contract)!=result['contract_sha256']:
        errors.append('Run contract differs')
    for entry in json.loads(contract.read_text(encoding='utf-8'))['files']:
        if sha(ROOT / entry['path'])!=entry['sha256']:
            errors.append('Frozen synthetic input differs: '+entry['path'])
    def check(label,actual,expected):
        gap=abs(actual-expected)
        exact_checks.append({'label':label,'observed':actual,'independent_expected':expected,'abs_error':gap})
        if gap>1e-12:
            errors.append(label)
    for sign,entry in zip((1,-1),result['fixed_mask']['two_truths']):
        check(f'nullspace {sign}',entry['full_gain_mse'],12*(sign*sign-(1-sign)**2)/16)
        check(f'projected base {sign}',entry['base_projected_sse'],0.)
        check(f'projected candidate {sign}',entry['candidate_projected_sse'],0.)
        if entry['observation']!=[0.,0.,0.,0.]:
            errors.append('Observed vector differs')
    phases=result['fixed_mask']['four_phase_enumeration']
    fixed_total=sum((i/16)**2 for i in range(1,17))/16
    check('fixed full risk',phases[0]['fixed_error_full_mse'],fixed_total)
    check('phase weighted fixed',sum(r['fixed_error_inverse_probability_projected_mse'] for r in phases)/4,fixed_total)
    check('phase dependent full',sum(r['dependent_error_full_mse'] for r in phases)/4,.75)
    check('phase dependent measured',sum(r['dependent_error_inverse_probability_projected_mse'] for r in phases)/4,0.)
    for entry in result['sure_conditions']:
        independent=quadrature_sure(entry['rho'])
        for name,value in independent.items():
            check(f'sure rho={entry["rho"]} {name}',entry[name]['exact_expectation'],value)
            stored=entry[name]
            if abs(stored['mean']-value)>6*stored['standard_error']+1e-12:
                errors.append('Stored mean inconsistent with independent quadrature: '+name)
        check(f'sure bias {entry["rho"]}',entry['exact_diagonal_sure_bias'],independent['diagonal_sure_minus_actual'])
    for entry in result['repetition_conditions']:
        independent=quadrature_repetition(entry['gamma'])
        for name,value in independent.items():
            check(f'repetition gamma={entry["gamma"]} {name}',entry[name]['exact_expectation'],value)
            stored=entry[name]
            if abs(stored['mean']-value)>6*stored['standard_error']+1e-12:
                errors.append('Stored mean inconsistent with independent quadrature: '+name)
        check(f'repetition bias {entry["gamma"]}',entry['exact_target_gain_bias'],independent['noisy_target_minus_actual'])
    proof={'checked_utc':datetime.now(timezone.utc).isoformat(),'source_sha256':sha(SOURCE),'verification_script_sha256':sha(__file__),
           'method':'scalar exact degree-two normal quadrature, no source import or matrix trace formula',
           'synthetic_configs_enumerated':3*9+3*81, 'exact_comparisons':exact_checks,'errors':errors,
           'does_not_replay_every_random_draw':True,'independent_patient_validation':False}
    (OUT / 'independent_quadrature_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'configs_enumerated':proof['synthetic_configs_enumerated'],'exact_comparisons':len(exact_checks),
                      'max_exact_difference':max(r['abs_error'] for r in exact_checks),'errors':errors},indent=2))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
