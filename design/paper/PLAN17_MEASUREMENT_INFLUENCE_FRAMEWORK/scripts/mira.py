"""Minimal reusable Measurement-Influence Reliability Audit (NumPy only).

An estimator is a callable F({physical_anchor_id: array}, target_location).
Weights, preprocessing and model mode must be fixed by the caller. This API
does not train a model or certify correctness without retrospective targets.
"""
from typing import Callable,Mapping
import numpy as np

def embedded_response_cosine(a,b):
    """Mappings anchor -> [seed, ...output dimensions]; all anchors in energy."""
    shared=set(a)&set(b)
    dot=sum(float(np.sum(np.asarray(a[j],float)*b[j])) for j in shared)
    ea=sum(float(np.sum(np.asarray(v,float)**2)) for v in a.values())
    eb=sum(float(np.sum(np.asarray(v,float)**2)) for v in b.values())
    return dot/np.sqrt(ea*eb) if ea>0 and eb>0 else float('nan')

def audit_pair(estimator:Callable,context_a:Mapping,context_b:Mapping,target_location,
               *,amplitude:float,seeds=(6101,6102,6103,6104),support=None,
               support_source='fixed',normalization_source='acquired',target=None):
    """Run Algorithm 1's prediction/influence/evaluation components.

    `amplitude` is in the estimator input's declared units. A stability audit
    calls this function at all declared settings; it cannot be inferred from
    one pair. Target/support provenance flags expose, rather than conceal,
    retrospective information use. Statistical aggregation is caller-owned.
    """
    if not np.isfinite(amplitude) or amplitude==0 or not seeds:raise ValueError('Finite nonzero amplitude and seeds required')
    if support_source not in {'fixed','acquired','prediction','target'}:raise ValueError('Unknown support provenance')
    if normalization_source not in {'fixed','acquired','full_target_volume'}:raise ValueError('Unknown scale provenance')
    if target_location in context_a or target_location in context_b:raise ValueError('Target cannot be an acquired anchor')
    for j in set(context_a)&set(context_b):
        if not np.array_equal(context_a[j],context_b[j]):raise ValueError('Shared anchor ID has inconsistent values')
    # Defensive copies prevent a mutating wrapper from changing the input registry.
    def run(c):
        out=np.asarray(estimator({j:np.asarray(v).copy() for j,v in c.items()},target_location),float)
        if not np.isfinite(out).all():raise ValueError('Non-finite prediction')
        return out
    a=run(context_a);b=run(context_b)
    if a.shape!=b.shape:raise ValueError('Predictions must have identical target shape')
    m=np.ones(a.shape,bool) if support is None else np.asarray(support,bool)
    if m.shape!=a.shape or not m.any():raise ValueError('Empty or incompatible support')
    responses=[]
    for context,base in [(context_a,a),(context_b,b)]:
        rr={}
        for j,x in context.items():
            rr[j]=[]
            for seed in seeds:
                field=np.random.default_rng(seed).choice([-1.,1.],size=np.asarray(x).shape);field-=field.mean()
                pert={k:np.asarray(v,float).copy() for k,v in context.items()};pert[j]+=amplitude*field
                rr[j].append((run(pert)-base)[m])
            rr[j]=np.stack(rr[j])
        responses.append(rr)
    delta=a[m]-b[m]
    result={'prediction_a':a,'prediction_b':b,'disagreement_mae':float(np.mean(abs(delta))),
            'disagreement_energy':float(delta@delta),'influence':embedded_response_cosine(*responses),
            'shared_anchors':sorted(set(context_a)&set(context_b)),
            'target_free_score_contract':support_source!='target' and normalization_source!='full_target_volume',
            'support_source':support_source,'normalization_source':normalization_source,
            'stability':'not assessed from a single setting'}
    if target is not None:
        y=np.asarray(target,float)
        if y.shape!=a.shape or not np.isfinite(y).all():raise ValueError('Invalid evaluation target')
        ea=(a-y)[m];eb=(b-y)[m];T=.5*(ea@ea+eb@eb)
        result['evaluation']={'paired_mae':float(.5*(abs(ea).mean()+abs(eb).mean())),
             'observable_fraction':float(.25*np.sum((ea-eb)**2)/T) if T>0 else float('nan'),
             'shared_fraction':float(.25*np.sum((ea+eb)**2)/T) if T>0 else float('nan'),
             'error_cosine':float(ea@eb/np.sqrt((ea@ea)*(eb@eb))) if (ea@ea)*(eb@eb)>0 else float('nan')}
    return result
