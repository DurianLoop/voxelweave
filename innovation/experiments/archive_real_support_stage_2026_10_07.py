"""Freeze new real-support stage and verify previous1431 without live-file reads."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/patient_baseline_stage_manifest_2026-10-07.json'
DEST=ROOT/'literature/real_support_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_REAL_SUPPORT_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,r):
    with p.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not DEST.exists() and not PROOF.exists()
    k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    assert k.SetPriorityClass(k.GetCurrentProcess(),0x4000)
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1431
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.is_file() and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    ledgerfile=ROOT/'SESSION_EXECUTION_LEDGER_REAL_SUPPORT_2026-10-07.json';ledger=read(ledgerfile)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    receipt=ROOT/'SESSION_OBSERVED_EXITS_REAL_SUPPORT_RECORD_2026-10-07.json'
    new(receipt,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],metadata_record_observed_tool_chunk='1e835b',
        metadata_record_observed_tool_exit=0,result=entry(ledgerfile)))
    names=['MC_RC_REAL_SUPPORT_CACHE_DIAGNOSTIC_PROTOCOL_2026-10-07.md','MC_RC_REAL_SUPPORT_CACHE_DIAGNOSTIC_RESULT_2026-10-07.md',
        'REAL_SUPPORT_TO_OBSERVED_TASK_FOLLOWUP_2026-10-07.md','SESSION_IMPORTED_HANDOFF_REAL_SUPPORT_VERBATIM_2026-10-07.md',
        'SESSION_VISIBLE_DIALOGUE_REAL_SUPPORT_2026-10-07.md','SESSION_RESULT_REAL_SUPPORT_2026-10-07.md','SESSION_HANDOFF_REAL_SUPPORT_LIVE_2026-10-07.md',
        'SESSION_FINAL_REPLY_REAL_SUPPORT_ACTUAL_2026-10-07.md','SESSION_TOOL_OBSERVATIONS_REAL_SUPPORT_2026-10-07.json',
        'SESSION_EXECUTION_LEDGER_REAL_SUPPORT_2026-10-07.json','SESSION_OBSERVED_EXITS_REAL_SUPPORT_RECORD_2026-10-07.json',
        'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07.py','experiments/verify_mc_rc_real_support_cache_diagnostic_2026_10_07.py',
        'experiments/record_real_support_stage_evidence_2026_10_07.py','literature/2026-10-07_spatial_compute_primary_protocol.md',
        'literature/2026-10-07_spatial_compute_sbnet_selection_addendum.md','literature/2026-10-07_spatial_compute_primary_reading.md',
        'literature/spatial_compute_reading_provenance_2026-10-07.json','literature/fetch_spatial_compute_primary_2026_10_07.py',
        'literature/fetch_spatial_compute_sbnet_2026_10_07.py']
    stage={ROOT/x for x in names}|{Path(__file__)}
    for folder in ['experiments/mc_rc_real_support_cache_diagnostic_2026_10_07',
        'literature/source_cache/spatial_compute_primary_2026-10-07','literature/source_cache/spatial_compute_sbnet_2026-10-07']:
        stage|={p for p in (ROOT/folder).rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT.resolve()) for p in stage)
    protected={v['path'] for v in prior['evidence_files']};assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<100_000_000
    more=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_PATIENT_BASELINE_2026-10-07.json',
        ROOT/'SESSION_POST_ARCHIVE_PATIENT_BASELINE_UPDATE_2026-10-07.md',ROOT/'SESSION_FINAL_REPLY_PATIENT_BASELINE_ACTUAL_2026-10-07.md',
        ROOT/'SESSION_CHECKPOINT_RECEIPT_PATIENT_BASELINE_2026-10-07.json',ROOT/'experiments/finalize_patient_baseline_checkpoint_2026_10_07.py'}
    bindings=[];links=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            doc=read(p)
            if isinstance(doc,dict):
                for b in doc.get('source_bindings',[]):
                    q=(ROOT/b['path']).resolve();assert q.is_file() and q.is_relative_to(ROOT.resolve()) and sha(q)==b['sha256'],(p,b)
                    more.add(q);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                q=Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else p.parent/target.split('#',1)[0]
                q=q.resolve();assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
                if q.is_file():more.add(q)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    prod=read(ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07/attempt01.json')
    check=read(ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07/independent_rational_support_attempt01.json')
    assert prod['complete'] and check['complete'] and not prod['errors'] and not check['errors']
    assert prod['development_patients']==11 and prod['development_series']==check['checked_series']==19 and prod['total_tiles']==1139
    assert check['checked_supports']==38 and check['checked_single_plane_actions']==806
    for b in prod['source_bindings']:
        snapshot=ROOT/'experiments/mc_rc_real_support_cache_diagnostic_2026_10_07'/(Path(b['path']).name+'.source_snapshot')
        assert sha(snapshot)==b['sha256']
    for s in prod['series']:assert sha(ROOT/s['label_source']['path'])==s['label_source']['sha256']
    reading=read(ROOT/'literature/spatial_compute_reading_provenance_2026-10-07.json')
    assert reading['complete'] and not reading['errors'] and reading['new_primary_papers_read']==3 and reading['physical_pages_visual_reviewed']==7
    for scope in reading['scopes']:
        for b in [scope['PDF']]+scope['page_texts']+scope['actual_visual_image_files']:assert sha(ROOT/b['path'])==b['sha256']
    assert ledger['developer_label_reads']==38 and ledger['new_MRI_pixel_arrays_loaded']==ledger['new_model_forwards']==ledger['new_GPU_forwards']==ledger['new_training_updates']==0
    assert ledger['own_live_runs']==[99542] and ledger['full_training_observed_tool_exit'] is None
    evidence={r['path']:r for r in prior['evidence_files']}
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:evidence[key]=entry(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        prior_manifest_file=PRIOR.relative_to(ROOT).as_posix(),prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=1431,
        stage_files=[entry(p) for p in sorted(stage)],evidence_files=[evidence[k] for k in sorted(evidence)],
        stage_bytes=sum(p.stat().st_size for p in stage),source_bindings_verified=bindings,local_links=links,
        new_primary_papers_read=3,main_text_pages_read=24,visual_pages_reviewed=7,developer_label_reads=38,
        checked_series=19,checked_supports=38,checked_single_plane_actions=806,
        new_MRI_pixel_arrays_loaded=0,new_model_or_GPU_forwards=0,new_training_updates=0,
        live_training_files_excluded=True,full_training_exit_not_claimed=True,publication_claim_confirmed=False,goal_status='active')
    new(DEST,result)
    for b in read(DEST)['evidence_files']:
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    new(PROOF,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=DEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(DEST),stage_files_frozen=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],
        previous1431_evidence_hashes_unchanged=True,all_final_evidence_hashes_verified=True,live_training_files_excluded=True,
        full_training_observed_tool_exit=None,publication_claim_confirmed=False,goal_status='active'))
    print(json.dumps(dict(complete=True,new_stage_files=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],
        previous1431_evidence_hashes_unchanged=True,new_primary_papers_read=3,developer_label_reads=38,publication_claim_confirmed=False)));return 0
if __name__=='__main__':raise SystemExit(main())
