"""Same math/state; checkpoint each conv/norm/activation segment instead of whole block."""
import torch
from torch import nn
from torch.utils.checkpoint import checkpoint
from compact_norm_task_model_v2 import HighPrecisionTaskUNet3D as Base,stable_production_total_loss
from high_precision_task_model_v2 import disjoint_max_pool3d
class SegmentedBlock(nn.Module):
 def __init__(self,original):super().__init__();self.layers=original.layers;assert len(self.layers)==6
 def forward(self,x):
  for start in (0,3):
   def segment(value,start=start):
    for index in range(start,start+3):value=self.layers[index](value)
    return value
   x=checkpoint(segment,x,use_reentrant=False,preserve_rng_state=True)
  return x
class HighPrecisionTaskUNet3D(Base):
 def __init__(self):
  super().__init__();before={n:tuple(v.shape) for n,v in self.state_dict().items()}
  for blocks in (self.encoders,self.decoders):
   for index,block in enumerate(blocks):blocks[index]=SegmentedBlock(block)
  assert before=={n:tuple(v.shape) for n,v in self.state_dict().items()} and len(before)==54
 def forward(self,x):
  assert x.dtype==torch.float32;x=x.to(torch.float64);skips=[]
  for index,enc in enumerate(self.encoders):
   if index:x=disjoint_max_pool3d(x)
   x=enc(x)
   if index<3:skips.append(x)
  outputs=[]
  for up,dec,head in zip(self.ups,self.decoders,self.heads):
   x=up(x);skip=skips.pop();assert x.shape[2:]==skip.shape[2:]
   merged=torch.cat((x,skip),1);del x,skip;x=dec(merged);del merged;outputs.append(head(x))
  assert not skips
  return tuple(reversed(outputs))
