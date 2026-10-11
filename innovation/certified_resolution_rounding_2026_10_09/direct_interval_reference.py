"""Independent direct stencil oracle; no coarse arrays or candidate implementation calls."""
import itertools,time
from fractions import Fraction as Q
import numpy as np
from exact_tensor_reference import combined_weights,point,nearest_float32,dimensions

def enclosed_weight(exact):
    value=float(exact);value_exact=Q(*value.as_integer_ratio())
    low=value if value_exact<=exact else float(np.nextafter(value,-np.inf))
    high=value if value_exact>=exact else float(np.nextafter(value,np.inf))
    assert Q(*low.as_integer_ratio())<=exact<=Q(*high.as_integer_ratio())
    return low,high

def interpolate_direct(source,coarse,queries,include_intervals=False):
    assert source.dtype==np.float32 and np.isfinite(source).all()
    allaxes=[]
    for n,m,query in zip(source.shape,coarse,queries):
        entries=[combined_weights(n,m,int(j)) for j in query]
        width=max(map(len,entries));indices=np.zeros((width,len(query)),dtype=np.int64)
        wl=np.zeros_like(indices,dtype=np.float64);wh=wl.copy()
        for col,weights in enumerate(entries):
            for row,(index,weight) in enumerate(weights.items()):
                indices[row,col]=index;wl[row,col],wh[row,col]=enclosed_weight(weight)
        allaxes.append((indices,wl,wh))
    shape=tuple(map(len,queries));lower=np.zeros(shape,dtype=np.float64);upper=lower.copy()
    started=time.perf_counter();terms=0
    for choices in itertools.product(*[range(len(axis[0])) for axis in allaxes]):
        index=[axis[0][k] for axis,k in zip(allaxes,choices)]
        weightlow=np.ones(shape,dtype=np.float64);weighthigh=weightlow.copy();nonzero=np.ones(shape,dtype=bool)
        for a,(axis,k) in enumerate(zip(allaxes,choices)):
            reshape=[1]*3;reshape[a]=len(queries[a]);wl=axis[1][k].reshape(reshape);wh=axis[2][k].reshape(reshape)
            nonzero&=wh>0
            weightlow=np.maximum(0,np.nextafter(weightlow*wl,-np.inf));weighthigh=np.nextafter(weighthigh*wh,np.inf)
        values=source[np.ix_(*index)].astype(np.float64)
        termlow=np.nextafter(np.minimum(values*weightlow,values*weighthigh),-np.inf)
        termhigh=np.nextafter(np.maximum(values*weightlow,values*weighthigh),np.inf)
        # Absent terms are exact zero and do not introduce interval widening.
        lower=np.where(nonzero,np.nextafter(lower+termlow,-np.inf),lower)
        upper=np.where(nonzero,np.nextafter(upper+termhigh,np.inf),upper);terms+=1
    assert np.isfinite(lower).all() and np.isfinite(upper).all() and np.all(lower<=upper)
    lo32=lower.astype(np.float32);hi32=upper.astype(np.float32);stable=lo32==hi32
    out=lo32.copy();out[out==0]=np.float32(0);locations=np.argwhere(~stable)
    for index in locations:
        position=tuple(map(int,index));query=tuple(int(queries[a][position[a]]) for a in range(3))
        exact=point(source,coarse,query)
        assert Q(*float(lower[position]).as_integer_ratio())<=exact<=Q(*float(upper[position]).as_integer_ratio())
        out[position]=nearest_float32(exact)
    metadata=dict(direct_source_terms=terms,direct_exact_fallback_voxels=len(locations),
        direct_stable_rounding_voxels=int(stable.sum()),max_direct_interval_width=float(np.max(upper-lower,initial=0)),
        elapsed_seconds=time.perf_counter()-started)
    if include_intervals:return out,metadata,(lower,upper)
    return out,metadata

def apply_reference(cache,grid,geometry,primitive,mode,patch_shape=(64,128,128),include_intervals=False):
    fine=tuple(map(int,grid['unpadded_shape_zrc']));coarse=dimensions(fine,primitive['scale'],primitive['enabled'],mode)
    pad=[int(v[0]) for v in grid['padding']]
    baseline=cache[tuple(slice(int(v),int(v)+int(k)) for v,k in zip(geometry['start'],patch_shape))].copy()
    for axis,flipped in enumerate(geometry['flips']):
        if flipped:baseline=baseline[(slice(None),)*axis+(slice(None,None,-1),)]
    output=(np.ascontiguousarray(baseline)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    support=np.zeros(patch_shape,np.float64);queries=[];local=[]
    for a,k in enumerate(patch_shape):
        seq=np.arange(int(geometry['start'][a])-pad[a],int(geometry['start'][a])-pad[a]+k)
        if geometry['flips'][a]:seq=seq[::-1]
        accepted=np.flatnonzero((seq>=0)&(seq<fine[a]));queries.append(seq[accepted]);local.append(accepted)
    valid=int(np.prod([len(v) for v in queries]));meta=dict(validity_voxels=valid,direct_exact_fallback_voxels=0,direct_source_terms=0)
    bounds=None
    if valid:
        target=np.ix_(*local);support[target]=1.
        if primitive['enabled']:
            source=cache[tuple(slice(p,p+n) for p,n in zip(pad,fine))]
            values=interpolate_direct(source,coarse,queries,include_intervals)
            if include_intervals:raw,details,bounds=values
            else:raw,details=values
            output[target]=(raw*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32);meta.update(details)
    if include_intervals:return output,support,meta,dict(queries=queries,local=local,bounds=bounds)
    return output,support,meta
