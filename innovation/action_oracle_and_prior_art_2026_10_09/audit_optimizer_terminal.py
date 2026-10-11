"""Audit the real ended first-update receipt, identities, tensors, costs and source hashes."""
import itertools,json,sys,time,math
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
started=time.perf_counter();res=resource_guard()
tp=HERE/'ACTUAL_OPTIMIZER_TERMINAL_TOOL.json';t=read(tp)
assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==61338
rp=HERE/'optimizer_smoke_attempt01/receipt.json';r=read(rp)
assert r['complete'] and r['status']=='completed' and not r['errors']
assert r['GPU_forwards']==r['GPU_backwards']==r['training_updates']==r['in_memory_captures']==6
assert r['MRI_input_arrays_loaded']==r['model_arrays_loaded']==2 and r['GT_arrays_loaded']==1
assert r['optimizer_created'] and r['activation_checkpointing'] and r['CUDA_initialized']
assert r['selected_step']==2 and r['selected_patient']=='VS-MC-RC-009'
for key in ['weights_saved','full_fov_inference','independent_probability_qualification','medical_effect_scored',
            'validation_pixels_loaded','confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated',
            'other_PIDs_modified','original_training_modified','strict_LOPO_warm_start_allowed','training_ready','publication_claim_confirmed']:
    assert not r[key],key
identities=[(b['kind'],b['mode']) for b in r['branches']]
assert len(identities)==len(set(identities))==6
assert set(identities)==set(itertools.product(['native_reference','raw_pchip'],['throughplane','inplane','allaxes']))
assert len({b['mother_label_sha256'] for b in r['branches']})==1
names=None;costs={};maxima=[0.,0.,0.]
for b in r['branches']:
    assert b['complete'] and b['optimizer_reset'] and not b['model_state_unchanged']
    assert b['starting_weights_sha256']!=b['ending_weights_sha256']
    assert 0<b['peak_allocated_bytes']<=b['peak_reserved_bytes']<=2_500_000_000
    assert b['outputs_shapes']==[[2,1,64,128,128],[2,1,32,64,64],[2,1,16,32,32]]
    assert all(math.isfinite(v) and v>0 for v in b['module_gradient_max'].values())
    check=b['optimizer_check'];ps=check['parameters'];current=[p['name'] for p in ps]
    assert check['parameter_tensors']==len(ps)==len(set(current)) and len(ps)>0
    if names is None:names=current
    else:assert current==names
    assert check['all_first_step_counters_one'] and check['absolute_gate']==3e-6
    assert check['capture_state_hash']==b['ending_weights_sha256'] and check['capture_bytes']>0
    for i,(field,summary) in enumerate([('weight_error','maximum_weight_error'),('first_moment_error','maximum_first_moment_error'),('second_moment_error','maximum_second_moment_error')]):
        assert all(p['elements']>0 and p['step']==1 and math.isfinite(p[field]) and 0<=p[field]<=3e-6 for p in ps)
        assert max(p[field] for p in ps)==check[summary];maxima[i]=max(maxima[i],check[summary])
    assert len(b['numerics'])==2 and {p['patch'] for p in b['numerics']}=={0,1}
    assert all(p['bitwise_disagreements']==p['padding_disagreements']==0 for p in b['numerics'])
    assert all(v>=0 and math.isfinite(v) for v in b['cost_seconds'].values())
    assert sum(b['cost_seconds'].values())<=b['branch_elapsed_seconds']
    for k,v in b['cost_seconds'].items():costs[k]=costs.get(k,0.)+v
for b in r['source_bindings']:bind(b)
assert r['elapsed_seconds']<1800 and r['aggregate_GPU_observation'][0]['free_MiB']>=8192
assert r['resources_after']['GPU_free_bytes']>=4_000_000_000
assert r['resources_after']['GPU_peak_reserved_bytes']<=2_500_000_000
assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000
result=dict(complete=True,errors=[],actual_overall_exit=0,all_six_first_update_identities_verified=True,
    all_first_step_parameter_and_moment_checks_verified=True,all_six_memory_captures_verified=True,
    actual_GPU_updates=6,parameter_tensors_per_branch=len(names),maximum_weight_m_v_errors=maxima,
    maximum_reserved_bytes=max(b['peak_reserved_bytes'] for b in r['branches']),total_cost_seconds=costs,
    scope='fixed_one_development_patient_first_step_only',independent_parameter_arrays_reexecuted_in_audit=False,
    disk_atomic_capture_qualified=False,full_fov_inference_qualified=False,complete_training_ready=False,
    publication_claim_confirmed=False,goal_status='active',sources=[entry(p) for p in [Path(__file__),tp,rp]],
    resources_before=res,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started)
out=HERE/'optimizer_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result)
print(json.dumps(result))
