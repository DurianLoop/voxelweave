"""Replay one developer-native input and separate resolution error from gamma propagation."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import json,sys,time
from pathlib import Path
import numpy as np
import torch
from inventory_frozen_text_storage import ROOT,HERE,entry,dump,guard
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,bind
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_3d_19series_common_init_2026_10_07 import development_cases,lattice,source_image,physical_mr,array_sha,QPATH
sys.path.insert(0,str(ROOT/'resolution_degradation_controls_2026_10_08'))
from resolution_control import apply
from independent_resolution import independent_apply
from independent_intensity import apply_reference
sys.path.insert(0,str(ROOT/'intensity_precision_failure_diagnosis_2026_10_09'))
import intensity_float64_stats as intensity

def gamma64(image,p):
    a=image.astype(np.float64);lo=float(a.min());hi=float(a.max());mu=float(a.mean());sd=float(a.std())
    if hi>lo and sd>0:
        b=np.power((a-lo)/(hi-lo),p['gamma']);bsd=float(b.std())
        if bsd>0:return ((b-b.mean())*(sd/bsd)+mu).astype(np.float32)
    return image.copy()

def main():
    sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(1);assert torch.get_num_interop_threads()==1
    started=time.perf_counter();before=guard(started)
    auditpath=HERE/'failed_v2_terminal_audit_attempt01/receipt.json';audit=read(auditpath)
    assert audit['complete'] and audit['actual_exit']==1 and audit['all14673_unique_journal_rows_exact_prefix_verified']
    for b in audit['sources']:bind(b)
    failed=ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01';rp=failed/'receipt.json';cp=failed/'frozen_config.json'
    r=read(rp);config=read(cp);f=r['failed_field'];assert (f['case'],f['kind'],f['step'],f['patch'],f['mode'])==(8,'native_reference',2879,1,'throughplane')
    sources={Path(__file__),HERE/'FAILED_V2_DIAGNOSTIC_PROTOCOL.md',auditpath,rp,cp,QPATH,
             ROOT/'resolution_degradation_controls_2026_10_08/resolution_control.py',
             ROOT/'resolution_degradation_controls_2026_10_08/independent_resolution.py',
             ROOT/'resolution_degradation_controls_2026_10_08/independent_intensity.py',Path(intensity.__file__)}
    cases=development_cases();c,row=cases[8];assert {k:c[k] for k in ['patient','uid']}==r['case_index'][8]
    for path in [c['header_file'],c['mr_zip_file']]:sources.add(bind(next(b for b in config['source_bindings'] if b['path']==path)))
    grid=lattice(c);normalized,stats=source_image(c,row,'native_reference');cache=physical_mr(normalized,grid);del normalized
    q=read(QPATH);ref=next(v for a in q['arms'] if a['kind']=='native_reference' for v in a['cache_records'] if v['uid']==c['uid'])
    cache_sha=array_sha(cache);assert cache_sha==ref['input_sha256']
    image,support,meta=apply(cache,grid,f['geometry'],f['primitive'],f['mode'])
    other,other_support,imeta=independent_apply(cache,grid,f['geometry'],f['primitive'],f['mode'])
    p=f['intensity_primitives'];assert p==intensity.primitives(f['step'])[f['patch']] and p['gamma_enabled'] and not p['bias_enabled'] and not p['noise_enabled']
    actual=intensity.apply(image[None,None],[p])[0,0];shared=intensity.apply(other[None,None],[p])[0,0]
    isolated=apply_reference(image,p);reference=apply_reference(other,p)
    errors=dict(pre=float(np.max(np.abs(image-other))),shared=float(np.max(np.abs(actual-shared))),
        isolated=float(np.max(np.abs(actual-isolated))),full=float(np.max(np.abs(actual-reference))))
    assert errors==dict(pre=f['pre_intensity_error'],shared=f['shared_post_intensity_error'],isolated=f['isolated_intensity_error'],full=f['full_chain_error'])
    gamma_image=gamma64(image,p);gamma_other=gamma64(other,p)
    diff=np.abs(actual-shared);flat=int(np.argmax(diff));index=np.unravel_index(flat,image.shape)
    witness=dict(index_zrc=list(map(int,index)),pre_production=float(image[index]),pre_independent=float(other[index]),
        post_production=float(actual[index]),post_shared=float(shared[index]),pre_error=float(abs(image[index]-other[index])),
        post_error=float(diff[index]),post_float32_ULP=float(abs(np.spacing(actual[index]))))
    stats_records=[]
    for name,a in [('production_resolution',image),('independent_resolution',other)]:
        lo,hi=float(a.min()),float(a.max());b=((a-lo)/(hi-lo))**p['gamma']
        stats_records.append(dict(name=name,min=lo,max=hi,mean64=float(a.mean(dtype=np.float64)),sd64=float(a.std(dtype=np.float64)),
                                  powered_mean64=float(b.mean(dtype=np.float64)),powered_sd64=float(b.std(dtype=np.float64))))
    assert np.array_equal(support,other_support) and array_sha(cache)==cache_sha and not torch.cuda.is_initialized()
    assert time.perf_counter()-started<180
    result=dict(complete=True,errors=[],failed_v2_field_reproduced=True,case_identity=r['case_index'][8],failed_field=f,
        observed_errors=errors,same_input_intensity_implementations_agree=True,
        discrepancy_origin='different resolution float32 outputs amplified by same gamma; not isolated gamma implementation disagreement',
        all_float64_gamma_diagnostic=dict(shared_post_error=float(np.max(np.abs(gamma_image-gamma_other))),
            production_change_to_v2=float(np.max(np.abs(gamma_image-actual))),reference_change_to_v2=float(np.max(np.abs(gamma_other-shared))),
            qualifies_complete_pipeline=False),gamma_stats=stats_records,failed_maximum_witness=witness,
        numerical_gate_unchanged=True,old_oracle_or_production_files_modified=False,new_production_selected=False,
        MRI_input_arrays_loaded=1,GT_arrays_loaded=0,model_arrays_loaded=0,neural_forwards=0,training_updates=0,
        confirmation_patients_opened=False,validation_arrays_loaded=0,lockedIXI_opened=False,publication_claim_confirmed=False,
        source_bindings=[entry(p) for p in sorted(sources)],resources_before=before,resources_after=guard(started),
        elapsed_seconds=time.perf_counter()-started,goal_status='active')
    out=HERE/'failed_v2_field_diagnostic_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','failed_field']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
