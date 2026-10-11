"""Audit completed 35904-field journal against immutable original geometry and metadata decisions."""
import os
for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='1'
import sys,time,json,gzip,itertools,collections,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
OLD=ROOT/'resolution_degradation_controls_2026_10_08'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    terminalpath=HERE/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json'
    terminal=read(terminalpath)
    assert terminal['exit_code']==0 and 'session_id' not in terminal
    assert terminal['observed_unified_exec_session']==read(HERE/'ACTUAL_FULL_REAL_PIPELINE_SESSION.json')['observed_unified_exec_session']
    live=HERE/'full_real_pipeline_attempt01';receiptpath=live/'receipt.json'
    r=read(receiptpath);configpath=live/'frozen_config.json';config=read(configpath)
    assert r['complete'] and r['status']=='completed' and not r['errors']
    assert r['all35904_full_target_MRI_and_intensity_fields_verified']
    assert r['frozen_config_sha256']==sha(configpath) and r['fields_completed']==35904
    for b in r['source_bindings']:bind(b)
    journal=ROOT/r['journal_path'];assert sha(journal)==r['journal_sha256']
    assert journal.stat().st_size==r['journal_bytes']<config['journal_limit_bytes']
    oldpath=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/receipt.json'
    old=read(oldpath);original=ROOT/old['journal_path'];assert sha(original)==old['journal_sha256']
    with gzip.open(original,'rt',encoding='utf-8') as f:geometries={(v['step'],v['patch']):v for v in map(json.loads,f)}
    metapath=OLD/'geometry_and_synthetic_attempt01/receipt.json';metadata=read(metapath)
    controlpath=bind(metadata['metadata_journal'])
    with gzip.open(controlpath,'rt',encoding='utf-8') as f:
        decisions={(v['step'],v['patch'],v['mode']):v for v in map(json.loads,f)}
    assert len(geometries)==5984 and len(decisions)==17952
    out=HERE/'full_real_terminal_audit_attempt01';out.mkdir(exist_ok=False)
    sources=[Path(__file__),HERE/'FULL_REAL_PIPELINE_PROTOCOL.md',terminalpath,
             receiptpath,configpath,journal,oldpath,original,metapath,controlpath,HERE/'ACTUAL_FULL_REAL_PIPELINE_SESSION.json']
    result=dict(complete=False,errors=[],MRI_arrays_loaded=0,GT_arrays_loaded=0,
                model_arrays_loaded=0,training_updates=0,patient_neural_forwards=0,
                confirmation_patients_opened=False,lockedIXI_opened=False,
                actual_fields_not_reexecuted_in_this_audit=True,training_ready=False,
                publication_claim_confirmed=False,goal_status='active')
    try:
        expected=set(itertools.product(range(1,2993),range(2),range(2),range(3)))
        seen=set();series=collections.defaultdict(collections.Counter)
        patients=collections.defaultdict(collections.Counter);maxima=collections.Counter()
        columns=config['journal_columns'];cases=r['case_index']
        assert columns==r['journal_columns'] and len(cases)==19
        with gzip.open(journal,'rt',encoding='utf-8') as f:
            for line in f:
                values=json.loads(line);assert len(values)==len(columns)
                v=dict(zip(columns,values));step,patch,ci,ki,mi=[v[k] for k in ['step','patch','case','kind','mode']]
                key=(step,patch,ki,mi);assert key in expected and key not in seen;seen.add(key)
                assert 0<=ci<19
                original_row=geometries[(step,patch)];c=cases[ci];mode=config['modes'][mi]
                decision=decisions[(step,patch,mode)]
                assert c['patient']==original_row['patient'] and c['uid']==original_row['uid']
                assert decision['uid']==c['uid'] and decision['patient']==c['patient']
                assert v['enabled']==int(original_row['primitive']['enabled'])==int(decision['enabled'])
                assert v['valid_voxels']==decision['mother_valid_voxels']
                assert v['binary_disagreements']==v['pre_intensity_padding_disagreements']==v['image_bitwise_disagreements']==0
                assert 0<=v['candidate_exact_fallback_voxels']<=v['valid_voxels'] and 0<=v['reference_exact_fallback_voxels']<=v['valid_voxels']
                assert 0<=v['changed_voxels']<=v['valid_voxels']<=1048576
                if not v['enabled']:assert v['changed_voxels']==0
                for name in columns[6:12]:
                    value=v[name];assert isinstance(value,(int,float)) and value>=0
                    assert value<=(3e-12 if name=='coordinate_error' else 3e-6)
                    maxima[name]=max(maxima[name],value)
                for counter in [series[f'{ci}/{ki}/{mi}'],patients[f'{c["patient"]}/{ki}/{mi}']]:
                    counter['fields']+=1;counter['enabled']+=v['enabled']
                    counter['effective_change']+=int(v['enabled'] and v['changed_voxels']>0)
                series[f'{ci}/{ki}/{mi}']['valid_voxels']+=v['valid_voxels']
                series[f'{ci}/{ki}/{mi}']['target_voxels']+=1048576
                if len(seen)%2000==0:
                    resource_guard();assert time.perf_counter()-started<600
        assert seen==expected and len(seen)==35904
        assert len(series)==114 and len(patients)==66
        assert all(v['fields']==544 and v['effective_change']>0 for v in patients.values())
        assert all(v['effective_change']>0 for v in series.values())
        assert {k:dict(v) for k,v in series.items()}==r['series_modes']
        assert {k:dict(v) for k,v in patients.items()}==r['patient_modes']
        assert dict(maxima)==r['max_errors']
        for ki in range(2):
            for mi in range(3):
                group=[v for k,v in series.items() if k.endswith(f'/{ki}/{mi}')]
                assert sum(v['fields'] for v in group)==5984
                assert sum(v['enabled'] for v in group)==1785
                assert sum(v['valid_voxels'] for v in group)==6041370624
        assert r['case_kind_steps_completed']==5984 and r['MRI_input_arrays_loaded']==38 and r['GT_arrays_loaded']==19
        result.update(complete=True,all35904_unique_journal_fields_verified=True,
                      all11_patient_and19_series_denominators_verified=True,
                      all_strict_numeric_gates_verified_from_actual_journal=True,
                      actual_terminal_chunk=terminal['chunk_id'],max_errors=dict(maxima),
                      total_target_exposure_voxels=35904*1048576,
                      total_valid_exposure_voxels=6041370624*6)
    except Exception as exc:
        result['errors'].append(type(exc).__name__+': '+str(exc))
        result['traceback']=traceback.format_exc();traceback.print_exc()
    result.update(elapsed_seconds=time.perf_counter()-started,
                  source_bindings=[entry(p) for p in sources],resources=resource_guard())
    dump(out/'receipt.json',result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_bindings','traceback']}),flush=True)
    return int(not result['complete'])


if __name__=='__main__':raise SystemExit(main())
