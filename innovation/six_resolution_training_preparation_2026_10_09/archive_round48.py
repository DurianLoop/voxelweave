"""Verify frozen7457 unchanged; append completed SSC/probes/offload and exclude live35904."""
import sys,time,json,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard
LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01';started=time.perf_counter()

def guard():
    r=resource_guard();size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    assert size<7_000_000 and r['workspace_free_bytes']-42_800_000-(7_000_000-size)>=8_000_000_000
    assert time.perf_counter()-started<1200;return r

guard();ip=HERE/'APPEND_ROUND48_INDEX.json';pp=HERE/'APPEND_ROUND48_PROOF.json';assert not ip.exists() and not pp.exists()
previous=HERE/'APPEND_ROUND47_INDEX.json'
assert sha(previous)=='c43c7dd3286c266280ff0137b6242ee629dffcdbde1d75cd18d320d371943608'
v=read(previous);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==7457
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
    q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7457
for i,b in enumerate(old,1):
    bind(b)
    if i%1000==0:guard();print(json.dumps(dict(previous7457_SHA_verified=i)),flush=True)
fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'
q=read(fov/'same_input_terminal_audit_attempt01/receipt.json')
assert q['complete'] and not q['errors'] and q['all96_batches192_unique_tiles4704_primary288_auxiliary_verified']
t=read(fov/'ACTUAL_SAME_INPUT_OPERATORS_TERMINAL_TOOL.json')
assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==6897
for folder in ('ssc_reading_provenance_attempt01','ssc_operator_preparation_attempt01','three_view_synthetic_attempt01',
               'three_view_synthetic_attempt02','three_view_offload_transparency_attempt02','three_view_offload_terminal_audit_attempt01'):
    q=read(HERE/folder/'receipt.json');assert q['complete'] and not q['errors']
assert read(HERE/'ssc_reading_provenance_attempt01/receipt.json')['publisher_maintext_and_reference_pages_read']==8
probe=read(HERE/'three_view_gpu_fullpatch_attempt01/receipt.json')
assert probe['complete'] and not probe['sequential_fullpatch_graph_completed'] and probe['synthetic_GPU_optimizer_updates']==0
failed=read(HERE/'three_view_offload_vjp_attempt01/receipt.json')
assert not failed['complete'] and failed['max_parameter_error']>3e-6
t=read(HERE/'ACTUAL_THREE_VIEW_OFFLOAD_VJP_FAILED_TERMINAL_TOOL.json')
assert t['exit_code']==1 and 'session_id' not in t
init_failure=read(HERE/'three_view_offload_transparency_attempt01/receipt.json')
assert not init_failure['complete'] and init_failure['synthetic_GPU_optimizer_updates']==0
passed=read(HERE/'three_view_offload_terminal_audit_attempt01/receipt.json')
assert passed['all240_saved224_restored_records_verified'] and passed['all_measured_comparison_errors_zero']
t=read(HERE/'ACTUAL_THREE_VIEW_OFFLOAD_TRANSPARENCY_V2_TERMINAL_TOOL.json')
assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==86184
plan=read(HERE/'gin19_metadata_preparation_attempt01/manifest.json')
assert plan['complete'] and not plan['execution_ready'] and plan['actual_GPU_optimizer_updates']==0
assert plan['unique_development_patients']==11 and plan['unique_development_series']==19
assert not any((HERE/name).exists() for name in ('training_attempt01','training_v2_attempt01','training_v3_attempt01'))
sources={p for folder in (HERE,fov) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in {ip,pp}}
sources.update(p for p in LIVE.parent.iterdir() if p.is_file())
opaque={ROOT/b['path'] for b in chain};scanned=set();pending=set(sources);n_bind=n_link=0;excluded_links=[]
while pending:
    p=sorted(pending)[0];pending.remove(p)
    if p in scanned:continue
    scanned.add(p);assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_relative_to(LIVE)
    if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
    if p.suffix=='.json':
        for b in bindings(read(p)):
            target=(ROOT/b['path']).resolve();assert not target.is_relative_to(LIVE),'live35904 unexpectedly bound: '+str(target)
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
       index_kind='completed_SSC_primary_same_input52_operators_three_view_synthetic_offload_and_negative_VJP_after7457',
       prior_chain=chain,previous7457_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
       cumulative_frozen_evidence_files=7457+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
       live_full35904_outputs_excluded=True,live_link_targets_excluded=excluded_links,
       new_distinct_primary_maintexts_read=1,SSC_primary_pages_read=8,SSC_figures_read=4,SSC_numbered_equations_read=3,
       author_SSC_implementation_read_or_executed=False,SSC_medical_effect_scored=False,
       same_input_unique_tiles=192,same_input_batches=96,same_input_primary_fields=4704,same_input_auxiliary_fields=288,
       same_input_actual_operator_evaluations_per_device=9984,
       all_original_fullpatch_packed_and_plain_sequential_graphs_OOM=True,
       two_pass_VJP_parameter_gate_failed=True,two_pass_VJP_parameter_max_error=failed['max_parameter_error'],
       CPU_offload_two_step_transparency_verified=True,offload_packed_tensors=240,offload_unpacks=224,
       offload_two_step_max_comparison_error=0,offload_GPU_peak_reserved_bytes=passed['GPU_peak_reserved_bytes'],
       formal_GIN_medical_training_launched=False,GIN19_protocol_metadata_prepared_only=True,
       full38_GPU_qualification_passed=False,full35904_qualification_passed=False,six_arm_training_ready=False,
       original_training_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
       publication_claim_confirmed=False,goal_status='active')
dump(ip,r)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7457_hashes_verified=True,new_frozen_hashes_verified=True,
           newly_bound_files=len(new),cumulative_frozen_evidence_files=7457+len(new),live_full35904_outputs_excluded=True,
           training_ready=False,publication_claim_confirmed=False,goal_status='active',resources=guard(),elapsed_seconds=time.perf_counter()-started)
dump(pp,proof);print(json.dumps(proof),flush=True)
