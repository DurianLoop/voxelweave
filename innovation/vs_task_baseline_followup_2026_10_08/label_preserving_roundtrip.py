"""Project prototype of image-only forward/inverse resampling; not the author's implementation."""
import sys
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'spatial_adaptation_matched_2026_10_08'))
from spatial_transform import theta
def apply_roundtrip(x,y,records,pivot_zrc,spacing_zrc):
    assert x.dtype==y.dtype==np.float32 and x.shape==y.shape and x.ndim==5 and x.shape[1]==1
    assert len(x)==len(records)==len(pivot_zrc) and np.isfinite(x).all() and np.isin(y,[0,1]).all()
    xx=x.copy();yy=y.copy();metadata=[]
    for i,(p,pivot) in enumerate(zip(records,pivot_zrc)):
        matrix=theta(p,pivot,spacing_zrc,x.shape[2:]);full=np.eye(4);full[:3]=matrix
        reverse=np.linalg.inv(full)[:3]
        meta=dict(first_sampling_theta=matrix.tolist(),second_sampling_theta=reverse.tolist(),resampling_calls=0,
            coordinate_and_intermediate_dtype='float64',output_dtype='float32',labels_transformed=False)
        if p['enabled'] and (p['scale']!=1 or any(p['degrees_xyz'])):
            with torch.inference_mode():
                source=torch.from_numpy(x[i:i+1].astype(np.float64))
                g1=F.affine_grid(torch.from_numpy(matrix[None]),source.shape,align_corners=False)
                first=F.grid_sample(source,g1,mode='bilinear',padding_mode='zeros',align_corners=False)
                g2=F.affine_grid(torch.from_numpy(reverse[None]),source.shape,align_corners=False)
                result=F.grid_sample(first,g2,mode='bilinear',padding_mode='zeros',align_corners=False)
                xx[i]=result[0].numpy().astype(np.float32);meta['resampling_calls']=2
        metadata.append(meta)
    assert np.isfinite(xx).all() and np.array_equal(y,yy)
    return xx,yy,metadata
