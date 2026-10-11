"""Independently enumerate every expected field after actual overall exit0, no image/model reads."""
import sys,itertools,json,time,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();before=resource_guard()
    terminal=read(HERE/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json')
    assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==43633
    path=HERE/'all_patient_stress_attempt01/receipt.json';r=read(path);assert r['complete'] and r['status']=='completed' and not r['errors']
    assert r['all542_full_fields_verified'] and r['all11_patients19_series_two_inputs_three_modes_verified']
    assert len(r['fields'])==542 and r['MRI_input_arrays_loaded']==38 and r['GT_arrays_loaded']==r['model_arrays_loaded']==r['neural_forwards']==r['training_updates']==0
    assert len(r['case_index'])==19 and len({x['patient'] for x in r['case_index']})==11 and len(r['cache_records'])==38
    for key in ['validation_pixels_loaded','confirmation_patients_opened','lockedIXI_opened','new_production_selected','training_ready','publication_claim_confirmed','full35904_qualification_passed']:assert not r[key]
    expected=set();modes=['throughplane','inplane','allaxes'];kinds=['native_reference','raw_pchip']
    for f,g,b,n in itertools.product(range(5),[False,True],[False,True],[False,True]):
        expected.add(json.dumps(dict(scope='intensity_synthetic',fixture=f,gamma=g,bias=b,noise=n),sort_keys=True))
    for f,t,g,e,m in itertools.product(range(5),['constant','linear','texture'],range(3),[False,True],modes):
        expected.add(json.dumps(dict(scope='resolution_synthetic',fixture=f,texture=t,geometry=g,enabled=e,mode=m),sort_keys=True))
    for c,k,p,m in itertools.product(range(19),kinds,range(2),modes):
        expected.add(json.dumps(dict(scope='real_stress',case=c,kind=k,patch=p,mode=m),sort_keys=True))
    failures=[read(ROOT/'resolution_degradation_controls_2026_10_08/full_real_pipeline_attempt01/receipt.json')['failed_field'],
        read(ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01/receipt.json')['failed_field']]
    for i,f in enumerate(failures):
        for m in (modes if i==0 else [f['mode']]):
            expected.add(json.dumps(dict(scope='old_failed_regression' if i==0 else 'v2_failed_regression',case=f['case'],kind=f['kind'],step=f['step'],patch=f['patch'],mode=m),sort_keys=True))
    observed=[json.dumps(f['identity'],sort_keys=True) for f in r['fields']];assert len(set(observed))==542 and set(observed)==expected
    maxima=collections.Counter();probes=candidate_fallback=direct_fallback=target_voxels=0
    for f in r['fields']:
        assert f['image_bitwise_disagreements']==f['binary_disagreements']==0
        for k in ['pre_intensity_error','shared_post_intensity_error','isolated_intensity_error','full_chain_error','support_error']:
            assert 0<=f[k]<=3e-6;maxima[k]=max(maxima[k],f[k])
        if 'coordinate_error' in f:
            assert 0<=f['coordinate_error']<=3e-12;maxima['coordinate_error']=max(maxima['coordinate_error'],f['coordinate_error'])
            assert 0<=f['exact_probes']<=64
            probes+=f['exact_probes'];candidate_fallback+=f['candidate_fallback'];direct_fallback+=f['direct_fallback']
        if f['identity']['scope'] in ['real_stress','old_failed_regression','v2_failed_regression']:assert f['target_voxels']==1048576
        target_voxels+=f['target_voxels']
    assert dict(maxima)==r['max_errors'] and probes==r['exact_probe_points'] and r['direct_extreme_exact_points']==9
    for b in r['source_bindings']:bind(b)
    out=HERE/'all_patient_terminal_audit_attempt01';out.mkdir(exist_ok=False)
    result=dict(complete=True,errors=[],actual_overall_exit=0,all542_unique_field_identities_verified=True,
        all11_patients19series_two_inputs_three_modes_verified=True,unchanged_numeric_gates_verified=True,
        total_target_voxels_compared=target_voxels,total_extra_Fraction_probe_points=probes,candidate_fallback_voxels=candidate_fallback,direct_fallback_voxels=direct_fallback,
        source_bindings=[entry(p) for p in [Path(__file__),path,HERE/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json']],
        full35904_qualification_passed=False,training_ready=False,publication_claim_confirmed=False,goal_status='active',
        resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(out/'receipt.json',result);print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
