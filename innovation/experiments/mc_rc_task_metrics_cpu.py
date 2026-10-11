"""Existing metric algorithms extracted without Torch; sources recorded beside this file."""
import numpy as np
import nibabel as nib
from scipy.ndimage import binary_erosion, distance_transform_edt, generate_binary_structure
from scipy.spatial import cKDTree
from mc_rc_observed_only_training_input import ROOT, sha, support_domains


def counts(pred,label):
    tp=int(np.count_nonzero(pred&label));fp=int(np.count_nonzero(pred&~label));fn=int(np.count_nonzero(~pred&label));g=tp+fn;s=tp+fp
    return dict(tp=tp,fp=fp,fn=fn,gt_foreground=g,pred_foreground=s,dice=2*tp/(s+g) if s+g else None,precision=tp/s if s else None,recall=tp/g if g else None,signed_relative_volume_error=(s-g)/g if g else None,absolute_relative_volume_error=abs(s-g)/g if g else None,empty_ground_truth=g==0,empty_prediction=s==0)

def surface_metrics(pred,label,affine):
    if not pred.any() or not label.any():return dict(assd_mm=None,hd95_mm=None,undefined_reason='empty prediction or ground truth')
    affine=np.asarray(affine);spacing=np.linalg.norm(affine[:3,:3],axis=0);unit=affine[:3,:3]/spacing
    assert np.allclose(unit.T@unit,np.eye(3),atol=1e-5)
    structure=generate_binary_structure(3,1);p=pred&~binary_erosion(pred,structure=structure,border_value=0);g=label&~binary_erosion(label,structure=structure,border_value=0)
    a=distance_transform_edt(~g,sampling=spacing)[p];b=distance_transform_edt(~p,sampling=spacing)[g];d=np.concatenate([a,b])
    return dict(assd_mm=float(d.mean()),hd95_mm=float(np.quantile(d,.95)),pred_surface_voxels=int(p.sum()),gt_surface_voxels=int(g.sum()),spacing_mm=spacing.tolist(),definition='pooled directed 6-connected voxel surfaces, physical Euclidean distances, linear percentile')

def metrics(pred,label,o):
    result={'full':counts(pred,label)}
    for name,mask in support_domains(o).items():result[name]=counts(pred[:,:,mask],label[:,:,mask]);result[name]['planes']=int(mask.sum())
    result['full_surface']=surface_metrics(pred,label,o.affine_rcz_ras);result['voxel_volume_mm3']=abs(float(np.linalg.det(np.asarray(o.affine_rcz_ras)[:3,:3])))
    return result

def independent_label(case):
    p=ROOT/case['label_file'];assert sha(p)==case['label_sha256'];raw=np.asanyarray(nib.load(p).dataobj);assert np.isin(raw,[0,1]).all()
    t=np.asarray(case['dicom_rcz_from_label_xyz'],int);axes=np.argmax(np.abs(t[:3,:3]),axis=1);assert len(set(axes))==3;result=np.transpose(raw,axes)
    for axis,src in enumerate(axes):
        sign=t[axis,src];assert sign in (-1,1)
        assert t[axis,3]==(result.shape[axis]-1 if sign==-1 else 0)
        if sign<0:result=np.flip(result,axis)
    return np.ascontiguousarray(result,dtype=bool)

def independent_counts(p,g):
    # Different count construction: encode the two binary labels and bincount each slice.
    sums=np.zeros(4,np.int64)
    for z in range(p.shape[2]):sums+=np.bincount((p[:,:,z].astype(np.uint8)+2*g[:,:,z].astype(np.uint8)).ravel(),minlength=4)
    tn,fp,fn,tp=map(int,sums);a=tp+fp;b=tp+fn
    return dict(tp=tp,fp=fp,fn=fn,gt_foreground=b,pred_foreground=a,dice=2*tp/(a+b) if a+b else None,precision=tp/a if a else None,recall=tp/b if b else None,signed_relative_volume_error=(a-b)/b if b else None,absolute_relative_volume_error=abs(a-b)/b if b else None,empty_ground_truth=b==0,empty_prediction=a==0)

def surface_points(x,affine):
    padded=np.pad(x,1);inside=x.copy()
    for axis in range(3):
        for direction in (-1,1):
            slices=[slice(1,1+n) for n in x.shape];slices[axis]=slice(1+direction,1+direction+x.shape[axis]);inside&=padded[tuple(slices)]
    xyz=np.argwhere(x&~inside);return xyz@np.asarray(affine)[:3,:3].T+np.asarray(affine)[:3,3]

def independent_surface(p,g,affine):
    if not p.any() or not g.any():return dict(assd_mm=None,hd95_mm=None)
    a,b=surface_points(p,affine),surface_points(g,affine);da=cKDTree(b).query(a,workers=1)[0];db=cKDTree(a).query(b,workers=1)[0];dist=np.sort(np.concatenate([da,db]));q=(len(dist)-1)*.95;lo=int(q);hi=min(lo+1,len(dist)-1)
    return dict(assd_mm=float(dist.sum()/len(dist)),hd95_mm=float(dist[lo]*(1-(q-lo))+dist[hi]*(q-lo)),pred_surface_voxels=len(a),gt_surface_voxels=len(b))
