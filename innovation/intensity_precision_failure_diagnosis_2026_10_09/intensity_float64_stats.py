"""Version 2: float64 reductions for gamma statistics; transforms and output remain float32.

Ordinary intensity augmentation, not a new scientific method. The old module
is immutable and continues to supply the original deterministic primitives.
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'adaptation_paired_pilot_2026_10_08'))
import augmentation as legacy
primitives=legacy.primitives

def apply(x,records):
    assert x.dtype==np.float32 and x.ndim==5 and x.shape[1]==1 and len(records)==len(x)
    out=x.copy();axes=[np.linspace(-1,1,n,dtype=np.float32) for n in x.shape[2:]]
    for i,p in enumerate(records):
        a=out[i,0]
        if p['gamma_enabled']:
            lo,hi=float(a.min()),float(a.max())
            mu=float(a.mean(dtype=np.float64));sd=float(a.std(dtype=np.float64))
            if hi>lo and sd>0:
                b=((a-lo)/(hi-lo))**p['gamma']
                bmu=float(b.mean(dtype=np.float64));bsd=float(b.std(dtype=np.float64))
                if bsd>0:a[:]=(b-bmu)*(sd/bsd)+mu
        if p['bias_enabled']:
            c=np.asarray(p['bias_coefficients'],dtype=np.float32)
            field=c[0]*axes[0][:,None,None]+c[1]*axes[1][None,:,None]+c[2]*axes[2][None,None,:]
            a*=np.exp(field)
        if p['noise_enabled']:
            rng=np.random.default_rng(p['noise_seed'])
            a+=rng.standard_normal(a.shape,dtype=np.float32)*p['noise_std']
    assert out.dtype==np.float32 and np.isfinite(out).all()
    return out
