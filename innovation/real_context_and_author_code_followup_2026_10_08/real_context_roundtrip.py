"""Image-only context with explicit unavailable values and unpadded domain support."""
import sys
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'resolution_and_lesion_followup_2026_10_08'))
from roundtrip_support import grid_for

def extract_context(cache,plan,geometry,grid):
    """No GT is accepted. Invalid coordinates have explicit fill and validity zero."""
    assert cache.ndim==3 and cache.dtype==np.float32 and np.isfinite(cache).all()
    low=np.array(plan['source_low_xyz'],np.int64)[::-1];shape=plan['source_shape_zrc']
    points=[];inside=[];unpadded=[];pad=np.array(grid['padding'])[:,0]
    for axis,n in enumerate(shape):
        local=np.arange(n,dtype=np.int64)+low[axis]
        if geometry['flips'][axis]:local=plan['target_shape_zrc'][axis]-1-local
        global_pos=geometry['start'][axis]+local
        points.append(np.clip(global_pos,0,cache.shape[axis]-1))
        inside.append((global_pos>=0)&(global_pos<cache.shape[axis]))
        unpadded.append((global_pos>=pad[axis])&(global_pos<pad[axis]+grid['unpadded_shape_zrc'][axis]))
    exists=inside[0][:,None,None]&inside[1][None,:,None]&inside[2][None,None,:]
    source=(cache[np.ix_(*points)]*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    source[~exists]=0.
    validity=(unpadded[0][:,None,None]&unpadded[1][None,:,None]&unpadded[2][None,None,:]).astype(np.float64)
    return source,validity,dict(cache_coordinates_read=int(exists.sum()),explicit_absent_coordinate_fills=int((~exists).sum()),
        unpadded_source_voxels=int(validity.sum()),source_value_bytes=int(source.nbytes),source_support_bytes=int(validity.nbytes),
        support_semantics='unpadded_resampled_image_domain_not_observed_slice_certificate',GT_read=False)

def apply_context(source,validity,plan):
    assert source.dtype==np.float32 and validity.dtype==np.float64 and source.shape==validity.shape==tuple(plan['source_shape_zrc'])
    assert np.isfinite(source).all() and np.isin(validity,[0.,1.]).all()
    with torch.inference_mode():
        values=torch.from_numpy(np.stack([source.astype(np.float64),validity]))[None]
        first_grid=grid_for(plan['intermediate_shape_zrc'],plan['intermediate_low_xyz'],plan['first_voxel_matrix'],plan['source_low_xyz'],source.shape)
        first=F.grid_sample(values,first_grid,mode='bilinear',padding_mode='zeros',align_corners=False)
        del first_grid,values
        second_grid=grid_for(plan['target_shape_zrc'],[0,0,0],plan['second_voxel_matrix'],plan['intermediate_low_xyz'],plan['intermediate_shape_zrc'])
        outputs=F.grid_sample(first,second_grid,mode='bilinear',padding_mode='zeros',align_corners=False)[0].numpy()
        image=outputs[0].astype(np.float32);support=outputs[1].copy()
    assert np.isfinite(image).all() and np.isfinite(support).all() and support.min()>=-1e-12 and support.max()<=1+1e-12
    return image,support,dict(labels_accepted_by_API=False,interpolated_channels=2,resampling_calls=2,
        source_value_dtype='float32',sampling_and_intermediate_dtype='float64',image_output_dtype='float32',support_output_dtype='float64',
        task_output_independence_certified=False,missing_information_restored=False)
