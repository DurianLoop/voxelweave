"""Reproduce one failed full field and isolate gamma arithmetic; source snapshots stay immutable."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,math
from pathlib import Path
import numpy as np
import torch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OLD=ROOT/'resolution_degradation_controls_2026_10_08'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,QPATH
sys.path.insert(0,str(ROOT/'adaptation_paired_pilot_2026_10_08'))
import augmentation as legacy
sys.path.insert(0,str(OLD))
from resolution_control import apply,baseline_patch
from independent_resolution import independent_apply
from independent_intensity import apply_reference
def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter();resources=resource_guard();assert resources['workspace_free_bytes']-3_200_000>=8_000_000_000
    receipt=OLD/'full_real_pipeline_attempt01/receipt.json';frozen=OLD/'full_real_pipeline_attempt01/frozen_config.json'
    terminal=OLD/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json';journal=OLD/'full_real_pipeline_attempt01/fields.jsonl.gz'
    assert sha(receipt)=='510724eb7b0b554bf0d0e426a74275afb918808a3d617ce2ed11b27804b1fdb5'
    assert sha(frozen)=='12077e91e16a271b686376138264d413d4fbbb1717d427f9267847de856c9c69'
    assert sha(journal)=='78a97242b31a7bf12fe22d427e80c8a96a0f6d86bf874af52f82e87302da48a6'
    r=read(receipt);f=r['failed_field'];config=read(frozen);t=read(terminal)
    assert t['exit_code']==1 and 'session_id' not in t and t['observed_unified_exec_session']==74234
    assert r['status']=='failed' and not r['complete'] and r['fields_completed']==6216
    assert (f['case'],f['kind'],f['step'],f['patch'],f['mode'])==(3,'raw_pchip',1868,0,'throughplane')
    assert not f['primitive']['enabled']
    sources={Path(__file__),HERE/'PROTOCOL.md',receipt,frozen,terminal,journal,Path(legacy.__file__),OLD/'independent_intensity.py',
             OLD/'resolution_control.py',OLD/'independent_resolution.py',QPATH,
             ROOT/'experiments/mc_rc_3d_19series_common_init_2026_10_07.py',ROOT/'experiments/mc_rc_3d_baseline_2026_10_07.py'}
    for p in list(sources):
        if p in [Path(__file__),HERE/'PROTOCOL.md',receipt,frozen,terminal,journal]:continue
        bind(next(b for b in config['source_bindings'] if b['path']==p.relative_to(ROOT).as_posix()))
    cases=development_cases();c,row=cases[f['case']]
    assert {k:c[k] for k in ['patient','uid']}==r['case_index'][3]
    for path in [c['header_file'],c['mr_zip_file'],row['observed_package']]:
        sources.add(bind(next(b for b in config['source_bindings'] if b['path']==path)))
    grid=lattice(c);norm,stats=source_image(c,row,'raw_pchip');cache=physical_mr(norm,grid);del norm
    qualification=read(QPATH);ref=next(v for arm in qualification['arms'] if arm['kind']=='raw_pchip' for v in arm['cache_records'] if v['uid']==c['uid'])
    cache_sha=array_sha(cache);assert cache_sha==ref['input_sha256']
    image,support,meta=apply(cache,grid,f['geometry'],f['primitive'],f['mode'])
    other,other_support,imeta=independent_apply(cache,grid,f['geometry'],f['primitive'],f['mode'])
    assert np.array_equal(image,other) and np.array_equal(support,other_support) and np.array_equal(image,baseline_patch(cache,f['geometry'],(64,128,128)))
    primitive=f['intensity_primitives'];assert primitive==legacy.primitives(f['step'])[f['patch']]
    assert primitive['gamma_enabled'] and primitive['bias_enabled'] and not primitive['noise_enabled']
    actual=legacy.apply(image[None,None],[primitive])[0,0];reference=apply_reference(image,primitive)
    old_error=float(np.max(np.abs(actual-reference)));assert old_error==f['isolated_intensity_error']==3.814697265625e-6
    p=dict(primitive,bias_enabled=False,noise_enabled=False)
    gamma_actual=legacy.apply(image[None,None],[p])[0,0];gamma_reference=apply_reference(image,p)
    lo,hi=float(image.min()),float(image.max());mu32=float(image.mean());sd32=float(image.std())
    mu64=float(image.mean(dtype=np.float64));sd64=float(image.std(dtype=np.float64))
    powered=((image-lo)/(hi-lo))**p['gamma']
    pm32=float(powered.mean());ps32=float(powered.std());pm64=float(powered.mean(dtype=np.float64));ps64=float(powered.std(dtype=np.float64))
    variants={}
    for mean_precision,sd_precision,restore_precision in [('32','32','32'),('64','32','32'),('32','64','32'),('64','64','32'),('64','64','64')]:
        a_mean=mu32 if mean_precision=='32' else mu64;b_mean=pm32 if mean_precision=='32' else pm64
        a_sd=sd32 if sd_precision=='32' else sd64;b_sd=ps32 if sd_precision=='32' else ps64
        tmp=(powered if restore_precision=='32' else powered.astype(np.float64))
        v=((tmp-b_mean)*(a_sd/b_sd)+a_mean).astype(np.float32)
        pbias=dict(primitive,gamma_enabled=False,noise_enabled=False)
        vbias=legacy.apply(v[None,None],[pbias])[0,0]
        variants[f'mean{mean_precision}_sd{sd_precision}_restore{restore_precision}']=dict(
            gamma_error_to_legacy=float(np.max(np.abs(v-gamma_actual))),
            gamma_error_to_old_reference=float(np.max(np.abs(v-gamma_reference))),
            final_error_to_legacy=float(np.max(np.abs(vbias-actual))),
            final_error_to_old_reference=float(np.max(np.abs(vbias-reference))))
    a64=image.astype(np.float64);b64=np.power((a64-lo)/(hi-lo),p['gamma'])
    candidate=((b64-b64.mean())*(a64.std()/b64.std())+a64.mean()).astype(np.float32)
    candidate_bias=legacy.apply(candidate[None,None],[dict(primitive,gamma_enabled=False,noise_enabled=False)])[0,0]
    diff=np.abs(actual-reference);indices=np.argpartition(diff.ravel(),-6)[-6:];witnesses=[]
    for flat in sorted(indices.tolist()):
        index=np.unravel_index(flat,image.shape);av=float(actual[index]);rv=float(reference[index])
        ulp=float(abs(np.spacing(np.float32(av))))
        witnesses.append(dict(index_zrc=list(map(int,index)),source=float(image[index]),legacy_gamma=float(gamma_actual[index]),reference_gamma=float(gamma_reference[index]),
            legacy_final=av,reference_final=rv,absolute_error=abs(av-rv),local_float32_ulp=ulp,error_in_ulps=abs(av-rv)/ulp if ulp else None))
    assert array_sha(cache)==cache_sha and time.perf_counter()-started<180 and not torch.cuda.is_initialized()
    result=dict(complete=True,errors=[],actual_old_failure_reproduced=True,old_isolated_error=old_error,
        original_success_fields=6216,original_expected_fields=35904,failed_field_identity={k:f[k] for k in ['case','kind','step','patch','mode']},
        resolution_enabled=False,resolution_and_shared_intensity_disagreement=0,
        gamma_stage_error=float(np.max(np.abs(gamma_actual-gamma_reference))),
        post_bias_stage_error=old_error,gamma_stats=dict(input_mean32=mu32,input_mean64=mu64,input_sd32=sd32,input_sd64=sd64,
            power_mean32=pm32,power_mean64=pm64,power_sd32=ps32,power_sd64=ps64,input_min=lo,input_max=hi),
        arithmetic_variants=variants,all_float64_candidate=dict(final_error_to_legacy=float(np.max(np.abs(candidate_bias-actual))),
            final_error_to_old_reference=float(np.max(np.abs(candidate_bias-reference)))),
        failed_maximum_witnesses=witnesses,new_production_module_not_yet_qualified=True,
        old_failure_preserved_gate_not_relaxed=True,MRI_input_arrays_loaded=1,GT_arrays_loaded=0,model_arrays_loaded=0,
        patient_neural_forwards=0,training_updates=0,new_patient_medical_effects=0,confirmation_patients_opened=False,
        validation_pixels_loaded=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in sorted(sources)])
    out=HERE/'failed_field_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    assert sum(p.stat().st_size for p in out.rglob('*'))<100_000
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','failed_maximum_witnesses']}),flush=True)
if __name__=='__main__':main()
