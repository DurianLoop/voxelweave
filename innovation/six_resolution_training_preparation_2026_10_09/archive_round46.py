"""Verify unchanged7291 content hashes; append ended numerical work and preparation, exclude live35904."""
import sys,time,json,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard
LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
started=time.perf_counter()
def guard():
 r=resource_guard();assert time.perf_counter()-started<1200
 size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
 assert size<7_000_000 and r['workspace_free_bytes']-42_800_000-(7_000_000-size)>=8_000_000_000
 return r
guard();ip=HERE/'APPEND_ROUND46_INDEX.json';pp=HERE/'APPEND_ROUND46_PROOF.json';assert not ip.exists() and not pp.exists()
previous=ROOT/'action_oracle_and_prior_art_2026_10_09/APPEND_INDEX.json'
assert sha(previous)=='6a78df3186809768867f5454466efb6f011ed20089cbc94aee7af943fd0698d4'
v=read(previous);assert v['complete'] and v['cumulative_frozen_evidence_files']==7291
chain=v['prior_chain']+[entry(previous)];old=[]
for b in chain:
 q=read(bind(b));assert q['complete'] and not q['errors'];old.extend(q.get('evidence_files',q.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7291
for i,b in enumerate(old,1):
 bind(b)
 if i%1000==0:guard();print(json.dumps(dict(previous7291_logical_SHA_verified=i)),flush=True)
coverage=ROOT/'development_optimizer_coverage_2026_10_09';fov=ROOT/'gpu_full_fov_and_atomic_capture_2026_10_09'
assert read(coverage/'terminal_audit_attempt01/receipt.json')['all228_unique_updates_and456_patch_fields_verified']
assert read(coverage/'selective_terminal_audit_attempt01/receipt.json')['all228_unique_GPU_input_hash_comparison_identities_verified']
assert read(fov/'negative_terminal_audit_attempt01/receipt.json')['both_attempted_interventions_failed_original_probability_gate']
assert not read(HERE/'preflight_v3_attempt01/receipt.json')['ready']
assert not any((HERE/name).exists() for name in ['training_attempt01','training_v2_attempt01','training_v3_attempt01'])
roots=[HERE,coverage,fov,ROOT/'frozen_checkpoint_storage_2026_10_09']
sources={p for folder in roots for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in {ip,pp}}
sources.update(p for p in previous.parent.iterdir() if p.is_file())
sources.update(p for p in LIVE.parent.iterdir() if p.is_file())
scanned=set();pending=set(sources);n_bind=n_link=0;excluded_links=[]
opaque={ROOT/b['path'] for b in chain}
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
new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
for b in new:bind(b)
result=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),
 index_kind='ended_all19_228GPU_optimizer_selective_exact_input_replay_negative_fullFOV_and_v3_preparation_after7291',
 prior_chain=chain,previous7291_logical_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
 cumulative_frozen_evidence_files=7291+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
 live_full35904_outputs_excluded=True,live_link_targets_excluded=excluded_links,
 GPU_optimizer_updates_qualified=228,selective_complete_batch_hashes_reproduced=228,selective_patch_fields=456,
 new_distinct_primary_maintexts_read=0,new_DOI_exact_metadata_abstracts_read=2,
 inherited_primary_maintexts_not_recounted=True,full38_GPU_qualification_passed=False,full35904_qualification_passed=False,
 six_arm_training_ready=False,new_formal_training_launched=False,original_training_modified=False,
 confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
dump(ip,result)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7291_logical_hashes_verified=True,
 new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=7291+len(new),
 live_full35904_outputs_excluded=True,NTFS_storage_attributes_not_part_of_logical_content_hash=True,
 training_ready=False,publication_claim_confirmed=False,goal_status='active',resources=guard(),elapsed_seconds=time.perf_counter()-started)
dump(pp,proof);print(json.dumps(proof),flush=True)
