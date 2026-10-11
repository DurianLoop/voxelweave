"""Paper-informed SSC CPU preparation; explicit replicate boundaries and constant convention."""
import itertools
import numpy as np
OFFSETS=((2,0,0),(-2,0,0),(0,2,0),(0,-2,0),(0,0,2),(0,0,-2))
PAIRS=tuple((a,b) for a,b in itertools.combinations(OFFSETS,2) if sum((u-v)**2 for u,v in zip(a,b))==8)
assert len(PAIRS)==12

def descriptor(image,pairs=PAIRS):
    value=np.asarray(image,dtype=np.float64)
    assert value.ndim==3 and np.isfinite(value).all() and min(value.shape)>6
    padded=np.pad(value,3,mode='edge');distances=[]
    for a,b in pairs:
        av=padded[tuple(slice(2+d,2+d+n+2) for d,n in zip(a,value.shape))]
        bv=padded[tuple(slice(2+d,2+d+n+2) for d,n in zip(b,value.shape))]
        difference=(av-bv)**2
        windows=np.lib.stride_tricks.sliding_window_view(difference,(3,3,3))
        distances.append(windows.mean(axis=(-3,-2,-1)))
    distances=np.stack(distances,axis=-1);variance=distances.mean(axis=-1,keepdims=True)
    safe=np.where(variance>0,variance,1.);minimum=distances.min(axis=-1,keepdims=True)
    return np.exp(-(distances-minimum)/safe).astype(np.float32)

def quantize(descriptor_values):
    x=np.asarray(descriptor_values)
    assert x.shape[-1]==12 and np.isfinite(x).all() and x.min()>=0 and x.max()<=1
    return np.floor(x.astype(np.float64)*5+.5).astype(np.uint8)

def pack(levels):
    q=np.asarray(levels);assert q.shape[-1]==12 and np.issubdtype(q.dtype,np.integer) and q.min()>=0 and q.max()<=5
    result=np.zeros(q.shape[:-1],np.uint64)
    for index in range(12):
        mask=(np.left_shift(np.uint64(1),q[...,index].astype(np.uint64))-np.uint64(1))
        result|=np.left_shift(mask,np.uint64(5*index))
    return result

def hamming_sad(first,second):
    a=np.asarray(first,np.uint64);b=np.asarray(second,np.uint64);assert a.shape==b.shape
    xor=np.bitwise_xor(a,b)
    return np.fromiter((int(v).bit_count()/60 for v in xor.reshape(-1)),dtype=np.float64,count=xor.size).reshape(xor.shape)
