"""Audit the actual completed 271-field repair receipt and fixed identity sets before full replay."""
import sys,time,itertools,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    terminal=HERE/'ACTUAL_REPAIRED_STRESS_TERMINAL_TOOL.json';t=read(terminal)
    assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==47298
    outpath=HERE/'repaired_stress_attempt01/receipt.json';r=read(outpath);configpath=HERE/'repaired_stress_attempt01/frozen_config.json';config=read(configpath)
    assert r['complete'] and r['status']=='completed' and not r['errors'] and len(r['fields'])==config['expected_fields']==271
    assert r['frozen_config_sha256']==sha(configpath) and r['MRI_input_arrays_loaded']==38 and r['GT_arrays_loaded']==0
    assert r['all40_synthetic228_real3_failed_regressions_verified'] and r['all11_patients19_series_two_inputs_three_modes_verified']
    assert len(r['case_index'])==19 and len({c['patient'] for c in r['case_index']})==11
    for b in config['source_bindings']+r['source_bindings']:bind(b)
    def key(v):
        i=v['identity'];scope=i['scope']
        if scope=='synthetic':return (scope,i['fixture'],i['gamma'],i['bias'],i['noise'])
        if scope=='real_stress':return (scope,i['case'],i['kind'],i['patch'],i['mode'])
        assert scope=='old_failed_regression';return (scope,i['case'],i['kind'],i['step'],i['patch'],i['mode'])
    expected={('synthetic',fi,g,b,n) for fi in range(5) for g,b,n in itertools.product([False,True],repeat=3)}
    expected|={('real_stress',ci,kind,pi,mode) for ci in range(19) for kind in ['native_reference','raw_pchip'] for pi in range(2) for mode in ['throughplane','inplane','allaxes']}
    expected|={('old_failed_regression',3,'raw_pchip',1868,0,mode) for mode in ['throughplane','inplane','allaxes']}
    assert len(expected)==271;seen=set();maxima=collections.Counter();regress=[]
    for v in r['fields']:
        k=key(v);assert k in expected and k not in seen;seen.add(k)
        for name in ['pre_intensity_error','shared_post_intensity_error','isolated_intensity_error','full_chain_error','support_error','coordinate_error']:
            val=v[name];assert val>=0 and val<=(3e-12 if name=='coordinate_error' else 3e-6);maxima[name]=max(maxima[name],val)
        assert v['binary_disagreements']==0 and 0<=v['valid_voxels']<=v['target_voxels']
        if k[0]=='old_failed_regression':assert v['isolated_intensity_error']==v['full_chain_error']==0.;regress.append(v)
    assert seen==expected and dict(maxima)==r['max_errors']
    result=dict(complete=True,errors=[],actual_terminal_exit=0,actual_terminal_chunk=t['chunk_id'],
        all271_exact_identity_sets_and_numeric_gates_verified=True,all11_patients19_series_denominators_verified=True,
        all_three_failed_regressions_zero_error=True,old_reference_source_unchanged=True,
        full35904_fields_not_yet_passed=True,training_ready=False,max_errors=dict(maxima),
        max_new_vs_legacy_intensity_delta=r['max_new_vs_legacy_intensity_delta'],
        MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,patient_neural_forwards=0,
        training_updates=0,new_patient_medical_effects=0,confirmation_patients_opened=False,
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'REPAIRED_INTENSITY_QUALIFICATION_PROTOCOL.md',terminal,outpath,configpath]])
    out=HERE/'repaired_terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    print({k:v for k,v in result.items() if k!='source_bindings'},flush=True)
if __name__=='__main__':main()
