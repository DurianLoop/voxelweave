"""Append two finished primary readings and exact tables after6412; exclude live outputs."""
import sys,time,re,json,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('prior_archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
OLDER=ROOT/'resolution_degradation_controls_2026_10_08'
LIVE=[ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01',OLDER/'full_real_pipeline_attempt01']
def allowed(p):return all(not p.is_relative_to(d) or p==d/'frozen_config.json' for d in LIVE)
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    prev=OLDER/'APPEND_CONTINUATION_INDEX_TURN29.json';prevproof=OLDER/'APPEND_CONTINUATION_PROOF_TURN29.json'
    assert sha(prev)=='1d44d6175613f3b681e81fe9615867211f40c97ecb330c472f9d93b2a0756353'
    assert sha(prevproof)=='3da424651ad8abac10a6c2faf7f4458358e97d14d43342627cb1c030b021da36'
    q=read(prev);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6412
    chain=q['prior_chain']+[entry(prev)];allrows=[]
    for b in chain:allrows.extend((v:=read(bind(b))).get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in allrows};assert len(allrows)==len(existing)==6412
    for i,b in enumerate(allrows,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(old_frozen_hashes_verified=i)),flush=True)
    provenance=read(HERE/'READING_PROVENANCE.json');assert provenance['complete'] and not provenance['errors']
    assert provenance['new_distinct_primary_maintexts_actually_read']==2
    audit=read(HERE/'table_audit_attempt01/receipt.json');assert audit['complete'] and not audit['errors'] and audit['weighting_formula_cases']==5456
    sources={p for folder in [HERE,OLDER] for p in folder.rglob('*') if p.is_file() and allowed(p) and p not in [index,proof]}
    sources.update(ROOT/b['path'] for b in chain);sources.add(prevproof)
    opaque={ROOT/b['path'] for b in chain}|{prevproof};pending=set(sources);seen=set();binding_count=0;link_count=0
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
                target=Path(raw.strip('<>').split('#',1)[0])
                if not target.is_absolute():target=p.parent/target
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT) and allowed(target)
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                link_count+=1
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    for b in provenance['root_file_bindings']:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='two_primary_maintexts_and_literal_table_audit_after6412',
        prior_chain=chain,previous6412_logical_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6412+len(new),new_source_binding_checks=binding_count,new_local_link_checks=link_count,
        source_binding_details_retained_in_original_documents=True,new_distinct_primary_maintexts_actually_read=2,
        completed_table_endpoint_comparisons=28,exact_formula_combinations=5456,clinical_significance_inferred=False,
        original_training_session=29823,full_real_pipeline_session=74234,both_actual_terminals_not_observed=True,
        rolling_outputs_excluded_except_frozen_configs=True,confirmation_patients_opened=False,new_patient_medical_effects=0,
        publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert sum(v.stat().st_size for v in HERE.rglob('*') if v.is_file())+estimate+15000+100000<1_200_000
    old_future=max(0,1_500_000-(OLDER/'full_real_pipeline_attempt01/fields.jsonl.gz').stat().st_size)+150_000+100_000
    assert sum(v.stat().st_size for v in OLDER.rglob('*') if v.is_file())+old_future<5_000_000
    resources=resource_guard();assert resources['workspace_free_bytes']-estimate-15000-100000-old_future-3_000_000>=8_000_000_000
    dump(index,result)
    out=dict(complete=True,errors=[],append_index=entry(index),previous6412_frozen_hashes_verified=True,new_frozen_hashes_verified=True,
        newly_bound_files=len(new),cumulative_frozen_evidence_files=6412+len(new),new_primary_maintexts=2,rolling_outputs_excluded=True,
        original_failed_routes_retained=True,new_medical_effects=0,root_files_unchanged=True,resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,
        publication_claim_confirmed=False,goal_status='active')
    dump(proof,out);print(json.dumps(out),flush=True)
if __name__=='__main__':main()
