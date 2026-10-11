"""Freeze completed round50 after7639: primary reading, synthetic failures and CPU audits; exclude live."""
import sys,time,json,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'adaptive_acquisition_primary_followup_2026_10_09'))
from resource_guard_v1 import guard,read,entry,bind,dump
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import sha,bindings
started=time.perf_counter();guard(started,1200)
LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
ADAPTIVE=ROOT/'adaptive_acquisition_primary_followup_2026_10_09'
ip=HERE/'APPEND_ROUND50_INDEX.json';pp=HERE/'APPEND_ROUND50_PROOF.json';assert not ip.exists() and not pp.exists()
previous=HERE/'APPEND_ROUND49_INDEX.json';assert sha(previous)=='6a76ef3d2e183e1df4cb757c0124ab9bfd593ffb332171bb9350e4059c945aa2'
v=read(previous);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==7639
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
 q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7639
for i,b in enumerate(old,1):
 bind(b)
 if i%1000==0:print(json.dumps(dict(previous7639_SHA_verified=i)),flush=True);guard(started,1200)
def terminal(p,code):
 q=read(p);assert q['exit_code']==code and 'session_id' not in q;return q
terminal(HERE/'ACTUAL_GIN_CPU_REFERENCE_V2_FAILED_TERMINAL_TOOL.json',1)
terminal(HERE/'ACTUAL_SYNTHETIC_ADAM_ATTRIBUTION_TERMINAL_TOOL.json',0)
terminal(ADAPTIVE/'ACTUAL_PRIMARY_CPU_AUDIT_V1_FAILED_TOOL.json',1)
terminal(ADAPTIVE/'ACTUAL_PRIMARY_CPU_AUDIT_V2_TERMINAL_TOOL.json',0)
terminal(ADAPTIVE/'ACTUAL_READING_PROVENANCE_TERMINAL_TOOL.json',0)
norm=read(HERE/'stable_norm_math_v2_attempt01/receipt.json');assert norm['complete'] and not norm['errors'] and norm['optimizer_updates']==0
meta=read(HERE/'OBSERVED_GIN_NORM_MATH_V2_TERMINAL_METADATA.json');assert not meta['complete_actual_tool_object_available'] and meta['reported_exit_code']==0
failed=read(HERE/'gin_cpu_reference_verification_attempt02/receipt.json');assert not failed['complete'] and failed['errors'] and failed['CPU_optimizer_updates']==2 and len(failed['steps'])==1
assert failed['steps'][0]['max_errors']['parameter']>3e-6
adam=read(HERE/'synthetic_adam_attribution_attempt01/receipt.json');assert adam['complete'] and not adam['errors'] and adam['CPU_optimizer_updates']==2
assert adam['max_errors']==failed['steps'][0]['max_errors'] and not adam['original_parameter_gate_passed']
assert len(adam['coordinates'])==54 and adam['worst_coordinate']['gradient_signs']==[1,1]
for folder in ('action_availability_mi_attempt01','primary_table_arithmetic_attempt01','independent_primary_cpu_audit_attempt02','reading_provenance_attempt01','preparation_reading_validation_attempt01'):
 q=read(ADAPTIVE/folder/'receipt.json');assert q['complete'] and not q['errors']
reading=read(ADAPTIVE/'reading_provenance_attempt01/receipt.json');assert reading['new_distinct_primary_text_papers_read']==3 and reading['graph_pixels_read_count']==reading['bibliography_items_read_count']==0
assert reading['greedy_omitted_Algorithm1_lines_actually_read']==37
live=read(HERE/'LAST_LIVE_FULL35904_OBSERVATION_ROUND50.json');assert live['actual_tool_return']['session_id']==44317 and live['prefix_observation_only'] and not live['complete_qualification_passed']
assert not any((HERE/n).exists() for n in ('training_attempt01','training_v2_attempt01','training_v3_attempt01'))
folders=(HERE,ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09',ROOT/'gin_accepted_primary_followup_2026_10_09',ADAPTIVE)
sources={p for folder in folders for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in {ip,pp}}
sources.update(p for p in LIVE.parent.iterdir() if p.is_file())
opaque={ROOT/b['path'] for b in chain};scanned=set();pending=set(sources);n_bind=n_link=0;excluded_links=[]
while pending:
 p=sorted(pending)[0];pending.remove(p)
 if p in scanned:continue
 scanned.add(p);assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_relative_to(LIVE)
 if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
 if p.suffix=='.json':
  for b in bindings(read(p)):
   target=(ROOT/b['path']).resolve();assert not target.is_relative_to(LIVE),'Live35904 bound: '+str(target)
   target=bind(b);n_bind+=1
   if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
 elif p.suffix=='.md':
  for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   if re.match(r'https?://|app://',raw):continue
   target=Path(raw.strip('<>').split('#',1)[0])
   if not target.is_absolute():target=p.parent/target
   target=target.resolve();assert target.exists() and target.is_relative_to(ROOT),raw
   if target.is_relative_to(LIVE):excluded_links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()));continue
   if target.is_file() and target not in sources:sources.add(target);pending.add(target)
   n_link+=1
 guard(started,1200)
new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing and p not in opaque]
for b in new:bind(b)
r=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),index_kind='three_adaptive_primary_texts_exact_MI_toy_failed_FP64_norm_model_and_Adam_attribution_after7639',
 prior_chain=chain,previous7639_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
 cumulative_frozen_evidence_files=7639+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
 live_full35904_outputs_excluded=True,live_link_targets_excluded=excluded_links,new_distinct_primary_text_papers_read=3,
 available_greedy_appendix_and_omitted_algorithm_read=True,figure_pixels_actually_inspected=0,bibliography_items_read=0,
 OpenMASC_is_MASC_followup_not_independent_replication=True,independent_primary_HTML_table_arithmetic_passed=True,
 exact_availability_only_MI_counterexample_verified=True,MI_counterexample_is_not_medical_benefit=True,
 high_precision_norm_math_record_passed=True,norm_terminal_complete_actual_object_unavailable_recorded=True,
 FP64_norm_full_synthetic_parameter_gate_passed=False,synthetic_verifier_step1_executed=False,
 total_round50_synthetic_CPU_optimizer_updates=4,additional_round50_GPU_optimizer_updates=0,additional_round50_medical_optimizer_updates=0,
 all54_synthetic_errors_and162_state_rows_reproduced_exactly=True,all54_Adam_first_step_math_audited=True,
 worst_synthetic_update_coordinates_have_same_positive_gradient_sign=True,failed_auditor_v1_preserved=True,
 future_registry_prepared_but_unlaunched=True,GIN_complete19series_qualification_passed=False,full38_GPU_qualification_passed=False,
 full35904_qualification_passed=False,formal_medical_training_launched=False,six_arm_training_ready=False,
 original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
 publication_claim_confirmed=False,goal_status='active',unchanged_six_arm_total_budget_bytes=104156359,
 unchanged_prep_FOV_accepted_adaptive_other_caps_bytes=[7000000,20000000,6000000,2000000,22800000])
dump(ip,r)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7639_hashes_verified=True,new_frozen_hashes_verified=True,
 newly_bound_files=len(new),cumulative_frozen_evidence_files=7639+len(new),live_full35904_outputs_excluded=True,
 synthetic_parameter_gate_failure_preserved=True,training_ready=False,publication_claim_confirmed=False,goal_status='active',
 resources=guard(started,1200),elapsed_seconds=time.perf_counter()-started)
dump(pp,proof);print(json.dumps(proof),flush=True)
