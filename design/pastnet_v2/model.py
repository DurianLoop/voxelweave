"""Physical Query Correspondence PAST-Net. No target or dense context in forward."""
from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint

from .vendor.model_ma3aggressive import PASTNetMA3Aggressive2p5D, DualDomainRefiner
from .vendor.model_ma import PASTNetMultiAnchor2p5D

VARIANTS = {
    'control': (False,False,False,False,4),
    'geometry': (True,False,False,False,4),
    'correspondence': (True,True,False,False,4),
    'frequency': (True,True,True,False,4),
    'risk': (True,True,True,True,4),
    'context': (True,True,True,True,6),
}


class PhysicalFiLM(nn.Module):
    def __init__(self,channels):
        super().__init__()
        self.net=nn.Sequential(nn.Linear(17,64),nn.SiLU(),nn.Linear(64,channels*2))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self,x,p):
        gain,bias=self.net(p).chunk(2,-1)
        return x*(1+.1*torch.tanh(gain)[:,:,None,None])+.1*bias[:,:,None,None]


class QueryCorrespondence(nn.Module):
    """Per-anchor 3x3 feature neighborhoods at 1/4 and 1/2 resolution.

    Queries derive exclusively from linear coarse. Match weights address spatial
    alternatives before the wide trunk; this is not attention over three offsets.
    Distance prior has mm units when observed, grid units when explicitly missing.
    """
    def __init__(self,channels):
        super().__init__()
        self.query=nn.Conv2d(channels,16,1)
        self.key=nn.Conv2d(channels,16,1)
        self.project=nn.Conv2d(channels*2,channels,1)
        nn.init.zeros_(self.project.weight)
        nn.init.zeros_(self.project.bias)
        self.temperature=nn.Parameter(torch.tensor(2.))

    def forward(self,anchors,coarse,valid,distance):
        b,a,c,h,w=anchors.shape
        results=[]
        for scale in (4,2):
            low=F.avg_pool2d(anchors.reshape(b*a,c,h,w),scale)
            lh,lw=low.shape[-2:]
            cq=F.avg_pool2d(coarse,scale)
            q=F.normalize(self.query(cq),dim=1)
            keys=F.normalize(self.key(low),dim=1)
            # Padding candidates are masked; zeros cannot win at image edges.
            k=F.unfold(keys,3,padding=1).view(b,a,16,9,lh,lw)
            values=F.unfold(low,3,padding=1).view(b,a,c,9,lh,lw)
            score=(q[:,None,:,None]*k).sum(2)*self.temperature.exp().clamp(max=30)
            spatial_mask=F.unfold(torch.ones_like(cq[:,:1]),3,padding=1).view(b,1,9,lh,lw)>0
            score=score.masked_fill(~spatial_mask,-1e4)
            weights=score.softmax(2)
            matched=(weights[:,:,None]*values).sum(3)
            prior=-distance.abs()/20
            prior=prior.masked_fill(valid==0,-1e4).softmax(1)
            fused=(matched*prior[:,:,None,None,None]).sum(1)
            results.append(F.interpolate(fused-cq,size=(h,w),mode='bilinear',align_corners=False))
        return self.project(torch.cat(results,1))


class PhysicalAnchorTrunk(PASTNetMultiAnchor2p5D):
    def __init__(self,physical,correspondence,**kwargs):
        super().__init__(**kwargs)
        self.physical_adapter=PhysicalFiLM(self.base_channels) if physical else None
        self.correspondence_adapter=QueryCorrespondence(self.base_channels) if correspondence else None
        self.batch_context=None
        self.activation_checkpointing=True
        self.checkpoint_blocks=None

    def encode_components(self,x):
        if self.batch_context is None:
            return super().encode_components(x)
        original=x
        x,ph,pw=self._pad(x)
        context=self.batch_context
        features=[self.slice_encoder(x[:,i:i+1]) for i in range(5)]
        aux=self.aux_encoder(torch.cat([x[:,5:10],x[:,10:13]],1))
        if self.physical_adapter is not None:
            aux=self.physical_adapter(aux,context['physical'])
        logits=self.gate(torch.cat([*features,aux],1))
        q=x[:,5:6].clamp(0,1)
        priors=torch.cat([(.35*x[:,8:9]).clamp_min(1e-4),(1-q).clamp_min(1e-4),
                          q.clamp_min(1e-4),(.35*x[:,9:10]).clamp_min(1e-4),torch.full_like(q,.4)],1)
        weights=(logits+priors.log()).softmax(1)
        transferred=sum(weights[:,i:i+1]*f for i,f in enumerate(features))
        if self.correspondence_adapter is not None:
            anchors=context['anchors']
            b,a,_,h,w=anchors.shape
            anchors=anchors.reshape(b*a,1,h,w)
            anchors=F.pad(anchors,(0,pw,0,ph),mode='reflect') if ph or pw else anchors
            af=self.slice_encoder(anchors).reshape(b,a,self.base_channels,*x.shape[-2:])
            transferred=transferred+self.correspondence_adapter(af,features[4],context['valid'],context['distance'])
        feat=self.fuse(torch.cat([transferred,aux],1))
        if self.training and self.activation_checkpointing:
            count=len(self.body) if self.checkpoint_blocks is None else self.checkpoint_blocks
            if not 0<=count<=len(self.body):
                raise ValueError('checkpoint_blocks outside trunk depth')
            if count:
                feat=checkpoint(self.body[:count],feat,use_reentrant=False)
            for block in list(self.body.children())[count:]:
                feat=block(feat)
        else:
            feat=self.body(feat)
        feat=self.context(self.mixer(feat))
        return dict(feature=feat,coarse=x[:,4:5],local_context=features[1]+features[2]-2*features[4],
                    gate=weights,pad_h=ph,pad_w=pw)


