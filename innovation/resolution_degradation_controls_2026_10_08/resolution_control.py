"""Ordinary image resolution controls on the existing unpadded cache, with inherited padding."""
import time
import numpy as np
import torch
from torch.nn import functional as F
AXES={'throughplane':(0,), 'inplane':(1,2), 'allaxes':(0,1,2)}

def plan(grid,primitive,mode):
    axes=AXES[mode];n=np.asarray(grid['unpadded_shape_zrc'],dtype=np.int64)
    assert n.shape==(3,) and np.all(n>=1)
    u=(float(primitive['scale'])-.85)/.30
    assert -1e-12<=u<=1+1e-12
    factor=1.1+.4*u
    active=bool(primitive['enabled'])
    m=n.copy()
    if active:
        for a in axes:
            if n[a]>1:m[a]=min(n[a],max(2,int(np.floor((n[a]-1)/factor+.5))+1))
    ratios=np.ones(3,dtype=np.float64)
    np.divide(n-1,m-1,out=ratios,where=m>1)
    return dict(mode=mode,active=active,axes=list(axes),requested_factor=factor,
                fine_shape_zrc=n.tolist(),coarse_shape_zrc=m.tolist(),realized_factor_zrc=ratios.tolist(),
                realized_coarse_spacing_zrc_mm=(ratios*np.asarray(grid['realized_spacing_zrc_mm'])).tolist(),
                align_corners=True,singleton_axes=np.flatnonzero(n==1).tolist())

def locations(grid,geometry,patch_shape):
    n=np.asarray(grid['unpadded_shape_zrc']);pad=np.asarray(grid['padding'])[:,0]
    q=[];local=[]
    for a,length in enumerate(patch_shape):
        idx=np.arange(length,dtype=np.int64)
        pos=geometry['start'][a]+(length-1-idx if geometry['flips'][a] else idx)-pad[a]
        good=np.flatnonzero((pos>=0)&(pos<n[a]))
        if len(good):assert np.array_equal(good,np.arange(good[0],good[-1]+1))
        q.append(pos[good]);local.append(good)
    return q,local

def baseline_patch(cache,geometry,patch_shape):
    p=cache[tuple(slice(int(s),int(s)+int(k)) for s,k in zip(geometry['start'],patch_shape))].copy()
    assert tuple(p.shape)==tuple(patch_shape)
    for a,flip in enumerate(geometry['flips']):
        if flip:p=np.flip(p,a)
    return (np.ascontiguousarray(p)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)

def apply(cache,grid,geometry,primitive,mode,patch_shape=(64,128,128)):
    """No labels or model. Numeric diagnostics retain the support channel in both stages."""
    started=time.perf_counter()
    assert cache.dtype==np.float32 and cache.ndim==3 and np.isfinite(cache).all()
    n=np.asarray(grid['unpadded_shape_zrc']);padding=np.asarray(grid['padding'])
    assert np.array_equal(np.asarray(cache.shape),n+padding.sum(axis=1))
    record=plan(grid,primitive,mode);base=baseline_patch(cache,geometry,patch_shape)
    result=base.copy();support=np.zeros(patch_shape,np.float64)
    q,local=locations(grid,geometry,patch_shape)
    valid_shape=tuple(map(len,q));valid_count=int(np.prod(valid_shape))
    metadata=dict(plan=record,labels_accepted=False,model_accepted=False,
                  source_domain='unpadded_resampled_cache_not_observed_slice_certificate',
                  inherited_padding_voxels=int(base.size-valid_count),validity_semantics='mother_domain_no_new_missing_support',
                  first_resample_seconds=0.,second_resample_seconds=0.,first_result_bytes=0,coordinate_grid_bytes=0)
    if valid_count:
        target=tuple(slice(int(a[0]),int(a[-1])+1) for a in local)
        if not record['active']:
            support[target]=1.
        else:
            source=cache[tuple(slice(int(p[0]),int(p[0])+int(k)) for p,k in zip(padding,n))]
            assert source.shape==tuple(n)
            values=np.stack([source.astype(np.float64),np.ones(tuple(n),np.float64)])
            at=time.perf_counter()
            with torch.inference_mode():
                coarse=F.interpolate(torch.from_numpy(values)[None],size=record['coarse_shape_zrc'],mode='trilinear',align_corners=True)
            del values
            metadata['first_resample_seconds']=time.perf_counter()-at
            metadata['first_result_bytes']=coarse.numel()*coarse.element_size()
            coords=[torch.from_numpy((2*pos.astype(np.float64)/(int(k)-1)-1) if k>1 else np.zeros(len(pos),np.float64)) for pos,k in zip(q,n)]
            zz,rr,cc=torch.meshgrid(*coords,indexing='ij');sampling=torch.stack((cc,rr,zz),dim=-1)[None]
            metadata['coordinate_grid_bytes']=sampling.numel()*sampling.element_size()
            at=time.perf_counter()
            with torch.inference_mode():
                output=F.grid_sample(coarse,sampling,mode='bilinear',padding_mode='zeros',align_corners=True)[0].numpy()
            result[target]=(output[0].astype(np.float32)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
            support[target]=output[1]
            metadata['second_resample_seconds']=time.perf_counter()-at
    assert np.isfinite(result).all() and np.isfinite(support).all()
    metadata['elapsed_seconds']=time.perf_counter()-started
    return result,support,metadata
