"""40 synthetic +228 fixed real stress +3 former-failure fields, unchanged independent oracle."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,itertools,gc,traceback
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OLD=ROOT/'resolution_degradation_controls_2026_10_08'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,QPATH
sys.path.insert(0,str(OLD))
from resolution_control import apply,baseline_patch
from independent_resolution import independent_apply
from qualify_synthetic_and_schedule_v2 import independent_domain
from independent_intensity import apply_reference
import intensity_float64_stats as production
MODES=['throughplane','inplane','allaxes'];KINDS=['native_reference','raw_pchip'];PATCH=(64,128,128)
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter();resources=resource_guard();assert resources['workspace_free_bytes']-4_800_000>=8_000_000_000
    diagnosis=read(HERE/'failed_field_attempt01/receipt.json');assert diagnosis['complete'] and not diagnosis['errors'] and diagnosis['actual_old_failure_reproduced']
    terminal=read(HERE/'ACTUAL_FAILED_FIELD_DIAGNOSIS_TERMINAL_TOOL.json');assert terminal['exit_code']==0 and 'session_id' not in terminal
    old_receipt=OLD/'full_real_pipeline_attempt01/receipt.json';old_config=OLD/'full_real_pipeline_attempt01/frozen_config.json';frozen=read(old_config)
    failed=read(old_receipt)['failed_field']
    assert sha(old_receipt)=='510724eb7b0b554bf0d0e426a74275afb918808a3d617ce2ed11b27804b1fdb5'
    assert sha(OLD/'independent_intensity.py')=='11f3946b80d7c687acb03fedc607881b6813a2982290e9588431ad96cc63c81e'
    metadata_path=ROOT/'vs_task_baseline_followup_2026_10_08/real_development_entry_attempt01/receipt.json'
    bind(next(b for b in frozen['source_bindings'] if b['path']==metadata_path.relative_to(ROOT).as_posix()))
    old=read(metadata_path);series={s['uid']:s for s in old['series']};assert old['complete'] and not old['errors']
    qualification=read(QPATH);refs={a['kind']:{v['uid']:v for v in a['cache_records']} for a in qualification['arms']}
    cases=development_cases();assert len(cases)==19 and len({c['patient'] for c,row in cases})==11
    sources={Path(__file__),HERE/'intensity_float64_stats.py',HERE/'REPAIRED_INTENSITY_QUALIFICATION_PROTOCOL.md',
        HERE/'failed_field_attempt01/receipt.json',HERE/'ACTUAL_FAILED_FIELD_DIAGNOSIS_TERMINAL_TOOL.json',old_receipt,old_config,
        OLD/'independent_intensity.py',OLD/'resolution_control.py',OLD/'independent_resolution.py',
        OLD/'qualify_synthetic_and_schedule_v2.py',metadata_path,QPATH,Path(production.legacy.__file__),
        ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py',
        ROOT/'experiments/mc_rc_3d_baseline_v2_2026_10_07.py'}
    for p in list(sources):
        if p.is_relative_to(HERE) or p in [old_receipt,old_config]:continue
        bind(next(b for b in frozen['source_bindings'] if b['path']==p.relative_to(ROOT).as_posix()))
    for c,row in cases:
        for path in [c['header_file'],c['mr_zip_file'],row['observed_package']]:
            sources.add(bind(next(b for b in frozen['source_bindings'] if b['path']==path)))
    out=HERE/'repaired_stress_attempt01';out.mkdir(exist_ok=False)
    dump(out/'frozen_config.json',dict(expected_fields=271,synthetic_fields=40,real_stress_fields=228,failed_regressions=3,
        image_gate=3e-6,coordinate_gate=3e-12,binary_gate=0,wall_seconds=1800,source_bindings=[entry(p) for p in sorted(sources)]))
    r=dict(complete=False,status='running',errors=[],fields=[],case_index=[{k:c[k] for k in ['patient','uid']} for c,row in cases],
        MRI_input_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,patient_neural_forwards=0,training_updates=0,
        validation_pixels_loaded=False,confirmation_patients_opened=False,lockedIXI_opened=False,new_patient_medical_effects=0,
        publication_claim_confirmed=False,goal_status='active',old_reference_unchanged=True,training_ready=False)
    maxima={};old_delta=0.;current=None
    def guard():
        resource_guard();assert time.perf_counter()-started<1800 and torch.get_num_threads()==1 and not torch.cuda.is_initialized()
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    def save():
        r.update(elapsed_seconds=time.perf_counter()-started,max_errors=maxima,max_new_vs_legacy_intensity_delta=old_delta)
        p=out/'receipt.json.tmp';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');p.replace(out/'receipt.json')
    def check(image,other,support,other_support,domain,coordinate_error,primitive,identity):
        nonlocal current,old_delta
        guard();actual=production.apply(image[None,None],[primitive])[0,0];shared=production.apply(other[None,None],[primitive])[0,0]
        reference=apply_reference(other,primitive);isolated=apply_reference(image,primitive)
        legacy=production.legacy.apply(image[None,None],[primitive])[0,0];old_delta=max(old_delta,float(np.max(np.abs(actual-legacy))))
        errors=dict(pre_intensity_error=float(np.max(np.abs(image-other))),shared_post_intensity_error=float(np.max(np.abs(actual-shared))),
            isolated_intensity_error=float(np.max(np.abs(actual-isolated))),full_chain_error=float(np.max(np.abs(actual-reference))),
            support_error=float(np.max(np.abs(support-other_support))),coordinate_error=float(coordinate_error))
        binary=int(np.count_nonzero((support>=1-1e-9)!=(other_support>=1-1e-9)))
        current=dict(identity=identity,errors=errors,binary_disagreements=binary,intensity_primitive=primitive)
        for name,value in errors.items():assert value<=(3e-12 if name=='coordinate_error' else 3e-6),(name,value)
        assert binary==0 and np.array_equal(support>=1-1e-9,domain) and np.array_equal(other_support>=1-1e-9,domain)
        for name,value in errors.items():maxima[name]=max(maxima.get(name,0.),value)
        r['fields'].append(dict(identity=identity,**errors,binary_disagreements=binary,target_voxels=int(image.size),valid_voxels=int(domain.sum())))
        save()
    save()
    try:
        fixtures=[np.full((7,11,13),2.5,np.float32),np.array([[[3.]]],np.float32)];rng=np.random.default_rng(2026100828)
        fixtures.append(rng.normal(size=(9,17,23)).astype(np.float32));fixtures.append(rng.normal(size=PATCH).astype(np.float32))
        padded=np.zeros(PATCH,np.float32);padded[12:52]=rng.normal(size=(40,128,128)).astype(np.float32);padded[32,50,50]=12.;padded[32,50,51]=-5.;fixtures.append(padded)
        for fi,image in enumerate(fixtures):
            before=array_sha(image);support=np.ones(image.shape,np.float64);domain=np.ones(image.shape,bool)
            for gamma,bias,noise in itertools.product([False,True],repeat=3):
                p=dict(gamma_enabled=gamma,gamma=.7 if fi%2 else 1.5,bias_enabled=bias,bias_coefficients=[-.3,.21,.3],
                       noise_enabled=noise,noise_std=.08,noise_seed=1701+fi)
                check(image,image,support,support,domain,0.,p,dict(scope='synthetic',fixture=fi,gamma=gamma,bias=bias,noise=noise))
                assert array_sha(image)==before
        del fixtures,image,padded;gc.collect();print(json.dumps(dict(synthetic_fields_completed=40,max_errors=maxima)),flush=True)
        for ci,(c,row) in enumerate(cases):
            grid=lattice(c)
            for kind in KINDS:
                guard();normal,st=source_image(c,row,kind);cache=physical_mr(normal,grid);del normal;r['MRI_input_arrays_loaded']+=1
                cache_sha=array_sha(cache);assert cache_sha==refs[kind][c['uid']]['input_sha256']
                arm=next(a for a in series[c['uid']]['arms'] if a['kind']==kind)
                base=np.stack([baseline_patch(cache,g,PATCH) for g in arm['geometry']])[:,None];assert array_sha(base)==arm['base_input_sha256']
                for pi,geometry in enumerate(arm['geometry']):
                    primitive=arm['stress_primitives'][pi];ip=arm['intensity_primitives'][pi];domain=independent_domain(grid,geometry,PATCH)
                    for mode in MODES:
                        image,support,meta=apply(cache,grid,geometry,primitive,mode,PATCH)
                        other,other_support,imeta=independent_apply(cache,grid,geometry,primitive,mode,PATCH)
                        assert np.array_equal(image[~domain],base[pi,0][~domain]) and np.array_equal(other[~domain],base[pi,0][~domain])
                        check(image,other,support,other_support,domain,imeta['coordinate_max_error'],ip,
                              dict(scope='real_stress',case=ci,kind=kind,patch=pi,mode=mode))
                if ci==failed['case'] and kind==failed['kind']:
                    geometry=failed['geometry'];domain=independent_domain(grid,geometry,PATCH)
                    for mode in MODES:
                        image,support,meta=apply(cache,grid,geometry,failed['primitive'],mode,PATCH)
                        other,other_support,imeta=independent_apply(cache,grid,geometry,failed['primitive'],mode,PATCH)
                        check(image,other,support,other_support,domain,imeta['coordinate_max_error'],failed['intensity_primitives'],
                              dict(scope='old_failed_regression',case=ci,kind=kind,step=failed['step'],patch=failed['patch'],mode=mode))
                assert array_sha(cache)==cache_sha;del cache,base;gc.collect()
            print(json.dumps(dict(series_completed=ci+1,expected_series=19,fields_completed=len(r['fields']),expected_fields=271,max_errors=maxima)),flush=True)
        assert len(r['fields'])==271 and r['MRI_input_arrays_loaded']==38
        assert sum(v['identity']['scope']=='synthetic' for v in r['fields'])==40
        assert sum(v['identity']['scope']=='real_stress' for v in r['fields'])==228
        assert sum(v['identity']['scope']=='old_failed_regression' for v in r['fields'])==3
        r.update(complete=True,status='completed',all40_synthetic228_real3_failed_regressions_verified=True,
                 all11_patients19_series_two_inputs_three_modes_verified=True,frozen_config_sha256=sha(out/'frozen_config.json'),
                 source_bindings=[entry(p) for p in sorted(sources)])
    except Exception as exc:
        r.update(status='failed',failed_field=current,traceback=traceback.format_exc());r['errors'].append(type(exc).__name__+': '+str(exc));traceback.print_exc()
    save();assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<200_000
    print(json.dumps({k:v for k,v in r.items() if k not in ['fields','source_bindings','case_index','traceback']}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
