"""Conservative real-context support for image roundtrip; no claim of invertible interpolation."""
import sys,itertools
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'spatial_adaptation_matched_2026_10_08'))
from spatial_transform import theta

def active(record):return record['enabled'] and (record['scale']!=1 or any(record['degrees_xyz']))

def voxel_matrices(record,pivot_zrc,spacing_zrc,shape_zrc):
    shape=np.asarray(shape_zrc,float)[::-1]
    normal=np.eye(4);normal[:3,:3]=np.diag(2/shape);normal[:3,3]=1/shape-1
    normalized=np.eye(4);normalized[:3]=theta(record,pivot_zrc,spacing_zrc,shape_zrc)
    forward=np.linalg.inv(normal)@normalized@normal
    return forward,np.linalg.inv(forward)

def corners(low,high):return np.asarray(list(itertools.product(*zip(low,high))),dtype=np.float64)

def transform(points,matrix):return points@matrix[:3,:3].T+matrix[:3,3]

def covering_box(points):
    return np.floor(points.min(axis=0)).astype(np.int64)-1,np.ceil(points.max(axis=0)).astype(np.int64)+1

def plan_support(record,pivot_zrc,spacing_zrc,shape_zrc):
    shape=np.asarray(shape_zrc,np.int64);assert shape.shape==(3,) and np.all(shape>1)
    spacing=np.asarray(spacing_zrc,float);assert np.isfinite(spacing).all() and np.all(spacing>0)
    pivot=np.asarray(pivot_zrc,float);assert pivot.shape==(3,) and np.isfinite(pivot).all()
    assert 0<float(record['scale']) and np.isfinite(record['degrees_xyz']).all()
    forward,reverse=voxel_matrices(record,pivot,spacing,shape)
    low=np.zeros(3,np.int64);high=shape[::-1]-1
    if active(record):
        ilow,ihigh=covering_box(transform(corners(low,high),reverse))
        slow,shigh=covering_box(transform(corners(ilow,ihigh),forward))
    else:ilow,ihigh=low.copy(),high.copy();slow,shigh=low.copy(),high.copy()
    return dict(target_shape_zrc=shape.tolist(),source_low_xyz=slow.tolist(),source_high_xyz=shigh.tolist(),
        source_shape_zrc=(shigh-slow+1)[::-1].tolist(),intermediate_low_xyz=ilow.tolist(),intermediate_high_xyz=ihigh.tolist(),
        intermediate_shape_zrc=(ihigh-ilow+1)[::-1].tolist(),first_voxel_matrix=forward.tolist(),second_voxel_matrix=reverse.tolist(),
        active=bool(active(record)),conservative_not_minimal=True,reads_GT=False,reads_image=False)

def grid_for(output_shape_zrc,output_low_xyz,sampling_matrix,input_low_xyz,input_shape_zrc):
    # Integer voxel centers in the shared original-patch lattice, mapped to input normalized coordinates.
    low=torch.as_tensor(output_low_xyz,dtype=torch.float64)
    z,r,c=torch.meshgrid(torch.arange(output_shape_zrc[0],dtype=torch.float64)+low[2],
        torch.arange(output_shape_zrc[1],dtype=torch.float64)+low[1],
        torch.arange(output_shape_zrc[2],dtype=torch.float64)+low[0],indexing='ij')
    xyz=torch.stack((c,r,z),dim=-1)
    matrix=torch.as_tensor(sampling_matrix,dtype=torch.float64)
    mapped=xyz@matrix[:3,:3].T+matrix[:3,3]
    shape=torch.as_tensor(list(input_shape_zrc)[::-1],dtype=torch.float64)
    inp_low=torch.as_tensor(input_low_xyz,dtype=torch.float64)
    return (2*(mapped-inp_low+.5)/shape-1)[None]

def apply_with_context(context,context_low_xyz,y,record,pivot_zrc,spacing_zrc):
    assert context.ndim==y.ndim==3 and context.dtype==y.dtype==np.float32
    assert np.isfinite(context).all() and np.isin(y,[0,1]).all()
    plan=plan_support(record,pivot_zrc,spacing_zrc,y.shape)
    supplied_low=np.asarray(context_low_xyz,np.int64);supplied_high=supplied_low+np.asarray(context.shape)[::-1]-1
    if not (np.all(supplied_low<=plan['source_low_xyz']) and np.all(supplied_high>=plan['source_high_xyz'])):
        raise ValueError('Insufficient real source context: do not synthesize halo with padding')
    labels=y.copy()
    if not plan['active']:
        start=-supplied_low;stop=start+np.asarray(y.shape)[::-1]
        image=context[start[2]:stop[2],start[1]:stop[1],start[0]:stop[0]].copy();return image,labels,plan
    with torch.inference_mode():
        source=torch.from_numpy(context.astype(np.float64))[None,None]
        grid1=grid_for(plan['intermediate_shape_zrc'],plan['intermediate_low_xyz'],plan['first_voxel_matrix'],supplied_low,context.shape)
        first=F.grid_sample(source,grid1,mode='bilinear',padding_mode='zeros',align_corners=False)
        del grid1,source
        grid2=grid_for(y.shape,[0,0,0],plan['second_voxel_matrix'],plan['intermediate_low_xyz'],plan['intermediate_shape_zrc'])
        image=F.grid_sample(first,grid2,mode='bilinear',padding_mode='zeros',align_corners=False)[0,0].numpy().astype(np.float32)
    assert np.isfinite(image).all() and np.array_equal(labels,y)
    return image,labels,plan
