"""Evaluate only needed two-stage linear-interpolation nodes with identical interval arithmetic."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'certified_resolution_rounding_2026_10_09'))
import certified_resolution as full
from certified_resolution import np,Fraction

def interpolate(source,coarse,queries,include_intervals=False):
 assert source.dtype==np.float32 and source.ndim==3 and np.isfinite(source).all()
 fine=source.shape;input_nodes=[];stage1=[];stage2=[]
 for n,m,q in zip(fine,coarse,queries):
  q=np.asarray(q,dtype=np.int64);assert np.all((0<=q)&(q<n)) and 1<=m<=n
  c0,c1,rem,den=full.rational_axis(q*(m-1),max(1,n-1),m)
  needed_coarse=np.unique(np.concatenate((c0,c1)))
  f0,f1,frem,fden=full.rational_axis(needed_coarse*(n-1),max(1,m-1),n)
  needed_fine=np.unique(np.concatenate((f0,f1)))
  input_nodes.append(needed_fine)
  stage1.append((np.searchsorted(needed_fine,f0),np.searchsorted(needed_fine,f1),frem,fden))
  stage2.append((np.searchsorted(needed_coarse,c0),np.searchsorted(needed_coarse,c1),rem,den))
 lo=source[np.ix_(*input_nodes)].astype(np.float64);hi=lo.copy()
 selected_input_shape=list(lo.shape)
 for a,(n,m,spec) in enumerate(zip(fine,coarse,stage1)):
  if n!=m:lo,hi=full.mix_axis(lo,hi,spec,a)
 for a,spec in enumerate(stage2):lo,hi=full.mix_axis(lo,hi,spec,a)
 assert np.isfinite(lo).all() and np.isfinite(hi).all() and np.all(lo<=hi)
 lower=lo.astype(np.float32);upper=hi.astype(np.float32);stable=lower==upper
 result=lower.copy();result[result==0]=np.float32(0);ambiguous=np.argwhere(~stable);examples=[]
 for local in ambiguous:
  query=tuple(int(queries[a][int(local[a])]) for a in range(3));exact=full.exact_nested_point(source,fine,coarse,query)
  index=tuple(map(int,local));assert Fraction(float(lo[index]))<=exact<=Fraction(float(hi[index]))
  result[index]=full.round_fraction32(exact)
  if len(examples)<5:examples.append(dict(local=list(index),query=list(query),exact=str(exact),lower=float(lo[index]),upper=float(hi[index]),rounded=float(result[index])))
 metadata=dict(target_voxels=int(result.size),stable_rounding_voxels=int(stable.sum()),exact_fallback_voxels=len(ambiguous),
  max_interval_width=float(np.max(hi-lo,initial=0)),fallback_examples=examples,
  selected_source_shape=selected_input_shape,full_source_voxels=int(source.size),selected_source_voxels=int(np.prod(selected_input_shape)))
 if include_intervals:return result,metadata,(lo,hi)
 return result,metadata

# Copy the inherited apply function with its original global helpers and a substituted interpreter.
# This creates a new function; it does not mutate full.interpolate or full.apply.
import types
namespace=dict(full.apply.__globals__);namespace['interpolate']=interpolate
apply=types.FunctionType(full.apply.__code__,namespace,'selective_apply',full.apply.__defaults__)
