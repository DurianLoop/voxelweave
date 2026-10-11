"""Check source-bound numerical records/Decimal arithmetic and saved-tensor journals independently."""
import sys,json,gzip,time
from pathlib import Path
from decimal import Decimal as D,localcontext
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;STAGE=ROOT/'adaptive_acquisition_primary_followup_2026_10_09'
sys.path.insert(0,str(STAGE));from resource_guard_v1 import guard,read,entry,bind,dump
start=time.perf_counter();before=guard(start);sources=[]
def receipt(p,complete=True):
 q=read(p);sources.append(entry(p));assert q['complete']==complete and bool(q['errors'])==(not complete)
 for b in q.get('source_bindings',[]):bind(b)
 return q
math=receipt(STAGE/'compact_double_norm_cpu_attempt02/receipt.json');old=receipt(STAGE/'compact_double_norm_cpu_attempt01/receipt.json',False)
assert len(math['cases'])==8 and len(math['finite_difference'])==12 and not math['CUDA_initialized'] and math['optimizer_updates']==0
assert {(v['case'],v['affine_dtype']) for v in math['cases']}=={(a,b) for a in ('random','constant','nearconstant','sparse') for b in ('torch.float64','torch.float32')}
for row in math['cases']:assert max(row['max_errors'].values())<=3e-6
for row in math['finite_difference']:
 assert [v['h'] for v in row['checks']]==[1e-3,1e-4,1e-5]
 for v in row['checks']:
  with localcontext() as context:
   context.prec=60;derivative=(D(v['plus_exact_decimal'])-D(v['minus_exact_decimal']))/(2*D.from_float(v['h']));error=abs(derivative-D.from_float(row['analytical']))
   assert derivative==D(v['derivative_exact_decimal']) and error==D(v['analytic_error_exact_decimal'])
  assert float(derivative)==v['derivative'] and float(error)==v['analytic_error']
 assert row['checks'][-1]['analytic_error']<=1e-8
 if row['parameter']=='input' and row['case'] in ('constant','nearconstant'):assert abs(row['direction_norm']-.001)<1e-15
assert old['finite_difference'][-1]['checks'][-1]['analytic_error']>1e-8
def numeric(q,count):
 assert len(q['steps'])==count
 for step in q['steps']:
  rows=step['all54_parameters'];assert len(rows)==len({v['name'] for v in rows})==54
  fields=[v for row in rows for v in row['optimizer_fields']];assert len(fields)==step['optimizer_fields_compared']==162
  assert all({v['field'] for v in row['optimizer_fields']}=={'step','exp_avg','exp_avg_sq'} for row in rows)
  assert step['max_errors']['gradient']==max(v['gradient_error'] for v in rows) and step['max_errors']['parameter']==max(v['parameter_error'] for v in rows)
  assert step['max_errors']['optimizer_state']==max(v['max_error'] for v in fields) and step['max_errors']['loss']==abs(step['loss_values'][0]-step['loss_values'][1])
  assert max(step['max_errors'].values())<=3e-6 and step['binary_disagreements']==0
def journal(q):
 p=bind(q.get('saved_tensor_journal',q.get('failure_saved_tensor_journal')));sources.append(entry(p))
 with gzip.open(p,'rt',encoding='utf-8') as f:rows=[json.loads(v) for v in f]
 assert len(rows)==q['packed_tensors'] and [v['id'] for v in rows]==list(range(len(rows)))
 events=[(v,e) for v in rows for e in v['unpack_events']];assert len(events)==q['unpack_events'] and events
 for v,e in events:assert e['bitwise_equal'] and e['shape_dtype_device_equal'] and e['sha256']==v['sha256']
 return dict(path=entry(p),packed_tensors=len(rows),unpack_events=len(events),runtime_hash_and_roundtrip_records_consistent=True,raw_saved_tensor_payloads_persisted=False,offline_replay_of_tensor_bytes_performed=False)
