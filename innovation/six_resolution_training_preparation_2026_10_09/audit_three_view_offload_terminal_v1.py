"""Independent record-level audit; no CUDA/MRI execution or synthetic rerun."""
import sys,json,gzip,time,math,traceback,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,resource_guard

def main():
    started=time.perf_counter();resource_guard();out=HERE/'three_view_offload_terminal_audit_attempt01';out.mkdir(exist_ok=False)
    r=dict(complete=False,errors=[],CUDA_initialized=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,
           training_updates=0,complete19series_GPU_three_view_qualified=False,medical_effect_scored=False,
           publication_claim_confirmed=False,goal_status='active')
    try:
        tp=HERE/'ACTUAL_THREE_VIEW_OFFLOAD_TRANSPARENCY_V2_TERMINAL_TOOL.json';t=read(tp)
        assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==86184
        last=json.loads(t['output'].strip().splitlines()[-1]);p=HERE/'three_view_offload_transparency_attempt02/receipt.json';q=read(p)
        for v in (last,q):assert v['complete'] and v['status']=='completed' and not v['errors'] and v['synthetic_GPU_optimizer_updates']==4
        assert last['elapsed_seconds']==q['elapsed_seconds']<360
        for b in q['source_bindings']:bind(b)
        assert q['MRI_arrays_loaded']==q['GT_arrays_loaded']==q['parent_model_arrays_loaded']==0
        assert not q['complete19series_GPU_three_view_qualified'] and not q['publication_claim_confirmed']
        branches=q['branches'];assert len(branches)==2
        assert [v['mode'] for v in branches]==['builtin_save_on_cpu','audited_CPU_saved_tensors_hooks']
        expected_blocks={f'{kind}.{i}' for kind,n in [('encoder',4),('decoder',3)] for i in range(n)}
        for v in branches:
            assert v['complete'] and not v['errors'] and v['optimizer_updates']==2 and v['actual_whole_model_forward_calls']==6
            assert set(v['checkpoint_block_invocations'])==expected_blocks and set(v['checkpoint_block_invocations'].values())=={12}
            assert len(v['steps'])==2 and [s['step'] for s in v['steps']]==[0,1]
            for s in v['steps']:
                assert math.isfinite(s['true_loss']) and s['input_target_unchanged']
                assert set(s['block_invocations'])==expected_blocks and set(s['block_invocations'].values())=={6}
                x=s['resources_after'];assert x['GPU_peak_reserved_bytes']<=2_500_000_000 and x['GPU_free_bytes']>=4_000_000_000
                assert x['workspace_free_bytes']>=8_000_000_000 and x['available_ram_bytes']>=8_000_000_000
                assert x['own_process_below_normal'] and x['cpu_threads']==1
            assert v['CPU_saved_payload_final_logical_bytes']==0
        for i in (0,1):assert branches[0]['steps'][i]['state_sha256']==branches[1]['steps'][i]['state_sha256']
        comparisons=q['step_comparisons'];assert len(comparisons)==2
        total_fields=0;paramnames=None
        for i,s in enumerate(comparisons):
            assert s['step']==i and set(s['max_errors'])=={'probability','loss','gradient','parameter','optimizer_state'}
            assert all(v==0 for v in s['max_errors'].values())
            rows=s['parameter_comparisons'];names={v['name'] for v in rows}
            assert len(names)==len(rows)==54
            if paramnames is None:paramnames=names
            assert names==paramnames
            for v in rows:
                assert v['gradient_error']==v['parameter_error']==0
                assert {f['field'] for f in v['optimizer_fields']}=={'step','exp_avg','exp_avg_sq'}
                assert all(f['max_error']==0 and f['bitwise_equal'] for f in v['optimizer_fields'])
            fields=sum(len(v['optimizer_fields']) for v in rows)
            assert fields==s['optimizer_fields_compared']==162;total_fields+=fields
        jp=bind(q['saved_tensor_journal']);counts=collections.Counter();unpacks=0;unused=0;logical=0
        with gzip.open(jp,'rt',encoding='utf-8') as f:
            records=[json.loads(line) for line in f]
        assert len(records)==q['packed_tensors']==240
        for index,v in enumerate(records):
            assert v['id']==index and v['step'] in (0,1) and v['mode']=='audited_CPU_saved_tensors_hooks'
            assert len(v['shape'])==len(v['original_stride'])==len(v['saved_stride'])
            dtype_bytes={'torch.float32':4,'torch.int64':8,'torch.int32':4,'torch.bool':1}
            assert v['dtype'] in dtype_bytes and v['logical_bytes']==math.prod(v['shape'])*dtype_bytes[v['dtype']]
            assert len(v['saved_sha256'])==64 and all(c in '0123456789abcdef' for c in v['saved_sha256'])
            counts[v['step']]+=1;logical+=v['logical_bytes'];unused+=int(not v['unpack_events'])
            for u in v['unpack_events']:
                assert u['restored_sha256']==v['saved_sha256'] and u['roundtrip_bitwise_equal'] and u['CPU_saved_value_unchanged']
                assert u['restored_device']==v['original_device'];unpacks+=1
        assert counts=={0:120,1:120} and unpacks==q['unpack_events']==224 and unused==q['packed_without_unpack']==16
        assert branches[1]['save_pack_count']==240 and branches[1]['unpack_count']==224
        assert q['all_actual_unpacks_bitwise_content_and_shape_dtype_device_verified']
        assert q['builtin_and_audited_two_steps_strict_numeric_gates_passed']
        costs=sum(v['model_input_optimizer_preparation_seconds']+
                  sum(s[k] for s in v['steps'] for k in ('full_graph_forward_loss_backward_seconds','probability_and_gradient_capture_seconds',
                       'AdamW_seconds','parameter_moment_capture_seconds','input_immutability_hash_seconds')) for v in branches)
        assert costs+q['synthetic_input_preparation_seconds']<=q['elapsed_seconds']
        r.update(complete=True,all240_saved224_restored_records_verified=True,all_two_steps54_parameter162_optimizer_fields_verified=True,
                 total_optimizer_fields_verified=total_fields,all_measured_comparison_errors_zero=True,
                 actual_whole_model_forwards_verified=12,actual_block_invocations_including_checkpoint_verified=168,
                 saved_tensor_logical_bytes_over_all_packs=logical,explicit_hook_peak_host_payload_logical_bytes=branches[1]['CPU_saved_payload_peak_logical_bytes'],
                 builtin_host_payload_not_instrumented=True,builtin_zero_counter_does_not_mean_no_host_memory=True,
                 GPU_peak_reserved_bytes=max(s['resources_after']['GPU_peak_reserved_bytes'] for v in branches for s in v['steps']),
                 record_level_audit_does_not_rerun_model=True,unused_packed_tensors=unused,
                 source_bindings=[entry(a) for a in (Path(__file__),tp,p,jp)])
    except Exception as e:
        r['errors'].append(type(e).__name__+': '+str(e));r['traceback']=traceback.format_exc()
    r['elapsed_seconds']=time.perf_counter()-started
    (out/'receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in r.items() if k!='source_bindings'}),flush=True)
    return int(not r['complete'])

if __name__=='__main__':raise SystemExit(main())
