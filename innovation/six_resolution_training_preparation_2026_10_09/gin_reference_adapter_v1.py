"""Small independent GIN preparation; author source is neither imported nor executed."""
import torch
from torch.nn import functional as F

def draw_parameters(shape,seed):
    assert len(shape)==5 and shape[1]==1
    batch=shape[0];g=torch.Generator(device='cpu').manual_seed(seed)
    alpha=torch.rand((batch,1,1,1,1),generator=g)
    layers=[]
    for inputs,outputs in [(1,2),(2,2),(2,2),(2,1)]:
        k=(1,3)[int(torch.randint(2,(1,),generator=g))]
        weight=torch.randn((batch,outputs,inputs,k,k,k),generator=g)
        bias=torch.randn((batch,outputs,1,1,1),generator=g)
        layers.append(dict(weight=weight,bias=bias,k=k))
    return dict(alpha=alpha,layers=layers)

def gin(x,parameters):
    assert x.ndim==5 and x.shape[1]==1 and x.dtype==torch.float32
    assert not x.requires_grad and torch.isfinite(x).all()
    batch=x.shape[0];spatial=x.shape[2:];value=x
    with torch.no_grad():
        for index,layer in enumerate(parameters['layers']):
            w=layer['weight'].to(x.device);bias=layer['bias'].to(x.device)
            outputs,inputs=w.shape[1:3];k=layer['k']
            assert value.shape[1]==inputs
            value=F.conv3d(value.reshape(1,batch*inputs,*spatial),w.reshape(batch*outputs,inputs,k,k,k),
                           padding=k//2,groups=batch).reshape(batch,outputs,*spatial)+bias
            if index<3:value=F.leaky_relu(value,negative_slope=.01)
        alpha=parameters['alpha'].to(x.device);mixed=alpha*value+(1-alpha)*x
        input_norm=torch.linalg.vector_norm(x.reshape(batch,-1),dim=1).reshape(batch,1,1,1,1)
        mixed_norm=torch.linalg.vector_norm(mixed.reshape(batch,-1),dim=1).reshape(batch,1,1,1,1)
        result=mixed*(1/(mixed_norm+1e-5))*input_norm
    return result,dict(input_norm=input_norm,mixed_norm=mixed_norm)

def complementary_mix(a,b,w):
    assert a.shape==b.shape==w.shape and torch.isfinite(w).all()
    assert float(w.min())>=0 and float(w.max())<=1
    return w*a+(1-w)*b,(1-w)*a+w*b

def mean_target_kl(logits,detach_target=False):
    """Author-code direction/reduction for view-first [3,B,C,...] logits."""
    assert logits.shape[0]==3 and logits.shape[2]>=2
    p=logits.softmax(dim=2);target=p.mean(dim=0,keepdim=True).expand_as(p)
    if detach_target:target=target.detach()
    return F.kl_div(logits.log_softmax(dim=2),target,reduction='mean')
