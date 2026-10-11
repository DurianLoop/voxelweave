"""Append round51 after7728, preserve old bytes and all failures; exclude active full pipeline."""
import sys,json,time,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,read,entry,bind,dump
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import sha,bindings
start=time.perf_counter();before=guard(start,1200);ADAPTIVE=ROOT/'adaptive_acquisition_primary_followup_2026_10_09';LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
ip=HERE/'APPEND_ROUND51_INDEX.json';pp=HERE/'APPEND_ROUND51_PROOF.json';assert not ip.exists() and not pp.exists()
previous=HERE/'APPEND_ROUND50_INDEX.json';assert sha(previous)=='97e4a4de6ff37a908732567e01f6e979125ea862dae1a7d4eb9a1f62979c4f73'
v=read(previous);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==7728
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
 q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7728
for index,b in enumerate(old,1):
 bind(b)
 if index%1000==0:print(json.dumps(dict(previous7728_SHA_verified=index)),flush=True);guard(start,1200)
def terminal(p,code):
 q=read(p);assert q['exit_code']==code and 'session_id' not in q;return q
for name,code in [('ACTUAL_STABLE_REDUCTION_FAILED_TERMINAL_TOOL.json',1),('ACTUAL_STABLE_REDUCTION_ADAM_TERMINAL_TOOL.json',0),('ACTUAL_HIGH_PRECISION_CPU_TERMINAL_TOOL.json',0),('ACTUAL_HIGH_PRECISION_GPU_V1_FAILED_TOOL.json',1),('ACTUAL_HIGH_PRECISION_GPU_V2_FAILED_TOOL.json',1),('ACTUAL_HIGH_PRECISION_GPU_V3_FAILED_TOOL.json',1),('ACTUAL_HIGH_PRECISION_GPU_V4_TERMINAL_TOOL.json',0),('ACTUAL_HIGH_PRECISION_FULLPATCH_COST_FAILED_TOOL.json',1)]:terminal(HERE/name,code)
failed=read(HERE/'stable_reduction_model_cpu_attempt01/receipt.json');assert not failed['complete'] and failed['errors'] and failed['CPU_optimizer_updates']==2 and len(failed['steps'])==1 and failed['steps'][0]['max_errors']['parameter']>3e-6
adam=read(HERE/'stable_reduction_adam_attribution_attempt01/receipt.json');assert adam['complete'] and not adam['errors'] and adam['max_errors']==failed['steps'][0]['max_errors'] and len(adam['coordinates'])==54
cpu=read(HERE/'high_precision_model_cpu_attempt01/receipt.json');gpu=read(HERE/'high_precision_model_gpu_attempt04/receipt.json')
for q in (cpu,gpu):
 assert q['complete'] and not q['errors'] and len(q['steps'])==2
 for step in q['steps']:assert max(step['max_errors'].values())<=3e-6 and step['binary_disagreements']==0 and len(step['all54_parameters'])==54 and step['optimizer_fields_compared']==162
cost=read(HERE/'high_precision_fullpatch_cost_attempt01/receipt.json');assert not cost['complete'] and 'OutOfMemoryError' in cost['errors'][0] and cost['forward_calls_started']==1 and cost['forward_calls_completed']==cost['synthetic_GPU_optimizer_updates']==0
assert cost['GPU_peak_reserved_bytes_on_failure']<=2500000000 and cost['GPU_free_bytes_on_failure']>=4000000000
for folder in ('foundation_table_arithmetic_attempt01','foundation_reading_scope_attempt01','independent_round51_audit_attempt02'):
 q=read(ADAPTIVE/folder/'receipt.json');assert q['complete'] and not q['errors']
