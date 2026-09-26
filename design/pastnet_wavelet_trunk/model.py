import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2.model import PASTNetV2

VARIANTS={'wavelet3':(False,False,False,False,4),'wavelet1':(False,False,False,False,4)}
def haar(x):
    h,w=x.shape[-2:];x=F.pad(x,(0,w%2,0,h%2))
    a,b,c,d=x[...,0::2,0::2],x[...,0::2,1::2],x[...,1::2,0::2],x[...,1::2,1::2]
    return torch.stack([(a+b+c+d)*.5,(a-b+c-d)*.5,(a+b-c-d)*.5,(a-b-c+d)*.5],2),(h,w)
def inverse_haar(bands,shape):
    ll,lh,hl,hh=bands.unbind(2)
    a=(ll+lh+hl+hh)*.5;b=(ll-lh+hl-hh)*.5;c=(ll+lh-hl-hh)*.5;d=(ll-lh-hl+hh)*.5
    upper=torch.stack([a,b],-1).flatten(-2);lower=torch.stack([c,d],-1).flatten(-2)
    y=torch.stack([upper,lower],-2).flatten(-3,-2)
    return y[...,:shape[0],:shape[1]]

class WaveletDepthwise(nn.Conv2d):
    def __init__(self,old,levels):
        super().__init__(old.in_channels,old.out_channels,3,padding=1,groups=old.groups,bias=old.bias is not None)
        self.load_state_dict(old.state_dict());self.levels=levels
        self.wavelet_gain_adapter=nn.Parameter(torch.zeros(old.out_channels))
    def tree(self,x,levels):
        bands,shape=haar(x);b,c,_,h,w=bands.shape
        flat=bands.permute(0,2,1,3,4).reshape(b*4,c,h,w)
        filtered=F.conv2d(flat,self.weight,None,padding=1,groups=self.groups).reshape(b,4,c,h,w).permute(0,2,1,3,4)
        if levels>1:filtered=torch.cat([self.tree(bands[:,:,0],levels-1).unsqueeze(2),filtered[:,:,1:]],2)
        return inverse_haar(filtered,shape)
    def forward(self,x):
        base=super().forward(x);wave=self.tree(x,self.levels)
        if self.bias is not None:wave=wave+self.bias.to(wave.dtype)[None,:,None,None]
        gain=(.5*torch.tanh(self.wavelet_gain_adapter)).to(base.dtype)[None,:,None,None]
        return base+gain*(wave-base)

class WaveletPASTNet(PASTNetV2):
    def __init__(self,variant):
        if variant not in VARIANTS:raise ValueError(variant)
        super().__init__('control');self.variant=variant
        for block in self.base.single.body:block.depthwise=WaveletDepthwise(block.depthwise,3 if variant=='wavelet3' else 1)
def make_model(variant):return WaveletPASTNet(variant)
