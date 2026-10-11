"""Frozen I3Net prior and query-conditioned PAST latent residual bridge."""
from pathlib import Path
import torch
from torch import nn
from pastnet_wavelet_trunk.model import WaveletPASTNet
from i3net_strict_reference.model import Reference

ROOT=Path(__file__).resolve().parent
I3=ROOT.parents[1]/'baseline/ixi_i3net/runs/full_test115_stable/checkpoints/i3net_epoch_best.pth'
PAST=ROOT.parent/'pastnet_ixi_wavelet/runs/full_wavelet3_ixi_seed3407/best.pth'
I3_SHA='48927b521c834f5f6bc26c0b28886d873aae41c0beee5cdbe01c7dec704977f9'
PAST_SHA='bee2006a5fde5e006feb42745b7048938c72e008068d7424867f8d0c4dc95acc'


class Teacher(nn.Module):
    def __init__(self):
        super().__init__();self.reference=Reference()
        self.reference.network.load_state_dict(torch.load(I3,map_location='cpu',weights_only=False)['model_state_dict'],strict=True)
        self.eval().requires_grad_(False)

    @torch.no_grad()
    def forward(self,anchors):
        captured=[]
        handle=self.reference.network.tail.register_forward_pre_hook(lambda module,args:captured.append(args[0]))
        try:
            # Keep the complete legacy predictor, including FP32 per-window clamp.
            with torch.autocast('cuda',enabled=False):
                y=self.reference.network(anchors[:,:,0].float().permute(0,2,3,1).contiguous()).float().clamp(0,1)
            return y,captured[-1].detach()
        finally:handle.remove()


class Bridge(nn.Module):
    def __init__(self,variant):
        super().__init__();assert variant in ('blind','latent');self.variant=variant
        self.past=WaveletPASTNet('wavelet3')
        self.past.load_state_dict(torch.load(PAST,map_location='cpu',weights_only=False)['model_state_dict'],strict=True)
        self.readout=nn.Sequential(nn.Conv2d(131,64,1),nn.GELU(),
            nn.Conv2d(64,64,3,padding=1,groups=64),nn.GELU(),nn.Conv2d(64,1,1))
        nn.init.zeros_(self.readout[-1].weight);nn.init.zeros_(self.readout[-1].bias)

    def forward(self,batch,teacher_prediction,teacher_feature):
        captured=[]
        handle=self.past.base.single.decoder.register_forward_pre_hook(lambda module,args:captured.append(args[0]))
        try:parts=self.past.forward_components(batch)
        finally:handle.remove()
        b,_,_,h,w=batch['cond'].shape
        feature=captured[-1][:,:,:h,:w] # Last decoder call: the actual mixed MA3 latent.
        assert feature.shape==(b*3,64,h,w)
        prior=teacher_feature[:,None].expand(-1,3,-1,-1,-1).reshape(b*3,64,h,w)
        if self.variant=='blind':prior=prior*0
        phase=batch['cond'][:,:,5:6].reshape(b*3,1,h,w)
        query=batch['teacher_query'].reshape(b*3,1,1,1).expand(-1,1,h,w)
        coarse=batch['cond'][:,:,4:5]
        past_residual=(parts['prediction']-coarse).reshape(b*3,1,h,w)
        delta=.05*torch.tanh(self.readout(torch.cat([feature,prior,phase,query,past_residual],1)))
        offsets=batch['teacher_interval'][:,None]*4+torch.arange(1,4,device=feature.device)[None]
        index=offsets[:,None,None,:].expand(-1,h,w,-1)
        base=teacher_prediction.gather(-1,index).permute(0,3,1,2).unsqueeze(2)
        # linear coarse + bounded I3 residual + bounded learned query residual.
        # Algebraically use base directly to retain bitwise initial I3 identity.
        return base+delta.reshape(b,3,1,h,w).float()
