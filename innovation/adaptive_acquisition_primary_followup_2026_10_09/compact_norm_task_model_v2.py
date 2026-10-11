"""Same operators with consumed skip references released before decoder execution."""
import torch
from torch.utils.checkpoint import checkpoint
from compact_norm_task_model_v1 import HighPrecisionTaskUNet3D as Base,stable_production_total_loss
from high_precision_task_model_v2 import disjoint_max_pool3d
class HighPrecisionTaskUNet3D(Base):
 def forward(self,x):
  assert x.dtype==torch.float32;x=x.to(torch.float64);skips=[]
  for index,enc in enumerate(self.encoders):
   if index:x=disjoint_max_pool3d(x)
   x=checkpoint(enc,x,use_reentrant=False,preserve_rng_state=True)
   if index<3:skips.append(x)
  outputs=[]
  for up,dec,head in zip(self.ups,self.decoders,self.heads):
   x=up(x);skip=skips.pop();assert x.shape[2:]==skip.shape[2:]
   merged=torch.cat((x,skip),dim=1);del x,skip
   x=checkpoint(dec,merged,use_reentrant=False,preserve_rng_state=True);del merged
   outputs.append(head(x))
  assert not skips
  return tuple(reversed(outputs))
