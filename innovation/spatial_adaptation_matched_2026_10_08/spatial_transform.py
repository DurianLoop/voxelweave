"""Physical 3D inverse sampling around a preserved supervised training pivot."""
import numpy as np
import torch

def primitives(step,batch=2):
    rng=np.random.default_rng(np.random.SeedSequence([20261007,20261008,824,step]))
    return [dict(enabled=bool(rng.random()<.3),degrees_xyz=rng.uniform(-15,15,3).tolist(),scale=float(rng.uniform(.85,1.15))) for _ in range(batch)]

def pivots(geometry,shape_zrc):
    result=[];shape=np.asarray(shape_zrc)
    for g in geometry:
        if g['forced_foreground']:
            p=np.asarray(g['center'],float)-np.asarray(g['start'],float)
            for axis,flip in enumerate(g['flips']):
                if flip:p[axis]=shape[axis]-1-p[axis]
        else:p=(shape-1)/2
        assert np.all(p>=0) and np.all(p<shape)
        result.append(p.tolist())
    return result

def theta(record,pivot_zrc,spacing_zrc,shape_zrc):
    if not record['enabled']:return np.c_[np.eye(3),np.zeros(3)]
    ax,ay,az=np.deg2rad(record['degrees_xyz']);cx,cy,cz=np.cos([ax,ay,az]);sx,sy,sz=np.sin([ax,ay,az])
    rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    rotation=rz@ry@rx
    spacing=np.asarray(spacing_zrc,float)[::-1];shape=np.asarray(shape_zrc,float)[::-1]
    a=np.diag(1/spacing)@rotation.T@np.diag(spacing)/record['scale']
    normalized=np.diag(2/shape)@a@np.diag(shape/2)
    pivot=2*(np.asarray(pivot_zrc)[::-1]+.5)/shape-1
    return np.c_[normalized,pivot-normalized@pivot]

def apply(x,y,records,pivot_zrc,spacing_zrc):
    assert x.dtype==y.dtype==np.float32 and x.shape==y.shape and x.ndim==5 and x.shape[1]==1
    assert len(x)==len(records)==len(pivot_zrc) and np.isin(y,[0,1]).all()
    xx=x.copy();yy=y.copy();matrices=[]
    for i,(p,pivot) in enumerate(zip(records,pivot_zrc)):
        matrix=theta(p,pivot,spacing_zrc,x.shape[2:]);matrices.append(matrix.tolist())
        if not p['enabled'] or (p['scale']==1 and not any(p['degrees_xyz'])):continue
        grid=torch.nn.functional.affine_grid(torch.from_numpy(matrix[None]),(1,1,*x.shape[2:]),align_corners=False)
        with torch.inference_mode():
            xx[i]=torch.nn.functional.grid_sample(torch.from_numpy(x[i:i+1].astype(np.float64)),grid,
                mode='bilinear',padding_mode='zeros',align_corners=False)[0].numpy().astype(np.float32)
            yy[i]=torch.nn.functional.grid_sample(torch.from_numpy(y[i:i+1].astype(np.float64)),grid,
                mode='nearest',padding_mode='zeros',align_corners=False)[0].numpy().astype(np.float32)
    assert np.isfinite(xx).all() and np.isin(yy,[0,1]).all()
    return xx,yy,matrices
