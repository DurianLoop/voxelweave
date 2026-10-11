"""Independent enumeration of ended228 steps against all19 original-series selections."""
import collections,gzip,itertools,json,math,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,dump,resource_guard
def main():
    started=time.perf_counter();resource_guard();tp=HERE/'ACTUAL_COVERAGE_TERMINAL_TOOL.json';t=read(tp)
    assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==78758
    rp=HERE/'coverage_attempt01/receipt.json';r=read(rp);cfgpath=rp.with_name('frozen_config.json');cfg=read(cfgpath)
    assert r['complete'] and r['status']=='completed' and not r['errors'] and r['frozen_config_sha256']==sha(cfgpath)
    assert r['GPU_forwards']==r['GPU_backwards']==r['training_updates']==r['in_memory_captures']==228
    assert r['MRI_input_arrays_loaded']==38 and r['GT_arrays_loaded']==19 and r['parent_model_arrays_loaded']==2
    for key in ['formal_six_arm_training_launched','weights_saved','full_fov_inference','medical_effect_scored','validation_pixels_loaded',
                'confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated','other_PIDs_modified','original_training_modified',
                'strict_LOPO_warm_start_allowed','training_ready','publication_claim_confirmed']:assert not r[key],key
    for b in r['source_bindings']:bind(b)
    journal=bind(r['journal']);assert journal.stat().st_size<1_400_000
    selections=cfg['cases'];assert len(selections)==19 and len({s['uid'] for s in selections})==19 and len({s['patient'] for s in selections})==11
    expected=set(itertools.product(range(19),cfg['kinds'],cfg['modes'],[1,2]));seen=set();seen_branches=set();labels={};names=None;maxima=[0.,0.,0.];costs=collections.Counter()
    branch_index={(b['case'],b['kind'],b['mode']):b for b in r['branches']};assert len(branch_index)==len(r['branches'])==114
    oldpath=ROOT/'real_context_and_author_code_followup_2026_10_08/full_schedule_attempt01/receipt.json';old=read(oldpath);original=ROOT/old['journal_path'];assert sha(original)==old['journal_sha256']
    with gzip.open(original,'rt',encoding='utf-8') as f:indexed={(v['step'],v['patch']):v for v in map(json.loads,f)}
    for s in selections:
        available=[n for n in range(1,2993) if indexed[(n,0)]['uid']==s['uid']]
        first=next(n for n in available if all(indexed[(n,p)]['primitive']['enabled'] for p in range(2)))
        second=next(n for n in available if n>first);assert s['scheduled_steps']==[first,second]
    with gzip.open(journal,'rt',encoding='utf-8') as f:
        for line in f:
            v=json.loads(line);key=(v['case'],v['kind'],v['mode'],v['optimizer_step']);assert key in expected and key not in seen;seen.add(key)
            ci,kind,mode,step=key;s=selections[ci];assert v['patient']==s['patient'] and v['uid']==s['uid']
            scheduled=s['scheduled_steps'][step-1];assert v['scheduled_step']==scheduled
            assert v['mother_label_sha256']==indexed[(scheduled,0)]['mother_label_sha256']==indexed[(scheduled,1)]['mother_label_sha256']
            lk=(ci,step)
            if lk in labels:assert labels[lk]==v['mother_label_sha256']
            else:labels[lk]=v['mother_label_sha256']
            ps=v['parameter_checks'];pn=[p['name'] for p in ps];assert len(ps)==len(set(pn))==54
            if names is None:names=pn
            else:assert names==pn
            for i,field in enumerate(['weight_error','m_error','v_error']):
                assert all(p['step']==step and p['elements']>0 and math.isfinite(p[field]) and 0<=p[field]<=3e-6 for p in ps)
                maxima[i]=max(maxima[i],max(p[field] for p in ps))
            assert v['model_and_optimizer_memory_reload_bitwise_equal'] and v['capture_bytes']>0
            assert v['ending_weights_sha256']!=v['starting_parent_weights_sha256'] and len(v['optimizer_state_sha256'])==64
            assert 0<v['peak_reserved_bytes']<=2_500_000_000 and math.isfinite(v['loss'])
            assert all(math.isfinite(n) and n>0 for n in v['module_gradient_max'].values())
            assert len(v['numerics'])==2 and {p['patch'] for p in v['numerics']}=={0,1}
            for p in v['numerics']:
                assert p['bitwise_disagreements']==p['padding_disagreements']==0 and 0<p['valid_voxels']<=1048576
                assert 0<=p['changed_voxels']<=p['valid_voxels']
                if not indexed[(scheduled,p['patch'])]['primitive']['enabled']:assert p['changed_voxels']==0
            for k,c in v['cost_seconds'].items():assert c>=0 and math.isfinite(c);costs[k]+=c
            b=branch_index[(ci,kind,mode)];bs=b['steps'][step-1]
            assert b['complete'] and b['optimizer_reset'] and b['starting_weights_sha256']==v['starting_parent_weights_sha256']
            assert bs['scheduled_step']==scheduled and bs['ending_weights_sha256']==v['ending_weights_sha256'] and bs['optimizer_state_sha256']==v['optimizer_state_sha256']
            assert bs['cost_seconds']==v['cost_seconds']
            if step==2:assert b['steps'][0]['ending_weights_sha256']!=bs['ending_weights_sha256'] and b['steps'][0]['optimizer_state_sha256']!=bs['optimizer_state_sha256'];seen_branches.add((ci,kind,mode))
    assert seen==expected and len(seen_branches)==114 and len(labels)==38
    assert len(r['cache_records'])==38 and {(v['case'],v['kind']) for v in r['cache_records']}==set(itertools.product(range(19),cfg['kinds']))
    assert r['elapsed_seconds']<7200 and r['resources_after']['GPU_free_bytes']>=4_000_000_000 and r['resources_after']['GPU_peak_reserved_bytes']<=2_500_000_000
    result=dict(complete=True,errors=[],all228_unique_updates_and456_patch_fields_verified=True,
        all19_series11_patients_and114_branch_denominators_verified=True,all_original_metadata_only_selections_verified=True,
        all_optimizer_step1_step2_parameter_moment_and_memory_capture_records_verified=True,actual_GPU_updates=228,
        maximum_weight_m_v_errors=maxima,total_measured_step_components_seconds=dict(costs),
        numerical_parameter_arrays_reexecuted_in_this_audit=False,full35904_passed=False,fullFOV_qualified=False,
        clinical_effect_confirmed=False,publication_claim_confirmed=False,training_ready=False,goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__),tp,rp,cfgpath,journal,oldpath,original]],resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    out=HERE/'terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result))
if __name__=='__main__':main()
