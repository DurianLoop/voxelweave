"""Independently enumerate the ended six-branch graph receipt and bound original resources."""
import sys,time,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
started=time.perf_counter();before=resource_guard()
t=read(HERE/'ACTUAL_GPU_SMOKE_V3_TERMINAL_TOOL.json');assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==42442
rp=HERE/'attempt03/receipt.json';r=read(rp);assert r['complete'] and r['status']=='completed' and not r['errors']
assert r['activation_checkpointing'] and r['backward_includes_recomputation'] and r['CUDA_initialized']
assert r['GPU_forwards']==r['GPU_backwards']==6 and r['MRI_input_arrays_loaded']==r['model_arrays_loaded']==2 and r['GT_arrays_loaded']==1
for k in ['training_updates','optimizer_created','weights_saved','full_fov_inference','independent_probability_qualification','medical_effect_scored','validation_pixels_loaded','confirmation_patients_opened','lockedIXI_opened','other_PIDs_enumerated','other_PIDs_modified','original_training_modified','strict_LOPO_warm_start_allowed','training_ready','publication_claim_confirmed']:assert not r[k],k
assert r['selected_step']==2 and r['selected_patient']=='VS-MC-RC-009'
observed=[(b['kind'],b['mode']) for b in r['branches']]
assert len(observed)==len(set(observed))==6 and set(observed)==set(itertools.product(['native_reference','raw_pchip'],['throughplane','inplane','allaxes']))
assert len({b['mother_label_sha256'] for b in r['branches']})==1
required=['resolution_candidate_and_independent_seconds','intensity_and_label_check_seconds','transfer_sync_seconds','forward_sync_seconds','loss_sync_seconds','backward_sync_seconds','finite_gradient_and_state_verification_seconds']
for b in r['branches']:
    assert b['complete'] and b['model_state_unchanged'] and b['starting_weights_sha256']==b['ending_weights_sha256']
    assert set(b['module_gradient_max'])=={'encoder','decoder','ups','heads'} and all(v>0 for v in b['module_gradient_max'].values())
    assert b['outputs_shapes']==[[2,1,64,128,128],[2,1,32,64,64],[2,1,16,32,32]]
    assert 0<b['peak_allocated_bytes']<=b['peak_reserved_bytes']<=2_500_000_000
    assert len(b['numerics'])==2 and {p['patch'] for p in b['numerics']}=={0,1}
    assert all(p['bitwise_disagreements']==p['padding_disagreements']==0 and 0<p['valid_voxels']<=1048576 for p in b['numerics'])
    assert set(b['cost_seconds'])==set(required) and all(v>=0 for v in b['cost_seconds'].values())
    assert sum(b['cost_seconds'].values())<=b['branch_elapsed_seconds']
for k in ['all_six_GPU_branches_finite_nonzero_gradients','all_parent_weights_unchanged','all12_numeric_patch_fields_bitwise_matched','all_mother_GT_geometry_paired']:assert r[k]
assert r['elapsed_seconds']<1800 and sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<1_000_000
assert r['CUDA_VISIBLE_DEVICES_after_CPU_imports']=='-1' and r['CUDA_VISIBLE_DEVICES_at_GPU_admission']=='0'
assert r['aggregate_GPU_observation'][0]['free_MiB']>=8192
for b in r['source_bindings']:bind(b)
qual=read(HERE/'checkpointed_cpu_qualification_attempt01/receipt.json');assert qual['complete'] and qual['all_outputs_loss_and_parameter_gradients_bitwise_equal']
assert all(x['exact_equal'] and x['maximum_error']==0 for x in qual['outputs']+qual['gradients'])
for b in qual['source_bindings']:bind(b)
costs={k:sum(b['cost_seconds'][k] for b in r['branches']) for k in required}
result=dict(complete=True,errors=[],actual_overall_exit=0,all_six_unique_branch_identities_verified=True,all12_numeric_fields_verified=True,
    all_GPU_module_gradients_finite_nonzero_verified=True,all_source_and_parent_state_hashes_verified=True,unchanged_resources_verified=True,
    CPU_synthetic_all_outputs_loss_and_parameter_gradients_exactly_equal=True,total_GPU_cost_seconds=costs,
    checkpointed_only=True,optimizer_memory_qualified=False,full35904_qualification_passed=False,training_ready=False,publication_claim_confirmed=False,goal_status='active',
    sources=[entry(p) for p in [Path(__file__),rp,HERE/'ACTUAL_GPU_SMOKE_V3_TERMINAL_TOOL.json',HERE/'checkpointed_cpu_qualification_attempt01/receipt.json']],
    resources_before=before,resources_after=resource_guard(),elapsed_seconds=time.perf_counter()-started)
out=HERE/'terminal_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result))
