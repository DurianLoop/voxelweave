"""Exhaustive independent CPU support verification on 38 previous development patch geometries."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,time,gc,traceback,hashlib,itertools
from pathlib import Path
import numpy as np
import torch
from scipy.ndimage import affine_transform
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,sha,resource_guard,dump
from full_geometry_support import torch_roundtrip_support

def independently_physical_matrices(record,pivot_zrc,spacing_zrc):
    spacing=np.asarray(spacing_zrc,float)[::-1];pivot=np.asarray(pivot_zrc,float)[::-1]
    def rotate(v,axis,angle):
        c,s=np.cos(angle),np.sin(angle);x,y,z=v
        if axis==0:return np.array([x,c*y-s*z,s*y+c*z])
        if axis==1:return np.array([c*x+s*z,y,-s*x+c*z])
        return np.array([c*x-s*y,s*x+c*y,z])
    matrices=[]
    for reverse in [False,True]:
        columns=[]
        for basis in np.eye(3):
            v=basis*spacing
            if reverse:
                v*=record['scale'];axes=zip([0,1,2],record['degrees_xyz'])
            else:axes=zip([2,1,0],[-a for a in record['degrees_xyz'][::-1]])
            for axis,deg in axes:v=rotate(v,axis,np.deg2rad(deg))
            if not reverse:v/=record['scale']
            columns.append(v/spacing)
        a=np.column_stack(columns);matrices.append((a,pivot-a@pivot))
    return matrices


def independent_mask(plan,geometry,full_shape):
    # Rebuild the original-FOV indicator using global bounds, not the production mask generator.
    lo=np.array(plan['source_low_xyz'])[::-1];hi=np.array(plan['source_high_xyz'])[::-1]
    start=np.array(geometry['start']);target=np.array(plan['target_shape_zrc']);axes=[]
    for axis in range(3):
        if geometry['flips'][axis]:validlo=start[axis]+target[axis]-full_shape[axis];validhi=start[axis]+target[axis]-1
        else:validlo=-start[axis];validhi=full_shape[axis]-1-start[axis]
        coords=np.arange(lo[axis],hi[axis]+1);axes.append((coords>=validlo)&(coords<=validhi))
    return np.minimum(np.minimum(axes[0][:,None,None],axes[1][None,:,None]),axes[2][None,None,:]).astype(np.float64)

def scipy_sampling(source,out_shape,out_low_xyz,in_low_xyz,matrix):
    a,b=matrix
    # Reverse xyz into array zrc. All coordinates are voxel centers, no normalized grids.
    array_a=a[::-1,::-1];offset=(a@np.asarray(out_low_xyz)+b-np.asarray(in_low_xyz))[::-1]
    return affine_transform(source,array_a,offset,output_shape=out_shape,output=np.float64,order=1,mode='grid-constant',cval=0.,prefilter=False)

def independent_support(row,matrices,crop_only):
    plan=row['plan'];target=plan['target_shape_zrc']
    if crop_only:source=np.ones(target,np.float64);slow=[0,0,0];intermediate=target;ilow=[0,0,0]
    else:source=independent_mask(plan,row['geometry'],row['full_shape_zrc']);slow=plan['source_low_xyz'];intermediate=plan['intermediate_shape_zrc'];ilow=plan['intermediate_low_xyz']
    first=scipy_sampling(source,intermediate,ilow,slow,matrices[0]);del source
    return scipy_sampling(first,target,[0,0,0],ilow,matrices[1])

def stats(x):
    supported=x>=1-1e-9
    return dict(voxels=int(x.size),minimum=float(x.min()),mean=float(x.mean()),maximum=float(x.max()),
        fully_supported_voxels=int(supported.sum()),fully_supported_fraction=float(supported.mean()),
        positive_but_incomplete_voxels=int(np.count_nonzero((x>1e-9)&~supported)),
        no_support_voxels=int(np.count_nonzero(x<=1e-9)),fully_supported_mask_sha256=hashlib.sha256(np.packbits(supported.ravel()).tobytes()).hexdigest())

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);torch.set_num_interop_threads(1);resource_guard();started=time.perf_counter()
    out=HERE/'full_support_attempt02';out.mkdir(exist_ok=False)
    src=ROOT/'resolution_and_lesion_followup_2026_10_08/development_geometry_attempt01/receipt.json'
    provenance=read(ROOT/'resolution_and_lesion_followup_2026_10_08/READING_PROVENANCE.json')
    binding=next(b for b in provenance['source_bindings'] if b['path']==src.relative_to(ROOT).as_posix());bind(binding)
    q=read(src);assert q['complete'] and not q['errors'] and len(q['records'])==76
    rows=[r for r in q['records'] if r['input']=='native_reference'];assert len(rows)==38
    receipt=dict(complete=False,errors=[],records=[],medical_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,CUDA_initialized=False,publication_claim_confirmed=False,goal_status='active')
    try:
        for i,row in enumerate(rows):
            tick=time.perf_counter();resource_guard();assert time.perf_counter()-started<600
            paired=next(r for r in q['records'] if r['uid']==row['uid'] and r['patch']==row['patch'] and r['input']=='raw_pchip')
            assert row['plan']==paired['plan'] and row['geometry']==paired['geometry'] and row['full_shape_zrc']==paired['full_shape_zrc']
            # spacing is recovered from the previous real development metadata, no image or GT access.
            previous=read(ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json')
            series=next(s for s in previous['series'] if s['uid']==row['uid'])
            matrices=independently_physical_matrices(row['primitive'],row['pivot_zrc'],series['realized_spacing_zrc_mm'])
            errors=[]
            for matrix,production in zip(matrices,[row['plan']['first_voxel_matrix'],row['plan']['second_voxel_matrix']]):
                a,b=matrix;p=np.array(production)
                for corner in itertools.product([0,127],[0,127],[0,63]):errors.append(float(np.max(np.abs(a@corner+b-(p[:3,:3]@corner+p[:3,3])))))
            coordinate_error=max(errors);assert coordinate_error<=3e-12
            record=dict(patient=row['patient'],uid=row['uid'],patch=row['patch'],all_target_voxels_verified=True,coordinate_max_voxel_error=coordinate_error)
            production_masks=[]
            for crop_only,key in [(True,'crop_only'),(False,'real_full_FOV_geometry')]:
                prod=torch_roundtrip_support(row['plan'],row['geometry'],row['full_shape_zrc'],crop_only)
                replay=independent_support(row,matrices,crop_only)
                error=float(np.max(np.abs(prod-replay)));disagreements=int(np.count_nonzero((prod>=1-1e-9)!=(replay>=1-1e-9)))
                assert error<=3e-6 and disagreements==0,(i,key,error,disagreements)
                record[key]=dict(**stats(prod),independent_all_voxel_max_error=error,independent_support_binary_disagreements=disagreements)
                production_masks.append(prod)
                del replay;gc.collect()
            cropped,full=production_masks;assert np.min(full-cropped)>=-3e-6
            record['mean_artificial_crop_support_loss_removed']=float((full-cropped).mean())
            record['residual_original_FOV_missing_mean_weight']=float((1-full).mean())
            record['full_target_support_is_sufficient']=bool(np.all(full>=1-1e-9))
            witness=row['corner_positive_weight_source_outside_full_FOV_witness']
            if witness:
                p=witness['target_xyz'];assert full[p[2],p[1],p[0]]<1-1e-9
                record['previous_positive_weight_witness_confirmed_by_full_mask']=True
            else:record['previous_positive_weight_witness_confirmed_by_full_mask']=None
            record['elapsed_seconds']=time.perf_counter()-tick;receipt['records'].append(record)
            print(json.dumps(dict(patch=i+1,full_support_fraction=record['real_full_FOV_geometry']['fully_supported_fraction'],crop_support_fraction=record['crop_only']['fully_supported_fraction'],all_voxel_verified=True)),flush=True)
            del cropped,full,production_masks;gc.collect()
        receipt.update(complete=True,all38_geometry_pairs_verified=True,all76_production_and_independent_fields_passed=True,
            distinct_geometry_patches=38,development_patients=11,development_series=19,target_voxels_per_patch=1048576,
            distinct_target_voxels_verified=38*1048576,operator_fields_verified=76,
            patches_entirely_supported=sum(r['full_target_support_is_sufficient'] for r in receipt['records']),
            patches_with_any_original_FOV_missing_support=sum(not r['full_target_support_is_sufficient'] for r in receipt['records']),
            support_fraction_range=[min(r['real_full_FOV_geometry']['fully_supported_fraction'] for r in receipt['records']),max(r['real_full_FOV_geometry']['fully_supported_fraction'] for r in receipt['records'])])
    except Exception as e:receipt['errors'].append(type(e).__name__+': '+str(e));traceback.print_exc()
    receipt.update(elapsed_seconds=time.perf_counter()-started,resources=resource_guard(),CUDA_initialized=torch.cuda.is_initialized(),
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'verify_full_geometry_support.py',HERE/'prepare_full_support_v2.py',HERE/'FLOAT64_ORACLE_V2_PROTOCOL.md',HERE/'full_geometry_support.py',HERE/'PROTOCOL.md',src,
            ROOT/'resolution_and_lesion_followup_2026_10_08/roundtrip_support.py',ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json']])
    assert not receipt['CUDA_initialized'];dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:receipt.get(k) for k in ['complete','errors','distinct_target_voxels_verified','patches_entirely_supported','patches_with_any_original_FOV_missing_support','support_fraction_range','elapsed_seconds']}),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
