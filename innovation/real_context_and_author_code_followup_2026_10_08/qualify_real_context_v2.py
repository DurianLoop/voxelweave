"""Full-voxel independent replay for paired 19 development MRI context inputs."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,json,time,gc,traceback,itertools,hashlib
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,source_image,lattice,physical_mr,physical_label,read_reference_label,array_sha,QPATH
sys.path.insert(0,str(ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'))
from verify_full_geometry_support_v2 import independently_physical_matrices,scipy_sampling
from real_context_roundtrip import extract_context,apply_context

def independent_context(cache,plan,geometry,grid):
    low=np.array(plan['source_low_xyz'])[::-1];high=np.array(plan['source_high_xyz'])[::-1];target=np.array(plan['target_shape_zrc'])
    start=np.array(geometry['start']);flip=np.array(geometry['flips']);shape=np.array(cache.shape)
    global_low=start+np.where(flip,target-1-high,low)
    global_high=start+np.where(flip,target-1-low,high)
    a=np.maximum(global_low,0);b=np.minimum(global_high,shape-1);assert np.all(b>=a)
    chunk=cache[tuple(slice(int(lo),int(hi)+1) for lo,hi in zip(a,b))].copy()
    domain=np.ones(chunk.shape,np.float64);pad=np.array(grid['padding'])[:,0];validhigh=pad+np.array(grid['unpadded_shape_zrc'])-1
    for axis,n in enumerate(chunk.shape):
        positions=a[axis]+np.arange(n);bad=(positions<pad[axis])|(positions>validhigh[axis])
        index=[slice(None)]*3;index[axis]=bad;domain[tuple(index)]=0.
    chunk=(chunk*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32)
    for axis,isflip in enumerate(flip):
        if isflip:chunk=np.flip(chunk,axis);domain=np.flip(domain,axis)
    begin=np.where(flip,start+target-1-b,a-start)-low
    result=np.zeros(plan['source_shape_zrc'],np.float32);valid=np.zeros(result.shape,np.float64)
    sl=tuple(slice(int(s),int(s)+n) for s,n in zip(begin,chunk.shape));result[sl]=chunk;valid[sl]=domain
    return result,valid

def patch_from_cache(cache,geometry):
    sl=tuple(slice(s,s+n) for s,n in zip(geometry['start'],[64,128,128]));p=cache[sl].copy()
    for axis,flip in enumerate(geometry['flips']):
        if flip:p=np.flip(p,axis)
    return np.ascontiguousarray(p)

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);resource_guard();started=time.perf_counter()
    out=HERE/'real_context_attempt02';out.mkdir(exist_ok=False)
    prevroot=ROOT/'full_support_oracle_and_vinn_followup_2026_10_08'
    provenance=read(prevroot/'READING_PROVENANCE.json')
    oldpath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    for p in [prevroot/'development_label_support_attempt01/receipt.json',prevroot/'full_support_attempt02/receipt.json']:
        bind(next(b for b in provenance['source_bindings'] if b['path']==p.relative_to(ROOT).as_posix()))
    full_support=read(prevroot/'full_support_attempt02/receipt.json')
    bind(next(b for b in full_support['source_bindings'] if b['path']==oldpath.relative_to(ROOT).as_posix()))
    previous=read(oldpath);diagnostic=read(prevroot/'development_label_support_attempt01/receipt.json')
    assert previous['complete'] and not previous['errors'] and diagnostic['complete'] and not diagnostic['errors']
    qualified=read(QPATH);assert qualified['complete'] and not qualified['errors']
    bind(next(b for b in previous['source_bindings'] if b['path']==QPATH.relative_to(ROOT).as_posix()))
    refs={a['kind']:{s['uid']:s for s in a['cache_records']} for a in qualified['arms']}
    geometrypath=ROOT/'resolution_and_lesion_followup_2026_10_08/development_geometry_attempt01/receipt.json'
    geo=read(geometrypath);assert geo['complete'] and not geo['errors']
    rows={(r['uid'],r['patch']):r for r in geo['records'] if r['input']=='native_reference'};assert len(rows)==38
    masks={(r['uid'],r['patch']):r for r in diagnostic['records']};oldseries={s['uid']:s for s in previous['series']}
    cases=development_cases();assert len(cases)==19 and len({c['patient'] for c,_ in cases})==11
    receipt=dict(complete=False,errors=[],series=[],records=[],MRI_input_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        patient_neural_forwards=0,training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        support_mask_generation_uses_GT=False,publication_claim_confirmed=False,goal_status='active')
    sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'REAL_CONTEXT_V2_PROTOCOL.md',HERE/'qualify_real_context.py',HERE/'real_context_roundtrip.py',oldpath,QPATH,geometrypath,
        prevroot/'READING_PROVENANCE.json',prevroot/'development_label_support_attempt01/receipt.json',prevroot/'full_support_attempt02/receipt.json',
        prevroot/'verify_full_geometry_support_v2.py',ROOT/'resolution_and_lesion_followup_2026_10_08/roundtrip_support.py',
        ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
        ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py'}
    try:
        for c,row in cases:
            resource_guard();assert time.perf_counter()-started<900
            old=oldseries[c['uid']];grid=lattice(c);begin=time.perf_counter()
            for key in ['label_file','header_file','mr_zip_file']:
                p=ROOT/c[key];sources.add(p);bind(next(b for b in previous['source_bindings'] if b['path']==c[key]))
            sources.add(ROOT/row['observed_package']);bind(next(b for b in previous['source_bindings'] if b['path']==row['observed_package']))
            target=physical_label(read_reference_label(c),grid);receipt['GT_arrays_loaded']+=1
            assert array_sha(target)==old['physical_label_sha256'];label_sha=array_sha(target)
            sr=dict(patient=c['patient'],uid=c['uid'],label_sha256=label_sha,arms=[])
            for kind in ['native_reference','raw_pchip']:
                resource_guard();at=time.perf_counter();normalized,observed_stats=source_image(c,row,kind);cache=physical_mr(normalized,grid);del normalized
                receipt['MRI_input_arrays_loaded']+=1;load_seconds=time.perf_counter()-at
                assert array_sha(cache)==refs[kind][c['uid']]['input_sha256'] and list(cache.shape)==refs[kind][c['uid']]['shape_zrc']
                arm=next(a for a in old['arms'] if a['kind']==kind)
                images=[];labels=[]
                for geometry in arm['geometry']:
                    images.append((patch_from_cache(cache,geometry)*geometry['intensity_scale']+geometry['intensity_shift']).astype(np.float32))
                    labels.append(patch_from_cache(target,geometry))
                mother=np.stack(labels)[:,None];base=np.stack(images)[:,None]
                assert array_sha(mother)==arm['mother_label_sha256'] and array_sha(base)==arm['base_input_sha256']
                del base;mother_sha=array_sha(mother)
                ar=dict(kind=kind,cache_load_seconds=load_seconds,physical_input_sha256=refs[kind][c['uid']]['input_sha256'],patches=[])
                for i,(baseline,truth) in enumerate(zip(images,labels)):
                    resource_guard();assert time.perf_counter()-started<900
                    record=rows[(c['uid'],i)];assert record['geometry']==arm['geometry'][i]
                    plan=record['plan'];geometry=record['geometry'];at=time.perf_counter()
                    context,validity,meta=extract_context(cache,plan,geometry,grid);extract_seconds=time.perf_counter()-at
                    at=time.perf_counter();other,other_valid=independent_context(cache,plan,geometry,grid)
                    assert np.array_equal(context,other) and np.array_equal(validity,other_valid)
                    extract_independent_seconds=time.perf_counter()-at
                    low=np.array(plan['source_low_xyz'])[::-1];sl=tuple(slice(int(-a),int(-a)+n) for a,n in zip(low,baseline.shape))
                    assert np.array_equal(context[sl],baseline)
                    baseline_sha=array_sha(baseline);truth_sha=array_sha(truth);context_sha=array_sha(context)
                    matrices=independently_physical_matrices(record['primitive'],record['pivot_zrc'],grid['realized_spacing_zrc_mm'])
                    coord=[]
                    for (a,b),prod in zip(matrices,[plan['first_voxel_matrix'],plan['second_voxel_matrix']]):
                        m=np.array(prod)
                        for p in itertools.product([0,127],[0,127],[0,63]):coord.append(float(np.max(np.abs(a@p+b-(m[:3,:3]@p+m[:3,3])))))
                    assert max(coord)<=3e-12
                    at=time.perf_counter();result,support,op=apply_context(context,validity,plan);production_seconds=time.perf_counter()-at
                    at=time.perf_counter();first=scipy_sampling(other,plan['intermediate_shape_zrc'],plan['intermediate_low_xyz'],plan['source_low_xyz'],matrices[0])
                    replay=scipy_sampling(first,plan['target_shape_zrc'],[0,0,0],plan['intermediate_low_xyz'],matrices[1]).astype(np.float32);del first
                    first=scipy_sampling(other_valid,plan['intermediate_shape_zrc'],plan['intermediate_low_xyz'],plan['source_low_xyz'],matrices[0])
                    replay_support=scipy_sampling(first,plan['target_shape_zrc'],[0,0,0],plan['intermediate_low_xyz'],matrices[1]);del first
                    replay_seconds=time.perf_counter()-at
                    error=float(np.max(np.abs(result.astype(np.float64)-replay.astype(np.float64))))
                    se=float(np.max(np.abs(support-replay_support)));binary=int(np.count_nonzero((support>=1-1e-9)!=(replay_support>=1-1e-9)))
                    mask_sha=hashlib.sha256(np.packbits((support>=1-1e-9).ravel()).tobytes()).hexdigest()
                    assert error<=3e-6 and se<=3e-6 and binary==0,(kind,c['uid'],i,error,se,binary)
                    assert mask_sha==masks[(c['uid'],i)]['unpadded_resampled_image_domain']['support_stats']['fully_supported_mask_sha256']
                    assert array_sha(truth)==truth_sha and array_sha(baseline)==baseline_sha and array_sha(context)==context_sha
                    r=dict(patient=c['patient'],uid=c['uid'],kind=kind,patch=i,source_geometry=geometry,
                        baseline_sha256=baseline_sha,context_sha256=context_sha,output_sha256=array_sha(result),mother_label_sha256=mother_sha,
                        target_label_sha256=truth_sha,all_target_voxels_independently_replayed=True,intensity_all_voxel_max_error=error,
                        support_all_voxel_max_error=se,support_binary_disagreements=binary,coordinate_max_voxel_error=max(coord),
                        fully_supported_mask_sha256=mask_sha,fully_supported_fraction=float((support>=1-1e-9).mean()),
                        foreground_input_support_incomplete=int(np.count_nonzero((truth>0)&(support<1-1e-9))),
                        changed_output_voxels=int(np.count_nonzero(result!=baseline)),mean_abs_change=float(np.abs(result-baseline).mean()),
                        explicit_support_semantics=meta['support_semantics'],context_metadata=meta,operator_metadata=op,
                        times=dict(context_extract_seconds=extract_seconds,independent_extract_seconds=extract_independent_seconds,
                            production_values_and_support_seconds=production_seconds,independent_values_and_support_seconds=replay_seconds),
                        intermediate_twochannel_bytes=int(2*np.prod(plan['intermediate_shape_zrc'])*8),input_label_unchanged=True)
                    receipt['records'].append(r);ar['patches'].append(i)
                    print(json.dumps(dict(field=len(receipt['records']),kind=kind,max_intensity_error=error,FG_support_incomplete=r['foreground_input_support_incomplete'],production_seconds=production_seconds)),flush=True)
                    del context,validity,other,other_valid,result,support,replay,replay_support;gc.collect()
                assert array_sha(mother)==mother_sha;sr['arms'].append(ar);del cache,mother,images,labels,baseline,truth;gc.collect()
            sr['elapsed_seconds']=time.perf_counter()-begin;receipt['series'].append(sr);del target;gc.collect()
        assert len(receipt['records'])==76
        for r in receipt['records']:
            other=next(s for s in receipt['records'] if s['uid']==r['uid'] and s['patch']==r['patch'] and s['kind']!=r['kind'])
            assert r['source_geometry']==other['source_geometry'] and r['fully_supported_mask_sha256']==other['fully_supported_mask_sha256'] and r['target_label_sha256']==other['target_label_sha256']
        receipt.update(complete=True,all76_real_MRI_fields_replayed=True,development_patients=11,development_series=19,
            distinct_geometry_patches=38,distinct_geometry_target_voxels=39845888,input_specific_intensity_voxels_replayed=76*1048576,
            max_intensity_error=max(r['intensity_all_voxel_max_error'] for r in receipt['records']),max_support_error=max(r['support_all_voxel_max_error'] for r in receipt['records']),
            all76_previous_support_mask_SHA_matched=True,all76_original_labels_kept=True,
            ordinary_augmentation_training_ready=False,full2992_training_geometry_qualified=False,new_patient_medical_effects=0)
    except Exception as e:receipt['errors'].append(type(e).__name__+': '+str(e));receipt['traceback']=traceback.format_exc();traceback.print_exc()
    receipt.update(elapsed_seconds=time.perf_counter()-started,CUDA_initialized=torch.cuda.is_initialized(),resources=resource_guard(),source_bindings=[entry(p) for p in sorted(sources)])
    assert not receipt['CUDA_initialized'];dump(out/'receipt.json',receipt)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps({k:receipt.get(k) for k in ['complete','errors','MRI_input_arrays_loaded','GT_arrays_loaded','all76_real_MRI_fields_replayed','max_intensity_error','max_support_error','elapsed_seconds']}),flush=True)
    return int(not receipt['complete'])
if __name__=='__main__':raise SystemExit(main())
