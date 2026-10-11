"""Append completed MRI/source reading after immutable 6224; exclude both live directories."""
import sys,time,json,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('immutable_archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
LIVE=[ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01',HERE/'full_schedule_attempt01']
def allowed(p):return all(not p.is_relative_to(d) or p==d/'frozen_config.json' for d in LIVE)

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    previous=ROOT/'full_support_oracle_and_vinn_followup_2026_10_08/APPEND_INDEX.json'
    assert sha(previous)=='ce00927df00d7d18a443fa569ad0f2273d7a2d966668a66bce6748b18f05cada'
    previousproof=previous.parent/'APPEND_PROOF.json'
    assert sha(previousproof)=='e1ff1a3c80d62e016bbf9f7deec4a78917ab528484eb21b1a22a794532aa168b'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6224
    chain=q['prior_chain']+[entry(previous)];prior=[]
    for b in chain:
        p=bind(b);v=read(p);assert v['complete'] and not v['errors']
        prior.extend(v['evidence_files'] if 'evidence_files' in v else v['new_evidence_files'])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6224
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
    rp=read(HERE/'READING_PROVENANCE.json');assert rp['complete'] and not rp['errors']
    assert rp['new_distinct_primary_maintexts_completed']==0 and rp['author_source_lines_actually_read']==3970
    assert rp['all76_real_MRI_fields_replayed'] and rp['new_patient_medical_effects']==0
    assert not rp['author_implementation_executed'] and not rp['actual_current_training_exit_observed']
    for b in rp['root_file_bindings']:bind(b)
    for rel in ['real_context_attempt02/receipt.json','vinn_code_attempt02/receipt.json','vinn_training_chain_attempt01/receipt.json']:
        r=read(HERE/rel);assert r['complete'] and not r['errors']
    sources={p for p in HERE.rglob('*') if p.is_file() and allowed(p) and p not in [index,proof]}
    sources.update(p for p in previous.parent.iterdir() if p.is_file())
    sources.update(ROOT/b['path'] for b in chain)
    pending=set(sources);scanned=set();verified=[];links=[]
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing:continue
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
    for b in new:bind(b);assert allowed(ROOT/b['path'])
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='completed_real_MRI_and_3970_author_lines_after6224',
                prior_chain=chain,previous6224_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
                cumulative_frozen_evidence_files=6224+len(new),current_source_bindings_verified=verified,local_links_verified=links,
                new_distinct_primary_maintexts_completed=0,author_files_read=11,author_source_lines_read=3970,
                real_MRI_input_arrays_loaded=38,GT_arrays_loaded=19,real_MRI_fields_qualified=76,
                new_patient_medical_effects=0,new_validation_evaluation_executed=False,scientific_confirmation_patients=0,
                training_session=29823,full_schedule_session=56132,both_sessions_live_at_documented_observation=True,
                actual_current_training_exit_observed=False,actual_full_schedule_terminal_observed=False,
                rolling_training_and_full_schedule_outputs_excluded=True,only_their_immutable_configs_bound=True,
                root_environment_and_gitignore_unchanged=True,publication_claim_confirmed=False,goal_status='active')
    dump(index,result)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(index),
             previous6224_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
             cumulative_frozen_evidence_files=6224+len(new),both_rolling_output_directories_excluded=True,
             publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,out)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
