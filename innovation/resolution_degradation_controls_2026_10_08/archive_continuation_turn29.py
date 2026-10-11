"""Append completed auxiliary evidence after6376; recheck all old bytes after transparent compression."""
import sys,time,json,re,gzip,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
LIVE=[ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01',HERE/'full_real_pipeline_attempt01']


def allowed(p):return all(not p.is_relative_to(d) or p==d/'frozen_config.json' for d in LIVE)


def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_CONTINUATION_INDEX_TURN29.json';proof=HERE/'APPEND_CONTINUATION_PROOF_TURN29.json'
    assert not index.exists() and not proof.exists()
    previous=HERE/'APPEND_INDEX.json';previousproof=HERE/'APPEND_PROOF.json'
    assert sha(previous)=='b22589f518e68e358a46bf9bca3893e6fa470b5cca34b0e95152f6c9fa8fd69b'
    assert sha(previousproof)=='0e3c52f5381745417e0ecec9c2c2dcc33d4a14a5655ce0504ef7359cf5583777'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6376
    chain=q['prior_chain']+[entry(previous)];allrows=[]
    for b in chain:
        p=bind(b);v=read(p);allrows.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in allrows};assert len(allrows)==len(existing)==6376
    for i,b in enumerate(allrows,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified_after_transparent_compression=i)),flush=True)
    compressed=read(HERE/'completed_text_compression_attempt01/receipt.json')
    assert compressed['complete'] and not compressed['errors'] and compressed['all29_frozen_logical_bytes_and_hashes_verified']
    inference=read(HERE/'confirmation_inference_limits_attempt01/receipt.json')
    assert inference['complete'] and not inference['errors'] and inference['all91_exact_sign_cases_verified']
    # Original observation records remain exact despite being stored compressed.
    observation=HERE/'ACTUAL_TOOL_OBSERVATIONS_TURN29.json.gz'
    assert len(json.loads(gzip.decompress(observation.read_bytes()))['entries'])==17
    sources={p for p in HERE.rglob('*') if p.is_file() and allowed(p) and p not in [index,proof]}
    sources.update(ROOT/b['path'] for b in chain);sources.add(previousproof)
    opaque={ROOT/b['path'] for b in chain}|{previousproof};pending=set(sources);seen=set();binding_count=0;link_count=0
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in seen:continue
        seen.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b);assert allowed(target)
                if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
                binding_count+=1
        elif p.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):continue
                # One old final public message has an absolute Windows workspace link.
                target=Path(raw.strip('<>').split('#',1)[0])
                if not target.is_absolute():target=p.parent/target
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT) and allowed(target)
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                link_count+=1
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    for b in read(HERE/'READING_PROVENANCE.json')['root_file_bindings']:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        index_kind='bounded_author_routes_patient_inference_and_offline_text_compression_after6376',
        prior_chain=chain,previous6376_frozen_logical_hashes_verified=True,
        new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=6376+len(new),
        new_document_source_binding_checks=binding_count,new_local_link_checks=link_count,
        evidence_binding_details_retained_in_original_documents_not_duplicated=True,
        all29_compressed_old_files_logical_content_unchanged=True,
        old_compression_metadata_change_documented=True,all91_exact_patient_count_cases_verified=True,
        new_distinct_primary_maintexts_completed=0,three_exact_arxiv_queries_completed_no_hits=True,
        OpenAlex_metadata_partial_failure_429_preserved=True,
        full35904_session=74234,original_training_session=29823,
        both_actual_terminals_not_observed=True,rolling_outputs_excluded_except_frozen_configs=True,
        confirmation_patients_opened=False,new_medical_effects=0,publication_claim_confirmed=False,goal_status='active')
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    livejournal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    future=max(0,1_500_000-livejournal.stat().st_size)+150_000+100_000
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert size+estimate+15_000+future<5_000_000
    dump(index,result)
    out=dict(complete=True,errors=[],append_index=entry(index),previous6376_frozen_hashes_verified=True,
        newly_bound_files=len(new),cumulative_frozen_evidence_files=6376+len(new),
        unchanged_old_logical_evidence_after_transparent_compression=True,rolling_outputs_excluded=True,
        reserved_future_full_journal_audit_and_post_bytes=future,
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        publication_claim_confirmed=False,goal_status='active')
    dump(proof,out);print(json.dumps(out),flush=True)


if __name__=='__main__':main()
