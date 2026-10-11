"""Separate experimental numeric version; FP32 state/convolutions with FP64 norm/loss reductions."""
import torch
from torch import nn
from torch.nn import functional as F
from checkpointed_model import CheckpointedTaskUNet3D
class StableReductionInstanceNorm3D(nn.Module):
 def __init__(self,original):
  super().__init__();assert isinstance(original,nn.InstanceNorm3d) and original.affine and not original.track_running_stats
  self.weight=nn.Parameter(original.weight.detach().clone());self.bias=nn.Parameter(original.bias.detach().clone());self.eps=original.eps
 def forward(self,x):
  assert x.dtype==torch.float32 and self.weight.dtype==self.bias.dtype==torch.float32
  z=x.to(torch.float64);var,mean=torch.var_mean(z,dim=(2,3,4),unbiased=False,keepdim=True)
  shape=(1,-1,1,1,1)
  result=(z-mean)*torch.rsqrt(var+self.eps)
  result=result*self.weight.to(torch.float64).reshape(shape)+self.bias.to(torch.float64).reshape(shape)
  return result.to(x.dtype)
class StableReductionTaskUNet3D(CheckpointedTaskUNet3D):
 def __init__(self):
  super().__init__();before={n:tuple(v.shape) for n,v in self.state_dict().items()};count=0
  for blocks in (self.encoders,self.decoders):
   for block in blocks:
    for idx in (1,4):block.layers[idx]=StableReductionInstanceNorm3D(block.layers[idx]);count+=1
  assert count==14 and before=={n:tuple(v.shape) for n,v in self.state_dict().items()} and len(before)==54
def stable_production_total_loss(outputs,target):
 assert len(outputs)==3 and target.dtype==torch.float32
 terms=[]
 for z in outputs[0]:
  truth=F.interpolate(target,size=z.shape[2:],mode='nearest-exact').to(torch.float64);zd=z.to(torch.float64);p=zd.sigmoid()
  ce=F.binary_cross_entropy_with_logits(zd,truth);dice=1-(2*(p*truth).sum()+1)/(p.sum()+truth.sum()+1);terms.append(ce+dice)
 supervised=sum(t*w for t,w in zip(terms,(4/7,2/7,1/7)))
 final=torch.stack([v[0].to(torch.float64) for v in outputs]);logits=torch.cat((torch.zeros_like(final),final),2)
 distribution=logits.softmax(2);mean=distribution.mean(0,keepdim=True)
 kl=F.kl_div(logits.log_softmax(2),mean,reduction='mean')
 return supervised+.1*kl
