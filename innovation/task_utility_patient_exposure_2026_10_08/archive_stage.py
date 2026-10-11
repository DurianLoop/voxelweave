"""Verify the previous frozen chain and bind this stage plus previous post appendices."""
import hashlib,json,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PRIOR=ROOT/'literature/deployment_feature_cost_stage_manifest_2026-10-08.json'
PRIOR_PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_DEPLOYMENT_FEATURE_COST_2026-10-08.json'
DEST=HERE/'ARCHIVE_MANIFEST.json'
PROOF=HERE/'ARCHIVE_PROOF.json'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1_048_576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter()
    assert not DEST.exists() and not PROOF.exists()
    prior=read(PRIOR);proof=read(PRIOR_PROOF)
    assert prior['complete'] and proof['complete'] and not prior['errors'] and not proof['errors']
    assert len(prior['evidence_files'])==3759 and sha(PRIOR)==proof['manifest_sha256']
    for index,v in enumerate(prior['evidence_files'],1):
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
        if index%1000==0:print(json.dumps(dict(previous_evidence_hashes_verified=index)),flush=True)
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<30_000_000
    existing={v['path']:v for v in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in existing for p in stage)
    post=['SESSION_FINAL_TOOL_OBSERVATIONS_DEPLOYMENT_FEATURE_COST_2026-10-08.json',
        'SESSION_POST_ARCHIVE_DEPLOYMENT_FEATURE_COST_UPDATE_2026-10-08.md',
        'SESSION_CHECKPOINT_RECEIPT_DEPLOYMENT_FEATURE_COST_2026-10-08.json',
        'SESSION_OBSERVED_EXITS_FINALIZE_DEPLOYMENT_FEATURE_COST_2026-10-08.json',
        'SESSION_DELIVERY_DEPLOYMENT_FEATURE_COST_2026-10-08.md',
        'SESSION_PREPARED_FINAL_REPLY_DEPLOYMENT_FEATURE_COST_2026-10-08.md',
        'experiments/finalize_deployment_feature_cost_checkpoint_2026_10_08.py']
    more=stage|{ROOT/s for s in post}|{PRIOR,PRIOR_PROOF};bindings=[];links=[]
    for p in sorted(stage|{ROOT/s for s in post}):
        if p.suffix=='.json':
            data=read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[]):
                    q=(ROOT/b['path']).resolve();assert q.is_file() and q.is_relative_to(ROOT.resolve())
                    assert sha(q)==b['sha256'],(p,b)
                    if 'bytes' in b:assert q.stat().st_size==b['bytes']
                    more.add(q);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                raw=target.split('#',1)[0]
                q=(Path(raw) if re.match(r'^[A-Za-z]:[/\\]',raw) else p.parent/raw).resolve()
                assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                if q.is_file():more.add(q)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
    ledger=read(HERE/'EXECUTION_LEDGER.json');readproof=read(HERE/'READING_PROVENANCE.json')
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active'
    assert readproof['new_independent_primary_papers_read']==2 and readproof['new_full_text_pages_read']==28 and readproof['visual_pages_reviewed']==6
    assert ledger['metadata_negative_checks_actually_executed']==11 and ledger['independent_metadata_folds_rebuilt']==11
    assert all(ledger[k]==0 for k in ('medical_arrays_loaded','model_arrays_loaded','neural_forwards','GPU_forwards','training_updates','head_fits','actual_task_action_labels_generated'))
    for v in ledger['root_files_observed']:assert sha(Path(v['path']))==v['sha256']==v['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in existing:
            v=entry(p);existing[key]=v;additions.append(v)
    newbytes=sum(v['bytes'] for v in additions);assert newbytes<30_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(PRIOR),entry(PRIOR_PROOF),entry(HERE/'EXECUTION_LEDGER.json')],
        previous_frozen_evidence_files_verified=3759,prior_manifest_sha256=sha(PRIOR),
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,new_evidence_files=additions,new_evidence_bytes=newbytes,
        evidence_files=[existing[k] for k in sorted(existing)],source_bindings_verified=bindings,local_links_verified=links,
        previous_post_appendices_incorporated=True,live_training_files_excluded=True,
        new_primary_papers_read=2,new_full_text_pages_read=28,visual_pages_reviewed=6,
        new_medical_arrays_loaded=0,new_model_arrays_loaded=0,new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        task_action_labels_generated=0,independent_metadata_folds_verified=11,whole_pipeline_patient_out_folds=0,
        actual_MRI_task_benefit_measured=False,full_action_cost_measured=False,final_training_tool_exit=None,
        publication_claim_confirmed=False,goal_status='active',
        excluded_previous_retained_temporary_directories=prior['excluded_previous_retained_temporary_directories'])
    new(DEST,result)
    for v in additions:assert (ROOT/v['path']).stat().st_size==v['bytes'] and sha(ROOT/v['path'])==v['sha256']
    proofout=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),previous3759_evidence_hashes_unchanged=True,
        all_new_evidence_hashes_verified=True,all_source_bindings_verified=True,all_local_links_verified=True,
        stage_files=len(stage),stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(existing),elapsed_seconds=time.perf_counter()-tick,
        original_live_training_not_modified=True,automatic_approval_review_rejections_received=0,
        actual_MRI_task_benefit_measured=False,publication_claim_confirmed=False,goal_status='active')
    new(PROOF,proofout)
    print(json.dumps({k:proofout[k] for k in ('complete','stage_files','stage_bytes','newly_bound_files','new_evidence_bytes',
        'cumulative_frozen_evidence_files','previous3759_evidence_hashes_unchanged','all_source_bindings_verified','all_local_links_verified','elapsed_seconds')},ensure_ascii=False),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
