"""Previous independently verified label/disk-metric functions; no sklearn/torch."""
import os
os.environ['CUDA_VISIBLE_DEVICES']='-1'
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import math,json,hashlib
from pathlib import Path
from fractions import Fraction
import nibabel as nib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def observed_labels(c):
    img=nib.load(ROOT/c['label_file']);inverse=np.rint(np.linalg.inv(np.asarray(c['dicom_rcz_from_label_xyz']))).astype(int)
    rr,cc=np.indices(c['native_shape'][:2]);coords=np.stack([rr.ravel(),cc.ravel(),np.zeros(rr.size,dtype=int)]);planes=[];indices=[]
    for z in range(0,c['native_shape'][2],4):
        coords[2]=z;xyz=inverse[:3,:3]@coords+inverse[:3,3,None];axes=[i for i in range(3) if np.ptp(xyz[i])==0];assert len(axes)==1
        axis=axes[0];index=int(xyz[axis,0]);selection=[slice(None)]*3;selection[axis]=index
        slab=np.asanyarray(img.dataobj[tuple(selection)]);assert slab.nbytes<=32_000_000 and np.isin(slab,[0,1]).all()
        planes.append(slab[tuple(xyz[i] for i in range(3) if i!=axis)].reshape(c['native_shape'][:2]).astype(bool))
        indices.append(dict(native_z=z,label_axis=axis,label_index=index))
    return np.stack(planes,axis=2),indices
def full_truth(c):
    image=nib.load(ROOT/c['label_file']);raw=np.empty(image.shape,bool)
    for z in range(0,image.shape[2],4):
        slab=np.asanyarray(image.dataobj[:,:,z:z+4]);assert slab.nbytes<=32_000_000 and np.isin(slab,[0,1]).all();raw[:,:,z:z+4]=slab
    matrix=np.rint(c['dicom_rcz_from_label_xyz']).astype(int);axes=np.argmax(np.abs(matrix[:3,:3]),axis=1);value=raw.transpose(axes)
    for axis,column in enumerate(axes):
        assert matrix[axis,3]==(value.shape[axis]-1 if matrix[axis,column]<0 else 0)
        if matrix[axis,column]<0:value=np.flip(value,axis)
    return np.ascontiguousarray(value)
def boundary(value):
    core=value.copy()
    for axis in range(3):
        for step in (-1,1):
            at=[slice(None)]*3;neighbor=at.copy();at[axis]=slice(1,None) if step<0 else slice(None,-1);neighbor[axis]=slice(None,-1) if step<0 else slice(1,None)
            core[tuple(at)]&=value[tuple(neighbor)]
        for edge in (0,-1):at=[slice(None)]*3;at[axis]=edge;core[tuple(at)]=False
    return value&~core
def compare(a,b):
    if isinstance(b,float):assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
    elif isinstance(b,dict):
        assert set(a)==set(b)
        for key in b:compare(a[key],b[key])
    else:assert a==b,(a,b)
def center_neighbors(n,m):
    low=[];high=[]
    for j in range(m):
        q=max(Fraction(0),min(Fraction((2*j+1)*n-m,2*m),Fraction(n-1)))
        low.append(q.numerator//q.denominator);high.append(-((-q.numerator)//q.denominator))
    return np.array(low),np.array(high)
def physical_support(native,grid):
    out=native.transpose(2,0,1).copy()
    for axis,(n,m) in enumerate(zip(out.shape,grid['unpadded_shape_zrc'])):
        low,high=center_neighbors(n,m);out=np.take(out,low,axis=axis)|np.take(out,high,axis=axis)
    return np.pad(out,grid['padding'],mode='constant',constant_values=False)

def roi_metrics(mask,truth,edge,targets):
    rows,cols=truth.shape[:2];counts=dict(roi_voxels=0,true_positive_voxels=0,boundary_covered_voxels=0,selected_tiles=0,tile_area_voxels=0,tile_true_positive_voxels=0);records=[]
    for z in targets:
        p=mask[:,:,z];t=truth[:,:,z];b=edge[:,:,z];expanded=np.zeros(p.shape,bool);selected=0
        for r in range(0,rows,32):
            for c in range(0,cols,32):
                sl=(slice(r,min(rows,r+32)),slice(c,min(cols,c+32)))
                if p[sl].any():expanded[sl]=True;selected+=1
        per=dict(roi_voxels=int(p.sum()),true_positive_voxels=int((p&t).sum()),boundary_covered_voxels=int((p&b).sum()),selected_tiles=selected,tile_area_voxels=int(expanded.sum()),tile_true_positive_voxels=int((expanded&t).sum()))
        for k,v in per.items():counts[k]+=v
        records.append(dict(z=z,counts=per))
    foreground=sum(int(truth[:,:,z].sum()) for z in targets);nb=sum(int(edge[:,:,z].sum()) for z in targets);area=len(targets)*rows*cols;roi=counts['roi_voxels'];tp=counts['true_positive_voxels']
    m=dict(counts,foreground_recall=tp/foreground if foreground else None,boundary_recall=counts['boundary_covered_voxels']/nb if nb else None,
        roi_precision=tp/roi if roi else None,geometric_mask_dice=2*tp/(roi+foreground) if roi+foreground else None,
        roi_fraction=roi/area,roi_foreground_inflation=roi/foreground if foreground else None,
        tile_foreground_recall=counts['tile_true_positive_voxels']/foreground if foreground else None,tile_fraction=counts['tile_area_voxels']/area)
    return dict(metrics=m,gate_passed=bool(m['foreground_recall']>=.99 and m['boundary_recall']>=.99 and m['tile_foreground_recall']>=.995 and m['roi_fraction']<=.05 and m['tile_fraction']<=.10),target_records=records)
