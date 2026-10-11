"""Exact finite-mask toy audit; no MRI/GPU or third-party model imports."""
from __future__ import annotations
import hashlib
import itertools
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mask_dependent_action_ranking_cpu'
PLAN=ROOT/'MASK_DEPENDENT_ACTION_RANKING_CPU_PLAN_2026-10-02.md'
BODY=ROOT/'literature/source_cache/author_repo_and_mslesseg_2026-10-02/ensure_long_attempt_01_maintext.txt'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True)
    attempt=len(list(OUT.glob('attempt_*.json')))+1
    masks=list(itertools.product((0,1),repeat=3))
    actions=list(itertools.product((0.,.5,1.),(0.,.5,1.,2.)))
    risks, pairs, controls=[],[],[]
    for sid,(signal,p) in enumerate(itertools.product(((1.,1.,1.),(.5,1.,2.),(2.,1.,.5)),itertools.product((.25,.5,.75),repeat=3))):
        pm=[math.prod(pi if mi else 1-pi for pi,mi in zip(p,m)) for m in masks]
        local=[]
        for aid,(a,b) in enumerate(actions):
            sq=[[((a*mi*xi+b*(1-mi))-xi)**2 for mi,xi in zip(m,signal)] for m in masks]
            risk=sum(w*sum(e) for w,e in zip(pm,sq))
            projected=sum(w*sum(mi*ei/pi for mi,ei,pi in zip(m,e,p)) for w,m,e in zip(pm,masks,sq))
            cov=[sum(w*m[i]*e[i] for w,m,e in zip(pm,masks,sq))-p[i]*sum(w*e[i] for w,e in zip(pm,sq)) for i in range(3)]
            bias=sum(ci/pi for ci,pi in zip(cov,p))
            independent=sum(wm*wt*sum(ti*ei/pi for ti,ei,pi in zip(t,e,p))
                            for wm,e in zip(pm,sq) for wt,t in zip(pm,masks))
            row={'scenario':sid,'signal':list(signal),'probabilities':list(p),'action':aid,'a':a,'b':b,
                 'full_risk':risk,'same_mask_weighted_risk':projected,'covariances':cov,'covariance_bias':bias,
                 'independent_mask_weighted_risk':independent,'squared_errors_by_mask':sq}
            risks.append(row);local.append(row)
        for left,right in itertools.combinations(local,2):
            dr=right['full_risk']-left['full_risk']; dj=right['same_mask_weighted_risk']-left['same_mask_weighted_risk']
            pairs.append({'scenario':sid,'left_action':left['action'],'right_action':right['action'],
                          'delta_full_risk':dr,'delta_same_mask_weighted_risk':dj,
                          'delta_covariance_bias':right['covariance_bias']-left['covariance_bias'],
                          'strict_ranking_reversal':dr*dj < -1e-12,'weighted_tie':abs(dj)<=1e-12})
        for b in (0.,.5,1.,2.):
            sq=[(b-xi)**2 for xi in signal]; risk=sum(sq)
            weighted=sum(w*sum(mi*ei/pi for mi,ei,pi in zip(m,sq,p)) for w,m in zip(pm,masks))
            controls.append({'scenario':sid,'b':b,'full_risk':risk,'same_mask_weighted_risk':weighted})
    errors=[]
    identity=max(abs(r['same_mask_weighted_risk']-r['full_risk']-r['covariance_bias']) for r in risks)
    independent=max(abs(r['independent_mask_weighted_risk']-r['full_risk']) for r in risks)
    pair_error=max(abs(r['delta_same_mask_weighted_risk']-r['delta_full_risk']-r['delta_covariance_bias']) for r in pairs)
    control_error=max(abs(r['same_mask_weighted_risk']-r['full_risk']) for r in controls)
    if max(identity,independent,pair_error,control_error)>1e-10: errors.append('Finite enumeration identity tolerance failed')
    result={'attempt':attempt,'created_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha(__file__),
            'plan_sha256':sha(PLAN),'ensure_long_body_sha256':sha(BODY),'scope':'synthetic masks; not patient evidence or ENSURE training reproduction',
            'scenarios':81,'actions_per_scenario':12,'risk_records':risks,'pairs':pairs,'constant_controls':controls,
            'strict_pair_ranking_reversals':sum(r['strict_ranking_reversal'] for r in pairs),
            'weighted_pair_ties':sum(r['weighted_tie'] for r in pairs),
            'max_covariance_identity_error':identity,'max_independent_mask_error':independent,
            'max_pair_identity_error':pair_error,'max_constant_control_error':control_error,
            'patient_inputs':0,'cuda_used':False,'errors':errors,'complete':not errors}
    (OUT/f'attempt_{attempt:02d}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('risk_records','pairs','constant_controls')},ensure_ascii=False,indent=2))
    return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
