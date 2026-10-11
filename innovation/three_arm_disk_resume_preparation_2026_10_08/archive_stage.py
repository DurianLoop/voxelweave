"""Append only after full prior archive and new execution scope verification."""
import json,re,sys,time
from pathlib import Path
import disk_resume_core as core
PREVIOUS=core.ROOT/'mri_joint_static_controls_prior_art_2026_10_08'
PRIOR=PREVIOUS/'ARCHIVE_MANIFEST.json'; PRIOR_PROOF=PREVIOUS/'ARCHIVE_PROOF.json'
DEST=core.HERE/'ARCHIVE_MANIFEST.json'; PROOF=core.HERE/'ARCHIVE_PROOF.json'
def main():
    sys.stdout.reconfigure(encoding='utf-8'); start=time.perf_counter()
    assert not DEST.exists() and not PROOF.exists(); core.guard(start,600,3_000_000)
    previous=core.read(PRIOR); proof=core.read(PRIOR_PROOF)
    assert previous['complete'] and proof['complete'] and not previous['errors'] and not proof['errors']
    assert core.sha(PRIOR)==proof['manifest_sha256'] and len(previous['evidence_files'])==4397
    for i,b in enumerate(previous['evidence_files'],1):
        p=core.ROOT/b['path']; assert p.stat().st_size==b['bytes'] and core.sha(p)==b['sha256'],b['path']
        if i%1000==0: print(json.dumps(dict(prior_hashes_verified=i)),flush=True); core.guard(start,600)
    stage={p for p in core.HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage) and sum(p.stat().st_size for p in stage)<197_000_000
    existing={b['path']:b for b in previous['evidence_files']}
    assert not any(p.relative_to(core.ROOT).as_posix() in existing for p in stage)
    post={PREVIOUS/'record_post_archive.py',PREVIOUS/'POST_ARCHIVE_OBSERVATIONS.json'}
    more=stage|post|{PRIOR,PRIOR_PROOF}; verified=[]; links=[]
    for p in sorted(stage|post):
        if p.suffix=='.json':
            q=core.read(p)
            if isinstance(q,dict):
                bindings=q.get('source_bindings',[])+q.get('output_bindings',[])
                core.verify_bindings(bindings)
                for b in bindings: more.add((core.ROOT/b['path']).resolve()); verified.append(dict(document=p.relative_to(core.ROOT).as_posix(),**b))
        if p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                raw=target.strip('<>').split('#',1)[0]
                if re.match(r'https?://|app://',raw): continue
                t=(Path(raw) if re.match(r'^[A-Za-z]:[/\\]',raw) else p.parent/raw).resolve()
                assert t.exists() and t.is_relative_to(core.ROOT.resolve()),(p,target)
                if t.is_file(): more.add(t)
                links.append(dict(document=p.relative_to(core.ROOT).as_posix(),target=t.relative_to(core.ROOT).as_posix()))
    ledger=core.read(core.HERE/'EXECUTION_LEDGER.json'); exits=core.read(core.HERE/'QUALIFICATION_OBSERVED_EXITS.json')
    assert ledger['complete'] and not ledger['errors'] and exits['complete'] and not exits['errors']
    assert ledger['synthetic_neural_forwards']==ledger['actual_synthetic_updates']==16 and ledger['synthetic_checkpoint_arrays_loaded_from_disk']==12
    assert exits['qualification_observed_tool_exit']==exits['verifier_observed_tool_exit']==0
    assert exits['failed_qualification_observed_tool_exit']==1 and ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert all(ledger[k]==0 for k in ('medical_arrays_loaded','old_checkpoint_arrays_loaded','MRI_neural_forwards','GPU_forwards',
        'real_medical_resource_updates','real_medical_formal_training_updates','head_fits','new_final_action_labels_generated','new_primary_papers_read','new_agents_delegated'))
    for b in ledger['root_files_observed']: assert core.sha(b['path'])==b['sha256']==b['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more), 'Live original training paths must not be frozen'
    additions=[]
    for p in sorted(more):
        key=p.relative_to(core.ROOT).as_posix()
        if key not in existing: b=core.entry(p); existing[key]=b; additions.append(b)
    newbytes=sum(b['bytes'] for b in additions); assert newbytes<200_000_000
    q=dict(created_utc=core.now(),complete=True,errors=[],source_bindings=[core.entry(p) for p in (Path(__file__),PRIOR,PRIOR_PROOF,core.HERE/'EXECUTION_LEDGER.json')],
        previous_frozen_evidence_files_verified=4397,prior_manifest_sha256=core.sha(PRIOR),
        stage_files=[core.entry(p) for p in sorted(stage)],stage_bytes=sum(p.stat().st_size for p in stage),
        new_evidence_files=additions,new_evidence_bytes=newbytes,evidence_files=[existing[k] for k in sorted(existing)],
        source_bindings_verified=verified,local_links_verified=links,previous_post_appendices_incorporated=True,live_training_files_excluded=True,
        synthetic_updates=16,synthetic_neural_forwards=16,synthetic_checkpoint_arrays_loaded_from_disk=12,
        medical_arrays_loaded=0,MRI_neural_forwards=0,GPU_forwards=0,real_medical_training_updates=0,new_primary_papers_read=0,
        actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',
        excluded_previous_retained_temporary_directories=previous['excluded_previous_retained_temporary_directories'])
    core.new_json(DEST,q)
    for b in additions:
        p=core.ROOT/b['path']; assert p.stat().st_size==b['bytes'] and core.sha(p)==b['sha256']
    core.guard(start,600)
    q=dict(created_utc=core.now(),complete=True,errors=[],manifest=DEST.relative_to(core.ROOT).as_posix(),manifest_sha256=core.sha(DEST),
        previous4397_evidence_hashes_unchanged=True,all_new_evidence_hashes_verified=True,all_source_bindings_verified=True,all_local_links_verified=True,
        stage_files=len(stage),stage_bytes=sum(p.stat().st_size for p in stage),newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(existing),original_terminal_training_not_modified=True,automatic_approval_review_rejections_received=0,
        synthetic_updates=16,synthetic_neural_forwards=16,medical_arrays_loaded=0,MRI_neural_forwards=0,GPU_forwards=0,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-start)
    core.new_json(PROOF,q)
    print(json.dumps({k:q[k] for k in ('complete','stage_files','stage_bytes','newly_bound_files','new_evidence_bytes','cumulative_frozen_evidence_files',
          'previous4397_evidence_hashes_unchanged','all_source_bindings_verified','all_local_links_verified','elapsed_seconds')},ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
