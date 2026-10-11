"""Full production-size nonmedical support experiment with independent physical and intensity oracles."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,hashlib,itertools,traceback
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,dump,resource_guard
sys.path.insert(0,str(ROOT/'vs_task_baseline_followup_2026_10_08'))
from label_preserving_roundtrip import apply_roundtrip
from roundtrip_support import plan_support,apply_with_context
SHAPE=(64,128,128)

def arrsha(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()

def physical_map(xyz,record,pivot_zrc,spacing_zrc,reverse=False):
    # Independently rotate physical vectors via three coordinate updates, without theta or matrix inverse.
    v=(np.asarray(xyz,float)-np.asarray(pivot_zrc)[::-1])*np.asarray(spacing_zrc)[::-1]
    if reverse:
        axes=list(zip([0,1,2],record['degrees_xyz']));v=v*record['scale']
    else:axes=list(zip([2,1,0],[-a for a in record['degrees_xyz'][::-1]]))
    for axis,deg in axes:
        a=np.deg2rad(deg);c,s=np.cos(a),np.sin(a);x,y,z=v.copy()
        if axis==0:v=np.array([x,c*y-s*z,s*y+c*z])
        elif axis==1:v=np.array([c*x+s*z,y,-s*x+c*z])
        else:v=np.array([c*x-s*y,s*x+c*y,z])
    if not reverse:v=v/record['scale']
    return v/np.asarray(spacing_zrc)[::-1]+np.asarray(pivot_zrc)[::-1]

def neighbors(pos):
    lo=np.floor(pos).astype(int);f=pos-lo
    for bits in itertools.product([0,1],repeat=3):
        b=np.asarray(bits);yield lo+b,float(np.prod(np.where(b,f,1-f)))

def value_at(context,low_xyz,point):
    ans=0.
    for ijk,w in neighbors(point):
        if w==0:continue
        j=ijk-np.asarray(low_xyz);assert np.all(j>=0) and np.all(j<np.asarray(context.shape)[::-1])
        ans+=w*float(context[j[2],j[1],j[0]])
    return ans

def oracle(context,low_xyz,point,record,pivot,spacing):
    value=0.
    for intermediate,w in neighbors(physical_map(point,record,pivot,spacing,True)):
        if w==0:continue
        value+=w*value_at(context,low_xyz,physical_map(intermediate,record,pivot,spacing))
    return value

def phantom(plan,kind):
    low=plan['source_low_xyz'];shape=plan['source_shape_zrc']
    z=np.arange(shape[0],dtype=float)[:,None,None]+low[2]
    r=np.arange(shape[1],dtype=float)[None,:,None]+low[1]
    c=np.arange(shape[2],dtype=float)[None,None,:]+low[0]
    if kind=='constant':return np.ones(shape,np.float32)
    if kind=='linear':return np.broadcast_to(.5+.001*c+.002*r+.003*z,shape).astype(np.float32).copy()
    if kind=='checker':return np.broadcast_to(((np.floor(c)+np.floor(r)+np.floor(z))%2),shape).astype(np.float32).copy()
    # Nonmedical ellipsoid at the crop border and a two-voxel sheet, with true context outside the target.
    return np.broadcast_to((((c-3)/18)**2+((r-64)/35)**2+((z-32)/16)**2<1)|((r>=93)&(r<95)),shape).astype(np.float32).copy()

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1)
    out=HERE/'support_synthetic_attempt01';out.mkdir(exist_ok=False);started=time.perf_counter();resource_guard()
    result=dict(complete=False,errors=[],records=[],medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        CUDA_initialized=False,validation_pixels_loaded=False,confirmation_patients_opened=False,publication_claim_confirmed=False)
    try:
        y=np.zeros(SHAPE,np.float32);y[17:20,61:66,1:4]=1;yh=arrsha(y)
        center=((np.asarray(SHAPE)-1)/2).tolist()
        trials=[('identity',dict(enabled=True,degrees_xyz=[0,0,0],scale=1.),center,[.9,.4,.4]),
            ('disabled',dict(enabled=False,degrees_xyz=[15,-15,10],scale=.85),center,[1.2,.5,.5]),
            ('centered',dict(enabled=True,degrees_xyz=[15,-12,9],scale=.85),center,[.9,.4,.4]),
            ('off_center',dict(enabled=True,degrees_xyz=[-11,14,-15],scale=1.15),[17,35,62],[1.2,.5,.5])]
        points=list(itertools.product([0,127],[0,127],[0,63]))
        rng=np.random.default_rng(20261008);points.extend(rng.integers([0,0,0],[128,128,64],size=(24,3)).tolist());assert len(points)==32
        for name,record,pivot,spacing in trials:
            resource_guard();assert time.perf_counter()-started<180
            plan=plan_support(record,pivot,spacing,SHAPE)
            if plan['active']:
                e=[]
                for p in points:
                    for reverse in [False,True]:
                        matrix=np.asarray(plan['second_voxel_matrix' if reverse else 'first_voxel_matrix'])
                        e.append(float(np.max(np.abs(matrix[:3,:3]@p+matrix[:3,3]-physical_map(p,record,pivot,spacing,reverse)))))
                assert max(e)<=3e-12
            else:e=[0.]
            for kind in ['constant','linear','checker','wide']:
                tick=time.perf_counter();context=phantom(plan,kind);before=arrsha(context)
                image,yy,observed=apply_with_context(context,plan['source_low_xyz'],y,record,pivot,spacing)
                assert observed==plan and arrsha(context)==before and arrsha(y)==yh and np.array_equal(yy,y)
                if plan['active']:
                    errors=[abs(float(image[p[2],p[1],p[0]])-oracle(context,plan['source_low_xyz'],p,record,pivot,spacing)) for p in points]
                else:errors=[0.]
                assert max(errors)<=3e-6
                start=-np.asarray(plan['source_low_xyz']);stop=start+np.asarray(SHAPE)[::-1]
                original=context[start[2]:stop[2],start[1]:stop[1],start[0]:stop[0]]
                if kind=='constant':assert np.max(np.abs(image-1))<=3e-6
                if kind=='linear':assert np.max(np.abs(image-original))<=3e-6
                if not plan['active']:assert np.array_equal(image,original)
                row=dict(trial=name,phantom=kind,plan=plan,coordinate_oracle_max_voxel_error=max(e),fixed32_point_intensity_oracle_max_error=max(errors),
                    output_min=float(image.min()),output_mean=float(image.mean()),output_max=float(image.max()),
                    max_absolute_change_from_original=float(np.max(np.abs(image-original))),mean_absolute_change=float(np.mean(np.abs(image-original))),
                    labels_exactly_unchanged=True,source_exactly_unchanged=True,elapsed_seconds=time.perf_counter()-tick,
                    target_voxels=int(np.prod(SHAPE)),source_voxels=int(context.size),intermediate_voxels=int(np.prod(plan['intermediate_shape_zrc'])))
                if kind=='constant' and plan['active']:
                    cropped,_,_=apply_roundtrip(original[None,None].copy(),y[None,None], [record],[pivot],spacing)
                    row['crop_only_zero_padding_control']=dict(mean=float(cropped.mean()),min=float(cropped.min()),max=float(cropped.max()))
                    assert float(cropped.mean())<.99
                    try:apply_with_context(original.copy(),[0,0,0],y,record,pivot,spacing)
                    except ValueError:row['insufficient_context_rejected']=True
                    else:raise AssertionError('Insufficient context was silently accepted')
                result['records'].append(row)
                print(json.dumps(dict(trial=name,phantom=kind,oracle_max_error=max(errors),output_mean=row['output_mean'],max_change=row['max_absolute_change_from_original'])),flush=True)
        result.update(complete=True,all16_synthetic_cases_passed=True,independent_full_voxel_intensity_oracle=False,
            independent_oracle_points_per_case=32,constant_support_checked_all_target_voxels=True,linear_preservation_checked_all_target_voxels=True)
    except Exception as e:result['errors'].append(type(e).__name__+': '+str(e));traceback.print_exc()
    result.update(elapsed_seconds=time.perf_counter()-started,resources=resource_guard(),CUDA_initialized=torch.cuda.is_initialized(),
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'roundtrip_support.py',HERE/'SUPPORT_EXPLORATION_PROTOCOL.md',ROOT/'spatial_adaptation_matched_2026_10_08/spatial_transform.py',ROOT/'vs_task_baseline_followup_2026_10_08/label_preserving_roundtrip.py']])
    assert not result['CUDA_initialized'];dump(out/'receipt.json',result)
    assert time.perf_counter()-started<180 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=result['complete'],errors=result['errors'],cases=len(result['records']),elapsed_seconds=result['elapsed_seconds'])),flush=True)
    return int(not result['complete'])
if __name__=='__main__':raise SystemExit(main())
