"""Verify immutable prior5535; append finished training/evaluation/repair and reading, exclude live pilot."""
import hashlib,json,sys,time,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def bind(b):
    p=(ROOT/b['path']).resolve()
    assert p.is_relative_to(ROOT) or p in {(ROOT.parent/'.gitignore').resolve(),(ROOT.parent/'environment.yml').resolve()},b['path']
    assert p.is_file() and sha(p)==b['sha256'],b['path']
    if 'bytes' in b:assert p.stat().st_size==b['bytes'],b['path']
    return p
def bindings(v):
    if isinstance(v,dict):
        if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str):yield v
        for c in v.values():yield from bindings(c)
    elif isinstance(v,list):
        for c in v:yield from bindings(c)
def dump(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    indexpath=HERE/'APPEND_INDEX.json';proofpath=HERE/'APPEND_PROOF.json';assert not indexpath.exists() and not proofpath.exists()
    chain=[(ROOT/'lossless_final_evaluation_entry_2026_10_08/ARCHIVE_MANIFEST.json','d6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e',5430,'evidence_files'),
      (ROOT/'task_routing_author_source_2026_10_08/APPEND_INDEX.json','274c0f1c5713e45f38d3e57a3b4b2d19bb9ffb90b3a121d6f81c6acf60ca7d39',30,'new_evidence_files'),
      (ROOT/'moediff_full_scope_and_author_2026_10_08/APPEND_INDEX_V2.json','056f2b0e7b105cf5e628293af3446a340640b81b4f90b0b9f15728a75d4d9bc4',75,'new_evidence_files')]
    prior=[]
    for p,s,n,key in chain:
        assert sha(p)==s;q=read(p);assert q['complete'] and not q['errors'] and len(q[key])==n;prior.extend(q[key])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==5535
    for i,b in enumerate(prior,1):
        bind(b)
        if i%1000==0:print(json.dumps(dict(previous_hashes_verified=i)),flush=True);resource_guard()
    v4=read(HERE/'ACTUAL_PRECISION_V4_EXIT.json');assert v4['observed_tool_exit']==0
    assert v4['result_sha256']==sha(ROOT/v4['result_file']);assert v4['all_strict_numeric_gates_passed'] and not v4['medical_capability_gates_passed']
    sources={p for p in HERE.rglob('*') if p.is_file() and p not in [indexpath,proofpath]}
    completed_roots=[ROOT/'lossless_final_evaluation_entry_2026_10_08/medical_attempt03',ROOT/'training_finalization_watch_2026_10_08',
      ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07']
    for folder in completed_roots:sources.update(p for p in folder.rglob('*') if p.is_file())
    for p in (ROOT/'moediff_full_scope_and_author_2026_10_08').iterdir():
        if p.name in ['APPEND_INDEX_V2.json','APPEND_PROOF_V2.json','POST_APPEND_TOOL_OBSERVATIONS.json','NEXT_STAGE_HANDOFF.md']:sources.add(p)
    for p in (ROOT/'lossless_final_evaluation_entry_2026_10_08').iterdir():
        if p.is_file():sources.add(p)
    sources.add(ROOT/'SESSION_OBSERVED_EXITS_19SERIES_COMMON_INIT_FINAL_2026-10-07.json')
    # Only preparation files from the new pilot; its attempt01 remains live and excluded.
    pilot=ROOT/'adaptation_paired_pilot_2026_10_08'
    sources.update(p for p in pilot.iterdir() if p.is_file())
    live=pilot/'attempt01';assert not any(p.is_relative_to(live) for p in sources)
    verified=[];scanned=set();links=[]
    while True:
        pending=sorted(sources-scanned)
        if not pending:break
        for p in pending:
            scanned.add(p)
            if p.suffix=='.json':
                for b in bindings(read(p)):
                    target=bind(b)
                    if target.is_relative_to(ROOT):
                        assert not target.is_relative_to(live),'Live pilot source unexpectedly bound'
                        sources.add(target)
                    verified.append(dict(binding_document=p.relative_to(ROOT).as_posix(),source_binding=b))
            elif p.suffix=='.md':
                for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                    if re.match(r'https?://|app://',raw):continue
                    target=(p.parent/raw.split('#',1)[0]).resolve();assert target.exists() and target.is_relative_to(ROOT),raw
                    if target.is_file():sources.add(target)
                    links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
            assert time.perf_counter()-started<1200;resource_guard()
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='delta_after_prior5535',
        prior_chain=[entry(p) for p,s,n,k in chain],previous_frozen_evidence_files_verified=5535,new_evidence_files=new,
        newly_bound_files=len(new),cumulative_frozen_evidence_files=5535+len(new),source_bindings_verified=verified,local_links_verified=links,
        former_original_rolling_training_files_now_frozen_after_actual_exit=True,live_pilot_files_excluded=True,
        actual_original_training_exit=0,actual_final_medical_evaluation_exit=0,actual_old_strict_replay_exit=1,
        actual_precision_v4_exit=0,strict_numerical_passed=True,medical_capability_passed=False,
        new_distinct_primary_text_papers_read=4,publication_claim_confirmed=False,goal_status='active')
    dump(indexpath,r)
    for b in new:bind(b)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(indexpath),
        previous5535_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=5535+len(new),live_pilot_files_excluded=True,resource_snapshot=resource_guard(),
        elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
    dump(proofpath,out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
