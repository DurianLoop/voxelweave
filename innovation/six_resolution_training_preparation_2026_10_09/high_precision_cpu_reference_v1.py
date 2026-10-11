"""Independent stable mathematical norm reference; FP32 parameters, FP64 convolutions/activations/norm."""
import torch
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
from gin_cpu_differentiable_reference_v1 import nearest_binary_target,independent_total_loss,independent_deep_binary_loss,independent_attached_consensus_loss

def stable_instance_norm(value,weight,bias,output_dtype=None):
    assert value.device.type==weight.device.type==bias.device.type=='cpu'
    x=value.to(torch.float64);w=weight.to(torch.float64);b=bias.to(torch.float64)
    axes=tuple(range(2,value.ndim));shape=(1,-1)+((1,)*(value.ndim-2))
    centered=x-x.mean(axes,keepdim=True)
    variance=(centered*centered).mean(axes,keepdim=True)
    normalized=centered*torch.rsqrt(variance+1e-5)
    return (normalized*w.reshape(shape)+b.reshape(shape)).to(output_dtype or value.dtype)

class FunctionalCPUReference:
    def __init__(self,state,checkpoint_blocks=True):
        self.state={n:torch.nn.Parameter(v.detach().cpu().clone()) for n,v in state.items()}
        self.checkpoint_blocks=checkpoint_blocks;self.block_calls=0;self.whole_model_calls=0
        assert len(self.state)==54 and all(v.dtype==torch.float32 for v in self.state.values())
    def named_parameters(self):return self.state.items()
    def parameters(self):return self.state.values()
    def state_dict(self):return self.state
    def __call__(self,value):
        assert value.device.type=='cpu' and value.dtype==torch.float32 and value.ndim==5
        assert value.shape[1]==1 and all(n%8==0 for n in value.shape[2:])
        self.whole_model_calls+=1;value=value.to(torch.float64);stored=[];heads=[]
        def block(tensor,prefix):
            self.block_calls+=1
            for first in (0,3):
                tensor=F.conv3d(tensor,self.state[f'{prefix}.layers.{first}.weight'].to(torch.float64),padding=(1,1,1))
                tensor=stable_instance_norm(tensor,self.state[f'{prefix}.layers.{first+1}.weight'],self.state[f'{prefix}.layers.{first+1}.bias'])
                tensor=F.leaky_relu(tensor,.01,inplace=False)
            return tensor
        def run(tensor,prefix):
            fn=lambda x:block(x,prefix)
            return checkpoint(fn,tensor,use_reentrant=False,preserve_rng_state=True) if self.checkpoint_blocks else fn(tensor)
        for depth in range(4):
            if depth:value=F.max_pool3d(value,(2,2,2),(2,2,2))
            value=run(value,f'encoders.{depth}');stored.append(value)
        for depth,skip in enumerate(stored[2::-1]):
            value=F.conv_transpose3d(value,self.state[f'ups.{depth}.weight'].to(torch.float64),self.state[f'ups.{depth}.bias'].to(torch.float64),stride=(2,2,2))
            assert value.shape[2:]==skip.shape[2:]
            value=run(torch.cat([value,skip],1),f'decoders.{depth}')
            heads.append(F.conv3d(value,self.state[f'heads.{depth}.weight'].to(torch.float64),self.state[f'heads.{depth}.bias'].to(torch.float64)))
        return tuple(heads[::-1])
