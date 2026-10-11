"""Candidate: rational-grid two-stage interpolation with outward intervals and exact fallback."""
import itertools,time
from fractions import Fraction
import numpy as np

AXES={'throughplane':(0,),'inplane':(1,2),'allaxes':(0,1,2)}

def shapes(grid,primitive,mode):
    fine=tuple(map(int,grid['unpadded_shape_zrc']));factor=1.1+.4*((float(primitive['scale'])-.85)/.30)
    assert all(n>=1 for n in fine) and 1.1-1e-12<=factor<=1.5+1e-12
    coarse=tuple(min(n,max(2,int(np.floor((n-1)/factor+.5))+1)) if n>1 and a in AXES[mode] and primitive['enabled'] else n for a,n in enumerate(fine))
    return fine,coarse

def rational_axis(numerator,denominator,length):
    numerator=np.asarray(numerator,dtype=np.int64);assert denominator>=1 and np.all(numerator>=0)
    low,rem=np.divmod(numerator,denominator);assert low.max(initial=0)<length
    high=np.minimum(low+1,length-1);assert np.all((rem==0)|(high>low))
    return low,high,rem,denominator

def multiply_nonnegative_interval(lo,hi,wl,wh):
    lower=np.minimum(lo*wl,lo*wh);upper=np.maximum(hi*wl,hi*wh)
    return np.nextafter(lower,-np.inf),np.nextafter(upper,np.inf)

def mix_axis(lo,hi,spec,axis):
    lower,upper,remainder,denominator=spec
    a_lo=np.take(lo,lower,axis=axis);a_hi=np.take(hi,lower,axis=axis)
    b_lo=np.take(lo,upper,axis=axis);b_hi=np.take(hi,upper,axis=axis)
    dimensions=[1]*lo.ndim;dimensions[axis]=len(lower)
    w=(remainder/denominator).reshape(dimensions);c=((denominator-remainder)/denominator).reshape(dimensions)
    wl,wh=np.nextafter(w,-np.inf),np.nextafter(w,np.inf)
    cl,ch=np.nextafter(c,-np.inf),np.nextafter(c,np.inf)
    al,ah=multiply_nonnegative_interval(a_lo,a_hi,cl,ch)
    bl,bh=multiply_nonnegative_interval(b_lo,b_hi,wl,wh)
    out_lo=np.nextafter(al+bl,-np.inf);out_hi=np.nextafter(ah+bh,np.inf)
    exact_node=(remainder==0).reshape(dimensions)
    return np.where(exact_node,a_lo,out_lo),np.where(exact_node,a_hi,out_hi)

def exact_nested_point(source,fine,coarse,query):
    def nodes(position,n,m):
        if n==1:return [(0,Fraction(1))]
        value=Fraction(position*(m-1),n-1);lo=value.numerator//value.denominator;weight=value-lo
        return [(lo,1-weight)] if weight==0 else [(lo,1-weight),(lo+1,weight)]
    def coarse_value(position):
        axis=[]
        for a,k in enumerate(position):
            value=Fraction(k*(fine[a]-1),coarse[a]-1) if coarse[a]>1 else Fraction(0)
            lo=value.numerator//value.denominator;weight=value-lo
            axis.append([(lo,1-weight)] if weight==0 else [(lo,1-weight),(lo+1,weight)])
        total=Fraction(0)
        for combo in itertools.product(*axis):
            coord=tuple(v[0] for v in combo);weight=np.prod([v[1] for v in combo])
            total+=Fraction(float(source[coord]))*weight
        return total
    total=Fraction(0)
    for combo in itertools.product(*[nodes(query[a],fine[a],coarse[a]) for a in range(3)]):
        weight=np.prod([v[1] for v in combo]);total+=coarse_value(tuple(v[0] for v in combo))*weight
    return total

def round_fraction32(value):
    guess=np.float32(float(value))
    candidates=[np.nextafter(guess,np.float32(-np.inf)),guess,np.nextafter(guess,np.float32(np.inf))]
    ranked=[]
    for candidate in candidates:
        if np.isfinite(candidate):ranked.append((abs(Fraction(float(candidate))-value),int(np.asarray(candidate).view(np.uint32))%2,candidate))
    result=min(ranked,key=lambda row:(row[0],row[1]))[2]
    return np.float32(0) if result==0 else result

