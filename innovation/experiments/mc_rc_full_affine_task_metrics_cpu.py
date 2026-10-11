"""Physical distances on full affine coordinates, including non-orthogonal axes."""
import numpy as np
from scipy.ndimage import binary_erosion,generate_binary_structure
from scipy.spatial import cKDTree
from mc_rc_task_metrics_cpu import counts
from mc_rc_observed_only_training_input import support_domains
def full_affine_surface(pred,label,affine):
    if not pred.any() or not label.any():return dict(assd_mm=None,hd95_mm=None,undefined_reason='empty prediction or ground truth')
    affine=np.asarray(affine,dtype=np.float64);basis=affine[:3,:3];assert np.isfinite(affine).all() and abs(np.linalg.det(basis))>0
    points=[]
    for mask in (pred,label):
        surface=mask&~binary_erosion(mask,structure=generate_binary_structure(3,1),border_value=0)
        coordinates=np.argwhere(surface).astype(np.float64)
        points.append(coordinates@basis.T+affine[:3,3])
    a,b=points;dist=np.concatenate((cKDTree(b).query(a,workers=1)[0],cKDTree(a).query(b,workers=1)[0]))
    return dict(assd_mm=float(np.mean(dist)),hd95_mm=float(np.quantile(dist,.95)),pred_surface_voxels=len(a),
        gt_surface_voxels=len(b),spacing_mm=np.linalg.norm(basis,axis=0).tolist(),
        definition='pooled directed 6-connected voxel surfaces; full affine RAS Euclidean distances; linear percentile',
        maximum_axis_orthogonality_residual=float(abs((basis/np.linalg.norm(basis,axis=0)).T@(basis/np.linalg.norm(basis,axis=0))-np.eye(3)).max()))
def metrics(pred,label,obs):
    result={'full':counts(pred,label)}
    for name,mask in support_domains(obs).items():result[name]=counts(pred[:,:,mask],label[:,:,mask]);result[name]['planes']=int(mask.sum())
    result['full_surface']=full_affine_surface(pred,label,obs.affine_rcz_ras)
    result['voxel_volume_mm3']=abs(float(np.linalg.det(np.asarray(obs.affine_rcz_ras)[:3,:3])))
    return result
