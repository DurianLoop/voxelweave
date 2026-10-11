"""Audit a real failed terminal and its exact successful prefix without replaying pixels."""
import sys,time,json,gzip,itertools,collections
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OLD=ROOT/'resolution_degradation_controls_2026_10_08'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    terminal=OLD/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json';t=read(terminal)
    assert t['exit_code']==1 and 'session_id' not in t and t['observed_unified_exec_session']==74234
    receipt=OLD/'full_real_pipeline_attempt01/receipt.json';r=read(receipt);f=r['failed_field']
    frozen=OLD/'full_real_pipeline_attempt01/frozen_config.json';config=read(frozen);journal=ROOT/r['journal_path']
    assert sha(receipt)=='510724eb7b0b554bf0d0e426a74275afb918808a3d617ce2ed11b27804b1fdb5'
    assert sha(frozen)=='12077e91e16a271b686376138264d413d4fbbb1717d427f9267847de856c9c69'
    assert sha(journal)=='78a97242b31a7bf12fe22d427e80c8a96a0f6d86bf874af52f82e87302da48a6'
    assert not r['complete'] and r['status']=='failed' and r['fields_completed']==6216 and config['expected_fields']==35904
    for b in config['source_bindings']:bind(b)
    previous=ROOT/'real_context_and_author_code_followup_2026_10_08';parentpath=previous/'full_schedule_attempt01/receipt.json';parent=read(parentpath)
    original=ROOT/parent['journal_path'];assert sha(original)==parent['journal_sha256']
    with gzip.open(original,'rt',encoding='utf-8') as stream:geometry={(v['step'],v['patch']):v for v in map(json.loads,stream)}
    metapath=OLD/'geometry_and_synthetic_attempt01/receipt.json';metadata=read(metapath);controlpath=bind(metadata['metadata_journal'])
    with gzip.open(controlpath,'rt',encoding='utf-8') as stream:decisions={(v['step'],v['patch'],v['mode']):v for v in map(json.loads,stream)}
    train=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07';schedule_config=train/'frozen_config.json';schedule_meta=read(schedule_config)
    schedule_path=train/schedule_meta['schedule_file'];assert sha(schedule_path)==schedule_meta['schedule_file_sha256']
    schedule=np.load(schedule_path,allow_pickle=False)[:2992];cases=r['case_index'];assert len(cases)==19 and len(geometry)==5984 and len(decisions)==17952
    expected=[(int(step),patch,ci,ki,mi) for ci in range(19) for ki in range(2)
        for step in (np.flatnonzero(schedule[:,1]==ci)+1) for patch in range(2) for mi in range(3)]
    assert len(expected)==len(set(expected))==35904
    with gzip.open(journal,'rt',encoding='utf-8') as stream:rows=[json.loads(line) for line in stream]
    assert len(rows)==r['fields_completed']==6216
    columns=config['journal_columns'];maxima=collections.Counter();series=collections.defaultdict(collections.Counter);patients=collections.defaultdict(collections.Counter)
    for i,values in enumerate(rows):
        assert len(values)==len(columns);v=dict(zip(columns,values));step,patch,ci,ki,mi=[v[k] for k in ['step','patch','case','kind','mode']]
        assert (step,patch,ci,ki,mi)==expected[i]
        original_row=geometry[(step,patch)];case=cases[ci];mode=config['modes'][mi];decision=decisions[(step,patch,mode)]
        assert case['patient']==original_row['patient']==decision['patient'] and case['uid']==original_row['uid']==decision['uid']
        assert v['enabled']==int(original_row['primitive']['enabled'])==int(decision['enabled']) and v['valid_voxels']==decision['mother_valid_voxels']
        assert v['binary_disagreements']==v['pre_intensity_padding_disagreements']==0
        assert 0<=v['changed_voxels']<=v['valid_voxels']<=1048576
        if not v['enabled']:assert v['changed_voxels']==0
        for name in columns[6:12]:
            val=v[name];assert val>=0 and val<=(3e-12 if name=='coordinate_error' else 3e-6);maxima[name]=max(maxima[name],val)
        for counter in [series[f'{ci}/{ki}/{mi}'],patients[f'{case["patient"]}/{ki}/{mi}']]:
            counter['fields']+=1;counter['enabled']+=v['enabled'];counter['effective_change']+=int(v['enabled'] and v['changed_voxels']>0)
        series[f'{ci}/{ki}/{mi}']['valid_voxels']+=v['valid_voxels'];series[f'{ci}/{ki}/{mi}']['target_voxels']+=1048576
    next_key=(f['step'],f['patch'],f['case'],config['kinds'].index(f['kind']),config['modes'].index(f['mode']))
    assert next_key==expected[6216] and dict(maxima)==r['max_errors']
    assert {k:dict(v) for k,v in series.items()}==r['series_modes'] and {k:dict(v) for k,v in patients.items()}==r['patient_modes']
    assert f['isolated_intensity_error']==f['full_chain_error']==3.814697265625e-6>config['image_gate']==3e-6
    assert f['pre_intensity_error']==f['shared_post_intensity_error']==0. and not f['primitive']['enabled']
    assert r['case_kind_steps_completed']*6==6216 and time.perf_counter()-started<600
    sources=[Path(__file__),HERE/'FAILED_TERMINAL_AUDIT_PROTOCOL.md',terminal,receipt,frozen,journal,parentpath,original,metapath,controlpath,schedule_config,schedule_path]
    result=dict(complete=True,errors=[],original_full_qualification_passed=False,original_actual_terminal_exit=1,actual_terminal_chunk=t['chunk_id'],
        all6216_journal_rows_verified_as_exact_prefix=True,all_success_numeric_gates_verified=True,
        next_field_matches_actual_failure=True,success_maxima_do_not_include_failed_field=True,
        successful_fields=6216,expected_fields=35904,uncompleted_fields_including_failed_field=35904-6216,
        failed_field=next_key,failed_isolated_error=f['isolated_intensity_error'],old_failure_preserved=True,
        success_max_errors=dict(maxima),MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
        patient_neural_forwards=0,training_updates=0,new_patient_medical_effects=0,
        confirmation_patients_opened=False,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,source_bindings=[entry(p) for p in sources])
    out=HERE/'failed_terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    assert sum(p.stat().st_size for p in out.rglob('*'))<30_000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings']}),flush=True)
if __name__=='__main__':main()
