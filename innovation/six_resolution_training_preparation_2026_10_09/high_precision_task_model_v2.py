"""Separate deterministic non-overlapping 2x2x2 pooling graph; same state/init."""
import torch
from torch.utils.checkpoint import checkpoint
from high_precision_task_model_v1 import HighPrecisionTaskUNet3D as Base,stable_production_total_loss
def disjoint_max_pool3d(x):
 assert x.ndim==5 and all(v%2==0 for v in x.shape[2:])
 b,c,d,h,w=x.shape
 # Window order matches native first maximum: z, then row, then column.
 windows=x.reshape(b,c,d//2,2,h//2,2,w//2,2).permute(0,1,2,4,6,3,5,7).reshape(b,c,d//2,h//2,w//2,8)
 return windows.max(dim=-1).values
class HighPrecisionTaskUNet3D(Base):
 def forward(self,x):
  assert x.dtype==torch.float32;x=x.to(torch.float64);skips=[]
  for i,enc in enumerate(self.encoders):
   if i:x=disjoint_max_pool3d(x)
   x=checkpoint(enc,x,use_reentrant=False,preserve_rng_state=True);skips.append(x)
  outputs=[]
  for up,dec,head,skip in zip(self.ups,self.decoders,self.heads,reversed(skips[:-1])):
   x=up(x);assert x.shape[2:]==skip.shape[2:]
   x=checkpoint(dec,torch.cat((x,skip),dim=1),use_reentrant=False,preserve_rng_state=True);outputs.append(head(x))
  return tuple(reversed(outputs))
