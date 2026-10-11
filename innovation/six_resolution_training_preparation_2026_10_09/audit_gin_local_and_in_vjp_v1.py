"""Independent immutable record audit of isolation matrices and failed finite-difference gate."""
import sys,time,math
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,entry,bind,dump,resource_guard
started=time.perf_counter();before=resource_guard()
def near(a,b,tol=2e-15):assert abs(a-b)<=tol,(a,b,tol)
sources=[]
for file,sid,code in (('ACTUAL_GIN_REAL_LOCAL_VJP_TERMINAL_TOOL.json',31564,0),('ACTUAL_GIN_REAL_IN_VJP_TERMINAL_TOOL.json',82611,0),('ACTUAL_GIN_REAL_IN_FINITE_DIFFERENCE_FAILED_TERMINAL_TOOL.json',24948,1)):
    p=HERE/file;v=read(p);assert v['exit_code']==code and 'session_id' not in v and v['observed_unified_exec_session']==sid;sources.append(p)
cp=HERE/'gin_real_local_vjp_attempt01/receipt.json';ip=HERE/'gin_real_in_vjp_attempt01/receipt.json';fp=HERE/'gin_real_in_finite_difference_attempt01/receipt.json'
c=read(cp);n=read(ip);fd=read(fp);sources.extend((cp,ip,fp,Path(__file__)))
for q in (c,n):
    assert q['complete'] and not q['errors'] and q['optimizer_updates']==0
    assert q['CPU_whole_forwards']==q['GPU_whole_forwards']==3 and q['CPU_whole_backwards']==q['GPU_whole_backwards']==1
    assert q['CPU_local_VJPs']==q['GPU_local_VJPs']==12 and len(q['local_matrix'])==8
    assert not q['full19_qualification_passed'] and not q['medical_effect_scored'] and not q['publication_claim_confirmed']
    assert q['MRI_arrays_loaded']==q['GT_arrays_loaded']==1 and q['parent_arrays_loaded']==0
    for b in q['source_bindings']:bind(b)
    assert len(q['global_branches'])==2
    for b in q['global_branches']:assert b['prior_gradient_bitwise_reproduced'] and b['worst_coordinate_gradient']==b['prior_gradient']
    for b in q['local_matrix']:
        assert len(b['per_view'])==3 and {v['view'] for v in b['per_view']}=={0,1,2}
        if q is c:
            import struct
            accumulated=0.
            for v in b['per_view']:accumulated=struct.unpack('<f',struct.pack('<f',accumulated+v['gradient_at_original_coordinate']))[0]
            near(b['coordinate_gradient_sum'],accumulated,0)
            near(b['independent_float64_coordinate_sum'],sum(b['independent_float64_per_view']))
            assert (b['coordinate_gradient_sum']>0)==(b['cotangent_source']=='cpu')
        else:
            near(b['coordinate_gradient_sum'],sum(v['coordinate_gradient'] for v in b['per_view']))
            near(b['independent_float64_coordinate_sum'],sum(v['independent_float64_coordinate'] for v in b['per_view']))
            assert (b['coordinate_gradient_sum']>0)==(b['backend']=='cpu') and b['independent_float64_coordinate_sum']<0
for a,b in zip(c['global_branches'],n['global_branches']):
    assert a['device']==b['device']
    for x,y in zip(a['captures'],b['captures']):
        for k in ('view','shape','input_sha256','output_sha256','cotangent_sha256'):assert x[k]==y[k]
assert len(c['whole_graph_local_reconstruction'])==2 and all(v['whole_weight_max_error']==v['coordinate_error']==0 for v in c['whole_graph_local_reconstruction'])
assert len(n['original_IN_dx_reconstruction'])==6 and all(v['bitwise_equal'] and v['max_error']==0 for v in n['original_IN_dx_reconstruction'])
assert len(n['same_input_upstream_backend_comparisons'])==12
assert not fd['complete'] and fd['errors'] and not fd['all_three_h_negative_and_error_le1e8'] and fd['optimizer_updates']==0 and fd['GPU_whole_forwards']==0
assert fd['CPU_whole_forwards']==3 and fd['CPU_whole_backwards']==1 and fd['finite_difference_h']==[1e-3,1e-4,1e-5]
checks=fd['sum_comparisons'];assert len(checks)==3 and all(v['finite_difference']<0 for v in checks)
assert checks[0]['error']>1e-8 and all(v['error']<=1e-8 for v in checks[1:])
for v in checks:
    near(v['error'],abs(v['finite_difference']-v['analytic']))
    near(v['finite_difference'],sum(next(z['finite_difference'] for z in p['checks'] if z['h']==v['h']) for p in fd['per_view']))
assert checks[0]['error']>checks[1]['error']>checks[2]['error']
for b in fd['source_bindings']:bind(b)
remaining=22_800_000
for p,cap in ((HERE,7_000_000),(ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',20_000_000),(ROOT/'gin_accepted_primary_followup_2026_10_09',6_000_000)):
    size=sum(v.stat().st_size for v in p.rglob('*') if v.is_file());assert size<cap;remaining+=cap-size
after=resource_guard();assert after['workspace_free_bytes']-remaining>=8_000_000_000
r=dict(complete=True,errors=[],source_bindings=[entry(p) for p in sources],
    actual_local_conv_and_IN_terminals_exit0=True,actual_finite_difference_terminal_exit1=True,
    original_global_worst_gradients_and_all_capture_hashes_reproduced=True,
    local_conv_entire_weight_gradient_reconstruction_bitwise_equal=True,local_IN_all6_input_cotangents_bitwise_equal=True,
    all8_conv_and_all8_IN_isolation_combinations_verified=True,
    conv_coordinate_sign_follows_input_cotangent_source=True,IN_coordinate_sign_follows_IN_backend=True,
    all4_float64_IN_coordinate_derivatives_negative=True,
    same_input_IN_backend_max_elementwise_dx_gap=max(v['dx_max_backend_error'] for v in n['same_input_upstream_backend_comparisons']),
    supervised_view0_IN_backend_coordinate_gap_range=[min(v['coordinate_gradient_backend_error'] for v in n['same_input_upstream_backend_comparisons'] if v['view']==0),max(v['coordinate_gradient_backend_error'] for v in n['same_input_upstream_backend_comparisons'] if v['view']==0)],
    finite_difference_all3_h_negative=True,finite_difference_errors=[v['error'] for v in checks],
    finite_difference_fixed_gate_passed=False,largest_h_failed_retained=True,smaller2_h_each_error_le1e8=True,
    independent_numeric_sensitivity_at_one_case_one_coordinate_recorded=True,
    findings_generalized_to_all_parameters_or_patients=False,clinical_harm_or_benefit_inferred=False,
    MRI_arrays_loaded=0,GT_arrays_loaded=0,CUDA_initialized=False,optimizer_updates=0,
    full19_qualification_passed=False,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active',
    resources_before=before,resources_after=after,elapsed_seconds=time.perf_counter()-started)
out=HERE/'gin_local_and_IN_audit_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',r)
print(__import__('json').dumps({k:r[k] for k in ('complete','all8_conv_and_all8_IN_isolation_combinations_verified','IN_coordinate_sign_follows_IN_backend','finite_difference_fixed_gate_passed','finite_difference_errors')}))
