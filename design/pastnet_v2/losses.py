from __future__ import annotations
import math
import torch
import torch.nn.functional as F


def smooth_cvar(squared, alpha=.9, temperature=.002):
    """Min_t t + E[tau softplus((e-t)/tau)]/(1-alpha), solved per slice.

    Bisection solves the *smooth* stationary equation, not a detached hard
    quantile. Envelope differentiation is valid up to solver tolerance.
    """
    x=squared.float().flatten(1)
    with torch.no_grad():
        lo=x.min(1,keepdim=True).values-20*temperature
        hi=x.max(1,keepdim=True).values+20*temperature
        for _ in range(28):
            mid=(lo+hi)/2
            mass=torch.sigmoid((x-mid)/temperature).mean(1,keepdim=True)
            lo=torch.where(mass>1-alpha,mid,lo)
            hi=torch.where(mass>1-alpha,hi,mid)
        eta=(lo+hi)/2
    return (eta+temperature*F.softplus((x-eta)/temperature).mean(1,keepdim=True)/(1-alpha)).mean()


def reverse_batch(batch):
    b=dict(batch)
    c=batch['cond'].flip(1).clone()
    old=c.clone()
    c[:,:,0:4]=old[:,:,0:4].flip(2)
    c[:,:,5]=1-old[:,:,5]
    c[:,:,6]=-old[:,:,6]
    c[:,:,8]=old[:,:,9]; c[:,:,9]=old[:,:,8]
    c[:,:,10]=-old[:,:,11]; c[:,:,11]=-old[:,:,10]
    c[:,:,12]=c[:,:,11]-c[:,:,10]
    b['cond']=c
    b['anchors']=batch['anchors'].flip(1)
    b['valid']=batch['valid'].flip(1)
    p=batch['physical'].flip(1).clone()
    oldp=p.clone()
    p[:,:,14]=1-oldp[:,:,14]
    p[:,:,15]=oldp[:,:,16]; p[:,:,16]=oldp[:,:,15]
    # axes flattened row-major: third physical direction column changes sign.
    p[:,:,[5,8,11]]=-p[:,:,[5,8,11]]
    b['physical']=p
    gap=torch.where(p[:,0,12]>0,(p[:,0,15]+p[:,0,16])*20,torch.full_like(p[:,0,12],4))
    b['anchor_z']=gap[:,None]-batch['anchor_z'].flip(1)
    return b


def objective(model,batch,epoch,total_epochs,soft_risk=False):
    out=model.forward_components(batch)
    pred=out['prediction'].float()
    target=batch['target'].float()
    e=pred-target
    flat=e.flatten(0,1)
    charb=torch.sqrt(e.square()+1e-6).mean()
    grad=(flat[:,:,1:]-flat[:,:,:-1]).abs().mean()+(flat[:,:,:,1:]-flat[:,:,:,:-1]).abs().mean()
    kernel=flat.new_tensor([[0,1,0],[1,-4,1],[0,1,0]]).view(1,1,3,3)
    lap=F.conv2d(flat,kernel,padding=1).abs().mean()
    # Observed endpoints have zero error, so curvature acts on errors only.
    interval=F.pad(e[:,:,0],(0,0,0,0,1,1))
    zloss=(interval[:,:-2]-2*interval[:,1:-1]+interval[:,2:]).abs().mean()
    symmetry=F.l1_loss(pred,model(reverse_batch(batch)).float().flip(1))
    if soft_risk:
        progress=min(1.,max(0.,(epoch/total_epochs-.2)/.4))
        risk=smooth_cvar(flat.square(),alpha=.5+.4*progress,temperature=.002)
        risk_weight=.2*progress
    else:
        x=flat.square().flatten(1)
        risk=x.topk(max(1,math.ceil(x.shape[1]*.1)),dim=1,sorted=False).values.mean()
        risk_weight=.2
    loss=(charb+.35*e.square().mean()+.04*grad+.003*lap+.01*zloss+.002*symmetry
          +.0008*(pred-batch['cond'][:,:,4:5]).abs().mean()
          +.005*(pred-out['base_prediction'].detach()).abs().mean()+risk_weight*risk)
    return loss,dict(loss=float(loss.detach()),mse=float(e.square().mean().detach()),risk=float(risk.detach()))
