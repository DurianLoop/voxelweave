"""Separate numeric branch: FP32 trainable leaves, FP64 graph and logits."""
import torch
from torch import nn
from torch.nn import functional as F
from checkpointed_model import CheckpointedTaskUNet3D
from stable_reduction_task_model_v1 import stable_production_total_loss
class DoubleConvolution(nn.Module):
 def __init__(self,original):
  super().__init__();self.weight=nn.Parameter(original.weight.detach().clone())
  if original.bias is None:self.register_parameter('bias',None)
  else:self.bias=nn.Parameter(original.bias.detach().clone())
  self.transpose=isinstance(original,nn.ConvTranspose3d)
  self.stride=original.stride;self.padding=original.padding;self.dilation=original.dilation;self.groups=original.groups
  self.output_padding=original.output_padding if self.transpose else None
  assert original.padding_mode=='zeros'
 def forward(self,x):
  assert x.dtype==torch.float64 and self.weight.dtype==torch.float32
  w=self.weight.to(torch.float64);b=None if self.bias is None else self.bias.to(torch.float64)
  if self.transpose:return F.conv_transpose3d(x,w,b,self.stride,self.padding,self.output_padding,self.groups,self.dilation)
  return F.conv3d(x,w,b,self.stride,self.padding,self.dilation,self.groups)
class DoubleInstanceNorm(nn.Module):
 def __init__(self,original):
  super().__init__();assert original.affine and not original.track_running_stats
  self.weight=nn.Parameter(original.weight.detach().clone());self.bias=nn.Parameter(original.bias.detach().clone());self.eps=original.eps
 def forward(self,x):
  assert x.dtype==torch.float64 and self.weight.dtype==self.bias.dtype==torch.float32
  var,mean=torch.var_mean(x,dim=(2,3,4),unbiased=False,keepdim=True)
  y=(x-mean)*torch.rsqrt(var+self.eps)
  return y*self.weight.to(torch.float64).reshape(1,-1,1,1,1)+self.bias.to(torch.float64).reshape(1,-1,1,1,1)
class HighPrecisionTaskUNet3D(CheckpointedTaskUNet3D):
 def __init__(self):
  super().__init__();before={n:tuple(v.shape) for n,v in self.state_dict().items()};counts=[0,0]
  def replace(module):
   for name,child in list(module.named_children()):
    if isinstance(child,(nn.Conv3d,nn.ConvTranspose3d)):setattr(module,name,DoubleConvolution(child));counts[0]+=1
    elif isinstance(child,nn.InstanceNorm3d):setattr(module,name,DoubleInstanceNorm(child));counts[1]+=1
    else:replace(child)
  replace(self)
  assert counts==[20,14] and before=={n:tuple(v.shape) for n,v in self.state_dict().items()} and len(before)==54
 def forward(self,x):
  assert x.dtype==torch.float32
  return super().forward(x.to(torch.float64))