class FrequencyDecoder(nn.Module):
    """Partition of unity applied to independent latent residual predictions."""
    def __init__(self,c):
        super().__init__()
        self.heads=nn.ModuleList([nn.Conv2d(c,1,3,padding=1) for _ in range(3)])
        for head in self.heads:
            nn.init.zeros_(head.weight)
            nn.init.zeros_(head.bias)

    def forward(self,feat):
        parts=[]
        for i,head in enumerate(self.heads):
            parts.append(DualDomainRefiner._bands(head(feat))[i])
        return sum(parts)


class PASTNetV2(PASTNetMA3Aggressive2p5D):
    def __init__(self,variant='correspondence',**config):
        if variant not in VARIANTS:
            raise ValueError(variant)
        defaults=dict(input_channels=13,base_channels=64,num_blocks=10,context_blocks=2,
                      temporal_refine=True,refine_scale=.35,latent_mixer='multiscale',
                      latent_scales=(2,4),latent_scale=.35,aggressive_mode='dual_domain',
                      aggressive_channels=48,aggressive_scale=.18)
        defaults.update(config)
        super().__init__(**defaults)
        self.variant=variant
        phy,corr,freq,_,self.anchor_count=VARIANTS[variant]
        previous=self.base.single
        trunk=PhysicalAnchorTrunk(phy,corr,input_channels=13,base_channels=defaults['base_channels'],
            num_blocks=defaults['num_blocks'],context_blocks=defaults['context_blocks'],
            temporal_refine=defaults['temporal_refine'],refine_scale=defaults['refine_scale'],
            residual_scale=defaults.get('residual_scale',1),window_size=defaults.get('window_size',8),
            mlp_ratio=defaults.get('mlp_ratio',2))
        trunk.load_state_dict(previous.state_dict(),strict=False)
        self.base.single=trunk
        self.frequency_decoder=FrequencyDecoder(defaults['base_channels']) if freq else None
        self._frequency_feature=None

    def load_g086(self,payload):
        state=payload['model_state_dict']
        own=self.state_dict()
        missing_old=[k for k,v in state.items() if k not in own or own[k].shape!=v.shape]
        if missing_old:
            raise ValueError(f'G086 mapping mismatch: {missing_old[:5]}')
        result=self.load_state_dict(state,strict=False)
        if result.unexpected_keys or any('adapter' not in k and not k.startswith('frequency_decoder.') for k in result.missing_keys):
            raise ValueError(str(result))
        return dict(mapped=len(state),new=len(result.missing_keys))

    def forward_components(self,batch):
        cond=batch['cond']; b,q,_,h,w=cond.shape
        if q!=3 or batch['anchors'].shape[1]!=self.anchor_count:
            raise ValueError('x4 interval / configured anchor count required')
        repeat=lambda x: x[:,None].expand(-1,3,*x.shape[1:]).reshape(b*3,*x.shape[1:])
        geo=batch['physical']
        interval_mm=(geo[:,:,15]+geo[:,:,16])*20
        phase=geo[:,:,14]
        known=geo[:,:,12]>0
        query_z=torch.where(known,geo[:,:,15]*20,phase*4)
        distances=batch['anchor_z'][:,None,:]-query_z[:,:,None]
        self.base.single.batch_context=dict(physical=geo.reshape(b*3,17),anchors=repeat(batch['anchors']),
            valid=repeat(batch['valid']),distance=distances.reshape(b*3,-1))
        handle=None
        if self.frequency_decoder is not None:
            # Decoder receives the mixed multi-scale latent, before image output.
            def capture(module,inputs):
                self._frequency_feature=inputs[0]
            handle=self.base.single.decoder.register_forward_pre_hook(capture)
        try:
            out=super().forward_components(cond)
            if self.frequency_decoder is not None:
                delta=self.frequency_decoder(self._frequency_feature)[:,:,:h,:w].reshape(b,3,1,h,w)
                out['prediction']=out['prediction']+.10*torch.tanh(delta)
            return out
        finally:
            self.base.single.batch_context=None
            self._frequency_feature=None
            if handle is not None:
                handle.remove()

    def forward(self,batch):
        return self.forward_components(batch)['prediction']
