import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2.model import PASTNetV2

VARIANTS={'shared':(False,False,False,False,4),'plain':(False,False,False,False,4)}

def spatial(x,a,inverse=False):
    k,f=a%4,a//4
    if inverse:
        x=torch.rot90(x,-k,(-2,-1))
        if f:x=x.flip(-1)
    else:
        if f:x=x.flip(-1)
        x=torch.rot90(x,k,(-2,-1))
    return x.contiguous()

class DirectionContext(nn.Module):
    def __init__(self):
        super().__init__()
        self.body=nn.Sequential(nn.Conv2d(9,24,3,padding=1),nn.GELU(),
            nn.Conv2d(24,24,3,padding=1),nn.GELU(),nn.Conv2d(24,24,3,padding=1),nn.GELU())
        self.project=nn.Conv2d(24,64,1)
        nn.init.zeros_(self.project.weight);nn.init.zeros_(self.project.bias)

    def forward(self,cond,shared=True):
        x=cond[:,[4,5,6,7,8,9,10,11,12]];maps=[]
        for scale in (4,8):
            low=F.avg_pool2d(x,scale)
            if shared:
                fields=[spatial(self.body(spatial(low,g)),g,True) for g in range(8)]
                feat=torch.stack(fields).mean(0)
            else:feat=self.body(low)
            maps.append(F.interpolate(feat,size=x.shape[-2:],mode='bilinear',align_corners=False))
        return .1*self.project((maps[0]+maps[1])*.5)

class FrameContextPASTNet(PASTNetV2):
    def __init__(self,variant='shared'):
        if variant not in VARIANTS:raise ValueError(variant)
        super().__init__('control');self.variant=variant
        self.direction_adapter=DirectionContext()

    def forward_components(self,batch):
        cond=batch['cond'].flatten(0,1)
        def inject(module,inputs,output):
            h,w=output.shape[-2:];x=cond
            if (h,w)!=x.shape[-2:]:x=F.pad(x,(0,w-x.shape[-1],0,h-x.shape[-2]),mode='reflect')
            return output+self.direction_adapter(x,self.variant=='shared')
        handle=self.base.single.fuse.register_forward_hook(inject)
        try:return super().forward_components(batch)
        finally:handle.remove()

def make_model(variant):return FrameContextPASTNet(variant)
