"""Full-patch synthetic prototype run; fixed sparse scalar oracle, no medical/model arrays."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,time,itertools,math
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
import retrieve_stronger_adaptation_primary as client
from label_preserving_roundtrip import apply_roundtrip,theta
SHAPE=(64,128,128)
def mapped(point,m):
    shape=np.asarray(SHAPE)[::-1];v=2*(np.asarray(point)[::-1]+.5)/shape-1
    return ((m[:,:3]@v+m[:,3]+1)*shape/2-.5)[::-1]
def physical(point,pivot,spacing,record,reverse=False):
    if not record['enabled']:return np.asarray(point,float)
    v=(np.asarray(point)-pivot)[::-1]*np.asarray(spacing)[::-1];ax,ay,az=np.deg2rad(record['degrees_xyz'])
    cx,cy,cz=np.cos([ax,ay,az]);sx,sy,sz=np.sin([ax,ay,az]);x,y,z=v
    if reverse:
        x,y,z=x,cx*y-sx*z,sx*y+cx*z
        x,y,z=cy*x+sy*z,y,-sy*x+cy*z
        x,y,z=cz*x-sz*y,sz*x+cz*y,z
        v=np.array([x,y,z])*record['scale']
    else:
        x,y,z=cz*x+sz*y,-sz*x+cz*y,z
        x,y,z=cy*x-sy*z,y,sy*x+cy*z
        x,y,z=x,cx*y+sx*z,-sx*y+cx*z
        v=np.array([x,y,z])/record['scale']
    return np.asarray(pivot)+(v/np.asarray(spacing)[::-1])[::-1]
def interpolate(point,value_at_integer):
    lower=np.floor(point).astype(int);delta=point-lower;value=0.
    for corner in itertools.product([0,1],repeat=3):
        index=lower+corner
        if np.any(index<0) or np.any(index>=SHAPE):continue
        weight=float(np.prod([delta[a] if corner[a] else 1-delta[a] for a in range(3)]))
        if weight:value+=weight*value_at_integer(tuple(index))
    return value
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1)
    started=time.perf_counter();res=client.resource_guard();out=HERE/'roundtrip_synthetic_attempt01';out.mkdir(exist_ok=False)
    source=np.zeros(SHAPE,np.float32);source[32,64,64]=1;source[12:52,40,80]=1;source[0,64,64]=1
    source[:,0,0]=1;source[6:10,8:12,9:13]=.7
    label=(source>.5).astype(np.float32)[None,None];x=source[None,None]
    source_sha=client.sha(HERE/'label_preserving_roundtrip.py')
    points=list(itertools.product(*[(0,n-1) for n in SHAPE]))
    points += [(32,64,64),(0,64,64),(20,40,80),(6,8,9),(8,10,11),(63,64,64),(32,0,0),(32,127,127)]
    points += [tuple(map(int,p)) for p in np.random.default_rng(20261008).integers([0,0,0],SHAPE,size=(16,3))]
    assert len(points)==32
    recipes=[dict(name='identity',record=dict(enabled=True,degrees_xyz=[0,0,0],scale=1),pivot=[32,64,64],spacing=[.5,.5,.5]),
        dict(name='single_x15',record=dict(enabled=True,degrees_xyz=[15,0,0],scale=1),pivot=[32,64,64],spacing=[.5,.5,.5]),
        dict(name='three_axis_scale085_anisotropic',record=dict(enabled=True,degrees_xyz=[15,-11,8],scale=.85),pivot=[32,64,64],spacing=[.7,.4,1.2]),
        dict(name='disabled_nonzero',record=dict(enabled=False,degrees_xyz=[15,-11,8],scale=1.15),pivot=[32,64,64],spacing=[.7,.4,1.2])]
    records=[]
    for recipe in recipes:
        client.resource_guard();assert time.perf_counter()-started<120 and not torch.cuda.is_initialized()
        begin=time.perf_counter();p=recipe['record'];pivot=np.asarray(recipe['pivot']);spacing=recipe['spacing']
        result,gt,meta=apply_roundtrip(x,label,[p],[pivot],spacing);m1=np.asarray(meta[0]['first_sampling_theta']);m2=np.asarray(meta[0]['second_sampling_theta'])
        a=np.eye(4);a[:3]=m1;b=np.eye(4);b[:3]=m2
        composition_error=float(np.max(np.abs(a@b-np.eye(4))))
        coordinate_error=max(float(np.max(np.abs(mapped(point,m)-physical(point,pivot,spacing,p,rev)))) for point in points for m,rev in [(m1,False),(m2,True)])
        def first_at(point):return interpolate(physical(point,pivot,spacing,p),lambda i:float(source[i]))
        checks=[]
        for point in points:
            expected=interpolate(physical(point,pivot,spacing,p,True),first_at) if meta[0]['resampling_calls'] else float(source[point])
            observed=float(result[(0,0,*point)]);checks.append(dict(point_zrc=point,oracle=expected,observed=observed,error=abs(expected-observed)))
        max_oracle_error=max(c['error'] for c in checks)
        assert composition_error<3e-12 and coordinate_error<3e-12 and max_oracle_error<3e-6
        assert np.array_equal(gt,label) and np.array_equal(x[0,0],source)
        delta=result[0,0]-source
        if meta[0]['resampling_calls']==0:assert np.count_nonzero(delta)==0
        records.append(dict(recipe=recipe,metadata=meta[0],max_composition_error=composition_error,max_physical_coordinate_error=coordinate_error,
            scalar_oracle_fixed_points=checks,max_fixed_point_oracle_error=max_oracle_error,labels_unchanged=True,
            image_changed_voxels=int(np.count_nonzero(delta)),image_max_difference=float(np.max(np.abs(delta))),
            original_nonzero=int(np.count_nonzero(source)),roundtrip_nonzero=int(np.count_nonzero(result)),
            center_impulse_original=1,center_impulse_roundtrip=float(result[0,0,32,64,64]),
            boundary_impulse_original=1,boundary_impulse_roundtrip=float(result[0,0,0,64,64]),elapsed_seconds=time.perf_counter()-begin))
    three=recipes[2];p=three['record'];wrong=dict(enabled=True,degrees_xyz=[-a for a in p['degrees_xyz']],scale=1/p['scale'])
    proper=np.asarray(records[2]['metadata']['second_sampling_theta']);tempting=theta(wrong,three['pivot'],three['spacing'],SHAPE)
    wrong_inverse_error=max(float(np.max(np.abs(mapped(point,tempting)-mapped(point,proper)))) for point in points)
    assert wrong_inverse_error>1e-3
    assert records[1]['image_changed_voxels']>0 and records[2]['image_changed_voxels']>0
    constant=np.ones((1,1,*SHAPE),np.float32);dummy=np.zeros_like(constant);cr,cy,cm=apply_roundtrip(constant,dummy,[recipes[1]['record']],[recipes[1]['pivot']],recipes[1]['spacing'])
    assert np.array_equal(cy,dummy) and float(cr.min())<.5 and float(cr.max())==1
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],shape_zrc=SHAPE,records=records,
        negating_three_Euler_angles_in_same_order_inverse_max_error_voxels=wrong_inverse_error,
        image_roundtrip_not_identity=True,GT_kept_exactly_unchanged=True,constant_image_zero_padding_min=float(cr.min()),
        constant_image_roundtrip_mean=float(cr.mean()),whole_probability_FOV_independent_verification=False,
        author_code_executed=False,medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,CUDA_initialized=False,
        publication_claim_confirmed=False,goal_status='active',resources=res,elapsed_seconds=time.perf_counter()-started,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=client.sha(p)) for p in [Path(__file__),HERE/'label_preserving_roundtrip.py',HERE/'ROUNDTRIP_IMAGE_AUGMENTATION_PROTOCOL.md',HERE/'extraction_attempt01/label_preserving_blocks.json',ROOT/'spatial_adaptation_matched_2026_10_08/spatial_transform.py']])
    assert client.sha(HERE/'label_preserving_roundtrip.py')==source_sha
    client.dump(out/'receipt.json',receipt);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(dict(complete=True,recipes=len(records),whole_synthetic_shape=SHAPE,oracle_points_per_recipe=32,
        max_oracle_error=max(r['max_fixed_point_oracle_error'] for r in records),wrong_negated_Euler_inverse_error_voxels=wrong_inverse_error,
        constant_roundtrip_min=float(cr.min()),constant_roundtrip_mean=float(cr.mean()),elapsed_seconds=receipt['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
