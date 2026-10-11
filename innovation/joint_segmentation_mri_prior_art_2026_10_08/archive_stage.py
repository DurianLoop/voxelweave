"""Extend the evidence chain only after verifying all 4686 previous frozen hashes."""
import json,sys,time,hashlib,re,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
PREVIOUS=ROOT/'task_routing_and_reconstruction_shift_prior_art_2026_10_08'
PRIOR=PREVIOUS/'ARCHIVE_MANIFEST.json';PRIOR_PROOF=PREVIOUS/'ARCHIVE_PROOF.json'
DEST=HERE/'ARCHIVE_MANIFEST.json';PROOF=HERE/'ARCHIVE_PROOF.json'
sys.path.insert(0,str(ROOT/'task_adaptation_compute_prior_art_2026_10_08'))
import query_primary as base
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    sys.stdout.reconfigure(encoding='utf-8');base.own_priority();tick=time.perf_counter();resource_guard()
    assert not DEST.exists() and not PROOF.exists() and shutil.disk_usage(ROOT).free>8_005_000_000
    prior=read(PRIOR);proof=read(PRIOR_PROOF)
    assert prior['complete'] and proof['complete'] and not prior['errors'] and not proof['errors']
    assert len(prior['evidence_files'])==4686 and sha(PRIOR)==proof['manifest_sha256']
    for i,b in enumerate(prior['evidence_files'],1):
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],b['path']
        if i%1000==0:print(json.dumps(dict(prior_hashes_verified=i)),flush=True);resource_guard()
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<27_000_000
    existing={b['path']:b for b in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in existing for p in stage)
    post={PREVIOUS/name for name in ('record_post_archive.py','POST_ARCHIVE_INPUT.json','POST_ARCHIVE_OBSERVATIONS.json')}
    more=stage|post|{PRIOR,PRIOR_PROOF};bindings=[];links=[]
    for p in sorted(stage|post):
        if p.suffix=='.json':
            q=read(p)
            if isinstance(q,dict):
                for b in q.get('source_bindings',[])+q.get('output_bindings',[]):
                    t=(ROOT/b['path']).resolve();assert t.is_relative_to(ROOT.resolve()) and t.is_file()
                    assert sha(t)==b['sha256'] and ('bytes' not in b or t.stat().st_size==b['bytes']),(p,b)
                    more.add(t);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                raw=target.strip('<>').split('#',1)[0]
                if re.match(r'https?://|app://',raw):continue
                t=(Path(raw) if re.match(r'^[A-Za-z]:[/\\]',raw) else p.parent/raw).resolve()
                assert t.exists() and t.is_relative_to(ROOT.resolve()),(p,target)
                if t.is_file():more.add(t)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=t.relative_to(ROOT).as_posix()))
    ledger=read(HERE/'EXECUTION_LEDGER.json');reading=read(HERE/'READING_PROVENANCE.json');audit=read(HERE/'table_audit_attempt01/receipt.json')
    for q in (ledger,reading,audit):assert q['complete'] and not q['errors']
    assert ledger['new_primary_papers_read']==reading['new_primary_papers_read']==2
    assert ledger['new_full_text_pages_read']==reading['new_full_text_pages_read']==15
    assert ledger['visual_pages_reviewed']==reading['visual_pages_reviewed']==10
    assert ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert all(ledger[k]==0 for k in ('medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards',
       'MRI_neural_forwards','GPU_forwards','real_medical_resource_updates','real_medical_formal_training_updates',
       'head_fits','new_final_action_labels_generated','new_agents_delegated'))
    for b in ledger['root_files_observed']:assert sha(Path(b['path']))==b['sha256']==b['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in existing:b=entry(p);existing[key]=b;additions.append(b)
    newbytes=sum(b['bytes'] for b in additions);assert newbytes<32_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       source_bindings=[entry(p) for p in (Path(__file__),PRIOR,PRIOR_PROOF,HERE/'EXECUTION_LEDGER.json')],
       previous_frozen_evidence_files_verified=4686,prior_manifest_sha256=sha(PRIOR),
       stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,
       new_evidence_files=additions,new_evidence_bytes=newbytes,evidence_files=[existing[k] for k in sorted(existing)],
       source_bindings_verified=bindings,local_links_verified=links,previous_post_appendices_incorporated=True,
       live_training_files_excluded=True,new_primary_papers_read=2,new_full_text_pages_read=15,visual_pages_reviewed=10,
       medical_arrays_loaded=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,real_medical_training_updates=0,
       actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,publication_claim_confirmed=False,
       goal_status='active',excluded_previous_retained_temporary_directories=prior['excluded_previous_retained_temporary_directories'])
    base.new(DEST,result)
    for b in additions:p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    resource_guard();assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<30_000_000
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       manifest=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),previous4686_evidence_hashes_unchanged=True,
       all_new_evidence_hashes_verified=True,all_source_bindings_verified=True,all_local_links_verified=True,
       stage_files=len(stage),stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
       cumulative_frozen_evidence_files=len(existing),original_terminal_training_not_modified=True,
       automatic_approval_review_rejections_received=0,new_primary_papers_read=2,new_full_text_pages_read=15,
       visual_pages_reviewed=10,publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    base.new(PROOF,output)
    print(json.dumps({k:output[k] for k in ('complete','stage_files','stage_bytes','newly_bound_files','new_evidence_bytes',
       'cumulative_frozen_evidence_files','previous4686_evidence_hashes_unchanged','all_source_bindings_verified',
       'all_local_links_verified','elapsed_seconds')}),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())

