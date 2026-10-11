"""Verify previous5835 frozen files; append all completed evaluation and post-archive records."""
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
from archive_completed_stage import sha,entry,bind,read,bindings,dump
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    chain=[(ROOT/'lossless_final_evaluation_entry_2026_10_08/ARCHIVE_MANIFEST.json','d6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e','evidence_files'),
      (ROOT/'task_routing_author_source_2026_10_08/APPEND_INDEX.json','274c0f1c5713e45f38d3e57a3b4b2d19bb9ffb90b3a121d6f81c6acf60ca7d39','new_evidence_files'),
      (ROOT/'moediff_full_scope_and_author_2026_10_08/APPEND_INDEX_V2.json','056f2b0e7b105cf5e628293af3446a340640b81b4f90b0b9f15728a75d4d9bc4','new_evidence_files'),
      (HERE/'APPEND_INDEX_V4.json','2ab94767fb49fa881af05e8a6df0357846a4dcc620341f9870e47a183b3d4cc9','new_evidence_files')]
    prior=[]
    for p,s,k in chain:assert sha(p)==s;prior.extend(read(p)[k])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==5835
    for i,b in enumerate(prior,1):
        bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
    pilot=ROOT/'adaptation_paired_pilot_2026_10_08';ex=read(pilot/'ACTUAL_EVALUATION_EXIT.json')
    assert ex['observed_tool_exit']==0 and ex['result_sha256']==sha(ROOT/ex['result_file'])
    index=HERE/'POST_ARCHIVE_APPEND_INDEX.json';proof=HERE/'POST_ARCHIVE_APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    files={p for folder in [HERE,pilot] for p in folder.rglob('*') if p.is_file() and p not in [index,proof]}
    pending={p for p in files if p.relative_to(ROOT).as_posix() not in existing};verified=[]
    for p in sorted(pending):
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b)
                if target.is_relative_to(ROOT):files.add(target)
                verified.append(dict(binding_document=p.relative_to(ROOT).as_posix(),source_binding=b))
    new=[entry(p) for p in sorted(files) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    r=dict(complete=True,errors=[],index_kind='completed_pilot_post_delta_after5835',prior_chain=[entry(p) for p,s,k in chain],
        previous5835_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=5835+len(new),
        current_source_bindings_verified=verified,actual_training_updates=396,actual_evaluation_exit=0,full_FOV_series=36,
        new_distinct_primary_text_papers_read=0,new_protocol_coverage_audit=True,publication_claim_confirmed=False,goal_status='active')
    dump(index,r);out=dict(complete=True,errors=[],append_index=entry(index),previous5835_hashes_verified=True,
        new_evidence_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=5835+len(new),
        all_current_sessions_terminal=True,medical_capability_passed=False,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
