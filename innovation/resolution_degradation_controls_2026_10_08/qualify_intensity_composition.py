"""228 complete MRI fields on the fixed development stress crops, never train or score a model."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,gc,hashlib
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,physical_label,read_reference_label,array_sha,QPATH
from resolution_control import apply,baseline_patch
from independent_resolution import independent_apply
sys.path.insert(0,str(ROOT/'adaptation_paired_pilot_2026_10_08'))
import augmentation as intensity
MODES=['throughplane','inplane','allaxes'];PATCH=(64,128,128)

def label_patch(target,geometry):
    p=target[tuple(slice(int(a),int(a)+n) for a,n in zip(geometry['start'],PATCH))].copy()
    for a,flip in enumerate(geometry['flips']):
        if flip:p=np.flip(p,a)
    return np.ascontiguousarray(p)

def mother_domain(grid,geometry):
    masks=[]
    for a,n in enumerate(PATCH):
        start=int(geometry['start'][a]);low=int(grid['padding'][a][0]);high=low+int(grid['unpadded_shape_zrc'][a])
        m=np.array([low<=start+i<high for i in range(n)],dtype=bool)
        if geometry['flips'][a]:m=m[::-1]
        masks.append(m)
    return masks[0][:,None,None]&masks[1][None,:,None]&masks[2][None,None,:]

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    resource_guard();started=time.perf_counter();out=HERE/'intensity_composition_attempt01';out.mkdir(exist_ok=False)
    terminal=read(HERE/'ACTUAL_REAL_STRESS_TERMINAL_TOOL.json')
    assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==5725
    parent=read(HERE/'real_stress_attempt01/receipt.json')
    assert parent['complete'] and not parent['errors'] and parent['all228_real_stress_MRI_fields_verified']
    for binding in parent['source_bindings']:bind(binding)
    geometrypath=HERE/'geometry_and_synthetic_attempt01/receipt.json';geometry=read(geometrypath)
    assert geometry['complete'] and not geometry['errors'] and geometry['all270_synthetic_fields_verified'] and geometry['all17952_schedule_control_records_verified']
    for b in geometry['source_bindings']:bind(b)
    previous=ROOT/'real_context_and_author_code_followup_2026_10_08'
    oldpath=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    oldcontext=read(previous/'real_context_attempt02/receipt.json')
    bind(next(b for b in oldcontext['source_bindings'] if b['path']==oldpath.relative_to(ROOT).as_posix()))
    old=read(oldpath);assert old['complete'] and not old['errors'];oldseries={x['uid']:x for x in old['series']}
    q=read(QPATH);assert q['complete'] and not q['errors']
    bind(next(b for b in old['source_bindings'] if b['path']==QPATH.relative_to(ROOT).as_posix()))
    refs={a['kind']:{x['uid']:x for x in a['cache_records']} for a in q['arms']}
    cases=development_cases();assert len(cases)==19
    sources={Path(__file__),HERE/'PROTOCOL.md',HERE/'REAL_STRESS_PROTOCOL.md',HERE/'resolution_control.py',HERE/'independent_resolution.py',
             geometrypath,oldpath,QPATH,previous/'real_context_attempt02/receipt.json',HERE/'INTENSITY_COMPOSITION_PROTOCOL.md',HERE/'ACTUAL_REAL_STRESS_TERMINAL_TOOL.json',HERE/'real_stress_attempt01/receipt.json',Path(intensity.__file__),ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',
             ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py'}
    dump(out/'frozen_config.json',dict(expected_fields=228,modes=MODES,primitive_source='fixed_old_stress_scale_0.85_and1.15',
         image_gate=3e-6,coordinate_gate=3e-12,support_binary_gate=0,wall_seconds=1800,source_bindings=[entry(p) for p in sorted(sources)]))
    r=dict(complete=False,errors=[],composition_numeric_failures=[],fields=[],series=[],MRI_input_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
           patient_neural_forwards=0,training_updates=0,validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,
           new_distinct_primary_maintexts_completed=0,new_patient_medical_effects=0,publication_claim_confirmed=False,goal_status='active')
    def guard():
        resource_guard();assert time.perf_counter()-started<1800 and torch.get_num_threads()==1 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    def save():
        r['elapsed_seconds']=time.perf_counter()-started;p=out/'receipt.json.tmp';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');p.replace(out/'receipt.json')
    save();max_image=0.;max_support=0.;max_coordinate=0.;target_exposure=0;valid_exposure=0
    try:
        for ci,(c,row) in enumerate(cases):
            guard();g=lattice(c);oldsr=oldseries[c['uid']]
            for rel in [c['label_file'],c['header_file'],c['mr_zip_file'],row['observed_package']]:
                sources.add(ROOT/rel);bind(next(b for b in old['source_bindings'] if b['path']==rel))
            target=physical_label(read_reference_label(c),g);r['GT_arrays_loaded']+=1
            target_sha=array_sha(target);assert target_sha==oldsr['physical_label_sha256']
            sr=dict(patient=c['patient'],uid=c['uid'],cache_load_seconds={},fields_done=0,physical_label_sha256=target_sha)
            for kind in ['native_reference','raw_pchip']:
                guard();at=time.perf_counter();normalized,st=source_image(c,row,kind);cache=physical_mr(normalized,g);del normalized
                r['MRI_input_arrays_loaded']+=1;sr['cache_load_seconds'][kind]=time.perf_counter()-at
                assert array_sha(cache)==refs[kind][c['uid']]['input_sha256'] and list(cache.shape)==refs[kind][c['uid']]['shape_zrc']
                arm=next(x for x in oldsr['arms'] if x['kind']==kind)
                base=np.stack([baseline_patch(cache,x,PATCH) for x in arm['geometry']])[:,None]
                labels=np.stack([label_patch(target,x) for x in arm['geometry']])[:,None]
                assert array_sha(base)==arm['base_input_sha256'] and array_sha(labels)==arm['mother_label_sha256']
                label_sha=array_sha(labels)
                for pi,geom in enumerate(arm['geometry']):
                    primitive=arm['stress_primitives'][pi];domain=mother_domain(g,geom)
                    domain_sha=hashlib.sha256(np.packbits(domain.ravel()).tobytes()).hexdigest()
                    for mode in MODES:
                        guard();at=time.perf_counter();image,support,meta=apply(cache,g,geom,primitive,mode,PATCH)
                        production_seconds=time.perf_counter()-at;at=time.perf_counter()
                        independent,other,imeta=independent_apply(cache,g,geom,primitive,mode,PATCH)
                        independent_seconds=time.perf_counter()-at
                        image_error=float(np.max(np.abs(image-independent)));support_error=float(np.max(np.abs(support-other)))
                        ip=arm['intensity_primitives'][pi]
                        at=time.perf_counter()
                        composed=intensity.apply(image[None,None],[ip])[0,0]
                        other_composed=intensity.apply(independent[None,None],[ip])[0,0]
                        composition_seconds=time.perf_counter()-at
                        post_error=float(np.max(np.abs(composed-other_composed)))
                        if post_error>3e-6:
                            r['composition_numeric_failures'].append(dict(patient=c['patient'],uid=c['uid'],kind=kind,patch=pi,mode=mode,pre_intensity_error=image_error,post_intensity_error=post_error,intensity_primitives=ip))
                        assert post_error<=3e-6,'Composed intensity error exceeds unchanged 3e-6 gate'
                        binary=int(np.count_nonzero((support>=1-1e-9)!=(other>=1-1e-9)))
                        assert image_error<=3e-6 and support_error<=3e-6 and imeta['coordinate_max_error']<=3e-12 and binary==0
                        assert np.array_equal(support>=1-1e-9,domain) and np.array_equal(other>=1-1e-9,domain)
                        assert np.array_equal(image[~domain],base[pi,0][~domain])
                        assert np.array_equal(independent[~domain],base[pi,0][~domain])
                        assert label_sha==array_sha(labels) and target_sha==array_sha(target)
                        assert hashlib.sha256(np.packbits((support>=1-1e-9).ravel()).tobytes()).hexdigest()==domain_sha
                        r['fields'].append(dict(patient=c['patient'],uid=c['uid'],kind=kind,patch=pi,mode=mode,
                            image_max_error=image_error,post_intensity_max_error=post_error,composition_seconds=composition_seconds,intensity_primitives=ip,postprocessor_independently_reimplemented=False,post_intensity_padding_bitwise_identity_not_claimed=True,support_max_error=support_error,coordinate_max_error=imeta['coordinate_max_error'],
                            binary_disagreements=binary,mother_domain_mask_sha256=domain_sha,inherited_padding_unchanged=True,
                            mother_label_sha256=label_sha,base_input_sha256=arm['base_input_sha256'],output_image_sha256=array_sha(image),
                            target_voxels=int(image.size),validity_voxels=int(domain.sum()),changed_voxels=int(np.count_nonzero(image!=base[pi,0])),
                            production_seconds=production_seconds,independent_seconds=independent_seconds,source=meta))
                        sr['fields_done']+=1;max_image=max(max_image,post_error);max_support=max(max_support,support_error)
                        max_coordinate=max(max_coordinate,imeta['coordinate_max_error']);target_exposure+=image.size;valid_exposure+=int(domain.sum())
                        save();print(json.dumps(dict(field=len(r['fields']),mode=mode,kind=kind,max_image_error=image_error,production_seconds=production_seconds)),flush=True)
                        del image,support,independent,other,composed,other_composed;gc.collect()
                del cache,base,labels;gc.collect()
            assert sr['fields_done']==12;r['series'].append(sr);del target;save()
        assert len(r['fields'])==228 and len(r['series'])==19 and len({x['patient'] for x in r['series']})==11
        r.update(complete=True,all228_stress_composition_error_propagations_verified=True,development_patients=11,development_series=19,
            max_image_error=max_image,max_support_error=max_support,max_coordinate_error=max_coordinate,
            target_input_specific_exposure_voxels=int(target_exposure),valid_input_specific_exposure_voxels=int(valid_exposure),
            resolution_stage_only_inherited_padding_bitwise_preserved=True,post_intensity_padding_identity_not_claimed=True,postprocessor_independently_reimplemented=False,all_original_mother_labels_kept=True,
            complete5984_schedule_real_MRI_not_yet_replayed=True,complete_gamma_bias_noise_not_yet_qualified=True,training_ready=False,
            source_bindings=[entry(p) for p in sorted(sources)])
    except Exception as exc:
        import traceback
        r['errors'].append(type(exc).__name__+': '+str(exc));r['traceback']=traceback.format_exc();traceback.print_exc()
    r['CUDA_initialized']=torch.cuda.is_initialized();save();guard()
    print(json.dumps({k:r.get(k) for k in ['complete','errors','MRI_input_arrays_loaded','GT_arrays_loaded','max_image_error','max_support_error','max_coordinate_error','elapsed_seconds']}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
