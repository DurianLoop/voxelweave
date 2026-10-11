"""Verify immutable previous evidence and append the completed primary-reading stage."""
import sys,json,time,hashlib,re,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;PREVIOUS=ROOT/'author_implementation_and_sampling_prior_art_2026_10_08'
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
DEST=HERE/'ARCHIVE_MANIFEST.json';PROOF=HERE/'ARCHIVE_PROOF.json'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8');client.resource_guard();tick=time.perf_counter()
    assert not DEST.exists() and not PROOF.exists() and shutil.disk_usage(ROOT).free>=8_005_000_000
    previous_manifest=PREVIOUS/'ARCHIVE_MANIFEST.json';previous_proof=PREVIOUS/'ARCHIVE_PROOF.json'
    before=read(previous_manifest);proof=read(previous_proof)
    assert before['complete'] and proof['complete'] and not before['errors'] and not proof['errors']
    assert sha(previous_manifest)==proof['manifest_sha256']=='3a852dc77705e915296ac7cd560dbab9086d958bb7e950ce1f8c2ed8c8bbf1ed'
    assert sha(previous_proof)=='bb14d974a592951e0b2ab26886160d02a95d8546daa899420d460654fbc25226'
    assert len(before['evidence_files'])==5191
    for i,b in enumerate(before['evidence_files'],1):
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],b['path']
        if i%1000==0:print(json.dumps(dict(prior_hashes_verified=i)),flush=True);client.resource_guard()
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<30_000_000
    more=stage|{previous_manifest,previous_proof}|{PREVIOUS/n for n in ('record_post_archive.py','POST_ARCHIVE_INPUT.json','POST_ARCHIVE_OBSERVATIONS.json')}
    bindings=[];links=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            q=read(p)
            if isinstance(q,dict):
                for b in q.get('source_bindings',[])+q.get('output_bindings',[]):
                    target=(ROOT/b['path']).resolve();assert target.is_relative_to(ROOT.resolve()) and target.is_file()
                    assert sha(target)==b['sha256'] and ('bytes' not in b or target.stat().st_size==b['bytes']),(p,b)
                    more.add(target);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for rawtarget in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                raw=rawtarget.strip('<>').split('#',1)[0]
                if re.match(r'https?://|app://',raw):continue
                target=(Path(raw) if re.match(r'^[A-Za-z]:[/\\]',raw) else p.parent/raw).resolve()
                assert target.exists() and target.is_relative_to(ROOT.resolve()),(p,rawtarget)
                if target.is_file():more.add(target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
    ledger=read(HERE/'EXECUTION_LEDGER.json');reading=read(HERE/'READING_PROVENANCE.json');audit=read(HERE/'cpu_audit_attempt01/receipt.json')
    for q in (ledger,reading,audit):assert q['complete'] and not q['errors']
    counts=dict(new_primary_papers_read=2,new_full_text_pages_read=32,visual_pages_reviewed=19,public_table_rows_checked=39)
    assert all(ledger[k]==reading[k]==v for k,v in counts.items())
    assert audit['rows_checked']==39 and audit['all39_transcribed_rows_match_actual_extracted_text']
    assert ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert all(ledger[k]==0 for k in ('medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards','MRI_neural_forwards',
        'GPU_forwards','real_medical_training_updates','head_fits','new_action_labels_generated','new_agents_delegated'))
    for b in ledger['root_files_observed']:assert sha(Path(b['path']))==b['sha256']==b['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    existing={b['path']:b for b in before['evidence_files']};additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in existing:b=entry(p);existing[key]=b;additions.append(b)
    newbytes=sum(b['bytes'] for b in additions);assert newbytes<35_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**counts,
        source_bindings=[entry(p) for p in (Path(__file__),previous_manifest,previous_proof,HERE/'EXECUTION_LEDGER.json')],
        previous_frozen_evidence_files_verified=5191,prior_manifest_sha256=sha(previous_manifest),
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,new_evidence_files=additions,new_evidence_bytes=newbytes,
        evidence_files=[existing[k] for k in sorted(existing)],source_bindings_verified=bindings,local_links_verified=links,
        previous_post_appendices_incorporated=True,live_training_files_excluded=True,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        publication_claim_confirmed=False,goal_status='active',excluded_previous_retained_temporary_directories=before['excluded_previous_retained_temporary_directories'])
    client.base.new(DEST,result)
    for b in additions:p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    client.resource_guard()
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**counts,
        manifest=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),previous5191_evidence_hashes_unchanged=True,
        all_new_evidence_hashes_verified=True,all_source_bindings_verified=True,all_local_links_verified=True,
        stage_files=len(stage),stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(existing),original_terminal_training_not_modified=True,
        automatic_approval_review_rejections_received=0,publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    client.base.new(PROOF,output);print(json.dumps(output,ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