cpu=receipt(STAGE/'compact_norm_model_cpu_attempt01/receipt.json');numeric(cpu,2)
small_names=['compact_norm_model_gpu_attempt01','compact_norm_offload_small_attempt01','compact_norm_reference_lifetime_small_attempt01','compact_norm_segmented_small_attempt01'];journals=[]
for name in small_names:
 q=receipt(STAGE/name/'receipt.json');numeric(q,2);assert q['synthetic_GPU_optimizer_updates']==q['synthetic_CPU_optimizer_updates']==2
 if 'saved_tensor_journal' in q:journals.append(journal(q))
cost=receipt(STAGE/'compact_norm_fullpatch_cost_attempt01/receipt.json');assert cost['forward_calls_started']==cost['forward_calls_completed']==3 and cost['synthetic_GPU_optimizer_updates']==1;journals.append(journal(cost))
fail1=receipt(STAGE/'compact_norm_fullpatch_independent_attempt01/receipt.json',False);assert len(fail1['steps'])==0 and fail1['synthetic_GPU_optimizer_updates']==fail1['synthetic_CPU_optimizer_updates']==0
fail2=receipt(STAGE/'compact_norm_fullpatch_independent_attempt02/receipt.json',False);numeric(fail2,1);assert fail2['synthetic_GPU_optimizer_updates']==fail2['synthetic_CPU_optimizer_updates']==1;journals.append(journal(fail2))
full=receipt(STAGE/'compact_norm_fullpatch_independent_attempt03/receipt.json');numeric(full,2);assert full['synthetic_GPU_optimizer_updates']==full['synthetic_CPU_optimizer_updates']==2 and full['original_fullpatch_two_synthetic_steps_passed'];journals.append(journal(full))
for q in (cpu,cost,fail1,fail2,full):assert q['MRI_arrays_loaded']==q['GT_arrays_loaded']==q['parent_arrays_loaded']==0 and not q['publication_claim_confirmed']
assert cost['resources_after']['GPU_peak_reserved_bytes']<=2500000000 and full['resources_after']['GPU_peak_reserved_bytes']<=2500000000 and full['resources_after']['GPU_free_bytes']>=4000000000
real=receipt(ROOT/'full_certified_schedule_2026_10_09/full_real_terminal_audit_attempt01/receipt.json');t=read(ROOT/'full_certified_schedule_2026_10_09/ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json');assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==44317
assert real['all35904_unique_journal_fields_verified'] and real['all11_patient_and19_series_denominators_verified'] and real['all_strict_numeric_gates_verified_from_actual_journal'];assert real['training_updates']==real['MRI_arrays_loaded']==real['GT_arrays_loaded']==0
gt=receipt(STAGE/'greedy_deployment_call_boundary_attempt01/receipt.json');assert not gt['author_code_executed'] and not gt['whole_author_pipeline_noninterference_proven']
out=HERE/'independent_round52_audit_attempt01';out.mkdir(exist_ok=False)
r=dict(complete=True,errors=[],source_bindings=[entry(Path(__file__)),entry(STAGE/'resource_guard_v1.py')]+sources,
 norm_eight_cases_and_twelve_exact_decimal_FD_records_audited=True,failed_float64_FD_gate_preserved=True,
 all_small_and_original_fullpatch_step_parameter_and162_state_arithmetic_verified=True,fullpatch_failed_first_attempt_and_step1_failure_preserved=True,
 saved_journal_audits=journals,all_journal_runtime_roundtrip_records_consistent=True,raw_tensor_bytes_independently_replayed=False,
 completed_full35904_actual_terminal_and_independent_audit_bound=True,author_GT_scoring_not_equated_with_deployment_leak=True,
 new_model_rerun=False,MRI_arrays_loaded=0,GT_arrays_loaded=0,new_optimizer_updates=0,medical_effect_scored=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start),elapsed_seconds=time.perf_counter()-start)
dump(out/'receipt.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_bindings','resources_before','resources_after','saved_journal_audits')}),flush=True)
