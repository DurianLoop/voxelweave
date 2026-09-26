import torch

def spatial(x,action,inverse=False):
    """T = rot90(k) after a flip of the last axis, on the two spatial axes."""
    k,f=action%4,action//4
    if not 0<=action<8:raise ValueError(action)
    if inverse:
        x=torch.rot90(x,-k,(-2,-1))
        if f:x=x.flip(-1)
    else:
        if f:x=x.flip(-1)
        x=torch.rot90(x,k,(-2,-1))
    return x.contiguous()

def transform(batch,action):
    out=dict(batch)
    for name in ('cond','anchors','target'):
        if name in batch:out[name]=spatial(batch[name],action)
    p=batch['physical'].clone();axes=p[...,3:12].reshape(*p.shape[:-1],3,3).clone()
    if action//4:axes[...,1]=-axes[...,1]
    for _ in range(action%4):
        # new row points opposite to old column; new column points along old row.
        first=axes[...,0].clone();axes[...,0]=-axes[...,1];axes[...,1]=first
        first=p[...,0].clone();p[...,0]=p[...,1];p[...,1]=first
    p[...,3:12]=axes.flatten(-2);out['physical']=p
    return out
