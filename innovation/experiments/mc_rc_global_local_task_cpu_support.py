"""Standard full-FOV/local task baseline, physical sparse context and CPU-only runtime."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from mc_rc_observed_only_training_input import ROOT,read,sha,array_sha,ObservedMRI,reconstruct,normalize,support_domains
torch.set_num_threads(1)
torch.set_num_interop_threads(1)
def deny_cuda(*args,**kwargs):raise RuntimeError('CUDA initialization prohibited')
torch.cuda._lazy_init=deny_cuda
SEED=20261004;TILE=128;STRIDE=96
DEVELOPERS={'VS-MC-RC-'+p for p in ('001','002','004','005','006','007','009','010','011','012','013')}
VALIDATORS={'VS-MC-RC-'+p for p in ('020','022','025','024')}
def require_task_role(case):
    if case['patient'] not in DEVELOPERS|VALIDATORS:raise ValueError('Confirmation and unallocated patients forbidden')
class Block(nn.Module):
    def __init__(self,i,o):
        super().__init__();self.layers=nn.Sequential(nn.Conv2d(i,o,3,padding=1,bias=False),nn.GroupNorm(4,o),nn.ReLU(),nn.Conv2d(o,o,3,padding=1,bias=False),nn.GroupNorm(4,o),nn.ReLU())
    def forward(self,x):return self.layers(x)
class UNet(nn.Module):
    def __init__(self,inputs,channels):
        super().__init__();self.encoders=nn.ModuleList([Block(inputs if i==0 else channels[i-1],c) for i,c in enumerate(channels)]);self.decoders=nn.ModuleList([Block(channels[i+1]+channels[i],channels[i]) for i in reversed(range(len(channels)-1))]);self.out=nn.Conv2d(channels[0],1,1)
    def forward(self,x):
        skip=[]
        for i,enc in enumerate(self.encoders):
            if i:x=F.max_pool2d(x,2)
            x=enc(x);skip.append(x)
        for dec,s in zip(self.decoders,reversed(skip[:-1])):x=dec(torch.cat((F.interpolate(x,size=s.shape[-2:],mode='bilinear',align_corners=False),s),1))
        return x,self.out(x)
class GlobalLocalUNet(nn.Module):
    def __init__(self):
        super().__init__();self.global_net=UNet(5,(8,16,32,64,128));self.local_net=UNet(14,(16,32,64,128));self.global_calls=0;self.local_calls=0
    def global_forward(self,x):self.global_calls+=1;features,logit=self.global_net(x);return torch.cat((features,logit),1),logit
    def local_forward(self,x,context):self.local_calls+=1;return self.local_net(torch.cat((x,context),1))[1]
def weight_hash(model):
    import hashlib
    h=hashlib.sha256()
    for k,v in model.state_dict().items():h.update(k.encode());h.update(array_sha(v.detach().numpy()).encode())
    return h.hexdigest()
def load_authenticated_observed(case,row):
    require_task_role(case);p=ROOT/row['observed_package'];assert sha(p)==row['observed_package_sha256']
    with np.load(p,allow_pickle=False) as q:o=ObservedMRI(q['observed_rcz'].copy(),tuple(map(int,q['observed_indices'])),int(q['native_shape'][2]),tuple(tuple(float(v) for v in a) for a in q['affine_rcz_ras']),(),())
    assert array_sha(o.pixels)==row['observed_array_sha256'] and list(o.pixels.shape[:2])+[o.native_planes]==case['native_shape'] and np.array_equal(o.affine_rcz_ras,case['affine_rcz_ras']);return o
def sparse_image(o,method,row):
    raw=reconstruct(o,method);assert array_sha(raw)==row['inputs'][method+'_observed_shared']['raw_reconstruction_sha256'];x,st=normalize(raw,o,'observed_shared');assert array_sha(x)==row['inputs'][method+'_observed_shared']['normalized_rcz_sha256'];return x,st
def physical_shape(case):
    a=np.asarray(case['affine_rcz_ras']);spacing=np.linalg.norm(a[:3,:3],axis=0);shape=tuple(max(TILE,int(round(n*s/.5))) for n,s in zip(case['native_shape'][:2],spacing[:2]));return shape,float(spacing[2])
def resize_image(x,shape):
    with torch.no_grad():return F.interpolate(torch.from_numpy(np.ascontiguousarray(x.transpose(2,0,1)))[:,None],size=shape,mode='bilinear',align_corners=False)[:,0].numpy().copy()
def resize_training_label(g,shape):
    with torch.no_grad():return F.interpolate(torch.from_numpy(np.ascontiguousarray(g.transpose(2,0,1),dtype=np.float32))[:,None],size=shape,mode='area')[:,0].numpy().copy()
def context_plane(image_zrc,z,zspacing):
    planes=[]
    for mm in (-2,-1,0,1,2):
        at=float(np.clip(z+mm/zspacing,0,image_zrc.shape[0]-1));lo=int(at);hi=min(lo+1,image_zrc.shape[0]-1);t=at-lo;planes.append(image_zrc[lo]*(1-t)+image_zrc[hi]*t)
    return np.ascontiguousarray(np.stack(planes),dtype=np.float32)
def global_view(plane):return F.interpolate(torch.from_numpy(plane)[None],size=(256,256),mode='bilinear',align_corners=False)
def context_tiles(global_features,locations,shape):
    # A local pixel center maps to the same full-FOV coordinate before the global resize.
    rbase=torch.arange(TILE,dtype=torch.float32)+.5;cbase=torch.arange(TILE,dtype=torch.float32)+.5;grids=[]
    for r,c in locations:
        rr=2*(rbase+r)/shape[0]-1;cc=2*(cbase+c)/shape[1]-1;y,x=torch.meshgrid(rr,cc,indexing='ij');grids.append(torch.stack((x,y),-1))
    grid=torch.stack(grids);return F.grid_sample(global_features.expand(len(locations),-1,-1,-1),grid,mode='bilinear',padding_mode='border',align_corners=False)
def segmentation_loss(logits,label):
    p=logits.sigmoid();return F.binary_cross_entropy_with_logits(logits,label)+1-(2*(p*label).sum()+1)/(p.sum()+label.sum()+1)
def training_example(item,rng):
    image,label=item['image_zrc'],item['label_zrc'];fg=item['native_foreground']
    z=int(fg[int(rng.integers(len(fg))),2]) if rng.random()<.5 else int(rng.integers(image.shape[0]));plane=context_plane(image,z,item['zspacing']);target=label[z].copy()
    if rng.random()<.5:plane=np.flip(plane,1);target=np.flip(target,0)
    if rng.random()<.5:plane=np.flip(plane,2);target=np.flip(target,1)
    k=int(rng.integers(4));plane=np.rot90(plane,k,axes=(1,2));target=np.rot90(target,k,axes=(0,1));plane=plane*float(rng.uniform(.9,1.1))+float(rng.uniform(-.1,.1));plane=np.ascontiguousarray(plane,dtype=np.float32);target=np.ascontiguousarray(target,dtype=np.float32)
    loc=[];xs=[];ys=[];coords=np.argwhere(target>0)
    for j in range(2):
        if j==0 and len(coords):rr,cc=coords[int(rng.integers(len(coords)))]+rng.integers(-32,33,size=2)
        else:rr,cc=[int(rng.integers(n)) for n in target.shape]
        r=int(np.clip(rr-TILE//2,0,target.shape[0]-TILE));c=int(np.clip(cc-TILE//2,0,target.shape[1]-TILE));loc.append((r,c));xs.append(plane[:,r:r+TILE,c:c+TILE]);ys.append(target[r:r+TILE,c:c+TILE][None])
    global_target=F.interpolate(torch.from_numpy(target)[None,None],size=(256,256),mode='area');return global_view(plane),torch.from_numpy(np.stack(xs)),torch.from_numpy(np.stack(ys)),global_target,loc,target.shape,dict(z=z,foreground_plane=bool(len(coords)))
def starts(n):return sorted(set(list(range(0,n-TILE+1,STRIDE))+[n-TILE]))
def infer_native(model,image_zrc,zspacing,native_shape,progress=None,only_planes=None):
    rs,cs=starts(image_zrc.shape[1]),starts(image_zrc.shape[2]);loc=[(r,c) for r in rs for c in cs];coverage=np.zeros(image_zrc.shape[1:],np.uint16)
    for r,c in loc:coverage[r:r+TILE,c:c+TILE]+=1
    assert coverage.min()>0;zs=list(range(image_zrc.shape[0])) if only_planes is None else list(only_planes);pred=np.zeros((native_shape[0],native_shape[1],len(zs)),bool);model.eval()
    with torch.inference_mode():
        for outz,z in enumerate(zs):
            plane=context_plane(image_zrc,z,zspacing);gf,_=model.global_forward(global_view(plane));scores=np.zeros(image_zrc.shape[1:],np.float64)
            for start in range(0,len(loc),4):
                chunk=loc[start:start+4];context=context_tiles(gf,chunk,plane.shape[1:]);patch=torch.from_numpy(np.stack([plane[:,r:r+TILE,c:c+TILE] for r,c in chunk]));output=model.local_forward(patch,context).sigmoid().numpy()[:,0]
                for (r,c),p in zip(chunk,output):scores[r:r+TILE,c:c+TILE]+=p
            scores/=coverage;assert np.isfinite(scores).all();mapped=F.interpolate(torch.from_numpy(scores)[None,None],size=native_shape[:2],mode='bilinear',align_corners=False)[0,0].numpy();pred[:,:,outz]=mapped>=.5
            if progress and (outz+1)%16==0:progress(outz+1,len(zs))
    return pred,dict(physical_input_shape=list(image_zrc.shape),row_starts=rs,col_starts=cs,coverage_min=int(coverage.min()),coverage_max=int(coverage.max()),coverage_sha256=array_sha(coverage),planes=zs,tiles_per_plane=len(loc),native_probability_interpolation='bilinear align_corners=False, float64, then threshold .5')
