"""Geometry-only support operator; neither image reconstruction nor medical segmentation."""
import sys
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'resolution_and_lesion_followup_2026_10_08'))
from roundtrip_support import grid_for

def source_validity(plan,geometry,full_shape_zrc):
    shape=plan['source_shape_zrc'];low=np.asarray(plan['source_low_xyz'])[::-1]
    axes=[]
    for axis,n in enumerate(shape):
        local=np.arange(n,dtype=np.int64)+low[axis]
        if geometry['flips'][axis]:local=plan['target_shape_zrc'][axis]-1-local
        global_points=geometry['start'][axis]+local
        axes.append((global_points>=0)&(global_points<full_shape_zrc[axis]))
    return (axes[0][:,None,None]&axes[1][None,:,None]&axes[2][None,None,:]).astype(np.float64)

def torch_roundtrip_support(plan,geometry,full_shape_zrc,crop_only=False):
    target=plan['target_shape_zrc'];intermediate=target if crop_only else plan['intermediate_shape_zrc']
    ilow=[0,0,0] if crop_only else plan['intermediate_low_xyz']
    if crop_only:source=np.ones(target,np.float64);slow=[0,0,0]
    else:source=source_validity(plan,geometry,full_shape_zrc);slow=plan['source_low_xyz']
    with torch.inference_mode():
        grid=grid_for(intermediate,ilow,plan['first_voxel_matrix'],slow,source.shape)
        first=F.grid_sample(torch.from_numpy(source)[None,None],grid,mode='bilinear',padding_mode='zeros',align_corners=False)
        del grid,source
        grid=grid_for(target,[0,0,0],plan['second_voxel_matrix'],ilow,intermediate)
        result=F.grid_sample(first,grid,mode='bilinear',padding_mode='zeros',align_corners=False)[0,0].numpy().copy()
    assert np.isfinite(result).all() and result.min()>=-1e-12 and result.max()<=1+1e-12
    return result
