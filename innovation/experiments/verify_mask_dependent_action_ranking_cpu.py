"""Independent rational closed-form verification, without importing experiment."""
from __future__ import annotations
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/mask_dependent_action_ranking_cpu'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def f(x):
    return Fraction(str(x))

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path=OUT/'attempt_01.json'; data=json.loads(path.read_text(encoding='utf-8'))
    errors=[]; closed={}; maxerr=0.
    for row in data['risk_records']:
        p=list(map(f,row['probabilities'])); x=list(map(f,row['signal'])); a,b=f(row['a']),f(row['b'])
        observed=[((a-1)*xi)**2 for xi in x]; missed=[(b-xi)**2 for xi in x]
        full=sum(pi*oi+(1-pi)*mi for pi,oi,mi in zip(p,observed,missed))
        weighted=sum(observed);bias=sum((1-pi)*(oi-mi) for pi,oi,mi in zip(p,observed,missed))
        for field,value in [('full_risk',full),('same_mask_weighted_risk',weighted),('covariance_bias',bias),('independent_mask_weighted_risk',full)]:
            delta=abs(row[field]-float(value)); maxerr=max(maxerr,delta)
            if delta>1e-10:errors.append(f'Closed form differs: {row["scenario"]}/{row["action"]}/{field}')
        if weighted-full!=bias:errors.append('Rational covariance identity failed')
        closed[(row['scenario'],row['action'])]=(full,weighted,bias)
    reversed_count=0;ties=0
    for row in data['pairs']:
        l,r=closed[(row['scenario'],row['left_action'])],closed[(row['scenario'],row['right_action'])]
        dr,dj,db=[r[i]-l[i] for i in range(3)];reversal=dr*dj<0;tie=dj==0
        reversed_count+=reversal;ties+=tie
        if row['strict_ranking_reversal']!=reversal or row['weighted_tie']!=tie:errors.append('Pair classification differs')
        for field,value in [('delta_full_risk',dr),('delta_same_mask_weighted_risk',dj),('delta_covariance_bias',db)]:
            delta=abs(row[field]-float(value));maxerr=max(maxerr,delta)
            if delta>1e-10:errors.append('Pair closed form differs')
        if dj-dr!=db:errors.append('Rational pair identity failed')
    if len(closed)!=972 or len(data['pairs'])!=5346 or len(data['constant_controls'])!=324:errors.append('Frozen grid count differs')
    for row in data['constant_controls']:
        x=next(r['signal'] for r in data['risk_records'] if r['scenario']==row['scenario'])
        expected=sum((f(row['b'])-f(xi))**2 for xi in x)
        if max(abs(row[k]-float(expected)) for k in ('full_risk','same_mask_weighted_risk'))>1e-10:errors.append('Constant control differs')
    proof={'scope':'independent rational closed form; not per-draw patient verification','source_sha256':sha(path),
           'verification_script_sha256':sha(__file__),'risks_checked':len(closed),'pairs_checked':len(data['pairs']),
           'constant_controls_checked':len(data['constant_controls']),'strict_pair_ranking_reversals':reversed_count,
           'weighted_pair_ties':ties,'max_absolute_float_difference':maxerr,'errors':errors}
    (OUT/'independent_fraction_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(proof,indent=2));return int(bool(errors))

if __name__=='__main__':
    raise SystemExit(main())
