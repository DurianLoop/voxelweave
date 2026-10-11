"""Append after6324, preserve opaque prior indices, exclude every live output except frozen config."""
import sys,time,json,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
LIVE=[ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01',HERE/'full_real_pipeline_attempt01']


def allowed(p):
    return all(not p.is_relative_to(folder) or p==folder/'frozen_config.json' for folder in LIVE)


def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json'
    assert not index.exists() and not proof.exists()
    previousdir=ROOT/'real_context_and_author_code_followup_2026_10_08'
    previous=previousdir/'APPEND_FULL_SCHEDULE_INDEX.json';previousproof=previousdir/'APPEND_FULL_SCHEDULE_PROOF.json'
    assert sha(previous)=='a527acc5eb9dc30348a53ac40e14aa89a3469f6df9a718aa325cbeeea9463fce'
    assert sha(previousproof)=='c624330afcd33afa681533351914588045ebc406b6143598ae3c9917751ab1eb'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6324
    chain=q['prior_chain']+[entry(previous)];prior=[]
    for b in chain:
        p=bind(b);v=read(p);assert v['complete'] and not v['errors']
        prior.extend(v['evidence_files'] if 'evidence_files' in v else v['new_evidence_files'])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6324
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
        assert time.perf_counter()-started<1200
    provenance=read(HERE/'READING_PROVENANCE.json')
    assert provenance['complete'] and not provenance['errors']
    assert len(provenance['completed_checks'])==4 and provenance['new_patient_medical_effects']==0
    for b in provenance['root_file_bindings']:bind(b)
    sources={p for p in HERE.rglob('*') if p.is_file() and allowed(p) and p not in [index,proof]}
    sources.update(ROOT/b['path'] for b in chain);sources.add(previousproof)
    for name in ['POST_TOOL_OBSERVATIONS_PART05.json','FINAL_PUBLIC_RESPONSE_TURN26.md','LAST_POST_ARCHIVE_HANDOFF_TURN26.md']:
        sources.add(previousdir/name)
    pending=set(sources);scanned=set();verified=[];links=[]
    opaque_indices={ROOT/b['path'] for b in chain}|{previousproof}
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing or p in opaque_indices:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b);assert allowed(target),'Live output unexpectedly bound'
                if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
                verified.append(dict(document=p.relative_to(ROOT).as_posix(),source_binding=b))
        elif p.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):continue
                target=(p.parent/raw.strip('<>').split('#',1)[0]).resolve()
                assert target.exists() and target.is_relative_to(ROOT) and allowed(target),raw
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        index_kind='ordinary_resolution_controls_and_independent_intensity_after6324',prior_chain=chain,
        previous6324_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6324+len(new),current_source_bindings_verified=verified,
        local_links_verified=links,full35904_session=74234,full35904_actual_terminal_observed=False,
        training_session=29823,actual_training_terminal_observed=False,
        rolling_training_and_full35904_outputs_excluded=True,only_frozen_configs_allowed_from_live_roots=True,
        completed270_synthetic_and17952_metadata_and228_real_and228_composition_and40_independent_intensity=True,
        new_distinct_primary_maintexts_completed=0,new_medical_effects=0,
        confirmation_patients_opened=False,publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    size=sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())
    livejournal=HERE/'full_real_pipeline_attempt01/fields.jsonl.gz'
    future=max(0,1_500_000-livejournal.stat().st_size)+150_000+100_000
    assert size+estimate+15000+future<5_000_000,'Preserve live-journal/audit/post-receipt storage reserve'
    dump(index,result)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(index),
        previous6324_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6324+len(new),rolling_outputs_excluded=True,
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        reserved_future_full_journal_audit_and_post_bytes=future,publication_claim_confirmed=False,goal_status='active')
    dump(proof,out);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(out),flush=True)


if __name__=='__main__':main()
