"""Sparse-input deployment API; observed slices are copied exactly."""
from __future__ import annotations
import numpy as np
import torch
from skimage.transform import resize
from .data import build_sample


@torch.no_grad()
def interpolate_sparse(model,sparse,geometry,device=None,image_size=256,amp=True):
    """sparse: [H,W,N] acquired images; geometry z_mm covers requested 4N-3 grid.

    No dense target argument. Geometry is the explicit query grid in patient mm;
    unknown metadata must use masks zero, never synthetic known orientation.
    Output: native H,W,4N-3 in the original observed intensity units.
    """
    sparse=np.asarray(sparse,dtype=np.float32)
    if sparse.ndim!=3 or sparse.shape[2]<2 or not np.isfinite(sparse).all():
        raise ValueError('At least two finite acquired slices are required')
    h,w,n=sparse.shape;depth=4*n-3
    if len(geometry['z_mm'])!=depth:
        raise ValueError('Geometry must describe every requested query coordinate')
    device=device or next(model.parameters()).device
    lo,hi=float(sparse.min()),float(sparse.max())
    scale=max(hi-lo,1e-8)
    anchors=resize((sparse-lo)/scale,(image_size,image_size,n),preserve_range=True,anti_aliasing=True).astype(np.float32)
    grid=np.zeros((image_size,image_size,depth),np.float32);grid[:,:,::4]=anchors
    out=np.empty((h,w,depth),np.float32)
    rec=dict(geometry=geometry,shape=[h,w,depth],case_id='inference',patient_id='inference')
    model.eval()
    for z in range(0,depth-4,4):
        sample=build_sample(grid,rec,z,image_size,model.anchor_count)
        # The deployment API explicitly discards dummy target construction.
        batch={k:v[None].to(device) for k,v in sample.items() if isinstance(v,torch.Tensor) and k!='target'}
        with torch.autocast(str(device).split(':')[0],enabled=amp and str(device).startswith('cuda')):
            pred=model(batch).float()[0,:,0].cpu().numpy()
        for j in range(3):
            out[:,:,z+j+1]=resize(pred[j],(h,w),preserve_range=True,anti_aliasing=True)*scale+lo
    out[:,:,::4]=sparse
    return out
