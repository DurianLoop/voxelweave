"""Development label overlap; distinguish padded cache from unpadded image domain."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'): os.environ[key]='1'
import sys,json,time,gc,hashlib,traceback,itertools
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,physical_label,read_reference_label,array_sha,QPATH
from full_geometry_support import torch_roundtrip_support
from verify_full_geometry_support_v2 import independently_physical_matrices,scipy_sampling,stats
from roundtrip_support import grid_for

def domain_masks(row,grid):
    plan=row['plan']; shape=plan['source_shape_zrc']; low=np.array(plan['source_low_xyz'])[::-1]
    pad=np.array(grid['padding'])[:,0]; high=pad+np.array(grid['unpadded_shape_zrc'])-1
    start=np.array(row['geometry']['start']); flip=row['geometry']['flips']; target=np.array(plan['target_shape_zrc'])
    prod_axes=[]; independent_axes=[]
    for axis,n in enumerate(shape):
        local=np.arange(n,dtype=np.int64)+low[axis]
        global_pos=start[axis]+(target[axis]-1-local if flip[axis] else local)
        prod_axes.append((global_pos>=pad[axis])&(global_pos<=high[axis]))
        # Independently solve the allowed interval of patch-local coordinates.
        if flip[axis]: validlo=start[axis]+target[axis]-1-high[axis]; validhi=start[axis]+target[axis]-1-pad[axis]
        else: validlo=pad[axis]-start[axis]; validhi=high[axis]-start[axis]
        independent_axes.append((local>=validlo)&(local<=validhi))
    a=(prod_axes[0][:,None,None]&prod_axes[1][None,:,None]&prod_axes[2][None,None,:]).astype(np.float64)
    b=np.minimum(np.minimum(independent_axes[0][:,None,None],independent_axes[1][None,:,None]),independent_axes[2][None,None,:]).astype(np.float64)
    assert np.array_equal(a,b)
    return a,b

def domain_support(row,grid,matrices):
    plan=row['plan']; prod,independent=domain_masks(row,grid)
    with torch.inference_mode():
        g=grid_for(plan['intermediate_shape_zrc'],plan['intermediate_low_xyz'],plan['first_voxel_matrix'],plan['source_low_xyz'],prod.shape)
        first=F.grid_sample(torch.from_numpy(prod)[None,None],g,mode='bilinear',padding_mode='zeros',align_corners=False)
        del g,prod
        g=grid_for(plan['target_shape_zrc'],[0,0,0],plan['second_voxel_matrix'],plan['intermediate_low_xyz'],plan['intermediate_shape_zrc'])
        result=F.grid_sample(first,g,mode='bilinear',padding_mode='zeros',align_corners=False)[0,0].numpy().copy()
        del first,g
    first=scipy_sampling(independent,plan['intermediate_shape_zrc'],plan['intermediate_low_xyz'],plan['source_low_xyz'],matrices[0])
    replay=scipy_sampling(first,plan['target_shape_zrc'],[0,0,0],plan['intermediate_low_xyz'],matrices[1])
    error=float(np.max(np.abs(result-replay)))
    disagreements=int(np.count_nonzero((result>=1-1e-9)!=(replay>=1-1e-9)))
    assert error<=3e-6 and disagreements==0,(error,disagreements)
    return result,error,disagreements

def overlap(support,fg):
    result={}
    for name,region in [('foreground',fg),('background',~fg)]:
        values=support[region]; n=int(values.size); missing=int(np.count_nonzero(values<1-1e-9))
        result[name]=dict(voxels=n,incomplete_support_voxels=missing,incomplete_support_fraction=missing/n if n else None,
            minimum_support=float(values.min()) if n else None,mean_support=float(values.mean()) if n else None,
            lost_interpolation_weight_sum=float(np.maximum(0,1-values).sum()),
            mean_lost_interpolation_weight=float(np.maximum(0,1-values).mean()) if n else None)
    return result

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);started=time.perf_counter();resource_guard()
    out=HERE/'development_label_support_attempt01';out.mkdir(exist_ok=False)
    priorpath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    prov=read(ROOT/'vs_task_baseline_followup_2026_10_08/READING_PROVENANCE.json')
    bind(next(b for b in prov['source_bindings'] if b['path']==priorpath.relative_to(ROOT).as_posix()))
    previous=read(priorpath);assert previous['complete'] and not previous['errors'] and previous['all38_real_batches_verified']
    qbind=next(b for b in previous['source_bindings'] if b['path']==QPATH.relative_to(ROOT).as_posix());bind(qbind)
    qualified=read(QPATH);assert qualified['complete'] and not qualified['errors']
    reference={s['uid']:s for a in qualified['arms'] if a['kind']=='native_reference' for s in a['cache_records']}
    geo=read(ROOT/'resolution_and_lesion_followup_2026_10_08/development_geometry_attempt01/receipt.json')
    supportpath=HERE/'full_support_attempt02/receipt.json';support=read(supportpath)
    assert support['complete'] and not support['errors'] and support['all76_production_and_independent_fields_passed']
    for b in support['source_bindings']:bind(b)
    rows=[r for r in geo['records'] if r['input']=='native_reference'];assert len(rows)==38
    oldseries={s['uid']:s for s in previous['series']};oldmask={(r['uid'],r['patch']):r for r in support['records']}
    cases=development_cases();assert len(cases)==19 and len({c['patient'] for c,_ in cases})==11
    receipt=dict(complete=False,errors=[],records=[],series=[],GT_arrays_loaded=0,MR_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        GT_used_to_generate_support=False,GT_used_to_select_policy=False,publication_claim_confirmed=False,goal_status='active')
    sources={Path(__file__),HERE/'DEVELOPMENT_LABEL_SUPPORT_PROTOCOL.md',HERE/'DEVELOPMENT_LABEL_SUPPORT_ADDENDUM_PADDING.md',
        priorpath,QPATH,supportpath,ROOT/'resolution_and_lesion_followup_2026_10_08/development_geometry_attempt01/receipt.json',
        HERE/'full_geometry_support.py',HERE/'verify_full_geometry_support_v2.py',ROOT/'resolution_and_lesion_followup_2026_10_08/roundtrip_support.py',
        ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py',
        ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_true_native_reference_v2_2026_10_07.py'}
    try:
        for c,_ in cases:
            resource_guard();assert time.perf_counter()-started<300
            old=oldseries[c['uid']]; grid=lattice(c)
            labelpath=ROOT/c['label_file'];bind(next(b for b in previous['source_bindings'] if b['path']==c['label_file']))
            sources.add(labelpath);target=physical_label(read_reference_label(c),grid);receipt['GT_arrays_loaded']+=1
            assert array_sha(target)==old['physical_label_sha256']==reference[c['uid']]['label_sha256']
            arm=next(a for a in old['arms'] if a['kind']=='native_reference');patches=[]
            for geom in arm['geometry']:
                sl=tuple(slice(s,s+n) for s,n in zip(geom['start'],[64,128,128]));p=target[sl].copy()
                for axis,flip in enumerate(geom['flips']):
                    if flip:p=np.flip(p,axis)
                patches.append(np.ascontiguousarray(p))
            batch=np.stack(patches)[:,None];assert array_sha(batch)==arm['mother_label_sha256'];del target,batch
            sr=dict(patient=c['patient'],uid=c['uid'],unpadded_shape_zrc=grid['unpadded_shape_zrc'],padding_zrc=grid['padding'],
                physical_label_sha256=old['physical_label_sha256'],mother_label_sha256=arm['mother_label_sha256'],patches=[])
            for i,p in enumerate(patches):
                resource_guard();assert time.perf_counter()-started<300
                row=next(r for r in rows if r['uid']==c['uid'] and r['patch']==i)
                assert row['geometry']==arm['geometry'][i] and row['full_shape_zrc']==reference[c['uid']]['shape_zrc']
                assert int(p.sum())==arm['GT_foreground_per_patch'][i]==row['geometry']['target_foreground']
                assert np.isin(p,[0.,1.]).all();fg=p.astype(bool);matrices=independently_physical_matrices(row['primitive'],row['pivot_zrc'],grid['realized_spacing_zrc_mm'])
                errors=[]
                for matrix,production in zip(matrices,[row['plan']['first_voxel_matrix'],row['plan']['second_voxel_matrix']]):
                    a,b=matrix; m=np.array(production)
                    for corner in itertools.product([0,127],[0,127],[0,63]):errors.append(float(np.max(np.abs(a@corner+b-(m[:3,:3]@corner+m[:3,3])))))
                coordinate_error=max(errors);assert coordinate_error<=3e-12
                record=dict(patient=c['patient'],uid=c['uid'],patch=i,forced_foreground=row['geometry']['forced_foreground'],
                    target_label_sha256=array_sha(p),coordinate_max_voxel_error=coordinate_error)
                masks=[]
                for crop,key,oldkey in [(True,'crop_only_cache','crop_only'),(False,'full_padded_cache','real_full_FOV_geometry')]:
                    mask=torch_roundtrip_support(row['plan'],row['geometry'],row['full_shape_zrc'],crop)
                    stat=stats(mask);assert stat['fully_supported_mask_sha256']==oldmask[(c['uid'],i)][oldkey]['fully_supported_mask_sha256']
                    record[key]=dict(support_stats=stat,overlap=overlap(mask,fg));masks.append(mask)
                domain,error,disagreements=domain_support(row,grid,matrices)
                assert np.min(masks[1]-domain)>=-3e-6
                if not any(lo or hi for lo,hi in grid['padding']):assert np.max(np.abs(masks[1]-domain))==0
                record['unpadded_resampled_image_domain']=dict(support_stats=stats(domain),overlap=overlap(domain,fg),
                    independent_all_voxel_max_error=error,independent_binary_disagreements=disagreements)
                record['padded_cache_support_mean_overstatement']=float((masks[1]-domain).mean())
                record['target_label_unchanged']=True;receipt['records'].append(record);sr['patches'].append(i)
                print(json.dumps(dict(patch=len(receipt['records']),foreground_voxels=int(fg.sum()),
                    crop_FG_incomplete=record['crop_only_cache']['overlap']['foreground']['incomplete_support_voxels'],
                    padded_cache_FG_incomplete=record['full_padded_cache']['overlap']['foreground']['incomplete_support_voxels'],
                    unpadded_domain_FG_incomplete=record['unpadded_resampled_image_domain']['overlap']['foreground']['incomplete_support_voxels'])),flush=True)
                del domain,masks,mask,fg;gc.collect()
            receipt['series'].append(sr);del patches,p;gc.collect()
        aggregates={}
        for key in ['crop_only_cache','full_padded_cache','unpadded_resampled_image_domain']:
            result=dict(patches_entirely_supported=sum(r[key]['support_stats']['fully_supported_fraction']==1. for r in receipt['records']),
                patches_with_foreground_incomplete_support=sum(r[key]['overlap']['foreground']['incomplete_support_voxels']>0 for r in receipt['records']))
            for region in ['foreground','background']:
                values=[r[key]['overlap'][region] for r in receipt['records']];n=sum(v['voxels'] for v in values);m=sum(v['incomplete_support_voxels'] for v in values)
                result[region]=dict(patch_exposure_voxels=n,incomplete_support_voxels=m,incomplete_support_fraction=m/n if n else None,
                    lost_interpolation_weight_sum=sum(v['lost_interpolation_weight_sum'] for v in values))
            aggregates[key]=result
        receipt.update(complete=True,development_patients=11,development_series=19,patches=38,distinct_geometry_target_voxels=39845888,
            patch_exposure_counts_are_not_distinct_anatomical_voxels=True,series_with_nonzero_padding=sum(any(lo or hi for lo,hi in s['padding_zrc']) for s in receipt['series']),
            aggregates=aggregates,all38_mother_batch_labels_matched=True,all76_previous_support_mask_hashes_matched=True,
            all38_unpadded_domain_fields_independently_verified=True,geometric_domain_is_not_a_certificate_of_observed_slice_information=True,
            actual_patient_medical_effect_evaluations=0)
    except Exception as e:receipt['errors'].append(type(e).__name__+': '+str(e));receipt['traceback']=traceback.format_exc();traceback.print_exc()
    receipt.update(elapsed_seconds=time.perf_counter()-started,resources=resource_guard(),CUDA_initialized=torch.cuda.is_initialized(),source_bindings=[entry(p) for p in sorted(sources)])
    assert not receipt['CUDA_initialized'];dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:receipt.get(k) for k in ['complete','errors','patches','series_with_nonzero_padding','aggregates','elapsed_seconds']}),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
