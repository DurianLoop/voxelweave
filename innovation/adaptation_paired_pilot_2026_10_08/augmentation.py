"""Standard intensity augmentation; deterministic primitives independent of image values."""
import numpy as np

def primitives(step, batch=2):
    rng = np.random.default_rng(np.random.SeedSequence([20261007, 20261008, 713, step]))
    return [dict(gamma_enabled=bool(rng.random()<.3), gamma=float(rng.uniform(.7,1.5)),
                 bias_enabled=bool(rng.random()<.3), bias_coefficients=rng.uniform(-.3,.3,3).tolist(),
                 noise_enabled=bool(rng.random()<.3), noise_std=float(rng.uniform(0,.08)),
                 noise_seed=int(rng.integers(0,2**32))) for _ in range(batch)]

def apply(x, records):
    assert x.dtype==np.float32 and x.ndim==5 and x.shape[1]==1 and len(records)==len(x)
    out=x.copy()
    axes=[np.linspace(-1,1,n,dtype=np.float32) for n in x.shape[2:]]
    for i,p in enumerate(records):
        a=out[i,0]
        if p['gamma_enabled']:
            lo,hi=float(a.min()),float(a.max()); mu=float(a.mean()); sd=float(a.std())
            if hi>lo and sd>0:
                b=((a-lo)/(hi-lo))**p['gamma']; bsd=float(b.std())
                if bsd>0: a[:]=(b-float(b.mean()))*(sd/bsd)+mu
        if p['bias_enabled']:
            c=np.asarray(p['bias_coefficients'],dtype=np.float32)
            field=c[0]*axes[0][:,None,None]+c[1]*axes[1][None,:,None]+c[2]*axes[2][None,None,:]
            a*=np.exp(field)
        if p['noise_enabled']:
            rng=np.random.default_rng(p['noise_seed'])
            a+=rng.standard_normal(a.shape,dtype=np.float32)*p['noise_std']
    assert out.dtype==x.dtype and np.isfinite(out).all()
    return out
