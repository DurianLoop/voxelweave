from __future__ import annotations
import numpy as np
from scipy.ndimage import binary_erosion, distance_transform_edt
from skimage.metrics import structural_similarity


def quality(pred,target,spacing=(1.,1.)):
    pred,target=np.asarray(pred,dtype=np.float64),np.asarray(target,dtype=np.float64)
    err=pred-target
    mse=float(np.mean(err**2))
    a=pred-pred.mean(); b=target-target.mean()
    ncc=float((a*b).sum()/max(float(np.linalg.norm(a)*np.linalg.norm(b)),1e-12))
    pm,tm=pred>.1,target>.1
    denom=int(pm.sum()+tm.sum())
    dice=2*int((pm&tm).sum())/denom if denom else 1.
    # This is an intensity-threshold proxy, not anatomical tissue segmentation.
    if pm.any() and tm.any():
        ps=pm^binary_erosion(pm); ts=tm^binary_erosion(tm)
        distances=np.concatenate([distance_transform_edt(~ps,sampling=spacing)[ts],
                                  distance_transform_edt(~ts,sampling=spacing)[ps]])
        hd=float(np.quantile(distances,.95))
    elif not pm.any() and not tm.any():
        hd=0.
    else:
        hd=float(np.hypot(pred.shape[0]*spacing[0],pred.shape[1]*spacing[1]))
    return dict(psnr=-10*np.log10(max(mse,1e-12)),ssim=float(structural_similarity(target,pred,data_range=1.)),
                mae=float(np.abs(err).mean()),mse=mse,ncc=ncc,dice_proxy=dice,hd95_proxy=hd,
                tail10_mse=float(np.sort(err.ravel()**2)[-max(1,err.size//10):].mean()))
