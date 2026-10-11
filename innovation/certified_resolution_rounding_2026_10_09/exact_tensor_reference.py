"""Independent rational oracle: collapsed one-axis weights and direct fine-grid tensor sum."""
import itertools,math,struct
from fractions import Fraction as Q
import numpy as np

def dimensions(shape,scale,enabled,mode):
    affected={'throughplane':{0},'inplane':{1,2},'allaxes':{0,1,2}}[mode]
    requested=1.1+.4*((float(scale)-.85)/.30)
    return tuple(min(n,max(2,math.floor((n-1)/requested+.5)+1)) if enabled and a in affected and n>1 else n for a,n in enumerate(shape))

def combined_weights(n,m,j):
    if n==1:return {0:Q(1)}
    coarse_position=Q(j*(m-1),n-1);lower=coarse_position.numerator//coarse_position.denominator;fraction=coarse_position-lower
    coarse_weights={lower:1-fraction}
    if fraction:coarse_weights[lower+1]=fraction
    fine_weights={}
    for k,w in coarse_weights.items():
        coordinate=Q(k*(n-1),m-1) if m>1 else Q(0)
        start=coordinate.numerator//coordinate.denominator;t=coordinate-start
        fine_weights[start]=fine_weights.get(start,Q(0))+w*(1-t)
        if t:fine_weights[start+1]=fine_weights.get(start+1,Q(0))+w*t
    assert sum(fine_weights.values())==1 and all(w>=0 for w in fine_weights.values())
    return {k:w for k,w in fine_weights.items() if w}

def point(source,coarse,query):
    axes=[combined_weights(n,m,j) for n,m,j in zip(source.shape,coarse,query)];total=Q(0)
    for index in itertools.product(*[list(axis) for axis in axes]):
        weight=axes[0][index[0]]*axes[1][index[1]]*axes[2][index[2]]
        value=Q(*float(source[index]).as_integer_ratio());total+=weight*value
    return total

def from_bits(bits):return struct.unpack('!f',struct.pack('!I',bits))[0]

def nearest_float32(exact):
    if exact==0:return np.float32(0)
    sign=-1 if exact<0 else 1;v=abs(exact);left=0;right=0x7f7fffff
    assert v<=Q(*from_bits(right).as_integer_ratio())
    while left<right:
        middle=(left+right+1)//2
        if Q(*from_bits(middle).as_integer_ratio())<=v:left=middle
        else:right=middle-1
    lower=left;upper=min(left+1,0x7f7fffff)
    dlo=v-Q(*from_bits(lower).as_integer_ratio());dhi=Q(*from_bits(upper).as_integer_ratio())-v
    selected=lower if dlo<dhi or (dlo==dhi and lower%2==0) else upper
    rounded=np.float32(sign*from_bits(selected));return np.float32(0) if rounded==0 else rounded

def patch_reference(cache,grid,geometry,primitive,mode,patch_shape):
    fine=tuple(map(int,grid['unpadded_shape_zrc']));coarse=dimensions(fine,primitive['scale'],primitive['enabled'],mode)
    pad=[int(v[0]) for v in grid['padding']]
    baseline=cache[tuple(slice(int(v),int(v)+int(k)) for v,k in zip(geometry['start'],patch_shape))].copy()
    for axis,flipped in enumerate(geometry['flips']):
        if flipped:baseline=baseline[(slice(None),)*axis+(slice(None,None,-1),)]
    output=(np.ascontiguousarray(baseline)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    source=cache[tuple(slice(p,p+n) for p,n in zip(pad,fine))];support=np.zeros(patch_shape,dtype=bool);exact_values={}
    for target in np.ndindex(*patch_shape):
        query=tuple(int(geometry['start'][a])+(patch_shape[a]-1-target[a] if geometry['flips'][a] else target[a])-pad[a] for a in range(3))
        if not all(0<=v<n for v,n in zip(query,fine)):continue
        support[target]=True
        if not primitive['enabled']:continue
        exact=point(source,coarse,query);raw=nearest_float32(exact)
        output[target]=(np.array([raw],dtype=np.float32)*geometry['intensity_scale']+geometry['intensity_shift'])[0]
        exact_values[target]=exact
    return output,support,exact_values
