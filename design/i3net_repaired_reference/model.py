from argparse import Namespace
import torch
from torch import nn
from torch.utils.checkpoint import checkpoint
from .vendor.basic_model import I3Net

CONFIG=dict(upscale=4,lr_slice_patch=4,hr_slice_patch=13,kernel_size=3,n_feats=64,
            num_blocks=16,res_scale=1,head_num=1,window_size=16,win_num_sqrt=16)


class CheckpointI3Net(I3Net):
    def __init__(self,checkpoint_groups=0):
        super().__init__(Namespace(**CONFIG));self.checkpoint_groups=checkpoint_groups

    def forward(self,x):
        if not self.training or self.checkpoint_groups==0:return super().forward(x)
        if not 0<=self.checkpoint_groups<=8:raise ValueError('0..8 I2 groups')
        x=x.permute(0,3,1,2).contiguous();head=self.head(x);res=head;align=[]
        res=self.alignment[0](res)+res;align.append(res)
        for i,layer in enumerate(self.body):
            res=checkpoint(layer,res,use_reentrant=False) if i<self.checkpoint_groups else layer(res)
            if i in (3,7):res=self.alignment[i//4+1](res)+res;align.append(res)
        res=self.fuse_align(torch.cat(align,1));res+=head
        out=self.tail(res);out[:,::self.args.upscale]=x
        return out.permute(0,2,3,1).contiguous()


class Reference(nn.Module):
    def __init__(self,checkpoint_groups=0):
        super().__init__();self.network=CheckpointI3Net(checkpoint_groups)

    def forward(self,batch):
        anchors=batch['anchors']
        if anchors.shape[1:]!=(4,1,256,256):raise ValueError('Official model requires four 256x256 anchors')
        sparse=anchors[:,:,0].permute(0,2,3,1).contiguous()
        dense=self.network(sparse)
        return dense[...,5:8].permute(0,3,1,2).unsqueeze(2).contiguous()
