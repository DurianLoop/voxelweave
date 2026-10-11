"""Append complete2019 UQ manuscript and2992 point geometry after6823; exclude live evaluations."""
import sys,time,json,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PREV=ROOT/'conditional_uq_and_task_capacity_followup_2026_10_09';MECH=ROOT/'task_capacity_mechanism_audit_2026_10_09'
spec=importlib.util.spec_from_file_location('prior_archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(a,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard();index=HERE/'APPEND_CAPACITY_INDEX.json';proof=HERE/'APPEND_CAPACITY_PROOF.json';assert not index.exists() and not proof.exists()
 previous=HERE/'APPEND_INDEX.json';previous_proof=HERE/'APPEND_PROOF.json'
 assert sha(previous)=='8d044e0e496aa3936ce016c33229676e66dfecd6ed658b361d1f63c7d421e6af'
 assert sha(previous_proof)=='70741d4dea43cb70e67171fe985c8295390ab99ea50d13bec5b8e4647df7beeb'
 prev=read(previous);assert prev['complete'] and not prev['errors'] and prev['cumulative_frozen_evidence_files']==6823
 chain=prev['prior_chain']+[entry(previous)];old=[]
 for b in chain:
  v=read(bind(b));assert v['complete'] and not v['errors'];old.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
 existing={b['path']:b for b in old};assert len(old)==len(existing)==6823
 closed=[ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01']
 def allowed(p):return all(not p.is_relative_to(f) or p==f/'frozen_config.json' for f in closed)
 for i,b in enumerate(old,1):
  assert allowed(ROOT/b['path']);bind(b)
  if i%2000==0:resource_guard();print(json.dumps(dict(previous_frozen_hashes_verified=i)),flush=True)
 reading=read(HERE/'READING_PROVENANCE.json');assert reading['complete'] and not reading['errors'] and reading['new_distinct_primary_maintexts_actually_read']==1 and reading['blocks_actually_read']==139 and reading['data_tables_read']==3 and reading['equation_layout_tables']==14
 obs=read(HERE/'ACTUAL_TOOL_OBSERVATIONS_PART02.json');mathterm=obs['dmri_constant_v2_actual'];centerterm=obs['center_actual_terminal']
 assert mathterm['exit_code']==centerterm['exit_code']==0 and 'session_id' not in mathterm and 'session_id' not in centerterm
 assert mathterm['chunk_id']=='fe41d8' and centerterm['chunk_id']=='93e08d'
 center=read(MECH/'center_position_attempt01/receipt.json');assert center['complete'] and not center['errors'] and center['probe_count']==2992 and center['patient_count']==11 and center['series_count']==19 and center['all_four_arm_mother_geometries_matched'] and center['max_weight_error']<=3e-6
 sources={p for folder in [HERE,MECH] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [index,proof] and allowed(p)}
 dev=ROOT/'development_capacity_after_matched_2026_10_09'
 terminal=read(dev/'ACTUAL_DEVELOPMENT_EVALUATION_TERMINAL_TOOL.json');capture=read(dev/'ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json')
 assert terminal['exit_code']==0 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==12652
 assert capture['observed_tool_exit']==0 and capture['all76_complete_FOVs_and_exact_case_sets_verified'] and capture['result_sha256']==sha(dev/'evaluation_attempt01/receipt.json')
 comparison=read(PREV/'complete_comparison_attempt01/receipt.json');assert comparison['complete'] and not comparison['errors'] and comparison['all76_development_and36_seen_validation_FOVs_retained'] and comparison['all_metrics_fraction_recounted']
 metadata=read(HERE/'cohort_metadata_attempt01/receipt.json');assert metadata['complete'] and metadata['all28_series15_patients_retained'] and metadata['all_four_arm_GT_counts_identical_per_case']
 sources.update(p for folder in [dev,PREV/'complete_comparison_attempt01'] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 sources.update(p for p in PREV.iterdir() if p.is_file());sources.update(ROOT/b['path'] for b in chain);sources.add(previous_proof)
 opaque={ROOT/b['path'] for b in chain}|{previous_proof};pending=set(sources);scanned=set();binding_count=link_count=0
 while pending:
  p=sorted(pending)[0];pending.remove(p)
  if p in scanned:continue
  scanned.add(p);assert p.is_file() and allowed(p)
  if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
  if p.suffix=='.json':
   for b in bindings(read(p)):
    target=bind(b);assert allowed(target)
    if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
    binding_count+=1
  elif p.suffix=='.md':
   for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
    if re.match(r'https?://|app://',raw):continue
    target=Path(raw.strip('<>').split('#',1)[0])
    if not target.is_absolute():target=p.parent/target
    target=target.resolve();assert target.exists() and target.is_relative_to(ROOT) and allowed(target),raw
    if target.is_file() and target not in sources:sources.add(target);pending.add(target)
    link_count+=1
  assert time.perf_counter()-started<1200
 new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
 for b in new:bind(b)
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='completed76_development112_comparison_and28_metadata_after6823',prior_chain=chain,previous6823_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=6823+len(new),new_source_binding_checks=binding_count,new_local_link_checks=link_count,new_distinct_primary_maintexts_actually_read=0,manuscript_version='1907.13418v1',all139_maintext_blocks_read=True,data_tables=3,result_tables=2,equation_layout_tables=14,all2992_foreground_probe_positions_described=True,all11_development_patients19_series_retained=True,version_specific_literal_math_sanity_actual_exit=0,completed_development76_FOV_outputs_frozen_after_actual_exit=True,unfinished_full_outputs_excluded=True,no_new_MRI_or_GT_arrays_or_neural_forwards=True,confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
 estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
 assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+100000<2_000_000
 res=resource_guard();assert res['workspace_free_bytes']-estimate-100000-2_000_000-3_000_000-2_800_000-1_200_000>=8_000_000_000
 dump(index,result);out=dict(complete=True,errors=[],append_index=entry(index),previous6823_frozen_hashes_verified=True,new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=6823+len(new),new_primary_maintexts=0,all139_extracted_blocks_read=True,all2992_foreground_probes_described=True,unfinished_rolling_outputs_excluded=True,independent_medical_confirmation=False,publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
 dump(proof,out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
