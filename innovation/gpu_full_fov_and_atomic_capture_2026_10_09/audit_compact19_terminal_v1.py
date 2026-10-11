"""Prepared full19 terminal/journal auditor; requires true exit0 and complete immutable output."""
import sys,time,json,gzip,base64
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'));from resource_guard_v1 import guard,read,entry,bind,dump
import numpy as np
def main():
 start=time.perf_counter();before=guard(start,600)
 terminalpath=HERE/'ACTUAL_COMPACT19_REAL_TERMINAL_TOOL.json';terminal=read(terminalpath)
 assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==44838
 live=HERE/'compact19_real_qualification_attempt01';rp=live/'receipt.json';r=read(rp);cfgpath=live/'frozen_config.json';cfg=read(cfgpath)
 assert r['complete'] and not r['errors'] and r['status']=='completed' and r['complete19series_GPU_three_view_qualified']
 assert not r['original_FP32_production_qualified'] and r['separate_numeric_branch'] and cfg['graph_precision']=='FP64' and cfg['parameter_and_optimizer_state_precision']=='FP32'
 for b in r['source_bindings']:bind(b)
 journal=bind(r['journal']);cases={(v['case'],kind):v for v in cfg['cases'] for kind in cfg['kinds']};assert len(cases)==38 and len({v['patient'] for v in cfg['cases']})==11
 preparations={};updates={};comparisons={};name_sets=set();captures=0;CPU_saved_packs=CPU_saved_unpacks=0
 def encoded(v):
  array=np.frombuffer(base64.b64decode(v['payload_base64']),dtype='<f4').reshape(v['shape']);assert v['dtype']=='little_endian_float32'
  import hashlib
  # Same recorded array hash contract is shape/dtype plus raw content in actual helper; bind via its pure helper.
  sys.path.insert(0,str(ROOT/'experiments'));from mc_rc_observed_only_training_input import array_sha
  assert array_sha(array)==v['sha256']
 with gzip.open(journal,'rt',encoding='utf-8') as f:
  for line in f:
   v=json.loads(line);key=(v['case'],v['kind']);assert key in cases
   if v['type']=='prepared_three_views':
    index=v['step_index'];fullkey=(*key,index);assert fullkey not in preparations;preparations[fullkey]=v
    assert index in (0,1) and v['scheduled_step']==cases[key]['scheduled_steps'][index]
    assert v['patient']==cases[key]['patient'] and v['uid']==cases[key]['uid'] and v['GT_not_used_to_generate_GIN'] and v['coordinates_and_target_unchanged'] and len(v['view_sha256'])==len(v['parameters'])==len(v['norms'])==3
    for params in v['parameters']:
     encoded(params['alpha'])
     for layer in params['layers']:encoded(layer['weight']);encoded(layer['bias'])
    for norms in v['norms']:
     for value in norms.values():encoded(value)
   elif v['type']=='actual_two_step_optimizer':
    index=v['step'];fullkey=(*key,v['device'],index);assert fullkey not in updates;updates[fullkey]=v
    assert v['device'] in ('cpu','cuda:0') and index in (0,1) and v['original_input_and_mother_unchanged'] and v['in_memory_capture_reload_bitwise_equal']
    checks=v['independent_NumPy_AdamW_checks'];assert len(checks)==54 and len({q['name'] for q in checks})==54
    assert all(max(q['errors'].values())<=3e-6 for q in checks);captures+=1
    if v['device']=='cuda:0':
     a=v['audited_CPU_saving'];assert a['all_actual_unpacks_bitwise_verified'] and a['packed_tensors']>0 and a['unpack_events']>0 and not a['raw_tensor_payloads_persisted'];CPU_saved_packs+=a['packed_tensors'];CPU_saved_unpacks+=a['unpack_events']
     assert v['resources']['GPU_peak_reserved_bytes']<=2500000000 and v['resources']['GPU_free_bytes']>=4000000000
   elif v['type']=='CPU_GPU_strict_comparison':
    fullkey=(*key,v['step']);assert fullkey not in comparisons;comparisons[fullkey]=v;rows=v['all54_parameter_comparisons'];assert len(rows)==54
    fields=[q for row in rows for q in row['optimizer_fields']];assert len(fields)==v['optimizer_fields_compared']==162
    assert v['max_errors']['gradient']==max(q['gradient_error'] for q in rows) and v['max_errors']['parameter']==max(q['parameter_error'] for q in rows) and v['max_errors']['optimizer_state']==max(q['max_error'] for q in fields)
    assert max(v['max_errors'].values())<=3e-6 and v['binary_disagreements']==0
    for q in rows:
     assert abs(q['CPU_parameter_at_index']-q['GPU_parameter_at_index'])==q['parameter_error']
    name_sets.add(tuple(sorted(q['name'] for q in rows)))
   else:raise AssertionError(v['type'])
 assert len(preparations)==len(comparisons)==76 and len(updates)==captures==152 and len(name_sets)==1
 assert set(preparations)=={(*key,step) for key in cases for step in (0,1)}
 assert set(updates)=={(*key,device,step) for key in cases for device in ('cpu','cuda:0') for step in (0,1)}
 for fullkey,q in preparations.items():
  case,kind,step=fullkey;other=cfg['kinds'][1] if kind==cfg['kinds'][0] else cfg['kinds'][0]
  assert q['mother_target_sha256']==preparations[(case,other,step)]['mother_target_sha256'] and q['parameters']==preparations[(case,other,step)]['parameters']
 assert r['MRI_arrays_loaded']==38 and r['GT_arrays_loaded']==19 and r['parent_arrays_loaded']==0 and len(r['branches'])==38 and all(q['complete'] for q in r['branches'])
 assert r['GPU_optimizer_updates']==r['CPU_reference_optimizer_updates']==76 and r['GPU_whole_model_forwards']==r['CPU_reference_whole_model_forwards']==228 and r['in_memory_captures']==152 and len(r['step_comparisons'])==76
 for q in r['step_comparisons']:
  row=comparisons[(q['case'],q['kind'],q['step'])];assert q['max_errors']==row['max_errors'] and q['binary_disagreements']==0
 out=HERE/'compact19_terminal_audit_attempt01';out.mkdir(exist_ok=False)
 result=dict(complete=True,errors=[],source_bindings=[entry(p) for p in (Path(__file__),terminalpath,rp,cfgpath,journal)],all38_case_kind_and76_steps_verified=True,all11_patient19_series_and_two_devices_verified=True,all54_parameters162_state_and_NumPy_record_arithmetic_verified=True,all152_in_memory_capture_records_verified=True,CPU_saved_pack_records=CPU_saved_packs,CPU_saved_unpack_records=CPU_saved_unpacks,raw_tensor_payloads_independently_replayed=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,model_arrays_loaded=0,additional_optimizer_updates=0,formal_training_ready=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start,600),elapsed_seconds=time.perf_counter()-start)
 dump(out/'receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_bindings','resources_before','resources_after')}),flush=True)
if __name__=='__main__':main()
