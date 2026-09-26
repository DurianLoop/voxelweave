import math
import torch
import torch.nn.functional as F
from pastnet_v2.losses import reverse_batch,smooth_cvar

TAU=.002


def tail_risk(squared,soft,temperature=TAU):
    x=squared.float().flatten(1);n=x.shape[1];k=max(1,math.ceil(.1*n))
    return smooth_cvar(squared,alpha=1-k/n,temperature=temperature) if soft else x.topk(k,dim=1,sorted=False).values.mean()


def objective(model,batch,epoch,total_epochs,soft_risk=False):
    out=model.forward_components(batch)
    pred=out['prediction'].float();target=batch['target'].float();e=pred-target;flat=e.flatten(0,1)
    charb=torch.sqrt(e.square()+1e-6).mean()
    grad=(flat[:,:,1:]-flat[:,:,:-1]).abs().mean()+(flat[:,:,:,1:]-flat[:,:,:,:-1]).abs().mean()
    kernel=flat.new_tensor([[0,1,0],[1,-4,1],[0,1,0]]).view(1,1,3,3)
    lap=F.conv2d(flat,kernel,padding=1).abs().mean()
    interval=F.pad(e[:,:,0],(0,0,0,0,1,1))
    zloss=(interval[:,:-2]-2*interval[:,1:-1]+interval[:,2:]).abs().mean()
    symmetry=F.l1_loss(pred,model(reverse_batch(batch)).float().flip(1))
    risk=tail_risk(flat.square(),soft_risk)
    loss=(charb+.35*e.square().mean()+.04*grad+.003*lap+.01*zloss+.002*symmetry
          +.0008*(pred-batch['cond'][:,:,4:5]).abs().mean()
          +.005*(pred-out['base_prediction'].detach()).abs().mean()+.2*risk)
    return loss,dict(loss=float(loss.detach()),mse=float(e.square().mean().detach()),risk=float(risk.detach()))
