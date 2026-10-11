"""First-order FP64 InstanceNorm with one forward buffer and channel-wise CPU-saved VJP."""
import torch
from torch import nn
from torch.autograd.function import once_differentiable
class CompactDoubleNormFunction(torch.autograd.Function):
 @staticmethod
 def forward(ctx,x,weight,bias,eps):
  assert x.dtype==torch.float64 and x.ndim==5 and weight.dtype==bias.dtype and weight.dtype in (torch.float32,torch.float64)
  assert x.device==weight.device==bias.device and eps==1e-5
  var,mean=torch.var_mean(x,dim=(2,3,4),unbiased=False,keepdim=True);inv=torch.rsqrt(var+eps)
  y=x-mean;y.mul_(inv);y.mul_(weight.to(torch.float64).reshape(1,-1,1,1,1));y.add_(bias.to(torch.float64).reshape(1,-1,1,1,1))
  ctx.input_device=x.device;ctx.weight_dtype=weight.dtype;ctx.bias_dtype=bias.dtype
  ctx.save_for_backward(x.detach().to('cpu',copy=True),weight.detach().to('cpu',dtype=torch.float64,copy=True),mean.detach().to('cpu',copy=True),inv.detach().to('cpu',copy=True))
  return y
 @staticmethod
 @once_differentiable
 def backward(ctx,dy):
  assert dy.dtype==torch.float64
  x,w,mean,inv=ctx.saved_tensors;dx=torch.empty_like(dy);dw=torch.zeros(x.shape[1],dtype=torch.float64);db=torch.zeros_like(dw)
  for batch in range(x.shape[0]):
   for channel in range(x.shape[1]):
    gamma=w[channel].to(ctx.input_device);ii=inv[batch,channel].to(ctx.input_device);mu=mean[batch,channel].to(ctx.input_device)
    normalized=x[batch,channel].to(ctx.input_device)-mu;normalized.mul_(ii)
    grad=dy[batch,channel];product=(grad*normalized).sum();dw[channel]+=product.to('cpu');db[channel]+=grad.sum().to('cpu')
    local=grad-grad.mean();local.sub_(normalized*(product/grad.numel()));local.mul_(gamma*ii);dx[batch,channel].copy_(local)
  return dx,dw.to(ctx.input_device,dtype=ctx.weight_dtype),db.to(ctx.input_device,dtype=ctx.bias_dtype),None
class CompactDoubleInstanceNorm(nn.Module):
 def __init__(self,original):
  super().__init__();self.weight=nn.Parameter(original.weight.detach().clone());self.bias=nn.Parameter(original.bias.detach().clone());self.eps=original.eps
 def forward(self,x):return CompactDoubleNormFunction.apply(x,self.weight,self.bias,self.eps)
