"""Append finished roundtrip reading and qualifications after 6060 immutable files."""
import sys,time,re,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
LIVE=ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01'
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard

def allowed(p):return not p.is_relative_to(LIVE) or p==LIVE/'frozen_config.json'

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    previous=ROOT/'tumor_qc_strength_followup_2026_10_08/APPEND_INDEX.json'
    assert sha(previous)=='3851809bc4bb6d6a92d9da526ea699b7299c54ff315fdf6b9430e3e202fce01c'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6060
    chain=q['prior_chain']+[entry(previous)];prior=[]
    for b in chain:
        p=bind(b);v=read(p);assert v['complete'] and not v['errors']
        prior.extend(v['evidence_files'] if 'evidence_files' in v else v['new_evidence_files'])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6060
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
    rp=read(HERE/'READING_PROVENANCE.json');assert rp['complete'] and not rp['errors'] and rp['new_distinct_primary_maintexts_completed']==2
    assert rp['new_patient_medical_effects']==0 and not rp['author_code_executed']
    for rel in ['roundtrip_synthetic_attempt01/receipt.json','roundtrip_texture_attempt01/receipt.json','clinical_time_audit_attempt01/receipt.json','real_development_entry_attempt01/receipt.json']:
        v=read(HERE/rel);assert v['complete'] and not v['errors'] and not v['CUDA_initialized']
    sources={p for p in HERE.rglob('*') if p.is_file() and p not in [index,proof]}
    old=previous.parent;sources.update(p for p in old.iterdir() if p.is_file())
    sources.add(ROOT/'CURRENT_RESEARCH_STATUS_VS_ROUNDTRIP_2026-10-08.md')
    sources.update(ROOT/b['path'] for b in chain)
    pending=set(sources);scanned=set();verified=[];links=[]
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b);assert allowed(target),'Live training file unexpectedly bound'
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
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='completed_VS_roundtrip_primary_and_qualifications_after6060',
        prior_chain=chain,previous6060_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6060+len(new),current_source_bindings_verified=verified,local_links_verified=links,
        new_distinct_primary_maintexts_completed=2,nonmedical_CPU_script_executions=3,development_entry_qualified_batches=38,
        new_patient_medical_effects=0,new_validation_evaluation_executed=False,scientific_confirmation_patients=0,
        latest_pre_archive_training_tool_chunk='39ae3c',latest_pre_archive_training_branch='native_reference_spatial',
        latest_pre_archive_training_updates=22,first_branch_last_updates_observed=2992,current_training_session=29823,
        current_training_still_live_at_latest_observation=True,rolling_training_receipt_journal_and_states_excluded=True,
        only_immutable_training_config_allowed=True,root_environment_and_gitignore_unchanged=True,
        publication_claim_confirmed=False,goal_status='active')
    dump(index,r)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(index),
        previous6060_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6060+len(new),rolling_training_files_excluded=True,actual_current_training_exit_observed=False,
        new_primary_maintexts_completed=2,new_patient_medical_effects=0,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,out)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(out),flush=True)
if __name__=='__main__':main()
