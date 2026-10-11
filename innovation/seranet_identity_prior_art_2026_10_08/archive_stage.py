"""Append evidence after verifying all 4942 previous frozen files; exclude rolling training."""
import json,sys,time,hashlib,re,shutil
from pathlib import Path
from datetime import datetime,timezone
import query_seranet_stdlib_v3 as prior_client
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREVIOUS=ROOT/'recurrent_joint_mri_prior_art_2026_10_08'
PRIOR=PREVIOUS/'ARCHIVE_MANIFEST.json'
PRIOR_PROOF=PREVIOUS/'ARCHIVE_PROOF.json'
DEST=HERE/'ARCHIVE_MANIFEST.json'
PROOF=HERE/'ARCHIVE_PROOF.json'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,q):
    with p.open('x',encoding='utf-8') as f:json.dump(q,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8');prior_client.base.own_priority();prior_client.resource_guard()
    tick=time.perf_counter();assert not DEST.exists() and not PROOF.exists()
    assert shutil.disk_usage(ROOT).free>=8_005_000_000
    before=read(PRIOR);proof=read(PRIOR_PROOF)
    assert before['complete'] and proof['complete'] and not before['errors'] and not proof['errors']
    assert len(before['evidence_files'])==4942 and sha(PRIOR)==proof['manifest_sha256']
    assert sha(PRIOR)=='b6fa940613941ac14ce6786b839a75924538a296a0783d16fbbfea85e1166fdd'
    assert sha(PRIOR_PROOF)=='fe1003e24bd1685e7e0700e9d177d522c67d92be1fe47dff5aa5cf87b1356088'
    for i,b in enumerate(before['evidence_files'],1):
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256'],b['path']
        if i%1000==0:
            print(json.dumps(dict(prior_hashes_verified=i)),flush=True);prior_client.resource_guard()
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<30_000_000
    existing={b['path']:b for b in before['evidence_files']}
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
    ledger=read(HERE/'EXECUTION_LEDGER.json');reading=read(HERE/'READING_PROVENANCE.json')
    sad=read(HERE/'table_audit_attempt01/receipt.json');audit=read(HERE/'recurrent_audit_attempt02/receipt.json')
    for q in (ledger,reading,sad,audit):assert q['complete'] and not q['errors']
    assert ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert ledger['new_primary_papers_read']==reading['new_primary_papers_read']==3
    assert ledger['new_full_text_pages_read']==reading['new_full_text_pages_read']==45
    assert ledger['visual_pages_reviewed']==reading['visual_pages_reviewed']==26
    assert len(audit['SERANet_source_mean_inconsistencies'])==1
    assert not audit['SERANet_printed_means_rounding_consistent']
    assert all(ledger[k]==0 for k in ('medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards',
        'MRI_neural_forwards','GPU_forwards','real_medical_training_updates','head_fits','new_action_labels_generated','new_agents_delegated'))
    for b in ledger['root_files_observed']:assert sha(Path(b['path']))==b['sha256']==b['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in existing:
            b=entry(p);existing[key]=b;additions.append(b)
    newbytes=sum(b['bytes'] for b in additions);assert newbytes<35_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(p) for p in (Path(__file__),PRIOR,PRIOR_PROOF,HERE/'EXECUTION_LEDGER.json')],
        previous_frozen_evidence_files_verified=4942,prior_manifest_sha256=sha(PRIOR),
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,
        new_evidence_files=additions,new_evidence_bytes=newbytes,evidence_files=[existing[k] for k in sorted(existing)],
        source_bindings_verified=bindings,local_links_verified=links,previous_post_appendices_incorporated=True,
        live_training_files_excluded=True,new_primary_papers_read=3,new_full_text_pages_read=45,
        reference_only_pages_read=4,visual_pages_reviewed=26,additional_detail_images_viewed=2,
        public_table_arithmetic_complete=True,source_mean_inconsistencies_retained=1,
        all_original_printed_summaries_consistent=False,medical_arrays_loaded=0,neural_forwards=0,GPU_forwards=0,
        real_medical_training_updates=0,actual_new_MRI_task_benefit_measured=False,publication_claim_confirmed=False,
        goal_status='active',excluded_previous_retained_temporary_directories=before['excluded_previous_retained_temporary_directories'])
    new(DEST,result)
    for b in additions:
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    prior_client.resource_guard()
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),previous4942_evidence_hashes_unchanged=True,
        all_new_evidence_hashes_verified=True,all_source_bindings_verified=True,all_local_links_verified=True,
        stage_files=len(stage),stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(existing),new_primary_papers_read=3,new_full_text_pages_read=45,
        visual_pages_reviewed=26,public_table_arithmetic_complete=True,source_mean_inconsistencies_retained=1,
        original_terminal_training_not_modified=True,automatic_approval_review_rejections_received=0,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    new(PROOF,output)
    print(json.dumps(output,ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
