"""Independent completed-record audit, full parameter payload checks and AdamW sign arithmetic."""
import sys,json,gzip,base64,hashlib,math,time,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,bind,entry,resource_guard

def verify_parameter(v):
    assert v['dtype']=='little_endian_float32'
    data=base64.b64decode(v['payload_base64'],validate=True);assert len(data)==math.prod(v['shape'])*4
    h=hashlib.sha256(json.dumps(dict(shape=v['shape'],dtype='<f4'),sort_keys=True).encode());h.update(data)
    assert h.hexdigest()==v['sha256'];return len(data)

def main():
    started=time.perf_counter();resource_guard();out=HERE/'gin_real_failure_audit_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],CUDA_initialized=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,training_updates=0,
           full19_qualification_passed=False,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active')
    try:
        terminalp=HERE/'ACTUAL_GIN19_REAL_GRAPH_V2_FAILED_TERMINAL_TOOL.json';terminal=read(terminalp)
        assert terminal['exit_code']==1 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==42978
        actual=json.loads(terminal['output'].strip().splitlines()[-1]);old=HERE/'gin19_real_graph_attempt02'
        failed=read(old/'receipt.json');cfg=read(old/'frozen_config.json')
        assert not failed['complete'] and failed['status']=='failed' and not actual['complete'] and actual['status']=='failed'
        assert actual['elapsed_seconds']==failed['elapsed_seconds']
        assert failed['GPU_optimizer_updates']==failed['CPU_reference_optimizer_updates']==2
        assert failed['GPU_whole_model_forwards']==failed['CPU_reference_whole_model_forwards']==6
        assert failed['MRI_arrays_loaded']==failed['GT_arrays_loaded']==1 and failed['parent_arrays_loaded']==0
        assert not failed['complete19series_GPU_three_view_qualified'] and not failed['formal_training_launched']
        assert cfg['expected_series']==len(cfg['cases'])==19 and cfg['expected_patients']==len({v['patient'] for v in cfg['cases']})==11
        assert cfg['expected_GPU_updates']==cfg['expected_CPU_reference_updates']==76
        assert cfg['expected_GPU_whole_model_forwards']==cfg['expected_CPU_reference_whole_model_forwards']==228
        for b in failed['source_bindings']:bind(b)
        journal=bind(failed['partial_journal'])
        with gzip.open(journal,'rt',encoding='utf-8') as f:records=[json.loads(v) for v in f]
        prep=[v for v in records if v['type']=='prepared_three_views'];steps=[v for v in records if v['type']=='actual_two_step_optimizer']
        comparisons=[v for v in records if v['type']=='CPU_GPU_strict_comparison']
        assert len(records)==7 and len(prep)==2 and len(steps)==4 and len(comparisons)==1
        assert {(v['device'],v['step']) for v in steps}=={(d,s) for d in ('cpu','cuda:0') for s in (0,1)}
        assert all(v['case']==0 and v['kind']=='native_reference' for v in records)
        payload_bytes=0;parameter_tensors=0
        for index,v in enumerate(prep):
            assert v['step_index']==index and len(v['view_sha256'])==len(v['parameters'])==len(v['norms'])==3
            assert v['GT_not_used_to_generate_GIN'] and v['coordinates_and_target_unchanged']
            for param in v['parameters']:
                payload_bytes+=verify_parameter(param['alpha']);parameter_tensors+=1
                assert len(param['layers'])==4
                for layer in param['layers']:
                    assert layer['k'] in (1,3)
                    for name in ('weight','bias'):payload_bytes+=verify_parameter(layer[name]);parameter_tensors+=1
            for stats in v['norms']:
                assert set(stats)=={'input_norm','mixed_norm'}
                for stats_tensor in stats.values():verify_parameter(stats_tensor)
        adam_rows=0
        for v in steps:
            assert v['original_input_and_mother_unchanged'] and v['in_memory_capture_reload_bitwise_equal']
            assert len(v['independent_NumPy_AdamW_checks'])==54
            assert len({c['name'] for c in v['independent_NumPy_AdamW_checks']})==54
            for c in v['independent_NumPy_AdamW_checks']:
                assert set(c['errors'])=={'parameter','exp_avg','exp_avg_sq'} and all(0<=e<=3e-6 for e in c['errors'].values());adam_rows+=1
            assert v['resources']['workspace_free_bytes']>=8_000_000_000 and v['resources']['available_ram_bytes']>=8_000_000_000
            assert v['resources']['GPU_peak_reserved_bytes']<=2_500_000_000 and v['resources']['GPU_free_bytes']>=4_000_000_000
        c=comparisons[0];rows=c['all54_parameter_comparisons'];assert len(rows)==len({v['name'] for v in rows})==54
        assert c['step']==0 and c['binary_disagreements']==5 and c['optimizer_fields_compared']==162
        assert max(v['parameter_error'] for v in rows)==c['max_errors']['parameter']>3e-6
        assert max(v['gradient_error'] for v in rows)==c['max_errors']['gradient']>3e-6
        assert c['max_errors']['probability']>3e-6
        for v in rows:
            assert {f['field'] for f in v['optimizer_fields']}=={'step','exp_avg','exp_avg_sq'}
            assert next(f for f in v['optimizer_fields'] if f['field']=='step')['max_error']==0
            assert abs(abs(v['CPU_parameter_at_index']-v['GPU_parameter_at_index'])-v['parameter_error'])<1e-12
        lp=HERE/'gin_real_loss_attribution_attempt01/receipt.json';loss=read(lp)
        lt=read(HERE/'ACTUAL_GIN_REAL_LOSS_ATTRIBUTION_TERMINAL_TOOL.json')
        assert lt['exit_code']==0 and 'session_id' not in lt and lt['observed_unified_exec_session']==12870
        assert loss['complete'] and not loss['errors'] and loss['CPU_diagnostic_optimizer_updates']==2 and loss['GPU_optimizer_updates']==0
        assert loss['independent_original_CPU_step0_model_and_optimizer_hashes_reproduced']
        assert loss['independent_old_loss_bitwise_reproduced'] and loss['max_CPU_loss_formula_parameter_difference']<=3e-6
        assert len(loss['parameter_comparisons'])==54 and sum(len(v['optimizer_fields']) for v in loss['parameter_comparisons'])==162
        for b in loss['source_bindings']:bind(b)
        analytical=[]
        for v in loss['original_worst_coordinate_checks']:
            q=v['original'];assert q in rows
            assert v['CPU_independent_gradient']==q['CPU_gradient_at_index'] and v['CPU_loss_formulas_gradient_sign_equal']
            assert (v['CPU_primary_gradient']>=0)!=(v['GPU_previous_gradient']>=0)
            cg=q['CPU_gradient_at_index'];gg=q['GPU_gradient_at_index']
            predicted=1e-4*abs(cg/(abs(cg)+1e-8)-gg/(abs(gg)+1e-8))
            error=abs(predicted-q['parameter_error']);assert error<=3e-6
            analytical.append(dict(name=q['name'],flat_index=q['maximum_parameter_flat_index'],
                                   observed_parameter_gap=q['parameter_error'],first_step_AdamW_gap_from_actual_gradients=predicted,
                                   absolute_arithmetic_gap_error=error,CPU_gradient=cg,GPU_gradient=gg,
                                   CPU_loss_formula_gradient_difference=v['CPU_loss_formula_gradient_difference']))
        r.update(complete=True,full19_scope_preserved_but_unqualified=True,actual_first_case_only=True,
                 actual_CPU_GPU_two_updates_each_verified=True,actual_CPU_GPU_whole_forwards_six_each_verified=True,
                 all216_actual_NumPy_parameter_update_rows_verified=True,independent_adam_checks=adam_rows,
                 all54_CPU_GPU_comparison_rows162_state_fields_verified=True,serialized_GIN_parameter_tensors_verified=parameter_tensors,
                 serialized_GIN_parameter_payload_bytes=payload_bytes,probability_gradient_parameter_and_binary_gates_failed=True,
                 first_step_CPU_GPU_max_errors=c['max_errors'],binary_disagreements=5,
                 loss_formula_CPU_max_gradient_difference=loss['max_CPU_loss_formula_gradient_difference'],
                 loss_formula_CPU_max_parameter_difference=loss['max_CPU_loss_formula_parameter_difference'],
                 loss_formula_effect_is_small_at_original_three_worst_sites=True,
                 original_three_worst_site_AdamW_arithmetic=analytical,
                 specific_forward_or_backward_operator_cause_not_identified=True,
                 source_bindings=[entry(p) for p in (Path(__file__),terminalp,old/'receipt.json',old/'frozen_config.json',journal,lp,
                                       HERE/'ACTUAL_GIN_REAL_LOSS_ATTRIBUTION_TERMINAL_TOOL.json')])
    except Exception as e:r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    (out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k not in ('source_bindings','original_three_worst_site_AdamW_arithmetic')}),flush=True)
    return int(not r['complete'])
if __name__=='__main__':raise SystemExit(main())
