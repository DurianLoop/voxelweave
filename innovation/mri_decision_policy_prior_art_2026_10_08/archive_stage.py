"""Append new MRI primary-reading evidence after checking the full prior archive."""
import json,re,sys,time,hashlib,ctypes,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
PREVIOUS=ROOT/'three_arm_resource_bridge_2026_10_08'
PRIOR=PREVIOUS/'ARCHIVE_MANIFEST.json';PRIOR_PROOF=PREVIOUS/'ARCHIVE_PROOF.json'
DEST=HERE/'ARCHIVE_MANIFEST.json';PROOF=HERE/'ARCHIVE_PROOF.json'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter()
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=(ctypes.c_void_p,ctypes.c_uint32);assert k.SetPriorityClass(k.GetCurrentProcess(),0x00004000)
    assert not DEST.exists() and not PROOF.exists() and shutil.disk_usage(ROOT).free>8_005_000_000
    prior=read(PRIOR);proof=read(PRIOR_PROOF)
    assert prior['complete'] and proof['complete'] and not prior['errors'] and not proof['errors']
    assert len(prior['evidence_files'])==4018 and sha(PRIOR)==proof['manifest_sha256']
    for i,v in enumerate(prior['evidence_files'],1):
        p=ROOT/v['path'];assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
        if i%1000==0:print(json.dumps(dict(previous_evidence_hashes_verified=i)),flush=True)
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in (DEST,PROOF)}
    assert not any(p.suffix=='.pyc' for p in stage)
    stagebytes=sum(p.stat().st_size for p in stage);assert stagebytes<30_000_000
    existing={v['path']:v for v in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in existing for p in stage)
    post={PREVIOUS/'POST_ARCHIVE_OBSERVATIONS.json',PREVIOUS/'record_post_archive.py'}
    more=stage|post|{PRIOR,PRIOR_PROOF};bindings=[];links=[]
    for p in sorted(stage|post):
        if p.suffix=='.json':
            data=read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[])+data.get('output_bindings',[]):
                    target=(ROOT/b['path']).resolve();assert target.is_file() and target.is_relative_to(ROOT.resolve())
                    assert sha(target)==b['sha256'],(p,b)
                    if 'bytes' in b:assert target.stat().st_size==b['bytes']
                    more.add(target);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                raw=target.split('#',1)[0];q=(Path(raw) if re.match(r'^[A-Za-z]:[/\\]',raw) else p.parent/raw).resolve()
                assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                if q.is_file():more.add(q)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
    ledger=read(HERE/'EXECUTION_LEDGER.json');provenance=read(HERE/'READING_PROVENANCE.json')
    audit=read(HERE/'table_audit_attempt01/receipt.json')
    for d in (ledger,provenance,audit):assert d['complete'] and not d['errors']
    assert ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    assert ledger['new_primary_papers_read']==provenance['new_primary_papers_read']==2
    assert ledger['new_full_text_pages_read']==provenance['new_full_text_pages_read']==33
    assert ledger['visual_pages_reviewed']==provenance['visual_pages_reviewed']==11
    assert ledger['index_abstracts_screened']==24 and len(audit['comparisons'])==6
    assert all(ledger[v]==0 for v in ('medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk',
        'neural_forwards','MRI_neural_forwards','GPU_forwards','real_medical_resource_updates',
        'real_medical_formal_training_updates','head_fits','new_final_action_labels_generated','new_agents_delegated'))
    for b in ledger['root_files_observed']:assert sha(Path(b['path']))==b['sha256']==b['previous_sha256']
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    additions=[]
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in existing:
            v=entry(p);existing[key]=v;additions.append(v)
    newbytes=sum(v['bytes'] for v in additions);assert newbytes<32_000_000
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(PRIOR),entry(PRIOR_PROOF),entry(HERE/'EXECUTION_LEDGER.json')],
        previous_frozen_evidence_files_verified=4018,prior_manifest_sha256=sha(PRIOR),
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,new_evidence_files=additions,new_evidence_bytes=newbytes,
        evidence_files=[existing[k] for k in sorted(existing)],source_bindings_verified=bindings,local_links_verified=links,
        previous_post_appendices_incorporated=True,live_training_files_excluded=True,
        new_primary_papers_read=2,new_full_text_pages_read=33,visual_pages_reviewed=11,index_abstracts_screened=24,
        medical_arrays_loaded=0,neural_forwards=0,MRI_neural_forwards=0,GPU_forwards=0,real_medical_training_updates=0,
        actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,final_original_training_tool_exit=None,
        publication_claim_confirmed=False,goal_status='active',
        excluded_previous_retained_temporary_directories=prior['excluded_previous_retained_temporary_directories'])
    new(DEST,result)
    for v in additions:assert (ROOT/v['path']).stat().st_size==v['bytes'] and sha(ROOT/v['path'])==v['sha256']
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest=DEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(DEST),previous4018_evidence_hashes_unchanged=True,all_new_evidence_hashes_verified=True,
        all_source_bindings_verified=True,all_local_links_verified=True,stage_files=len(stage),stage_bytes=stagebytes,
        newly_bound_files=len(additions),new_evidence_bytes=newbytes,cumulative_frozen_evidence_files=len(existing),
        original_terminal_training_not_modified=True,automatic_approval_review_rejections_received=0,
        new_primary_papers_read=2,new_full_text_pages_read=33,visual_pages_reviewed=11,
        publication_claim_confirmed=False,goal_status='active',elapsed_seconds=time.perf_counter()-tick)
    new(PROOF,output)
    print(json.dumps({v:output[v] for v in ('complete','stage_files','stage_bytes','newly_bound_files','new_evidence_bytes',
        'cumulative_frozen_evidence_files','previous4018_evidence_hashes_unchanged','all_source_bindings_verified',
        'all_local_links_verified','elapsed_seconds')},ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
