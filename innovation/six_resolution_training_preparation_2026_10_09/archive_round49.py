"""Append completed real negative qualification, isolated IN attribution, accepted-version reading."""
import sys,time,json,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard
LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
FOV=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09';PAPER=ROOT/'gin_accepted_primary_followup_2026_10_09'
started=time.perf_counter()
def guard():
    v=resource_guard();remaining=22_800_000;sizes={}
    for p,cap in ((HERE,7_000_000),(FOV,20_000_000),(PAPER,6_000_000)):
        size=sum(q.stat().st_size for q in p.rglob('*') if q.is_file());assert size<cap;remaining+=cap-size;sizes[p.name]=size
    assert v['workspace_free_bytes']-remaining>=8_000_000_000 and time.perf_counter()-started<1200
    v.update(remaining_all_stage_allowance_bytes=remaining,stage_sizes_bytes=sizes,
             accounting='Free already excludes occupied bytes; reserve only unspent portions of unchanged caps, plus other22.8MB')
    return v
guard();ip=HERE/'APPEND_ROUND49_INDEX.json';pp=HERE/'APPEND_ROUND49_PROOF.json';assert not ip.exists() and not pp.exists()
previous=HERE/'APPEND_ROUND48_INDEX.json';assert sha(previous)=='b9825de3824978e7a62dac4094455cdd292f32179930c07c1cb6e45ba5411615'
v=read(previous);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==7538
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
    q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7538
for i,b in enumerate(old,1):
    bind(b)
    if i%1000==0:guard();print(json.dumps(dict(previous7538_SHA_verified=i)),flush=True)
for name,code,sid in (('ACTUAL_GIN_CPU_REFERENCE_TERMINAL_TOOL.json',0,None),('ACTUAL_GIN19_REAL_GRAPH_V1_PRELAUNCH_FAILED_TOOL.json',1,None),
 ('ACTUAL_GIN19_REAL_GRAPH_V2_FAILED_TERMINAL_TOOL.json',1,42978),('ACTUAL_GIN_REAL_LOSS_ATTRIBUTION_TERMINAL_TOOL.json',0,12870),
 ('ACTUAL_GIN_REAL_FAILURE_AUDIT_TERMINAL_TOOL.json',0,None),('ACTUAL_GIN_REAL_LOCAL_VJP_TERMINAL_TOOL.json',0,31564),
 ('ACTUAL_GIN_REAL_IN_VJP_TERMINAL_TOOL.json',0,82611),('ACTUAL_GIN_REAL_IN_FINITE_DIFFERENCE_FAILED_TERMINAL_TOOL.json',1,24948)):
    q=read(HERE/name);assert q['exit_code']==code and 'session_id' not in q and q['observed_unified_exec_session']==sid
cpu=read(HERE/'gin_cpu_reference_verification_attempt01/receipt.json');assert cpu['complete'] and cpu['all_two_steps54_parameters162_optimizer_fields_strict_passed']
pre=read(HERE/'gin19_real_graph_attempt01/receipt.json');assert not pre['complete'] and pre['MRI_arrays_loaded']==pre['GT_arrays_loaded']==pre['GPU_optimizer_updates']==0
real=read(HERE/'gin19_real_graph_attempt02/receipt.json');assert not real['complete'] and not real['complete19series_GPU_three_view_qualified']
assert real['GPU_optimizer_updates']==real['CPU_reference_optimizer_updates']==2 and real['GPU_whole_model_forwards']==real['CPU_reference_whole_model_forwards']==6
assert real['MRI_arrays_loaded']==real['GT_arrays_loaded']==1 and real['parent_arrays_loaded']==0 and len(real['step_comparisons'])==1
cfg=read(HERE/'gin19_real_graph_attempt02/frozen_config.json');assert cfg['expected_series']==19 and cfg['expected_patients']==11 and cfg['expected_GPU_updates']==76
for folder in ('gin_real_failure_audit_attempt01','gin_real_loss_attribution_attempt01','gin_real_local_vjp_attempt01','gin_real_in_vjp_attempt01','gin_local_and_IN_audit_attempt01'):
    q=read(HERE/folder/'receipt.json');assert q['complete'] and not q['errors']
fd=read(HERE/'gin_real_in_finite_difference_attempt01/receipt.json');assert not fd['complete'] and not fd['all_three_h_negative_and_error_le1e8'] and fd['errors']
reading=read(PAPER/'accepted_reading_provenance_attempt01/receipt.json');assert reading['complete'] and not reading['errors']
assert reading['new_distinct_papers_read']==0 and reading['new_accepted_primary_versions_read']==1 and reading['all12_text_pages_actually_read'] and reading['all12_page_renders_actually_inspected']
live=read(HERE/'LAST_LIVE_FULL35904_OBSERVATION_ROUND49.json');assert live['actual_tool_return']['session_id']==44317 and live['prefix_observation_only'] and not live['complete_qualification_passed']
assert not any((HERE/name).exists() for name in ('training_attempt01','training_v2_attempt01','training_v3_attempt01'))
sources={p for folder in (HERE,FOV,PAPER) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in {ip,pp}}
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
            if target.is_relative_to(LIVE):
                excluded_links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()));continue
            if target.is_file() and target not in sources:sources.add(target);pending.add(target)
            n_link+=1
    guard()
new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing and p not in opaque]
for b in new:bind(b)
r=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),
 index_kind='real_GIN_negative_qualification_loss_conv_IN_attribution_failed_FD_and_accepted_primary_version_after7538',
 prior_chain=chain,previous7538_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
 cumulative_frozen_evidence_files=7538+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
 live_full35904_outputs_excluded=True,live_link_targets_excluded=excluded_links,
 new_distinct_primary_papers_read=0,new_accepted_primary_versions_read=1,accepted_primary_text_pages_read=12,accepted_renders_inspected=12,
 accepted_figures_read=8,accepted_numbered_tables_read=7,accepted_numbered_equations_read=6,publisher_typeset_final_read=False,
 source_agreement_selector_prior_art_recorded=True,GIN_complete19series_qualification_passed=False,
 actual_real_first_case_GPU_optimizer_updates=2,actual_real_first_case_CPU_reference_optimizer_updates=2,
 actual_cross_device_steps_compared=1,all216_actual_NumPy_update_rows_verified=True,
 one_case_one_coordinate_IN_backward_numeric_sensitivity_isolated=True,all_conv_weight_gradients_local_reconstructed_bitwise=True,
 all6_original_IN_input_cotangents_reconstructed_bitwise=True,finite_difference_fixed_gate_passed=False,
 largest_predeclared_h_failure_retained=True,additional_attribution_GPU_optimizer_updates=0,
 full38_GPU_qualification_passed=False,full35904_qualification_passed=False,formal_medical_training_launched=False,six_arm_training_ready=False,
 original_training_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
 publication_claim_confirmed=False,goal_status='active',unchanged_six_arm_total_budget_bytes=104156359,
 unchanged_prep_FOV_other_plus_added_paper_caps_bytes=[7000000,20000000,22800000,6000000],
 disk_accounting_changed_to_remaining_allowance_not_reduced_caps=True)
dump(ip,r)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7538_hashes_verified=True,new_frozen_hashes_verified=True,
 newly_bound_files=len(new),cumulative_frozen_evidence_files=7538+len(new),live_full35904_outputs_excluded=True,
 training_ready=False,publication_claim_confirmed=False,goal_status='active',resources=guard(),elapsed_seconds=time.perf_counter()-started)
dump(pp,proof);print(json.dumps(proof),flush=True)
