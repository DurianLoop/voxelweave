"""Verify7380 unchanged logical hashes; append ended GIN/192tile/FP32 findings, exclude live35904."""
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
guard();ip=HERE/'APPEND_ROUND47_INDEX.json';pp=HERE/'APPEND_ROUND47_PROOF.json';assert not ip.exists() and not pp.exists()
previous=HERE/'APPEND_ROUND46_INDEX.json';assert sha(previous)=='ab87e6883439aed33c7e6291cb760a6645042de52d6e20d86b700e16294bbc66'
v=read(previous);assert v['complete'] and not v['errors'] and v['cumulative_frozen_evidence_files']==7380
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
 q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7380
for i,b in enumerate(old,1):
 bind(b)
 if i%1000==0:guard();print(json.dumps(dict(previous7380_logical_SHA_verified=i)),flush=True)
fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'
for folder in ['layerwise_all_tiles_attempt01','layerwise_terminal_audit_attempt01','fp32_norm_arithmetic_attempt01','fp32_norm_arithmetic_audit_attempt01']:
 q=read(fov/folder/'receipt.json');assert q['complete'] and not q['errors']
for name,session in [('ACTUAL_ALL_TILES_LAYERWISE_TERMINAL_TOOL.json',58242),('ACTUAL_FP32_NORM_ARITHMETIC_TERMINAL_TOOL.json',28213)]:
 t=read(fov/name);assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==session
assert read(fov/'layerwise_terminal_audit_attempt01/receipt.json')['all96_batches192_unique_tiles4704_layer_fields_verified']
assert read(fov/'fp32_norm_arithmetic_audit_attempt01/receipt.json')['qualifying_single_case_candidates']==[]
assert read(HERE/'gin_reading_provenance_attempt01/receipt.json')['unique_author_source_lines_actually_read']==1489
assert read(HERE/'gin_operator_preparation_attempt01/receipt.json')['synthetic_cases_completed']==24
assert not read(HERE/'preflight_round47_attempt01/receipt.json')['ready']
assert not any((HERE/name).exists() for name in ['training_attempt01','training_v2_attempt01','training_v3_attempt01'])
sources={p for folder in [HERE,fov] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in {ip,pp}}
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
   if target.is_relative_to(LIVE):excluded_links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()));continue
   if target.is_file() and target not in sources:sources.add(target);pending.add(target)
   n_link+=1
 guard()
new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing and p not in opaque]
for b in new:bind(b)
r=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),index_kind='ended_GIN_primary_and_author_reading_synthetic_oracle_all192tile_and_negative_FP32_after7380',
 prior_chain=chain,previous7380_logical_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=7380+len(new),
 source_binding_checks=n_bind,local_link_checks=n_link,live_full35904_outputs_excluded=True,live_link_targets_excluded=excluded_links,
 new_distinct_primary_maintexts_read=1,primary_version='arXiv2111.12525v5_early_not_final',primary_maintext_blocks_read=104,unique_experimental_tables_read=4,
 unique_author_source_files_read=7,unique_author_source_lines_read=1489,synthetic_GIN_cases_verified=24,
 unique_layerwise_tiles=192,layerwise_batches=96,layer_fields_verified=4704,new_GPU_actual_tile_forwards=1728,
 all_two_FP32_norm_candidates_failed=True,full38_GPU_qualification_passed=False,full35904_qualification_passed=False,
 six_arm_training_ready=False,new_formal_training_launched=False,original_training_modified=False,confirmation_patients_opened=False,lockedIXI_opened=False,
 publication_claim_confirmed=False,goal_status='active')
dump(ip,r)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7380_logical_hashes_verified=True,new_frozen_hashes_verified=True,
 newly_bound_files=len(new),cumulative_frozen_evidence_files=7380+len(new),live_full35904_outputs_excluded=True,
 training_ready=False,publication_claim_confirmed=False,goal_status='active',resources=guard(),elapsed_seconds=time.perf_counter()-started)
dump(pp,proof);print(json.dumps(proof),flush=True)
