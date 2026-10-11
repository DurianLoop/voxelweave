"""Binary sigmoid adaptation of audited author formulas, explicit per-image/class averaging."""
import torch
def asymmetric_unified(logits,target,weight=.5,delta=.6,gamma=.5,epsilon=1e-7):
    assert logits.shape==target.shape and logits.ndim==4 and logits.shape[1]==1
    assert 0<=weight<=1 and 0<delta<1 and 0<gamma<1 and 0<epsilon<.5
    assert torch.isfinite(logits).all() and torch.isfinite(target).all() and (target>=0).all() and (target<=1).all()
    p=logits.sigmoid();prob=torch.cat((1-p,p),1).clamp(epsilon,1-epsilon)
    truth=torch.cat((1-target,target),1)
    tp=(truth*prob).sum((2,3));fn=(truth*(1-prob)).sum((2,3));fp=((1-truth)*prob).sum((2,3))
    index=(tp+epsilon)/(tp+delta*fn+(1-delta)*fp+epsilon)
    residual=(1-index).clamp_min(0)
    regional=torch.stack((residual[:,0],residual[:,1].pow(1-gamma)),1).mean()
    ce=-truth*prob.log()
    pixel=((1-delta)*(1-prob[:,0]).pow(gamma)*ce[:,0]+delta*ce[:,1]).mean()
    return weight*regional+(1-weight)*pixel
