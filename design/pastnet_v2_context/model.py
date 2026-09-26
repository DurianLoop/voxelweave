"""Query-centred, masked quadratic trajectories over actual sparse observations."""
import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2.model import PASTNetV2

VARIANTS={'trajectory_local':(False,False,False,False,6),
          'trajectory_extended':(False,False,False,False,6)}


def trajectory_weights(valid, phase):
    """Return ridge WLS coefficient weights [B,Q,3,A], in sparse-gap units.

    Intercept/value, signed slope and quadratic coefficient are kept separately.
    This is a latent polynomial summary, not a claim about anatomy being quadratic.
    Physical spacing/orientation is deliberately absent from this two-arm test.
    """
    offsets=valid.new_tensor([-2.,-1.,0.,1.,2.,3.])
    distance=offsets[None,None,:]-phase[:,:,None]
    basis=torch.stack([torch.ones_like(distance),distance,distance.square()],-1)
    weights=torch.exp(-.5*(distance/2).square())*valid[:,None,:]
    rhs=basis.transpose(-1,-2)*weights[:,:,None,:]
    gram=rhs@basis
    ridge=torch.diag(valid.new_tensor([0.,.001,.001]))
    return torch.linalg.solve(gram+ridge,rhs)


class SparseTrajectory(nn.Module):
    def __init__(self,channels=64):
        super().__init__()
        self.encoder=nn.Sequential(nn.Conv2d(1,16,3,padding=1),nn.SiLU(),
                                   nn.Conv2d(16,16,3,padding=1),nn.SiLU())
        self.fuse=nn.Sequential(nn.Conv2d(2*3*16+2,32,3,padding=1),nn.SiLU(),
                                nn.Conv2d(32,32,3,padding=1),nn.SiLU())
        self.project=nn.Conv2d(32,channels,1)
        nn.init.zeros_(self.project.weight);nn.init.zeros_(self.project.bias)

    def forward(self,batch,extended):
        anchors=batch['anchors'];b,a,_,h,w=anchors.shape
        if a!=6 or min(h,w)<32:raise ValueError('Six sparse slots and images >=32 required')
        valid=batch['valid'].float().clone()
        if not extended:valid[:,[0,5]]=0
        # Mask *before* encoding: ignored values cannot leak via nonlinear ops.
        anchors=anchors*valid[:,:,None,None,None]
        phase=batch['cond'][:,:,5,0,0].float()
        with torch.autocast(anchors.device.type,enabled=False):
            weights=trajectory_weights(valid,phase)
        coarse=batch['cond'][:,:,4:5]
        maps=[]
        for scale in (4,8):
            lo=F.avg_pool2d(anchors.reshape(b*a,1,h,w),scale)
            eh,ew=lo.shape[-2:]
            feat=self.encoder(lo).reshape(b,a,16,eh,ew)
            cf=self.encoder(F.avg_pool2d(coarse.reshape(b*3,1,h,w),scale)).reshape(b,3,16,eh,ew)
            coeff=torch.einsum('bqka,bachw->bqkchw',weights.to(feat.dtype),feat)
            # Value relative to the linear coarse; preserve slope and curvature.
            coeff=torch.cat([(coeff[:,:,0]-cf)[:,:,None],coeff[:,:,1:]],2)
            flat=coeff.reshape(b*3,48,eh,ew)
            maps.append(F.interpolate(flat,size=(h//4,w//4),mode='bilinear',align_corners=False))
        shape=(b*3,1,h//4,w//4)
        count=(valid.sum(1)/6)[:,None].expand(-1,3).reshape(b*3,1,1,1).expand(shape)
        q=phase.reshape(b*3,1,1,1).expand(shape)
        low=self.project(self.fuse(torch.cat([*maps,count,q],1)))
        return F.interpolate(low,size=(h,w),mode='bilinear',align_corners=False)


class TrajectoryPASTNet(PASTNetV2):
    def __init__(self,variant):
        if variant not in VARIANTS:raise ValueError(variant)
        super().__init__('control')
        self.variant=variant;self.anchor_count=6
        self.trajectory_adapter=SparseTrajectory()

    def forward_components(self,batch):
        # All new computation is before the unchanged wide MA3 body and decoder.
        trajectory=self.trajectory_adapter(batch,self.variant=='trajectory_extended')
        def add_context(module,inputs,output):
            ph=output.shape[-2]-trajectory.shape[-2];pw=output.shape[-1]-trajectory.shape[-1]
            return output+F.pad(trajectory,(0,pw,0,ph),mode='replicate')
        hook=self.base.single.fuse.register_forward_hook(add_context)
        try:return super().forward_components(batch)
        finally:hook.remove()
