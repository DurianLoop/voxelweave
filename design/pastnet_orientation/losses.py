import torch
from pastnet_v2.losses import objective as original
from .transforms import transform
def objective(model,batch,epoch,total_epochs,soft_risk=False):
    action=int(torch.randint(8,()).item()) if model.variant=='orientation' and model.training else 0
    loss,parts=original(model,transform(batch,action),epoch,total_epochs,False)
    parts['orientation_action']=action
    return loss,parts
