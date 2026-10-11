"""Append completed hallucination primary, author files and descriptive log diagnosis."""
import sys,json,time,gzip,hashlib,re,posixpath,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PREV=ROOT/'imputation_mask_and_conditional_uncertainty_2026_10_09'
spec=importlib.util.spec_from_file_location('frozen_archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(a,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
def main():
 sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard();index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
 previous=PREV/'APPEND_INDEX.json';previous_proof=PREV/'APPEND_PROOF.json'
 assert sha(previous)=='36c4f0589788d27017ea8b7dd879737404833841b358bbf5d588f7f94721ce14'
 assert sha(previous_proof)=='7c4fe5e52c3073e5566f99d1602604cf671af474195b62daf5285da4f56fef69'
 prev=read(previous);assert prev['complete'] and not prev['errors'] and prev['cumulative_frozen_evidence_files']==6719
 chain=prev['prior_chain']+[entry(previous)];old=[]
 for b in chain:
  v=read(bind(b));assert v['complete'] and not v['errors'];old.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
 existing={b['path']:b for b in old};assert len(old)==len(existing)==6719
 closed=[ROOT/'development_capacity_after_matched_2026_10_09/evaluation_attempt01',ROOT/'full_real_intensity_v2_2026_10_09/full_real_pipeline_attempt01',HERE/'complete_comparison_attempt01']
 def allowed(p):return all(not p.is_relative_to(f) or p==f/'frozen_config.json' for f in closed)
 for i,b in enumerate(old,1):
  assert allowed(ROOT/b['path']);bind(b)
  if i%2000==0:resource_guard();print(json.dumps(dict(previous_frozen_hashes_verified=i)),flush=True)
 r=read(HERE/'READING_PROVENANCE.json');assert r['complete'] and not r['errors'] and r['new_distinct_primary_maintexts_actually_read']==1
 assert r['author_files_actually_read']==3 and r['author_file_lines']==336 and r['result_data_tables']==1 and r['formula_and_algorithm_table_nodes']==40 and not r['Tanno_fulltext_read']
 t=read(HERE/'training_trajectory_attempt01/receipt.json');assert t['complete'] and not t['errors'] and t['all11968_rows_used'] and t['all2992_paired_mother_exposures_verified']
 author={bind(v['source_binding']):v['author_path'] for v in r['author_sources']};tree=read(HERE/'hallucination_author_tree_attempt02/receipt.json');repo_paths={v['path'] for v in tree['files']}
 sources={p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.raw.json') and p not in [index,proof] and allowed(p)}
 sources.update(p for p in PREV.iterdir() if p.is_file());sources.update(ROOT/b['path'] for b in chain);sources.add(previous_proof)
 opaque={ROOT/b['path'] for b in chain}|{previous_proof};pending=set(sources);scanned=set();binding_count=link_count=repo_link_count=0
 while pending:
  p=sorted(pending)[0];pending.remove(p)
  if p in scanned:continue
  scanned.add(p);assert p.is_file() and allowed(p)
  if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
  if p.suffix=='.json':
   v=read(p)
   if p.name.startswith('OBSERVATION_COMPRESSION_RECEIPT_'):
    for b in v['records']:
     assert Path(b['path']).name==b['path'];target=(p.parent/b['path']).resolve();assert target.stat().st_size==b['bytes'] and sha(target)==b['sha256']
     with gzip.open(target,'rb') as f:data=f.read()
     assert len(data)==b['uncompressed_bytes'] and hashlib.sha256(data).hexdigest()==b['uncompressed_sha256']
     if target not in sources:sources.add(target);pending.add(target)
     binding_count+=1
   else:
    for b in bindings(v):
     target=bind(b);assert allowed(target)
     if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
     binding_count+=1
  elif p.suffix=='.md':
   for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
    if re.match(r'https?://|app://',raw):continue
    if p in author:
     target=posixpath.normpath(posixpath.join(posixpath.dirname(author[p]),raw.split('#',1)[0]));assert target in repo_paths,raw;repo_link_count+=1;continue
    target=Path(raw.strip('<>').split('#',1)[0])
    if not target.is_absolute():target=p.parent/target
    target=target.resolve();assert target.exists() and target.is_relative_to(ROOT) and allowed(target),raw
    if target.is_file() and target not in sources:sources.add(target);pending.add(target)
    link_count+=1
  assert time.perf_counter()-started<1200
 new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
 for b in new:bind(b)
 result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='hallucination_primary_author_and_descriptive_training_after6719',prior_chain=chain,previous6719_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=6719+len(new),new_source_binding_checks=binding_count,new_local_link_checks=link_count,new_author_repo_relative_link_checks=repo_link_count,new_distinct_primary_maintexts_actually_read=1,new_author_files_wholly_read=3,new_author_file_lines=336,result_data_tables=1,formula_and_algorithm_layout_table_nodes=40,all11968_frozen_training_records_described=True,new_training_or_inference=False,Tanno_fulltext_obtained=False,unfinished_development_and_full_outputs_excluded=True,complete_development_comparison_prepared_only=True,confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
 estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
 assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+100000<2_000_000
 res=resource_guard();assert res['workspace_free_bytes']-estimate-100000-2_000_000-3_000_000-2_800_000>=8_000_000_000
 dump(index,result);out=dict(complete=True,errors=[],append_index=entry(index),previous6719_frozen_hashes_verified=True,new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=6719+len(new),new_primary_maintexts=1,new_author_files=3,new_author_lines=336,all11968_training_records_described=True,unfinished_rolling_outputs_excluded=True,independent_medical_confirmation=False,publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
 dump(proof,out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
