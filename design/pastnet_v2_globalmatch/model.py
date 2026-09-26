import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2.model import PASTNetV2

VARIANTS={'global':(False,False,False,False,4),'local':(False,False,False,False,4)}


class GlobalCorrespondence(nn.Module):
    """Read each real anchor over its full low-resolution spatial support."""
    def __init__(self,c=64,hidden=32):
        super().__init__()
        self.qk=nn.Conv2d(c,hidden,1,bias=False)
        self.value=nn.Conv2d(c,hidden,1)
        self.read=nn.Sequential(nn.Conv2d(hidden*5+5,64,1),nn.GELU(),
                               nn.Conv2d(64,64,3,padding=1),nn.GELU())
        self.project=nn.Conv2d(64,c,1)
        nn.init.zeros_(self.project.weight);nn.init.zeros_(self.project.bias)
        self._bias_cache={}

    def bias(self,h,w,like,global_support):
        key=(h,w,like.device,like.dtype,global_support)
        if key not in self._bias_cache:
            yy,xx=torch.meshgrid(torch.arange(h,device=like.device),torch.arange(w,device=like.device),indexing='ij')
            y=yy.flatten();x=xx.flatten();dy=y[:,None]-y[None,:];dx=x[:,None]-x[None,:]
            # Fixed broad proximity prior in array coordinates, not claimed mm geometry.
            prior=-.5*((dy.float()/max(1,h/4)).square()+(dx.float()/max(1,w/4)).square())
            if not global_support:prior=prior.masked_fill((dy.abs()>1)|(dx.abs()>1),-torch.inf)
            self._bias_cache[key]=prior.to(like.dtype)
        return self._bias_cache[key]

    def match(self,query,key,value,h,w,global_support):
        q=F.normalize(query.flatten(2).transpose(1,2),dim=-1)
        k=F.normalize(key.flatten(2).transpose(1,2),dim=-1)
        v=value.flatten(2).transpose(1,2)
        result=F.scaled_dot_product_attention(q[:,None],k[:,None],v[:,None],
            attn_mask=self.bias(h,w,q,global_support)[None,None],dropout_p=0.,scale=10.)
        return result[:,0].transpose(1,2).reshape_as(value)

    def forward(self,features,valid,phase,global_support):
        h,w=features[0].shape[-2:]
        low=[F.avg_pool2d(x,8) for x in features]
        sh,sw=low[0].shape[-2:]
        query=self.qk(low[4]);coarse=self.value(low[4]);differences=[]
        for i in range(4):
            values=self.value(low[i])
            matched=self.match(query,self.qk(low[i]),values,sh,sw,global_support)
            differences.append((matched-values)*valid[:,i,None,None,None])
        masks=valid[:,:,None,None].expand(-1,-1,sh,sw)
        q=phase[:,None,None,None].expand(-1,1,sh,sw)
        result=self.project(self.read(torch.cat([*differences,coarse,masks,q],1)))
        return F.interpolate(result,size=(h,w),mode='bilinear',align_corners=False)


class GlobalMatchPASTNet(PASTNetV2):
    def __init__(self,variant='global'):
        if variant not in VARIANTS:raise ValueError(variant)
        super().__init__('control');self.variant=variant
        self.global_adapter=GlobalCorrespondence()

    def forward_components(self,batch):
        features=[];b,q=batch['cond'].shape[:2]
        valid=batch['valid'][:,None].expand(-1,q,-1).reshape(b*q,4)
        phase=batch['cond'][:,:,5,0,0].reshape(-1)
        def capture(module,inputs,output):features.append(output)
        def inject(module,inputs,output):
            if len(features)!=5:raise RuntimeError('Expected four anchors and coarse')
            clean=[x*valid[:,i,None,None,None] if i<4 else x for i,x in enumerate(features)]
            return output+self.global_adapter(clean,valid,phase,self.variant=='global')
        handles=[self.base.single.slice_encoder.register_forward_hook(capture),
                 self.base.single.fuse.register_forward_hook(inject)]
        try:return super().forward_components(batch)
        finally:
            for handle in handles:handle.remove()
