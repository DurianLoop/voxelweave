"""Reuse the frozen STC path on the fixed IXI wavelet checkpoint."""
from pathlib import Path
import torch
from torch import nn
import torch.nn.functional as F
from pastnet_v2_context.model import SparseTrajectory
from pastnet_ixi_wavelet.run import load_model as wavelet_model

ROOT=Path(__file__).resolve().parent
INIT=ROOT.parent/'pastnet_ixi_wavelet/runs/full_wavelet3_ixi_seed3407/best.pth'
INIT_SHA='bee2006a5fde5e006feb42745b7048938c72e008068d7424867f8d0c4dc95acc'
VARIANTS={'local':(False,False,False,False,6),'extended':(False,False,False,False,6)}


class ContextModel(nn.Module):
    def __init__(self,variant):
        super().__init__()
        if variant not in VARIANTS:raise ValueError(variant)
        self.variant=variant
        self.wavelet=wavelet_model('wavelet3',INIT)
        self.trajectory_adapter=SparseTrajectory()

    @property
    def base(self):return self.wavelet.base

    def forward_components(self,batch):
        context=self.trajectory_adapter(batch,self.variant=='extended')
        def inject(module,inputs,output):
            dh=output.shape[-2]-context.shape[-2];dw=output.shape[-1]-context.shape[-1]
            return output+F.pad(context,(0,dw,0,dh),mode='replicate')
        handle=self.base.single.fuse.register_forward_hook(inject)
        central=dict(batch)
        for key in ('anchors','valid','anchor_z'):central[key]=batch[key][:,1:5]
        try:return self.wavelet.forward_components(central)
        finally:handle.remove()

    def forward(self,batch):return self.forward_components(batch)['prediction']


def load_model(variant,checkpoint=None):
    model=ContextModel(variant)
    if checkpoint:
        payload=torch.load(checkpoint,map_location='cpu',weights_only=False)
        if payload['variant']!=variant:raise ValueError('Variant changed')
        model.load_state_dict(payload['model_state_dict'],strict=True)
    return model