reading=read(ADAPTIVE/'foundation_reading_scope_attempt01/receipt.json');assert reading['recovered_original_foundation_reading_chunks']==2 and reading['recovered_complete_original_paper_chunk_sets']==0 and reading['Swin_omitted_algorithm_lines_actually_read_and_verified']==22
future=read(ADAPTIVE/'FUTURE_EXPERIMENT_REGISTRY_ROUND51_V2.json');assert not any(v['execute_now'] for v in future['experiments']) and not future['publication_claim_confirmed']
live=read(HERE/'LAST_LIVE_FULL35904_OBSERVATION_ROUND51.json');assert live['actual_tool_return']['session_id']==44317 and live['prefix_observation_only'] and not live['complete_qualification_passed']
assert not any((HERE/n).exists() for n in ('training_attempt01','training_v2_attempt01','training_v3_attempt01'))
folders=(HERE,ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',ROOT/'gin_accepted_primary_followup_2026_10_09',ADAPTIVE)
sources={p for folder in folders for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in (ip,pp)};sources.update(p for p in LIVE.parent.iterdir() if p.is_file())
opaque={ROOT/b['path'] for b in chain};scanned=set();pending=set(sources);n_bind=n_link=0;excluded=[]
while pending:
 p=sorted(pending)[0];pending.remove(p)
 if p in scanned:continue
 scanned.add(p);assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_relative_to(LIVE)
 if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
 if p.suffix=='.json':
  for b in bindings(read(p)):
   target=(ROOT/b['path']).resolve();assert not target.is_relative_to(LIVE),'Live35904 source binding'
   target=bind(b);n_bind+=1
   if target not in sources:sources.add(target);pending.add(target)
 elif p.suffix=='.md':
  for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   if re.match(r'https?://|app://',raw):continue
   target=Path(raw.strip('<>').split('#',1)[0]);target=(target if target.is_absolute() else p.parent/target).resolve();assert target.exists() and target.is_relative_to(ROOT),raw
   if target.is_relative_to(LIVE):excluded.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()));continue
   if target.is_file() and target not in sources:sources.add(target);pending.add(target)
   n_link+=1
 guard(start,1200)
new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing and p not in opaque]
for b in new:bind(b)
r=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),index_kind='foundation_source_audit_and_separate_high_precision_synthetic_GPU_pass_fullpatch_OOM_after7728',prior_chain=chain,
 previous7728_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=7728+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
 live_full35904_outputs_excluded=True,live_link_targets_excluded=excluded,inherited_round51_distinct_primary_texts_reported_read=2,recovered_original_foundation_chunks=2,recovered_complete_original_paper_chunk_sets=0,
 omitted_Swin_algorithm_lines_actually_read=22,figure_pixels_actually_inspected=0,bibliography_items_read=0,author_code_executed=False,authenticated_publication_time_Greedy_commit=False,
 foundation_native_HTML_arithmetic_independently_audited=True,source_discrepancies_preserved=True,
 stable_reduction_parameter_gate_passed=False,stable_reduction_step1_executed=False,stable_reduction_Adam_all54_coordinates_audited=True,
 separate_high_precision_two_synthetic_CPU_steps_passed=True,separate_high_precision_two_synthetic_GPU_CPU_steps_passed=True,
 strict_deterministic_disjoint_pool_six_CPU_checks_passed=True,high_precision_original_fullpatch_cost_passed=False,fullpatch_OOM_forward_started=1,fullpatch_OOM_forward_completed=0,fullpatch_OOM_optimizer_updates=0,
 GPU_v1_exact_runtime_optimizer_count_not_recoverable=True,known_recorded_round51_CPU_optimizer_updates=10,known_recorded_round51_GPU_optimizer_updates=2,total_round51_actual_optimizer_count_claimed_exact=False,
 original_FP32_production_qualified=False,GIN_complete19series_qualification_passed=False,full38_GPU_qualification_passed=False,full35904_qualification_passed=False,formal_medical_training_launched=False,six_arm_training_ready=False,
 original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
 publication_claim_confirmed=False,goal_status='active',unchanged_six_arm_total_budget_bytes=104156359,unchanged_prep_FOV_accepted_adaptive_other_caps_bytes=[7000000,20000000,6000000,2000000,22800000])
dump(ip,r)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7728_hashes_verified=True,new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=7728+len(new),live_full35904_outputs_excluded=True,synthetic_GPU_pass_and_fullpatch_OOM_scopes_preserved=True,original_FP32_training_ready=False,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start,1200),elapsed_seconds=time.perf_counter()-start)
dump(pp,proof);print(json.dumps(proof),flush=True)
