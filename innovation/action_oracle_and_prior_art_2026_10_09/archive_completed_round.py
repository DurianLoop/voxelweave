"""Verify old7180 chain and append ended reading, oracle, first AdamW qualification and preparation."""
import sys,time,re,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard
LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
started=time.perf_counter()
def guard():
    r=resource_guard();assert time.perf_counter()-started<1200
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file());assert size<2_000_000
    assert r['workspace_free_bytes']-16_800_000-(2_000_000-size)>=8_000_000_000
    return r
guard();ip=HERE/'APPEND_INDEX.json';pp=HERE/'APPEND_PROOF.json';assert not ip.exists() and not pp.exists()
previous=ROOT/'acquisition_action_generalization_author_2026_10_09/APPEND_INDEX.json'
prevproof=previous.with_name('APPEND_PROOF.json')
assert sha(previous)=='8cfc6bc2738b05f1a530ea42af3f502c2ea9d100a54776d53d03b6a864332f52'
assert sha(prevproof)=='806dfe4a81ea42c1727cf482d4abc2cf504bcdc3c284596c07abee4801f6e018'
oldindex=read(previous);assert oldindex['complete'] and oldindex['cumulative_frozen_evidence_files']==7180
chain=oldindex['prior_chain']+[entry(previous)];old=[]
for b in chain:
    v=read(bind(b));assert v['complete'] and not v['errors'];old.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
existing={b['path']:b for b in old};assert len(old)==len(existing)==7180
for i,b in enumerate(old,1):
    bind(b)
    if i%1000==0:guard();print(json.dumps(dict(previous7180_hashes_verified=i)),flush=True)
reading=read(HERE/'READING_PROVENANCE.json');assert reading['complete'] and reading['blocks_actually_read']==330
assert reading['new_distinct_primary_maintexts_actually_read']==2 and reading['tables_text_actually_read']==22
for terminal in ['ACTUAL_ORACLE_TERMINAL_TOOL.json','ACTUAL_ORACLE_AUDIT_TERMINAL_TOOL.json','ACTUAL_OPTIMIZER_TERMINAL_TOOL.json','ACTUAL_OPTIMIZER_AUDIT_TERMINAL_TOOL.json']:
    v=read(HERE/terminal);assert v['exit_code']==0 and 'session_id' not in v
assert read(HERE/'oracle_terminal_audit_attempt01/receipt.json')['complete']
assert read(HERE/'optimizer_audit_attempt01/receipt.json')['all_six_first_update_identities_verified']
prep=ROOT/'six_resolution_training_preparation_2026_10_09'
assert not read(prep/'preflight_attempt01/receipt.json')['ready']
assert not (prep/'training_attempt01').exists()
assert read(prep/'ACTUAL_UNREADY_LAUNCH_REFUSAL.json')['expected_refusal']
sources={p for folder in [HERE,prep] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [ip,pp]}
sources.update(p for p in previous.parent.iterdir() if p.is_file());sources.add(prevproof)
pending=set(sources);scanned=set();n_bind=n_link=0;live_links=[]
opaque={ROOT/b['path'] for b in chain}|{prevproof}
while pending:
    p=sorted(pending)[0];pending.remove(p)
    if p in scanned:continue
    scanned.add(p);assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_relative_to(LIVE)
    if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
    if p.suffix=='.json':
        for b in bindings(read(p)):
            target=(ROOT/b['path']).resolve();assert not target.is_relative_to(LIVE)
            target=bind(b);n_bind+=1
            if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
    elif p.suffix=='.md':
        for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if re.match(r'https?://|app://',raw):continue
            target=Path(raw.strip('<>').split('#',1)[0])
            if not target.is_absolute():target=p.parent/target
            target=target.resolve();assert target.exists() and target.is_relative_to(ROOT),raw
            if target.is_relative_to(LIVE):live_links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()));continue
            if target.is_file() and target not in sources:sources.add(target);pending.add(target)
            n_link+=1
    guard()
new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
for b in new:bind(b)
result=dict(complete=True,errors=[],created_utc=datetime.now(timezone.utc).isoformat(),
    index_kind='two_primary_oracle_bound_first_GPU_AdamW_updates_and_guarded_six_arm_preparation_after7180',
    prior_chain=chain,previous7180_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
    cumulative_frozen_evidence_files=7180+len(new),source_binding_checks=n_bind,local_link_checks=n_link,
    live_link_targets_excluded=live_links,live_full35904_outputs_excluded=True,
    new_primary_maintexts=2,extracted_text_blocks=330,tables_text=22,author_text_files_read=21,author_text_lines_read=631,
    first_step_development_GPU_updates=6,full35904_qualification_passed=False,six_branch_training_ready=False,
    medical_claim_independently_confirmed=False,confirmation_patients_opened=False,lockedIXI_opened=False,
    publication_claim_confirmed=False,goal_status='active')
estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+20_000<2_000_000
dump(ip,result)
for b in new:bind(b)
proof=dict(complete=True,errors=[],append_index=entry(ip),previous7180_frozen_hashes_verified=True,
    new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=7180+len(new),
    live_full35904_outputs_excluded=True,training_ready=False,publication_claim_confirmed=False,goal_status='active',
    resources=guard(),elapsed_seconds=time.perf_counter()-started)
dump(pp,proof);print(json.dumps(proof),flush=True)
