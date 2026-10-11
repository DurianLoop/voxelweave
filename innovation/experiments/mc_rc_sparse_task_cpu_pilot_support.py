"""Frozen CPU-only task pilot components. No native MR or evaluation label enters inference."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,math,hashlib
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from scipy.ndimage import binary_erosion,distance_transform_edt,generate_binary_structure
from mc_rc_observed_only_training_input import ROOT,ObservedMRI,read,sha,array_sha,reconstruct,normalize,read_supervised_label,support_domains
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
def deny_cuda(*args,**kwargs):raise RuntimeError('CUDA initialization prohibited in CPU pilot')
torch.cuda._lazy_init=deny_cuda
TILE=96;STRIDE=64;SEED=20261003
class Block(nn.Module):
    def __init__(self,i,o):
        super().__init__();self.layers=nn.Sequential(nn.Conv2d(i,o,3,padding=1,bias=False),nn.GroupNorm(4,o),nn.ReLU(),nn.Conv2d(o,o,3,padding=1,bias=False),nn.GroupNorm(4,o),nn.ReLU())
    def forward(self,x):return self.layers(x)
class PilotUNet(nn.Module):
    def __init__(self):
        super().__init__();self.e0=Block(5,8);self.e1=Block(8,16);self.e2=Block(16,32);self.e3=Block(32,64);self.d2=Block(96,32);self.d1=Block(48,16);self.d0=Block(24,8);self.out=nn.Conv2d(8,1,1);self.forward_calls=0
    def forward(self,x):
        self.forward_calls+=1
        a=self.e0(x);b=self.e1(F.max_pool2d(a,2));c=self.e2(F.max_pool2d(b,2));d=self.e3(F.max_pool2d(c,2))
        d=self.d2(torch.cat((F.interpolate(d,size=c.shape[-2:],mode='bilinear',align_corners=False),c),1))
        d=self.d1(torch.cat((F.interpolate(d,size=b.shape[-2:],mode='bilinear',align_corners=False),b),1))
        d=self.d0(torch.cat((F.interpolate(d,size=a.shape[-2:],mode='bilinear',align_corners=False),a),1));return self.out(d)
def weight_hash(model):
    h=hashlib.sha256()
    for k,v in model.state_dict().items():h.update(k.encode());h.update(array_sha(v.detach().cpu().numpy()).encode())
    return h.hexdigest()
def load_package(case,production_row):
    p=ROOT/production_row['observed_package'];assert sha(p)==production_row['observed_package_sha256']
    with np.load(p,allow_pickle=False) as q:
        o=ObservedMRI(np.array(q['observed_rcz'],copy=True),tuple(int(z) for z in q['observed_indices']),int(q['native_shape'][2]),tuple(tuple(float(v) for v in row) for row in q['affine_rcz_ras']),(),())
    assert array_sha(o.pixels)==production_row['observed_array_sha256']
    assert list(o.pixels.shape[:2])+[o.native_planes]==case['native_shape'] and np.array_equal(o.affine_rcz_ras,case['affine_rcz_ras'])
    return o
def image_input(o,method,production_row):
    raw=reconstruct(o,method);assert array_sha(raw)==production_row['inputs'][method+'_observed_shared']['raw_reconstruction_sha256']
    x,st=normalize(raw,o,'observed_shared');assert array_sha(x)==production_row['inputs'][method+'_observed_shared']['normalized_rcz_sha256'];return x,st
def tensor_patch(image,z,r,c):
    zs=np.clip(np.arange(z-2,z+3),0,image.shape[2]-1)
    return np.ascontiguousarray(image[r:r+TILE,c:c+TILE,zs].transpose(2,0,1))
def training_batch(item,rng):
    image,label,foreground=item['image'],item['label'],item['foreground'];images=[];labels=[]
    for j in range(4):
        if j<2:
            rr,cc,z=foreground[int(rng.integers(len(foreground)))];rr+=int(rng.integers(-24,25));cc+=int(rng.integers(-24,25))
        else:rr,cc,z=[int(rng.integers(n)) for n in image.shape]
        r=int(np.clip(rr-TILE//2,0,image.shape[0]-TILE));c=int(np.clip(cc-TILE//2,0,image.shape[1]-TILE));z=int(z)
        x=tensor_patch(image,z,r,c);y=label[r:r+TILE,c:c+TILE,z].astype(np.float32)[None]
        if rng.random()<.5:x=np.flip(x,1);y=np.flip(y,1)
        if rng.random()<.5:x=np.flip(x,2);y=np.flip(y,2)
        k=int(rng.integers(4));x=np.rot90(x,k,axes=(1,2));y=np.rot90(y,k,axes=(1,2))
        x=x*float(rng.uniform(.9,1.1))+float(rng.uniform(-.1,.1));images.append(x);labels.append(y)
    return torch.from_numpy(np.ascontiguousarray(np.stack(images))),torch.from_numpy(np.ascontiguousarray(np.stack(labels)))
def loss_fn(logits,target):
    p=logits.sigmoid();return F.binary_cross_entropy_with_logits(logits,target)+1-(2*(p*target).sum()+1)/(p.sum()+target.sum()+1)
def starts(n):
    assert n>=TILE
    return sorted(set(list(range(0,n-TILE+1,STRIDE))+[n-TILE]))
def infer(model,image,on_progress=None):
    rs,cs=starts(image.shape[0]),starts(image.shape[1]);coverage=np.zeros(image.shape[:2],np.uint16)
    locations=[(r,c) for r in rs for c in cs]
    for r,c in locations:coverage[r:r+TILE,c:c+TILE]+=1
    assert coverage.min()>0
    prediction=np.zeros(image.shape,bool);probhash=hashlib.sha256();model.eval()
    with torch.inference_mode():
        for z in range(image.shape[2]):
            scores=np.zeros(image.shape[:2],np.float64)
            for start in range(0,len(locations),4):
                loc=locations[start:start+4];batch=torch.from_numpy(np.stack([tensor_patch(image,z,r,c) for r,c in loc]))
                output=model(batch).sigmoid().numpy()[:,0];assert np.isfinite(output).all()
                for (r,c),p in zip(loc,output):scores[r:r+TILE,c:c+TILE]+=p
            scores/=coverage;probhash.update(scores.tobytes());prediction[:,:,z]=scores>=.5
            if on_progress and (z+1)%16==0:on_progress(z+1,image.shape[2])
    return prediction,dict(tile_shape=[TILE,TILE],stride=STRIDE,row_starts=rs,col_starts=cs,coverage_min=int(coverage.min()),coverage_max=int(coverage.max()),coverage_sha256=array_sha(coverage),probabilities_float64_stream_sha256=probhash.hexdigest(),planes=image.shape[2],tiles_per_plane=len(locations))
def counts(pred,label):
    tp=int(np.count_nonzero(pred&label));fp=int(np.count_nonzero(pred&~label));fn=int(np.count_nonzero(~pred&label));g=tp+fn;s=tp+fp
    return dict(tp=tp,fp=fp,fn=fn,gt_foreground=g,pred_foreground=s,dice=2*tp/(s+g) if s+g else None,precision=tp/s if s else None,recall=tp/g if g else None,signed_relative_volume_error=(s-g)/g if g else None,absolute_relative_volume_error=abs(s-g)/g if g else None,empty_ground_truth=g==0,empty_prediction=s==0)
def surface_metrics(pred,label,affine):
    if not pred.any() or not label.any():return dict(assd_mm=None,hd95_mm=None,undefined_reason='empty prediction or ground truth')
    affine=np.asarray(affine);spacing=np.linalg.norm(affine[:3,:3],axis=0);unit=affine[:3,:3]/spacing
    assert np.allclose(unit.T@unit,np.eye(3),atol=1e-5)
    structure=generate_binary_structure(3,1);p=pred&~binary_erosion(pred,structure=structure,border_value=0);g=label&~binary_erosion(label,structure=structure,border_value=0)
    a=distance_transform_edt(~g,sampling=spacing)[p];b=distance_transform_edt(~p,sampling=spacing)[g];d=np.concatenate([a,b])
    return dict(assd_mm=float(d.mean()),hd95_mm=float(np.quantile(d,.95)),pred_surface_voxels=int(p.sum()),gt_surface_voxels=int(g.sum()),spacing_mm=spacing.tolist(),definition='pooled directed 6-connected voxel surfaces, physical Euclidean distances, linear percentile')
def metrics(pred,label,o):
    result={'full':counts(pred,label)}
    for name,mask in support_domains(o).items():result[name]=counts(pred[:,:,mask],label[:,:,mask]);result[name]['planes']=int(mask.sum())
    result['full_surface']=surface_metrics(pred,label,o.affine_rcz_ras);result['voxel_volume_mm3']=abs(float(np.linalg.det(np.asarray(o.affine_rcz_ras)[:3,:3])))
    return result
