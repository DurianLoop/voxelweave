"""High-precision graph v2 with independently verified compact first-order norm."""
from high_precision_task_model_v2 import HighPrecisionTaskUNet3D as Base,stable_production_total_loss
from compact_double_norm_v1 import CompactDoubleInstanceNorm
class HighPrecisionTaskUNet3D(Base):
 def __init__(self):
  super().__init__();before={n:tuple(v.shape) for n,v in self.state_dict().items()};count=0
  for blocks in (self.encoders,self.decoders):
   for block in blocks:
    for index in (1,4):block.layers[index]=CompactDoubleInstanceNorm(block.layers[index]);count+=1
  assert count==14 and before=={n:tuple(v.shape) for n,v in self.state_dict().items()} and len(before)==54
