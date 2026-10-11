"""Inference-only FP32 forms; no reference modification or hidden FP64 statistics."""
import types
import torch
def install(model,mode,guard):
 assert mode in ('fp32_centered','fp32_affine_addcmul');count=0
 def normalize(self,x):
  assert not self.training and not torch.is_grad_enabled() and x.dtype==torch.float32
  guard();variance,mean=torch.var_mean(x,dim=(2,3,4),correction=0,keepdim=True)
  inv=torch.rsqrt(variance+self.eps);weight=self.weight.reshape(1,-1,1,1,1);bias=self.bias.reshape(1,-1,1,1,1)
  if mode=='fp32_centered':value=((x-mean)*inv)*weight+bias
  else:
   scale=inv*weight;shift=bias-mean*scale;value=torch.addcmul(shift,x,scale)
  assert value.dtype==torch.float32 and value.shape==x.shape;guard();return value
 for module in model.modules():
  if isinstance(module,torch.nn.InstanceNorm3d):
   assert module.affine and not module.track_running_stats and module.eps==1e-5
   module.forward=types.MethodType(normalize,module);count+=1
 assert count==14
 return count
