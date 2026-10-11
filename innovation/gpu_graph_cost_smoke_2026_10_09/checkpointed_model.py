"""Same TaskUNet3D operators/state with non-reentrant block activation recomputation."""
import torch
from torch.utils.checkpoint import checkpoint
from mc_rc_3d_baseline_2026_10_07 import TaskUNet3D

class CheckpointedTaskUNet3D(TaskUNet3D):
    def forward(self,x):
        skips=[]
        for i,enc in enumerate(self.encoders):
            if i:x=torch.nn.functional.max_pool3d(x,2)
            x=checkpoint(enc,x,use_reentrant=False,preserve_rng_state=True);skips.append(x)
        outputs=[]
        for up,dec,head,skip in zip(self.ups,self.decoders,self.heads,reversed(skips[:-1])):
            x=up(x);assert x.shape[2:]==skip.shape[2:]
            x=checkpoint(dec,torch.cat((x,skip),dim=1),use_reentrant=False,preserve_rng_state=True);outputs.append(head(x))
        return tuple(reversed(outputs))
