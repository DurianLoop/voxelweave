"""Verify a genuine failed terminal, the exact successful prefix, and the next failing identity."""
import collections,gzip,json,sys,time
from pathlib import Path
import numpy as np
from inventory_frozen_text_storage import ROOT,HERE,entry,dump
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,bind,sha,resource_guard

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    failed=ROOT/'full_real_intensity_v2_2026_10_09';terminalpath=failed/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json'
    t=read(terminalpath);assert t['exit_code']==1 and 'session_id' not in t and t['observed_unified_exec_session']==90446 and t['chunk_id']=='fdcb62'
    rp=failed/'full_real_pipeline_attempt01/receipt.json';cp=failed/'full_real_pipeline_attempt01/frozen_config.json'
    r=read(rp);config=read(cp);f=r['failed_field'];assert not r['complete'] and r['status']=='failed' and r['fields_completed']==14673
    assert config['expected_fields']==35904
    for b in config['source_bindings']:bind(b)
    train=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07';sp=train/'frozen_config.json';schedule_config=read(sp)
    schedulepath=train/schedule_config['schedule_file'];assert sha(schedulepath)==schedule_config['schedule_file_sha256']
    schedule=np.load(schedulepath,allow_pickle=False)[:2992]
    geompath=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/receipt.json';geommeta=read(geompath)
    geomjournal=ROOT/geommeta['journal_path'];assert sha(geomjournal)==geommeta['journal_sha256']
    with gzip.open(geomjournal,'rt',encoding='utf-8') as stream:geoms={(v['step'],v['patch']):v for v in map(json.loads,stream)}
    metapath=ROOT/'resolution_degradation_controls_2026_10_08/geometry_and_synthetic_attempt01/receipt.json';meta=read(metapath);decisionpath=bind(meta['metadata_journal'])
    with gzip.open(decisionpath,'rt',encoding='utf-8') as stream:decisions={(v['step'],v['patch'],v['mode']):v for v in map(json.loads,stream)}
    expected=[(int(step),patch,ci,ki,mi) for ci in range(19) for ki in range(2)
              for step in (np.flatnonzero(schedule[:,1]==ci)+1) for patch in range(2) for mi in range(3)]
    assert len(expected)==len(set(expected))==35904 and len(geoms)==5984 and len(decisions)==17952
    journal=ROOT/r['journal_path']
    with gzip.open(journal,'rt',encoding='utf-8') as stream:rows=[json.loads(line) for line in stream]
    assert len(rows)==14673;maxima=collections.Counter();series=collections.defaultdict(collections.Counter);patients=collections.defaultdict(collections.Counter)
    for i,values in enumerate(rows):
        assert len(values)==len(config['journal_columns']);v=dict(zip(config['journal_columns'],values))
        key=tuple(v[k] for k in ['step','patch','case','kind','mode']);assert key==expected[i]
        step,patch,ci,ki,mi=key;case=r['case_index'][ci];g=geoms[(step,patch)];d=decisions[(step,patch,config['modes'][mi])]
        assert case['patient']==g['patient']==d['patient'] and case['uid']==g['uid']==d['uid']
        assert v['enabled']==int(g['primitive']['enabled'])==int(d['enabled']) and v['valid_voxels']==d['mother_valid_voxels']
        assert v['binary_disagreements']==v['pre_intensity_padding_disagreements']==0
        assert 0<=v['changed_voxels']<=v['valid_voxels']<=1048576
        if not v['enabled']:assert v['changed_voxels']==0
        for name in config['journal_columns'][6:12]:
            assert 0<=v[name]<=(3e-12 if name=='coordinate_error' else 3e-6);maxima[name]=max(maxima[name],v[name])
        for counter in [series[f'{ci}/{ki}/{mi}'],patients[f'{case["patient"]}/{ki}/{mi}']]:
            counter['fields']+=1;counter['enabled']+=v['enabled'];counter['effective_change']+=int(v['enabled'] and v['changed_voxels']>0)
        series[f'{ci}/{ki}/{mi}']['valid_voxels']+=v['valid_voxels'];series[f'{ci}/{ki}/{mi}']['target_voxels']+=1048576
    next_key=(f['step'],f['patch'],f['case'],config['kinds'].index(f['kind']),config['modes'].index(f['mode']))
    assert next_key==expected[14673]==(2879,1,8,0,0)
    assert dict(maxima)==r['max_errors'] and {k:dict(v) for k,v in series.items()}==r['series_modes'] and {k:dict(v) for k,v in patients.items()}==r['patient_modes']
    assert f['isolated_intensity_error']==0 and f['shared_post_intensity_error']==f['full_chain_error']==3.814697265625e-6>config['image_gate']==3e-6
    assert f['pre_intensity_error']==1.9073486328125e-6 and f['primitive']['enabled']
    assert len(rows)//6==r['case_kind_steps_completed']==2445 and time.perf_counter()-started<600
    sources=[Path(__file__),HERE/'FAILED_V2_DIAGNOSTIC_PROTOCOL.md',terminalpath,rp,cp,journal,sp,schedulepath,geompath,geomjournal,metapath,decisionpath]
    result=dict(complete=True,errors=[],actual_exit=1,actual_terminal_chunk='fdcb62',qualification_passed=False,
        all14673_unique_journal_rows_exact_prefix_verified=True,next_failed_key=list(next_key),success_maxima_exclude_failed_field=True,
        successful_fields=14673,expected_fields=35904,failed_field=f,success_maxima=dict(maxima),MRI_arrays_loaded=0,GT_arrays_loaded=0,
        model_arrays_loaded=0,training_updates=0,publication_claim_confirmed=False,goal_status='active',
        sources=[entry(p) for p in sources],resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    out=HERE/'failed_v2_terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['sources','failed_field']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
