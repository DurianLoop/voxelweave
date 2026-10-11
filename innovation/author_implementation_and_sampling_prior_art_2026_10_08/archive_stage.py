"""Verify all 5112 prior hashes, then append this stage and previous post records."""
import sys,json,time,re,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
import query_author_sources as client
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
PREVIOUS=ROOT/'seranet_identity_prior_art_2026_10_08'
spec=importlib.util.spec_from_file_location('previous_archive_helpers',PREVIOUS/'archive_stage.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
sha,entry,read,new=helpers.sha,helpers.entry,helpers.read,helpers.new
DEST=HERE/'ARCHIVE_MANIFEST.json';PROOF=HERE/'ARCHIVE_PROOF.json'

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.base.own_priority();client.previous.resource_guard();tick=time.perf_counter()
    prior=PREVIOUS/'ARCHIVE_MANIFEST.json';prior_proof=PREVIOUS/'ARCHIVE_PROOF.json'
    assert not DEST.exists() and not PROOF.exists() and shutil.disk_usage(ROOT).free>=8_005_000_000
    before=read(prior);proof=read(prior_proof)
    assert before['complete'] and proof['complete'] and not before['errors'] and not proof['errors']
    assert sha(prior)==proof['manifest_sha256']=='6df11fca788455b94a47e45d56ed790e054e8e973a29e7fe015335f878d414f9'
    assert sha(prior_proof)=='32c35c59ea7673a08d0b6a3fc902a877e94feba9017a56c0b7deba97a85d35e1'
    assert len(before['evidence_files'])==5112
    for i,b in enumerate(before['evidence_files'],1):
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],b['path']
        if i%1000==0:print(json.dumps(dict(prior_hashes_verified=i)),flush=True);client.previous.resource_guard()
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<30_000_000
    more=stage|{prior,prior_proof}|{PREVIOUS/n for n in ('record_post_archive.py','POST_ARCHIVE_INPUT.json','POST_ARCHIVE_OBSERVATIONS.json')}
    bindings=[];links=[]
    for p in sorted(stage):
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
    assert ledger['new_primary_papers_read']==reading['new_primary_papers_read']==1
    assert ledger['new_full_text_pages_read']==reading['new_full_text_pages_read']==9
    assert ledger['visual_pages_reviewed']==reading['visual_pages_reviewed']==8
    assert audit['all_16_rows_match_extracted_text'] and ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert all(ledger[k]==0 for k in ('medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards',
        'MRI_neural_forwards','GPU_forwards','real_medical_training_updates','head_fits','new_action_labels_generated','new_agents_delegated'))
    for b in ledger['root_files_observed']:assert sha(Path(b['path']))==b['sha256']==b['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    existing={b['path']:b for b in before['evidence_files']};additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in existing:b=entry(p);existing[key]=b;additions.append(b)
    newbytes=sum(b['bytes'] for b in additions);assert newbytes<35_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),PREVIOUS/'archive_stage.py',prior,prior_proof,HERE/'EXECUTION_LEDGER.json')],
        previous_frozen_evidence_files_verified=5112,prior_manifest_sha256=sha(prior),
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,new_evidence_files=additions,new_evidence_bytes=newbytes,
        evidence_files=[existing[k] for k in sorted(existing)],source_bindings_verified=bindings,local_links_verified=links,
        previous_post_appendices_incorporated=True,live_training_files_excluded=True,new_primary_papers_read=1,new_full_text_pages_read=9,
        visual_pages_reviewed=8,public_table_arithmetic_complete=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        publication_claim_confirmed=False,goal_status='active',excluded_previous_retained_temporary_directories=before['excluded_previous_retained_temporary_directories'])
    new(DEST,result)
    for b in additions:p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    client.previous.resource_guard()
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest=DEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(DEST),previous5112_evidence_hashes_unchanged=True,all_new_evidence_hashes_verified=True,
        all_source_bindings_verified=True,all_local_links_verified=True,stage_files=len(stage),stage_bytes=stagebytes,
        newly_bound_files=len(additions),new_evidence_bytes=newbytes,cumulative_frozen_evidence_files=len(existing),
        new_primary_papers_read=1,new_full_text_pages_read=9,visual_pages_reviewed=8,public_table_rows_checked=16,
        original_terminal_training_not_modified=True,automatic_approval_review_rejections_received=0,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    new(PROOF,output);print(json.dumps(output,ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
