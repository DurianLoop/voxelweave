"""Independent physical-coordinate and full patch image/label oracle, no medical arrays/forward."""
import os
for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[k]='1'
os.environ['CUDA_VISIBLE_DEVICES']='-1'
import json,hashlib,sys,time,traceback
from pathlib import Path
import numpy as np
import torch
from scipy.ndimage import map_coordinates
from spatial_transform import apply,theta,primitives
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
torch.set_num_threads(1);torch.set_num_interop_threads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def oracle_coordinates(p,pivot_zrc,spacing_zrc,shape):
    axes=np.indices(shape,dtype=np.float64);xyz=axes[::-1].reshape(3,-1)
    pivot=np.asarray(pivot_zrc)[::-1,None];spacing=np.asarray(spacing_zrc)[::-1,None]
    v=(xyz-pivot)*spacing
    if p['enabled']:
        # R^-1=Rx^-1 Ry^-1 Rz^-1. Explicit axis updates independent of production matrices.
        for axis in (2,1,0):
            angle=-np.deg2rad(p['degrees_xyz'][axis]);c,s=np.cos(angle),np.sin(angle)
            a,b=[(1,2),(2,0),(0,1)][axis]
            va,vb=v[a].copy(),v[b].copy();v[a]=c*va-s*vb;v[b]=s*va+c*vb
        v/=p['scale']
    return ((v/spacing)+pivot)[::-1].reshape(3,*shape)

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();out=HERE/'synthetic_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],checks=[],medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False)
    try:
        resource_guard();shape=(64,128,128);rng=np.random.default_rng(20261008)
        x=rng.standard_normal((2,1,*shape),dtype=np.float32);y=np.zeros_like(x);pivots=[[8,14,9],[31,63,63]];spacing=[.49,.51,.505]
        for i,pivot in enumerate(pivots):
            zz,rr,cc=np.indices(shape);y[i,0]=((zz-pivot[0])**2+(rr-pivot[1])**2+(cc-pivot[2])**2)<=25
        for mode in ['identity','rotation','scale','combined','sampled']:
            records=primitives(1)
            for p in records:
                if mode!='sampled':p['enabled']=mode!='identity'
                if mode in ['identity','scale']:p['degrees_xyz']=[0,0,0]
                if mode in ['identity','rotation']:p['scale']=1
            result,label,matrices=apply(x,y,records,pivots,spacing)
            repeat,relabel,_=apply(x,y,records,pivots,spacing)
            assert np.array_equal(result,repeat) and np.array_equal(label,relabel)
            for i,p in enumerate(records):
                coords=oracle_coordinates(p,pivots[i],spacing,shape)
                grid=torch.nn.functional.affine_grid(torch.tensor(matrices[i],dtype=torch.float64)[None],(1,1,*shape),align_corners=False)[0].numpy()
                sizes=np.asarray(shape[::-1]);prod=((grid+1)*sizes-1)/2;prod=prod[...,::-1].transpose(3,0,1,2)
                coordinate_error=float(np.max(np.abs(prod-coords)));assert coordinate_error<=3e-12
                image=map_coordinates(x[i,0].astype(np.float64),coords,order=1,mode='grid-constant',prefilter=False).astype(np.float32)
                indices=np.rint(coords).astype(np.int64);valid=np.ones(shape,bool)
                for axis,n in enumerate(shape):valid&=(indices[axis]>=0)&(indices[axis]<n)
                truth=np.zeros(shape,np.float32);truth[valid]=y[i,0][tuple(a[valid] for a in indices)]
                label_error=int(np.count_nonzero(truth!=label[i,0]));image_error=float(np.max(np.abs(image-result[i,0])))
                assert label_error==0 and image_error<=3e-6
                assert label[i,0][tuple(pivots[i])]==1
                if mode=='identity':assert np.array_equal(result[i],x[i]) and np.array_equal(label[i],y[i])
                r['checks'].append(dict(mode=mode,sample=i,max_physical_coordinate_error=coordinate_error,max_image_error=image_error,
                    label_disagreements=label_error,pivot_foreground_preserved=True,deterministic=True))
                resource_guard();assert time.perf_counter()-started<300
        r.update(complete=True,all10_full_patch_gates_passed=True,resources_after=resource_guard(),
            source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in [Path(__file__),HERE/'spatial_transform.py',HERE/'PROTOCOL.md']])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    with (out/'receipt.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r),flush=True);return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
