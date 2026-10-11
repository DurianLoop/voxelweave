"""Append evidence after7857; include now-terminal35904 and exclude active compact19."""
import sys,time,json,re,gzip
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PREP=ROOT/'six_resolution_training_preparation_2026_10_09';ADAPT=ROOT/'adaptive_acquisition_primary_followup_2026_10_09';REAL=ROOT/'full_certified_schedule_2026_10_09';LIVE=HERE/'compact19_real_qualification_attempt01'
sys.path.insert(0,str(ADAPT));from resource_guard_v1 import guard,read,entry,bind,dump
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'));from archive_completed_stage import sha,bindings
start=time.perf_counter();before=guard(start,1200);ip=HERE/'APPEND_ROUND52_INDEX.json';pp=HERE/'APPEND_ROUND52_PROOF.json';assert not ip.exists() and not pp.exists()
previous=PREP/'APPEND_ROUND51_INDEX.json';assert sha(previous)=='02cc9c6fdf8e4a5558fe7c2ed5abdad9c3e9dc922484b1195ff88b10df8d3fb7'
v=read(previous);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==7857
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
 q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7857
for index,b in enumerate(old,1):
 bind(b)
 if index%1000==0:print(json.dumps(dict(previous7857_SHA_verified=index)),flush=True);guard(start,1200)
def receipt(p,complete=True):
 q=read(p);assert q['complete']==complete and bool(q['errors'])==(not complete)
 for b in q.get('source_bindings',[]):bind(b)
 return q
audit=receipt(PREP/'independent_round52_audit_attempt01/receipt.json');assert audit['completed_full35904_actual_terminal_and_independent_audit_bound'] and audit['all_small_and_original_fullpatch_step_parameter_and162_state_arithmetic_verified']
terminal=read(REAL/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json');assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==44317
terminalaudit=read(REAL/'ACTUAL_FULL_REAL_TERMINAL_AUDIT_V2_TOOL.json');assert terminalaudit['exit_code']==0 and 'session_id' not in terminalaudit
real=receipt(REAL/'full_real_pipeline_attempt01/receipt.json');real_audit=receipt(REAL/'full_real_terminal_audit_attempt01/receipt.json');assert real['fields_completed']==35904 and real_audit['all35904_unique_journal_fields_verified'] and real_audit['all_strict_numeric_gates_verified_from_actual_journal']
math=receipt(ADAPT/'compact_double_norm_cpu_attempt02/receipt.json');assert len(math['cases'])==8 and len(math['finite_difference'])==12
fd_failed=receipt(ADAPT/'compact_double_norm_cpu_attempt01/receipt.json',False);assert fd_failed['finite_difference'][-1]['checks'][-1]['analytic_error']>1e-8
full=receipt(ADAPT/'compact_norm_fullpatch_independent_attempt03/receipt.json');assert len(full['steps'])==2 and full['synthetic_GPU_optimizer_updates']==full['synthetic_CPU_optimizer_updates']==2
for step in full['steps']:assert max(step['max_errors'].values())<=3e-6 and step['binary_disagreements']==0 and len(step['all54_parameters'])==54 and step['optimizer_fields_compared']==162
for name in ('compact_norm_fullpatch_independent_attempt01','compact_norm_fullpatch_independent_attempt02'):receipt(ADAPT/name/'receipt.json',False)
live=read(HERE/'LAST_LIVE_COMPACT19_OBSERVATION_ROUND52.json');assert live['actual_tool_return']['session_id']==44838 and live['prefix_observation_only'] and not live['complete19series_qualified']
assert not any((PREP/n).exists() for n in ('training_attempt01','training_v2_attempt01','training_v3_attempt01'))
folders=(PREP,HERE,ROOT/'gin_accepted_primary_followup_2026_10_09',ADAPT,REAL)
sources={p for folder in folders for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(LIVE) and p not in (ip,pp)}
opaque={ROOT/b['path'] for b in chain};scanned=set();pending=set(sources);n_bind=n_link=0;excluded=[]
while pending:
 p=sorted(pending)[0];pending.remove(p)
 if p in scanned:continue
 scanned.add(p);assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_relative_to(LIVE)
 if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
 if p.suffix=='.json':
  for b in bindings(read(p)):
   target=(ROOT/b['path']).resolve();assert not target.is_relative_to(LIVE),'Live compact19 source binding'
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
r=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),index_kind='completed35904_and_compact_norm_original_fullpatch_two_step_synthetic_pass_after7857',prior_chain=chain,
 previous7857_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=7857+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
 old_full35904_actual_terminal_and_independent_audit_completed=True,now_terminal_full35904_outputs_included=True,
 live_compact19_outputs_excluded=True,live_compact19_session=44838,live_link_targets_excluded=excluded,
 compact_norm_eight_cases_twelve_Decimal_FD_passed=True,failed_float64_FD_preserved=True,
 compact_norm_small_two_step_GPU_CPU_passed=True,compact_norm_offload_content_journals_audited=True,
 original_fullpatch_two_synthetic_GPU_CPU_steps_passed=True,fullpatch_first_backward_and_step1_OOM_failures_preserved=True,
 all54_parameter_and162_optimizer_fields_independently_audited=True,synthetic_CPU_optimizer_updates_completed_and_recorded=15,synthetic_GPU_optimizer_updates_completed_and_recorded=12,
 current_medical_qualification_updates_not_in_synthetic_totals=True,additional_formal_medical_training_updates=0,additional_confirmation_data_reads=0,
 new_primary_papers_counted_this_round=0,selected_Greedy_AST_calls_audited=True,whole_author_pipeline_noninterference_proven=False,author_code_executed=False,
 original_FP32_production_qualified=False,complete19series_new_numeric_branch_qualified=False,full38_GPU_qualification_passed=False,formal_medical_training_launched=False,six_arm_training_ready=False,
 original_training_modified=False,other_PIDs_enumerated=False,other_PIDs_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
 publication_claim_confirmed=False,goal_status='active',unchanged_six_arm_total_budget_bytes=104156359,unchanged_prep_FOV_accepted_adaptive_other_caps_bytes=[7000000,20000000,6000000,2000000,22800000])
dump(ip,r)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7857_hashes_verified=True,new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=7857+len(new),live_compact19_outputs_excluded=True,completed35904_outputs_included=True,synthetic_original_fullpatch_pass_and_medical_scope_separate=True,publication_claim_confirmed=False,goal_status='active',resources_before=before,resources_after=guard(start,1200),elapsed_seconds=time.perf_counter()-start)
dump(pp,proof);print(json.dumps(proof),flush=True)
