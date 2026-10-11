"""Paired supervised training draws and target-free two-channel full-FOV inference."""
from dataclasses import dataclass
import numpy as np
from mc_rc_3d_baseline_v2_2026_10_07 import PATCH,torch,F,tile_plan,blending_weight,array_sha
from mc_rc_3d_direct_observed_2026_10_07 import augment_pair

@dataclass(frozen=True)
class TrainingDraw:
    forced_foreground:bool
    center:tuple
    start:tuple
    flips:tuple
    intensity_scale:float
    intensity_shift:float
    target_foreground:int

def draw_training_batch(target,rng,patch=PATCH):
    assert target.ndim==3 and np.isfinite(target).all() and np.isin(target,[0,1]).all()
    assert len(patch)==3 and all(p>0 and n>=p for n,p in zip(target.shape,patch))
    foreground=np.argwhere(target>0);assert len(foreground),'Forced-foreground sampler requires a supervised foreground'
    draws=[]
    for force in (True,False):
        center=foreground[int(rng.integers(len(foreground)))] if force else np.asarray([rng.integers(n) for n in target.shape])
        at=np.clip(center-np.asarray(patch)//2,0,np.asarray(target.shape)-patch).astype(int)
        sl=tuple(slice(int(s),int(s)+int(p)) for s,p in zip(at,patch))
        flags=tuple(bool(rng.random()<.5) for axis in range(3))
        scale=float(rng.uniform(.9,1.1));shift=float(rng.uniform(-.1,.1))
        draws.append(TrainingDraw(force,tuple(map(int,center)),tuple(map(int,at)),flags,scale,shift,int(target[sl].sum())))
    assert draws[0].target_foreground>0
    return tuple(draws)

def apply_training_draws(value,availability,valid_grid,target,draws,kind,patch=PATCH):
    assert kind in ('dense','direct') and len(draws)==2
    assert value.shape==availability.shape==valid_grid.shape==target.shape and value.ndim==3
    assert all(a.dtype==np.float32 for a in (value,availability,valid_grid,target))
    assert all(np.isfinite(a).all() for a in (value,availability,valid_grid,target))
    assert np.min(availability)>=0 and np.max(availability)<=1 and np.isin(valid_grid,[0,1]).all()
    assert np.isin(target,[0,1]).all() and np.all(availability[valid_grid==0]==0)
    xs=[];ys=[]
    for draw in draws:
        assert isinstance(draw,TrainingDraw) and all(0<=s<=n-p for s,n,p in zip(draw.start,value.shape,patch))
        sl=tuple(slice(s,s+p) for s,p in zip(draw.start,patch))
        x=augment_pair(value[sl],availability[sl],valid_grid[sl],draw.intensity_scale,draw.intensity_shift,kind,draw.flips)
        y=target[sl]
        for axis,flag in enumerate(draw.flips):
            if flag:y=np.flip(y,axis)
        y=np.ascontiguousarray(y);assert int(y.sum())==draw.target_foreground
        xs.append(x);ys.append(y)
    return torch.from_numpy(np.stack(xs)),torch.from_numpy(np.stack(ys)[:,None])

def infer_two_channel_full_fov(model,value,availability,grid,native_shape_rcz,device='cpu',patch=PATCH):
    """No target/label/ROI argument. Original blend and pixel-center return map."""
    assert value.shape==availability.shape and value.ndim==3
    assert value.dtype==availability.dtype==np.float32
    assert np.isfinite(value).all() and np.isfinite(availability).all()
    assert float(availability.min())>=0 and float(availability.max())<=1
    assert len(grid['padding'])==3 and len(native_shape_rcz)==3 and min(native_shape_rcz)>0
    assert tuple(n+lo+hi for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))==value.shape
    model.eval();locations,axes=tile_plan(value.shape,patch);weight=blending_weight(patch)
    sums=np.zeros(value.shape,dtype=np.float64);coverage=np.zeros_like(sums);tiles=[];calls=0
    with torch.inference_mode():
        for offset in range(0,len(locations),2):
            chunk=locations[offset:offset+2]
            cuts=[tuple(slice(s,s+p) for s,p in zip(start,patch)) for start in chunk]
            inputs=np.stack([np.stack([value[cut],availability[cut]]) for cut in cuts])
            probabilities=model(torch.from_numpy(inputs).to(device))[0].sigmoid().cpu().numpy()[:,0];calls+=1
            assert probabilities.shape==(len(chunk),*patch) and np.isfinite(probabilities).all()
            for start,cut,p in zip(chunk,cuts,probabilities):
                sums[cut]+=p*weight;coverage[cut]+=weight
                tiles.append(dict(start=list(start),probability_sha256=array_sha(p)))
    assert float(coverage.min())>0
    crop=tuple(slice(lo,lo+n) for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))
    physical=np.ascontiguousarray((sums/coverage)[crop],dtype=np.float32)
    with torch.no_grad():
        mapped=F.interpolate(torch.from_numpy(physical)[None,None],
            size=(native_shape_rcz[2],native_shape_rcz[0],native_shape_rcz[1]),mode='trilinear',align_corners=False)[0,0].numpy()
    native=np.ascontiguousarray(mapped.transpose(1,2,0))
    metadata=dict(shape_zrc=list(value.shape),axis_starts=axes,total_tiles=len(locations),forward_calls=calls,
        input_channels=2,coverage_min=float(coverage.min()),coverage_max=float(coverage.max()),coverage_sha256=array_sha(coverage),
        physical_probability_sha256=array_sha(physical),native_probability_sha256=array_sha(native),
        blend_weight_sha256=array_sha(weight),full_fov=True,label_used_for_inference=False,threshold=.5,tiles=tiles)
    return native,physical,metadata
