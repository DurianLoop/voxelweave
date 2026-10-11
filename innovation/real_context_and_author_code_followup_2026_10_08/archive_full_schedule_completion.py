"""6293 delta: freeze formerly live geometry only after real complete qualification/audit."""
import sys,time,json,re,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
LIVE=ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01'
def allowed(p):return not p.is_relative_to(LIVE) or p==LIVE/'frozen_config.json'

def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard();started=time.perf_counter()
    index=HERE/'APPEND_FULL_SCHEDULE_INDEX.json';proof=HERE/'APPEND_FULL_SCHEDULE_PROOF.json'
    assert not index.exists() and not proof.exists()
    previous=HERE/'APPEND_INDEX.json';previousproof=HERE/'APPEND_PROOF.json'
    assert sha(previous)=='4674cffe9b66e6a41707c3acf83ae5b9a7df70549c7df71d0eebc1ca2d4135b5'
    assert sha(previousproof)=='2cca61ee4e1bab5c49a5172dfb57dd5f009dac58ff361e1acb953872d8c87826'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6293
    chain=q['prior_chain']+[entry(previous)];prior=[]
    for b in chain:
        p=bind(b);v=read(p);assert v['complete'] and not v['errors']
        prior.extend(v['evidence_files'] if 'evidence_files' in v else v['new_evidence_files'])
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6293
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_hashes_verified=i)),flush=True)
    completion=read(HERE/'FULL_SCHEDULE_COMPLETION_PROVENANCE.json')
    assert completion['complete'] and not completion['errors'] and completion['all5984_geometry_targets_verified']
    assert completion['all2992_original_sampler_labels_and_geometry_matched'] and completion['new_patient_medical_effects']==0
    for b in read(HERE/'READING_PROVENANCE.json')['root_file_bindings']:bind(b)
    sources={p for p in HERE.rglob('*') if p.is_file() and allowed(p) and p not in [index,proof]}
    sources.update(ROOT/b['path'] for b in chain);pending=set(sources);scanned=set();verified=[];links=[]
    opaque_indices={ROOT/b['path'] for b in chain}|{previousproof}
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing or p in opaque_indices:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b);assert allowed(target),'Live training unexpectedly bound'
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
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='complete_geometry_and_ranker_after6293',
        prior_chain=chain,previous6293_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6293+len(new),current_source_bindings_verified=verified,local_links_verified=links,
        full_schedule_formerly_rolling_now_frozen_after_actual_exit_and_audit=True,
        training_session=29823,actual_training_terminal_observed=False,rolling_training_outputs_excluded=True,
        whole_patch_policy_only_prepared=True,new_medical_effects=0,confirmation_patients_opened=False,
        publication_claim_confirmed=False,goal_status='active')
    dump(index,result)
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],append_index=entry(index),
        previous6293_hashes_verified=True,new_evidence_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6293+len(new),full_schedule_completed_and_audited=True,training_outputs_excluded=True,
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started,publication_claim_confirmed=False,goal_status='active')
    dump(proof,out);assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<5_000_000
    print(json.dumps(out),flush=True)

if __name__=='__main__':main()
