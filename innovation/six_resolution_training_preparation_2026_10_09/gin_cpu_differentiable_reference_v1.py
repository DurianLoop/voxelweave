"""Independent functional CPU graph, binary deep loss and attached mean-target KL."""
import torch
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint

class FunctionalCPUReference:
    def __init__(self,state,checkpoint_blocks=True):
        self.state={n:torch.nn.Parameter(v.detach().cpu().clone()) for n,v in state.items()}
        self.checkpoint_blocks=checkpoint_blocks
        self.block_calls=0;self.whole_model_calls=0
        assert len(self.state)==54 and all(v.dtype==torch.float32 for v in self.state.values())
    def named_parameters(self):return self.state.items()
    def parameters(self):return self.state.values()
    def state_dict(self):return self.state
    def __call__(self,value):
        assert value.device.type=='cpu' and value.dtype==torch.float32 and value.ndim==5
        assert value.shape[1]==1 and all(n%8==0 for n in value.shape[2:])
        self.whole_model_calls+=1;stored=[];heads=[]
        def block(tensor,prefix):
            self.block_calls+=1
            for first in (0,3):
                tensor=F.conv3d(tensor,self.state[f'{prefix}.layers.{first}.weight'],padding=(1,1,1))
                tensor=F.instance_norm(tensor,None,None,self.state[f'{prefix}.layers.{first+1}.weight'],
                                       self.state[f'{prefix}.layers.{first+1}.bias'],True,.1,1e-5)
                tensor=F.leaky_relu(tensor,negative_slope=.01,inplace=False)
            return tensor
        def run(tensor,prefix):
            fn=lambda x:block(x,prefix)
            return checkpoint(fn,tensor,use_reentrant=False,preserve_rng_state=True) if self.checkpoint_blocks else fn(tensor)
        for depth in range(4):
            if depth:value=F.max_pool3d(value,kernel_size=(2,2,2),stride=(2,2,2))
            value=run(value,f'encoders.{depth}');stored.append(value)
        for depth,skip in enumerate(stored[2::-1]):
            value=F.conv_transpose3d(value,self.state[f'ups.{depth}.weight'],self.state[f'ups.{depth}.bias'],stride=(2,2,2))
            assert value.shape[2:]==skip.shape[2:]
            value=run(torch.cat([value,skip],1),f'decoders.{depth}')
            heads.append(F.conv3d(value,self.state[f'heads.{depth}.weight'],self.state[f'heads.{depth}.bias']))
        return tuple(heads[::-1])

def nearest_binary_target(target,shape):
    """Explicit nearest-exact voxel-centre indexes; no interpolation helper."""
    assert target.device.type=='cpu' and target.dtype==torch.float32
    result=target
    for axis,size in enumerate(shape,2):
        old=result.shape[axis]
        index=torch.floor((torch.arange(size,dtype=torch.float64)+.5)*old/size).to(torch.int64)
        index=index.clamp(0,old-1);result=result.index_select(axis,index)
    return result

def independent_deep_binary_loss(outputs,target):
    assert target.device.type=='cpu' and bool(((target==0)|(target==1)).all())
    total=target.new_zeros(())
    for depth,z in enumerate(outputs):
        truth=nearest_binary_target(target,z.shape[2:]);prob=z.sigmoid()
        ce=torch.where(truth.bool(),F.softplus(-z),F.softplus(z)).mean()
        dice=1-(2*(prob*truth).sum()+1)/(prob.sum()+truth.sum()+1)
        total=total+(4,2,1)[depth]/7*(ce+dice)
    return total

def independent_attached_consensus_loss(final_view_logits):
    assert final_view_logits.device.type=='cpu' and final_view_logits.shape[0]==3
    logits=torch.cat((torch.zeros_like(final_view_logits),final_view_logits),2)
    probs=logits.softmax(2);mean=probs.sum(0,keepdim=True)/3
    log_each=logits.log_softmax(2)
    # The mean retains its graph. No detach and no forward-JS substitution.
    return (torch.special.xlogy(mean,mean)-mean*log_each).mean()

def independent_total_loss(all_heads,target,coefficient=.1):
    assert len(all_heads)==3
    final=torch.stack([v[0] for v in all_heads],0)
    return independent_deep_binary_loss(all_heads[0],target)+coefficient*independent_attached_consensus_loss(final)
