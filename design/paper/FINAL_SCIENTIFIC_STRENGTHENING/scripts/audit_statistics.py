"""Fresh paired-examination statistics; no historical summary table inputs."""
import numpy as np
from scipy.stats import rankdata

def rho(x,y,axis=-1):
 a=rankdata(x,axis=axis);b=rankdata(y,axis=axis);a-=a.mean(axis=axis,keepdims=True);b-=b.mean(axis=axis,keepdims=True)
 den=np.sqrt((a*a).sum(axis=axis)*(b*b).sum(axis=axis));return np.divide((a*b).sum(axis=axis),den,out=np.full_like(den,np.nan,dtype=float),where=den>0)
def simultaneous(points,reps):
 points=np.asarray(points);reps=np.asarray(reps);eligible=np.isfinite(points)&np.isfinite(reps).any(axis=0);out=np.full((len(points),2),np.nan)
 if not eligible.any():return out,0
 r=reps[:,eligible];ok=np.isfinite(r).all(axis=1);r=r[ok];n=len(r)
 if n<2:return out,n
 p=points[eligible];se=r.std(axis=0,ddof=1);standard=np.divide(abs(r-p),se,out=np.zeros_like(r),where=se>0);q=np.quantile(standard.max(axis=1),.95)
 out[eligible]=np.column_stack([p-q*se,p+q*se]);return out,n
def bootstrap_indices(n,seed,B=5000):return np.random.default_rng(seed).integers(0,n,(B,n))
def weighted_rank(x,w):
 values,codes=np.unique(x,return_inverse=True);mass=np.stack([w[:,codes==i].sum(axis=1) for i in range(len(values))],axis=1)
 return (np.cumsum(mass,axis=1)-.5*mass+.5)[:,codes]
def weighted_rho(x,y,w):
 a=weighted_rank(x,w);b=weighted_rank(y,w);total=w.sum(axis=1,keepdims=True)
 a-=np.sum(w*a,axis=1,keepdims=True)/total;b-=np.sum(w*b,axis=1,keepdims=True)/total
 return np.sum(w*a*b,axis=1)/np.sqrt(np.sum(w*a*a,axis=1)*np.sum(w*b*b,axis=1))
def partial(x,y,c,cases):
 a=rankdata(x);b=rankdata(y);z=np.column_stack([rankdata(v) for v in np.asarray(c).T]);cases=np.asarray(cases)
 for v in np.unique(cases):
  k=cases==v;a[k]-=a[k].mean();b[k]-=b[k].mean();z[k]-=z[k].mean(axis=0)
 z=np.column_stack([np.ones(len(a)),z]);a-=z@np.linalg.lstsq(z,a,rcond=None)[0];b-=z@np.linalg.lstsq(z,b,rcond=None)[0]
 return float(a@b/np.sqrt((a@a)*(b@b)))

def weighted_partial(x,y,c,cases,w):
 # Rows sorted by case; all observations from a case have equal bootstrap weight.
 a=weighted_rank(x,w);b=weighted_rank(y,w);z=np.stack([weighted_rank(v,w) for v in np.asarray(c).T],axis=-1)
 cases=np.asarray(cases)
 for value in np.unique(cases):
  k=cases==value;a[:,k]-=a[:,k].mean(axis=1,keepdims=True);b[:,k]-=b[:,k].mean(axis=1,keepdims=True);z[:,k]-=z[:,k].mean(axis=1,keepdims=True)
 gram=np.einsum('bni,bn,bnj->bij',z,w,z);inverse=np.linalg.pinv(gram)
 coef_a=np.einsum('bij,bj->bi',inverse,np.einsum('bni,bn,bn->bi',z,w,a));coef_b=np.einsum('bij,bj->bi',inverse,np.einsum('bni,bn,bn->bi',z,w,b))
 a-=np.einsum('bni,bi->bn',z,coef_a);b-=np.einsum('bni,bi->bn',z,coef_b)
 return np.sum(w*a*b,axis=1)/np.sqrt(np.sum(w*a*a,axis=1)*np.sum(w*b*b,axis=1))
