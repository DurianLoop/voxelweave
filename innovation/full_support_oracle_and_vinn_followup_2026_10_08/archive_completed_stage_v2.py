"""Append completed support and two primary readings after immutable 6164 evidence files."""
import sys,time,json,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('immutable_archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(helper,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
LIVE=ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01'
def allowed(p):return not p.is_relative_to(LIVE) or p==LIVE/'frozen_config.json'
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    previous=ROOT/'resolution_and_lesion_followup_2026_10_08/APPEND_INDEX.json'
    assert sha(previous)=='9e305e8909cc490ebbf32684e097819966a1917a76188362c72e9175c9afa551'
    previousproof=previous.parent/'APPEND_PROOF.json'
    assert sha(previousproof)=='5bb3eeada2792af8c2f2d39e6acfd95f9beafe29abfc565ff78f71bce24336db'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6164
    chain=q['prior_chain']+[entry(previous)];prior=[]
    for b in chain:
        p=bind(b);v=read(p);assert v['complete'] and not v['errors']
        prior.extend(v['evidence_files'] if 'evidence_files' in v else v['new_evidence_files'])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6164
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
    rp=read(HERE/'READING_PROVENANCE.json');assert rp['complete'] and not rp['errors'] and rp['new_distinct_primary_maintexts_completed']==2
    assert rp['new_patient_medical_effects']==0 and not rp['author_implementation_executed']
    for b in rp['root_file_bindings']:bind(b)
    for rel in ['full_support_attempt02/receipt.json','development_label_support_attempt01/receipt.json','normalization_support_attempt01/receipt.json']:
        v=read(HERE/rel);assert v['complete'] and not v['errors']
    assert not read(HERE/'full_support_attempt01/receipt.json')['complete']
    sources={p for p in HERE.rglob('*') if p.is_file() and p not in [index,proof]}
    sources.update(p for p in previous.parent.iterdir() if p.is_file())
    sources.update(ROOT/b['path'] for b in chain)
    pending=set(sources);scanned=set();verified=[];links=[]
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing:continue
        known_failed_response=HERE/'author_sources_attempt01/lesion_ensemble_bioc.json'
        if p==known_failed_response:
            assert sha(p)=='478f38e0765ee9c406831bb2fc27e8019ac5227c20c6b28ca0de582d8449354a'
            assert p.read_text(encoding='utf-8').startswith('[Error] : No result can be found')
            continue
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
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='completed_full_support_two_primaries_after6164',
        prior_chain=chain,previous6164_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6164+len(new),current_source_bindings_verified=verified,local_links_verified=links,
        new_distinct_primary_maintexts_completed=2,distinct_development_geometry_target_voxels=39845888,
        old_two_path_support_fields=76,new_unpadded_domain_fields=38,development_labels_loaded=19,normalization_synthetic_cases=2,
        new_patient_medical_effects=0,new_validation_evaluation_executed=False,scientific_confirmation_patients=0,
        current_training_session=29823,current_training_still_live_at_latest_observation=True,actual_current_training_exit_observed=False,
        rolling_training_receipt_journal_and_states_excluded=True,only_immutable_training_config_allowed=True,
        root_environment_and_gitignore_unchanged=True,publication_claim_confirmed=False,goal_status='active')
    dump(index,r)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(index),
        previous6164_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6164+len(new),rolling_training_files_excluded=True,actual_current_training_exit_observed=False,
        new_primary_maintexts_completed=2,new_patient_medical_effects=0,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,out)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(out),flush=True)
if __name__=='__main__':main()
