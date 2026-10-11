"""Independent collapsed rational weights, outward intervals, separable direct fine-grid sum."""
import sys,time,itertools
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
BASE=Path(__file__).resolve().parent.parent/'certified_resolution_rounding_2026_10_09'
sys.path.insert(0,str(BASE))
from exact_tensor_reference import combined_weights,point,nearest_float32,dimensions
from direct_interval_reference import enclosed_weight

def interpolate_direct(source,coarse,queries,include_intervals=False):
    assert source.dtype==np.float32 and source.ndim==3 and np.isfinite(source).all()
    started=time.perf_counter();axes=[]
    for n,m,query in zip(source.shape,coarse,queries):
        weights=[combined_weights(n,m,int(j)) for j in query];width=max(map(len,weights))
        indices=np.zeros((width,len(query)),np.int64);wl=np.zeros_like(indices,dtype=np.float64);wh=wl.copy()
        for col,values in enumerate(weights):
            for row,(idx,weight) in enumerate(values.items()):indices[row,col]=idx;wl[row,col],wh[row,col]=enclosed_weight(weight)
        axes.append((indices,wl,wh))
    lower=source.astype(np.float64);upper=lower.copy();order=sorted(range(3),key=lambda a:(len(queries[a])/source.shape[a],a));terms=0
    for axis in order:
        indices,wl,wh=axes[axis];shape=list(lower.shape);shape[axis]=len(queries[axis]);outlo=np.zeros(shape,np.float64);outhi=outlo.copy()
        dimensions_shape=[1]*3;dimensions_shape[axis]=len(queries[axis])
        for k in range(len(indices)):
            a=np.take(lower,indices[k],axis=axis);b=np.take(upper,indices[k],axis=axis)
            weightlo=wl[k].reshape(dimensions_shape);weighthi=wh[k].reshape(dimensions_shape);present=weighthi>0
            termlo=np.nextafter(np.minimum(a*weightlo,a*weighthi),-np.inf)
            termhi=np.nextafter(np.maximum(b*weightlo,b*weighthi),np.inf)
            outlo=np.where(present,np.nextafter(outlo+termlo,-np.inf),outlo)
            outhi=np.where(present,np.nextafter(outhi+termhi,np.inf),outhi);terms+=1
        lower,upper=outlo,outhi
    assert np.isfinite(lower).all() and np.isfinite(upper).all() and np.all(lower<=upper)
    lo32=lower.astype(np.float32);hi32=upper.astype(np.float32);stable=lo32==hi32;result=lo32.copy();result[result==0]=np.float32(0)
    points=np.argwhere(~stable)
    for position in points:
        index=tuple(map(int,position));query=tuple(int(queries[a][index[a]]) for a in range(3));exact=point(source,coarse,query)
        assert Q(float(lower[index]))<=exact<=Q(float(upper[index]));result[index]=nearest_float32(exact)
    meta=dict(direct_source_terms=terms,direct_exact_fallback_voxels=len(points),direct_stable_rounding_voxels=int(stable.sum()),
        max_direct_interval_width=float(np.max(upper-lower,initial=0)),axis_order=order,elapsed_seconds=time.perf_counter()-started)
    if include_intervals:return result,meta,(lower,upper)
    return result,meta

def apply_reference(cache,grid,geometry,primitive,mode,patch_shape=(64,128,128),include_intervals=False):
    fine=tuple(map(int,grid['unpadded_shape_zrc']));coarse=dimensions(fine,primitive['scale'],primitive['enabled'],mode);pad=[int(v[0]) for v in grid['padding']]
    base=cache[tuple(slice(int(v),int(v)+int(k)) for v,k in zip(geometry['start'],patch_shape))].copy()
    for axis,flipped in enumerate(geometry['flips']):
        if flipped:base=base[(slice(None),)*axis+(slice(None,None,-1),)]
    output=(np.ascontiguousarray(base)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    support=np.zeros(patch_shape,np.float64);queries=[];local=[]
    for a,k in enumerate(patch_shape):
        seq=np.arange(int(geometry['start'][a])-pad[a],int(geometry['start'][a])-pad[a]+k)
        if geometry['flips'][a]:seq=seq[::-1]
        good=np.flatnonzero((seq>=0)&(seq<fine[a]));queries.append(seq[good]);local.append(good)
    count=int(np.prod([len(v) for v in queries]));meta=dict(validity_voxels=count,direct_exact_fallback_voxels=0,direct_source_terms=0);bounds=None
    if count:
        target=np.ix_(*local);support[target]=1.
        if primitive['enabled']:
            source=cache[tuple(slice(p,p+n) for p,n in zip(pad,fine))];values=interpolate_direct(source,coarse,queries,include_intervals)
            if include_intervals:raw,details,bounds=values
            else:raw,details=values
            output[target]=(raw*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32);meta.update(details)
    if include_intervals:return output,support,meta,dict(queries=queries,local=local,bounds=bounds)
    return output,support,meta
