"""Standard 3D task candidate with isolated native-reference and observed-PCHIP inputs."""
import os
for _key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[_key]='1'
import itertools
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from mc_rc_true_native_reference_v2_2026_10_07 import ROOT, read, sha, array_sha, fixed_cases, read_reference, read_reference_label, require_reference_role, resource_guard
from mc_rc_observed_only_training_input import ObservedMRI, reconstruct, stats
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
PATCH = (64,128,128)
SEED = 20261007

def observed_package(case, row):
    require_reference_role(case)
    p = ROOT/row['observed_package']; assert sha(p) == row['observed_package_sha256']
    with np.load(p,allow_pickle=False) as q:
        values = q['observed_rcz'].copy(); indices = tuple(map(int,q['observed_indices']))
        affine = q['affine_rcz_ras']; shape = q['native_shape']
    assert array_sha(values) == row['observed_array_sha256']
    assert np.array_equal(affine,case['affine_rcz_ras']) and np.array_equal(shape,case['native_shape'])
    assert indices == tuple(range(0,int(shape[2]),4))
    values.flags.writeable=False
    return ObservedMRI(values,indices,int(shape[2]),tuple(map(tuple,affine)),(),())

def lattice(case):
    affine = np.asarray(case['affine_rcz_ras'],float)
    spacing = np.linalg.norm(affine[:3,:3],axis=0)
    old = np.asarray(case['native_shape'])[[2,0,1]]
    step = spacing[[2,0,1]]
    new = np.maximum(1,np.rint(old*step/.5).astype(int))
    scale = old/new
    center_map = np.eye(4); center_map[:3,:3] = np.diag(scale); center_map[:3,3] = scale/2-.5
    permutation = np.eye(4); permutation[:3,:3] = np.array([[0,1,0],[0,0,1],[1,0,0]])
    grid_affine = affine@permutation@center_map
    padding = [((max(0,p-int(n)))//2,(max(0,p-int(n))+1)//2) for n,p in zip(new,PATCH)]
    pad_map = np.eye(4); pad_map[:3,3] = -np.array([p[0] for p in padding])
    return dict(unpadded_shape_zrc=new.tolist(),native_shape_zrc=old.tolist(),padding=padding,
                native_coordinate_scale_zrc=scale.tolist(),physical_affine_zrc_ras=grid_affine.tolist(),
                padded_affine_zrc_ras=(grid_affine@pad_map).tolist(),realized_spacing_zrc_mm=(step*scale).tolist())

def physical_mr(normalized_rcz, grid):
    image = torch.from_numpy(np.ascontiguousarray(normalized_rcz.transpose(2,0,1)))[None,None]
    with torch.no_grad(): out = F.interpolate(image,size=grid['unpadded_shape_zrc'],mode='trilinear',align_corners=False)[0,0].numpy()
    return np.pad(out,grid['padding'],mode='constant',constant_values=0).astype(np.float32,copy=False)

def physical_label(label_rcz, grid):
    target = torch.from_numpy(np.ascontiguousarray(label_rcz.transpose(2,0,1),dtype=np.float32))[None,None]
    with torch.no_grad(): out = F.interpolate(target,size=grid['unpadded_shape_zrc'],mode='nearest-exact')[0,0].numpy()
    return np.pad(out,grid['padding'],mode='constant',constant_values=0).astype(np.float32,copy=False)

def source_image(case,row,kind):
    obs = observed_package(case,row); st=stats(obs.pixels)
    if kind == 'raw_pchip':
        raw = reconstruct(obs,'raw_pchip')
        assert array_sha(raw) == row['inputs']['raw_pchip_observed_shared']['raw_reconstruction_sha256']
    elif kind == 'native_reference':
        cert = read(ROOT/'experiments/mc_rc_true_native_reference_attempt02_2026_10_07/attempt_01.json')
        assert cert['complete'] and not cert['errors']
        certified = {x['uid']:x for x in cert['series']}[case['uid']]
        native = read_reference(case); raw = native.full_pixels_rcz
        assert array_sha(raw) == certified['native_array_sha256']
    else: raise ValueError('Unsupported input')
    normalized = ((raw.astype(np.float64)-st['mean'])/st['divisor']).astype(np.float32)
    if kind == 'raw_pchip': assert array_sha(normalized) == row['inputs']['raw_pchip_observed_shared']['normalized_rcz_sha256']
    return normalized, st

class ConvBlock(nn.Module):
    def __init__(self,i,o):
        super().__init__()
        self.layers=nn.Sequential(nn.Conv3d(i,o,3,padding=1,bias=False),nn.InstanceNorm3d(o,affine=True),nn.LeakyReLU(.01),
                                  nn.Conv3d(o,o,3,padding=1,bias=False),nn.InstanceNorm3d(o,affine=True),nn.LeakyReLU(.01))
    def forward(self,x): return self.layers(x)

class TaskUNet3D(nn.Module):
    def __init__(self):
        super().__init__(); channels=(16,32,64,128)
        self.encoders=nn.ModuleList([ConvBlock(1 if i==0 else channels[i-1],c) for i,c in enumerate(channels)])
        self.ups=nn.ModuleList([nn.ConvTranspose3d(channels[i+1],channels[i],2,stride=2) for i in (2,1,0)])
        self.decoders=nn.ModuleList([ConvBlock(2*channels[i],channels[i]) for i in (2,1,0)])
        self.heads=nn.ModuleList([nn.Conv3d(channels[i],1,1) for i in (2,1,0)])
    def forward(self,x):
        skips=[]
        for i,enc in enumerate(self.encoders):
            if i: x=F.max_pool3d(x,2)
            x=enc(x); skips.append(x)
        outputs=[]
        for up,dec,head,skip in zip(self.ups,self.decoders,self.heads,reversed(skips[:-1])):
            x=up(x); assert x.shape[2:]==skip.shape[2:]
            x=dec(torch.cat((x,skip),dim=1)); outputs.append(head(x))
        return tuple(reversed(outputs))

def loss(outputs,target):
    terms=[]
    for output in outputs:
        truth=F.interpolate(target,size=output.shape[2:],mode='nearest-exact')
        probability=output.sigmoid()
        ce=F.binary_cross_entropy_with_logits(output,truth)
        dice=1-(2*(probability*truth).sum()+1)/(probability.sum()+truth.sum()+1)
        terms.append(ce+dice)
    return sum(t*w for t,w in zip(terms,(4/7,2/7,1/7)))

def sample_batch(image,target,rng):
    assert image.shape==target.shape and all(n>=p for n,p in zip(image.shape,PATCH))
    fg=np.argwhere(target>0); assert len(fg)
    locations=[]; xs=[]; ys=[]
    for force in (True,False):
        center=fg[int(rng.integers(len(fg)))] if force else np.asarray([rng.integers(n) for n in image.shape])
        start=np.clip(center-np.asarray(PATCH)//2,0,np.asarray(image.shape)-PATCH).astype(int)
        sl=tuple(slice(int(s),int(s)+p) for s,p in zip(start,PATCH))
        x=image[sl].copy(); y=target[sl].copy(); flips=[]
        for axis in range(3):
            flag=bool(rng.random()<.5); flips.append(flag)
            if flag: x=np.flip(x,axis); y=np.flip(y,axis)
        scale=float(rng.uniform(.9,1.1)); shift=float(rng.uniform(-.1,.1)); x=x*scale+shift
        xs.append(np.ascontiguousarray(x)); ys.append(np.ascontiguousarray(y))
        locations.append(dict(forced_foreground=force,center=center.tolist(),start=start.tolist(),flips=flips,
                              intensity_scale=scale,intensity_shift=shift,target_foreground=int(y.sum())))
    assert locations[0]['target_foreground']>0
    return torch.from_numpy(np.stack(xs)[:,None]),torch.from_numpy(np.stack(ys)[:,None]),locations

def axis_starts(n,p):
    assert n>=p
    return sorted(set(list(range(0,n-p+1,p//2))+[n-p]))

def tile_plan(shape,patch=PATCH):
    starts=[axis_starts(n,p) for n,p in zip(shape,patch)]
    return list(itertools.product(*starts)),starts

def blending_weight(patch=PATCH):
    factors=[np.exp(-.5*((np.arange(p)-(p-1)/2)/(p/8))**2) for p in patch]
    w=np.einsum('i,j,k->ijk',*factors); w/=w.max()
    return np.maximum(w,1e-4).astype(np.float32)

def infer_full_fov(model,image_zrc,grid,native_shape_rcz,device='cpu',patch=PATCH):
    model.eval(); locations,starts=tile_plan(image_zrc.shape,patch); weight=blending_weight(patch)
    sums=np.zeros(image_zrc.shape,dtype=np.float64); coverage=np.zeros_like(sums)
    with torch.inference_mode():
        for at in range(0,len(locations),2):
            chunk=locations[at:at+2]; slabs=[tuple(slice(s,s+p) for s,p in zip(start,patch)) for start in chunk]
            x=torch.from_numpy(np.stack([image_zrc[sl] for sl in slabs])[:,None]).to(device)
            probabilities=model(x)[0].sigmoid().cpu().numpy()[:,0]
            assert probabilities.shape[1:]==patch and np.isfinite(probabilities).all()
            for sl,prob in zip(slabs,probabilities): sums[sl]+=prob*weight; coverage[sl]+=weight
    assert coverage.min()>0
    probs=sums/coverage
    crop=tuple(slice(lo,lo+n) for n,(lo,hi) in zip(grid['unpadded_shape_zrc'],grid['padding']))
    probs=np.ascontiguousarray(probs[crop],dtype=np.float32)
    with torch.no_grad(): mapped=F.interpolate(torch.from_numpy(probs)[None,None],size=(native_shape_rcz[2],native_shape_rcz[0],native_shape_rcz[1]),mode='trilinear',align_corners=False)[0,0].numpy()
    result=np.ascontiguousarray(mapped.transpose(1,2,0))
    return result,dict(shape_zrc=list(image_zrc.shape),axis_starts=starts,total_tiles=len(locations),
                       coverage_min=float(coverage.min()),coverage_max=float(coverage.max()),coverage_sha256=array_sha(coverage),
                       full_fov=True,label_used_for_inference=False,threshold=.5,blend_weight_sha256=array_sha(weight))
