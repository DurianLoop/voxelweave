import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2.model import PASTNetV2

VARIANTS={'per_anchor':(False,False,False,False,4),'crossview':(False,False,False,False,4)}


class AnchorPlaneBlock(nn.Module):
    """Same depthwise plane kernel on (anchor,x) and (anchor,y)."""
    def __init__(self,c=24):
        super().__init__()
        self.norm=nn.GroupNorm(1,c)
        self.plane=nn.Conv2d(c,c,(3,5),padding=(1,2),groups=c,bias=False)
        self.mix=nn.Sequential(nn.Conv2d(c,c*2,1),nn.GELU(),nn.Conv2d(c*2,c,1))

    def width_plane(self,f,cross):
        b,c,a,h,w=f.shape
        if cross:
            x=f.permute(0,3,1,2,4).reshape(b*h,c,a,w)
            return self.plane(x).reshape(b,h,c,a,w).permute(0,2,3,1,4)
        # Exact same trainable kernel, applied with the centre anchor repeated.
        # This removes communication with other anchors without removing weights.
        x=f.permute(0,3,2,1,4).reshape(b*h*a,c,1,w).expand(-1,-1,3,-1)
        y=F.conv2d(x,self.plane.weight,padding=(0,2),groups=c)
        return y.reshape(b,h,a,c,w).permute(0,3,2,1,4)

    def forward(self,f,valid,cross):
        b,c,a,h,w=f.shape
        flat=f.permute(0,2,1,3,4).reshape(b*a,c,h,w)
        norm=self.norm(flat).reshape(b,a,c,h,w).permute(0,2,1,3,4)
        norm=norm*valid[:,None,:,None,None]
        plane=(self.width_plane(norm,cross)+self.width_plane(norm.transpose(-1,-2),cross).transpose(-1,-2))*.5
        mixed=self.mix(plane.permute(0,2,1,3,4).reshape(b*a,c,h,w))
        return (f+.2*mixed.reshape(b,a,c,h,w).permute(0,2,1,3,4))*valid[:,None,:,None,None]


class LateAnchorFusion(nn.Module):
    def __init__(self,c=64,hidden=24):
        super().__init__()
        self.reduce=nn.Conv2d(c,hidden,1)
        self.blocks=nn.ModuleList([AnchorPlaneBlock(hidden) for _ in range(3)])
        self.query_read=nn.Sequential(nn.Conv2d(hidden*5+5,64,1),nn.GELU(),nn.Conv2d(64,32,3,padding=1),nn.GELU())
        self.project=nn.Conv2d(64,c,1)
        nn.init.zeros_(self.project.weight);nn.init.zeros_(self.project.bias)

    def forward(self,features,valid,q,cross):
        b,c,h,w=features[0].shape;maps=[]
        for scale in (4,8):
            encoded=[self.reduce(F.avg_pool2d(x,scale)) for x in features]
            sh,sw=encoded[0].shape[-2:]
            anchors=torch.stack(encoded[:4],2)*valid[:,None,:,None,None]
            for block in self.blocks:anchors=block(anchors,valid,cross)
            # The anchor axis survives all three nonlinear plane blocks.
            ordered=anchors.permute(0,2,1,3,4).reshape(b,-1,sh,sw)
            masks=valid[:,:,None,None].expand(-1,-1,sh,sw)
            phase=q[:,None,None,None].expand(-1,1,sh,sw)
            query=self.query_read(torch.cat([ordered,encoded[4],masks,phase],1))
            maps.append(F.interpolate(query,size=(h//4,w//4),mode='bilinear',align_corners=False))
        return F.interpolate(self.project(torch.cat(maps,1)),size=(h,w),mode='bilinear',align_corners=False)


class CrossViewPASTNet(PASTNetV2):
    def __init__(self,variant='crossview'):
        if variant not in VARIANTS:raise ValueError(variant)
        super().__init__('control');self.variant=variant
        self.crossview_adapter=LateAnchorFusion()

    def forward_components(self,batch):
        features=[];b,q=batch['cond'].shape[:2]
        valid=batch['valid'][:,None].expand(-1,q,-1).reshape(b*q,4)
        phase=batch['cond'][:,:,5,0,0].reshape(-1)
        def capture(module,inputs,output):features.append(output)
        def inject(module,inputs,output):
            if len(features)!=5:raise RuntimeError('Expected four observed encodings plus coarse')
            # Invalid padded values cannot enter the NEW path. Original G086 input
            # semantics are unchanged and retain the original repeated endpoints.
            clean=[x*valid[:,i,None,None,None] if i<4 else x for i,x in enumerate(features)]
            return output+self.crossview_adapter(clean,valid,phase,self.variant=='crossview')
        handles=[self.base.single.slice_encoder.register_forward_hook(capture),self.base.single.fuse.register_forward_hook(inject)]
        try:return super().forward_components(batch)
        finally:
            for handle in handles:handle.remove()