def interpolate(source,coarse,queries,include_intervals=False):
    assert source.dtype==np.float32 and source.ndim==3 and np.isfinite(source).all()
    fine=source.shape;lo=source.astype(np.float64);hi=lo.copy()
    for a,(n,m) in enumerate(zip(fine,coarse)):
        assert 1<=m<=n
        if n==m:continue
        spec=rational_axis(np.arange(m,dtype=np.int64)*(n-1),max(1,m-1),n)
        lo,hi=mix_axis(lo,hi,spec,a)
    for a,(n,m,q) in enumerate(zip(fine,coarse,queries)):
        q=np.asarray(q,dtype=np.int64);assert np.all((0<=q)&(q<n))
        spec=rational_axis(q*(m-1),max(1,n-1),m)
        lo,hi=mix_axis(lo,hi,spec,a)
    assert np.isfinite(lo).all() and np.isfinite(hi).all() and np.all(lo<=hi)
    lower=lo.astype(np.float32);upper=hi.astype(np.float32);stable=lower==upper
    result=lower.copy();result[result==0]=np.float32(0)
    ambiguous=np.argwhere(~stable);examples=[]
    for local in ambiguous:
        query=tuple(int(queries[a][int(local[a])]) for a in range(3));exact=exact_nested_point(source,fine,coarse,query)
        index=tuple(map(int,local));assert Fraction(float(lo[index]))<=exact<=Fraction(float(hi[index]))
        result[index]=round_fraction32(exact)
        if len(examples)<5:examples.append(dict(local=list(index),query=list(query),exact=str(exact),lower=float(lo[index]),upper=float(hi[index]),rounded=float(result[index])))
    metadata=dict(target_voxels=int(result.size),stable_rounding_voxels=int(stable.sum()),exact_fallback_voxels=len(ambiguous),
                  max_interval_width=float(np.max(hi-lo,initial=0)),fallback_examples=examples)
    if include_intervals:return result,metadata,(lo,hi)
    return result,metadata

def apply(cache,grid,geometry,primitive,mode,patch_shape=(64,128,128),include_intervals=False):
    started=time.perf_counter();fine,coarse=shapes(grid,primitive,mode);padding=np.asarray(grid['padding'])
    assert np.array_equal(np.asarray(cache.shape),np.asarray(fine)+padding.sum(axis=1))
    baseline=cache[tuple(slice(int(s),int(s)+int(k)) for s,k in zip(geometry['start'],patch_shape))].copy()
    assert baseline.shape==tuple(patch_shape)
    for a,flip in enumerate(geometry['flips']):
        if flip:baseline=np.flip(baseline,a)
    baseline=(np.ascontiguousarray(baseline)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    result=baseline.copy();support=np.zeros(patch_shape,np.float64);queries=[];local=[]
    for a,k in enumerate(patch_shape):
        positions=int(geometry['start'][a])+np.arange(k,dtype=np.int64)
        if geometry['flips'][a]:positions=positions[::-1]
        positions-=int(padding[a,0]);accepted=np.flatnonzero((positions>=0)&(positions<fine[a]))
        local.append(accepted);queries.append(positions[accepted])
    valid=int(np.prod([len(v) for v in local]));meta=dict(fine_shape=list(fine),coarse_shape=list(coarse),validity_voxels=valid,
        exact_fallback_voxels=0,stable_rounding_voxels=0,max_interval_width=0.,active=bool(primitive['enabled']),canonical_interpolated_zero=True)
    bounds=None
    if valid:
        target=np.ix_(*local);support[target]=1.
        if primitive['enabled']:
            source=cache[tuple(slice(int(p[0]),int(p[0])+int(n)) for p,n in zip(padding,fine))]
            values=interpolate(source,coarse,queries,include_intervals)
            if include_intervals:raw,details,bounds=values
            else:raw,details=values
            result[target]=(raw*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
            meta.update(details)
    assert np.isfinite(result).all();meta['elapsed_seconds']=time.perf_counter()-started
    if include_intervals:return result,support,meta,dict(queries=queries,local=local,bounds=bounds)
    return result,support,meta
