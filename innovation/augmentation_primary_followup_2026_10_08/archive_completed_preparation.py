"""Append completed literature/preparation after immutable5907; leave rolling training entirely out."""
import hashlib,json,re,sys,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
SPATIAL=ROOT/'spatial_adaptation_matched_2026_10_08';LIVE=SPATIAL/'training_attempt01'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard

def allowed(p):return not p.is_relative_to(LIVE) or p==LIVE/'frozen_config.json'
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    chain=[(ROOT/'lossless_final_evaluation_entry_2026_10_08/ARCHIVE_MANIFEST.json','d6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e','evidence_files',5430),
        (ROOT/'task_routing_author_source_2026_10_08/APPEND_INDEX.json','274c0f1c5713e45f38d3e57a3b4b2d19bb9ffb90b3a121d6f81c6acf60ca7d39','new_evidence_files',30),
        (ROOT/'moediff_full_scope_and_author_2026_10_08/APPEND_INDEX_V2.json','056f2b0e7b105cf5e628293af3446a340640b81b4f90b0b9f15728a75d4d9bc4','new_evidence_files',75),
        (ROOT/'final_training_medical_execution_2026_10_08/APPEND_INDEX_V4.json','2ab94767fb49fa881af05e8a6df0357846a4dcc620341f9870e47a183b3d4cc9','new_evidence_files',300),
        (ROOT/'final_training_medical_execution_2026_10_08/POST_ARCHIVE_APPEND_INDEX.json','ebb5eebb3dfb7d895fde4b4685b74d544fcf1ac74dc3f06566f583515edb96d0','new_evidence_files',72)]
    prior=[]
    for p,s,k,n in chain:
        assert sha(p)==s;q=read(p);assert q['complete'] and not q['errors'] and len(q[k])==n;prior.extend(q[k])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==5907
    for i,b in enumerate(prior,1):
        bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
    literature=read(HERE/'READING_PROVENANCE.json');assert literature['complete'] and literature['new_distinct_primary_maintexts_completed']==2
    preparation=read(SPATIAL/'ENTRY_PREPARATION_CHECK.json');assert preparation['complete'] and preparation['all_five_entry_files_compile']
    sources={p for p in HERE.rglob('*') if p.is_file() and p not in [index,proof]}
    sources.update(p for p in SPATIAL.rglob('*') if p.is_file() and allowed(p))
    final=ROOT/'final_training_medical_execution_2026_10_08'
    sources.update(p for p in final.iterdir() if p.is_file())
    # New current-state entry files and prior archive manifests/proofs are themselves append evidence.
    sources.update([p for p,s,k,n in chain])
    sources.add(ROOT/'CURRENT_RESEARCH_STATUS_SPATIAL_QC_2026-10-08.md')
    assert all(allowed(p) for p in sources)
    pending=set(sources);scanned=set();verified=[];links=[]
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b);assert allowed(target),'Rolling training was unexpectedly hash-bound'
                if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
                verified.append(dict(document=p.relative_to(ROOT).as_posix(),source_binding=b))
        elif p.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):continue
                raw=raw.strip('<>');target=(p.parent/raw.split('#',1)[0]).resolve()
                assert target.exists() and target.is_relative_to(ROOT) and allowed(target),raw
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b);assert allowed(ROOT/b['path'])
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='completed_reading_and_preparation_after5907',
        prior_chain=[entry(p) for p,s,k,n in chain],previous5907_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=5907+len(new),current_source_bindings_verified=verified,local_links_verified=links,
        new_distinct_primary_maintexts_completed=2,prepared_four_branch_final_entry=True,actual_new_final_training_exit_observed=False,
        current_training_session=29823,current_training_still_live_at_latest_tool_observation=True,
        rolling_training_receipt_and_journals_excluded=True,only_immutable_training_config_included=True,
        new_final_validation_evaluation_executed=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    dump(index,r)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(index),
        previous5907_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=5907+len(new),rolling_training_files_excluded=True,
        all_current_sessions_terminal=False,current_live_session=29823,medical_capability_passed=False,
        publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
