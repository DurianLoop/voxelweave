"""Query-centred bilateral cost volume; only observed anchor features are matched."""
import math
import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2.model import PASTNetV2

VARIANTS={name:(False,False,False,False,4) for name in ('bilateral','stationary')}

def interpolation_stencil(sign):
    # The only queries in this x4 protocol are 1/4, 1/2, 3/4.
    # Express constant subpixel translations as a fixed 5x5 bilinear stencil.
    matrices=torch.zeros(3,25,25)
    for q,t in enumerate((.25,.5,.75)):
        for d,(dy,dx) in enumerate(( (y,x) for y in range(-2,3) for x in range(-2,3))):
            y,x=(-t*dy,-t*dx) if sign=='left' else ((1-t)*dy,(1-t)*dx)
            iy,ix=math.floor(y),math.floor(x)
            for yy in (iy,iy+1):
                for xx in (ix,ix+1):
                    weight=(1-abs(y-yy))*(1-abs(x-xx))
                    if weight>0:matrices[q,d,(yy+2)*5+xx+2]+=weight
    return matrices

class BilateralTransport(nn.Module):
    def __init__(self,stationary=False):
        super().__init__();self.stationary=stationary
        self.descriptor=nn.Conv2d(64,16,1,bias=False)
        with torch.no_grad():
            self.descriptor.weight.zero_()
            for c in range(16):self.descriptor.weight[c,4*c:4*c+4]=.25
        self.log_temperature=nn.Parameter(torch.tensor(math.log(10.)))
        self.project=nn.Conv2d(64,64,1)
        nn.init.zeros_(self.project.weight);nn.init.zeros_(self.project.bias)
        self.register_buffer('left_stencil',interpolation_stencil('left'),persistent=False)
        self.register_buffer('right_stencil',interpolation_stencil('right'),persistent=False)
        self.register_buffer('distance',torch.tensor([y*y+x*x for y in range(-2,3) for x in range(-2,3)]).float(),persistent=False)

    def sample(self,x,stencil):
        n,c,h,w=x.shape
        if n%3:raise ValueError('Expected three ordered x4 queries per interval')
        patches=F.unfold(x,5,padding=2).reshape(n//3,3,c,25,h*w)
        return torch.einsum('bqckp,qdk->bqcdp',patches,stencil.to(x.dtype)).reshape(n,c,25,h,w)

    def transport(self,left,right,return_weights=False):
        l=self.sample(left,self.left_stencil);r=self.sample(right,self.right_stencil)
        with torch.autocast(left.device.type,enabled=False):
            score=(F.normalize(l.float(),dim=1)*F.normalize(r.float(),dim=1)).sum(1)
            score=score*self.log_temperature.exp().clamp(5,30)-.05*self.distance[None,:,None,None]
            one=torch.ones_like(left[:,:1],dtype=torch.float32)
            valid=(self.sample(one,self.left_stencil)[:,0]>.999)&(self.sample(one,self.right_stencil)[:,0]>.999)
            if self.stationary:valid=valid & (self.distance[None,:,None,None]==0)
            weights=score.masked_fill(~valid,-1e4).softmax(1)
        t=left.new_tensor([.25,.5,.75]).repeat(left.shape[0]//3)[:,None,None,None,None]
        mixed=((1-t)*l+t*r)
        matched=(mixed*weights[:,None].to(mixed.dtype)).sum(2)
        disagreement=((l-r).abs()*weights[:,None].to(l.dtype)).sum(2)
        return (matched,disagreement,weights) if return_weights else (matched,disagreement)

    def forward(self,left,right,coarse):
        n,c,h,w=left.shape;features=[]
        for scale in (4,8):
            l,r,cq=[self.descriptor(F.avg_pool2d(x,scale)) for x in (left,right,coarse)]
            matched,disagreement=self.transport(l,r)
            f=torch.cat([matched-cq,disagreement],1)
            features.append(F.interpolate(f,size=(h,w),mode='bilinear',align_corners=False))
        return self.project(torch.cat(features,1))

class BilateralPASTNet(PASTNetV2):
    def __init__(self,variant):
        if variant not in VARIANTS:raise ValueError(variant)
        super().__init__('control');self.variant=variant
        self.bilateral_adapter=BilateralTransport(variant=='stationary')

    def forward_components(self,batch):
        phases=batch['cond'][:,:,5,0,0]
        if not torch.allclose(phases,phases.new_tensor([.25,.5,.75])[None].expand_as(phases)):
            raise ValueError('Fixed x4 query contract required')
        features=[]
        def capture(module,args,output):features.append(output)
        def fuse(module,args):
            if len(features)!=5:raise RuntimeError('Unexpected anchor encoder calls')
            x=args[0]
            delta=self.bilateral_adapter(features[1],features[2],features[4])
            return (torch.cat([x[:,:64]+delta,x[:,64:]],1),)
        h1=self.base.single.slice_encoder.register_forward_hook(capture)
        h2=self.base.single.fuse.register_forward_pre_hook(fuse)
        try:return super().forward_components(batch)
        finally:h1.remove();h2.remove()

def make_model(variant):return BilateralPASTNet(variant)
