"""Freeze all new evidence; verify the previous1516 without live training files."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/real_support_stage_manifest_2026-10-07.json'
DEST=ROOT/'literature/observed_roi_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_OBSERVED_ROI_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def new(p,r):
    with p.open('x',encoding='utf-8') as stream:json.dump(r,stream,ensure_ascii=False,indent=2);stream.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not DEST.exists() and not PROOF.exists()
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p;kernel.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000)
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1516
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.is_file() and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    ledgerfile=ROOT/'SESSION_EXECUTION_LEDGER_OBSERVED_ROI_2026-10-07.json';ledger=read(ledgerfile)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active' and not ledger['publication_claim_confirmed']
    receipt=ROOT/'SESSION_OBSERVED_EXITS_RECORD_OBSERVED_ROI_2026-10-07.json'
    new(receipt,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],metadata_record_actual_observed_tool_chunk='3a0cb8',metadata_record_actual_observed_tool_exit=0,ledger=entry(ledgerfile)))
    names=['MC_RC_OBSERVED_ROI_CACHE_COST_PROTOCOL_2026-10-07.md','MC_RC_OBSERVED_ROI_CACHE_COST_RESULT_2026-10-07.md',
        'MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_PROTOCOL_2026-10-07.md','MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_RESULT_2026-10-07.md',
        'OBSERVED_ROI_TO_NET_BENEFIT_CLAIM_PREPARATION_2026-10-07.md','SESSION_RESULT_OBSERVED_ROI_2026-10-07.md',
        'SESSION_VISIBLE_DIALOGUE_OBSERVED_ROI_2026-10-07.md','SESSION_IMPORTED_HANDOFF_OBSERVED_ROI_2026-10-07.md',
        'SESSION_PREPARED_FINAL_REPLY_OBSERVED_ROI_2026-10-07.md','SESSION_HANDOFF_OBSERVED_ROI_LIVE_2026-10-07.md',
        'SESSION_POST_RECORD_UPDATE_OBSERVED_ROI_2026-10-07.md','SESSION_TOOL_OBSERVATIONS_OBSERVED_ROI_2026-10-07.json',
        'SESSION_EXECUTION_LEDGER_OBSERVED_ROI_2026-10-07.json','SESSION_OBSERVED_EXITS_RECORD_OBSERVED_ROI_2026-10-07.json',
        'experiments/mc_rc_observed_roi_cache_cost_2026_10_07.py','experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07.py',
        'experiments/verify_mc_rc_observed_roi_cache_cost_v2_2026_10_07.py','experiments/mc_rc_observed_roi_real_input_probe_2026_10_07.py',
        'experiments/verify_mc_rc_observed_roi_real_input_probe_2026_10_07.py','experiments/verify_mc_rc_observed_roi_real_input_probe_v2_2026_10_07.py',
        'experiments/record_observed_roi_stage_2026_10_07.py','literature/2026-10-07_temporal_cache_primary_protocol.md',
        'literature/2026-10-07_temporal_cache_primary_reading.md','literature/temporal_cache_reading_provenance_2026-10-07.json',
        'literature/fetch_temporal_cache_primary_2026_10_07.py']
    stage={ROOT/x for x in names}|{Path(__file__)}
    for folder in ['experiments/mc_rc_observed_roi_cache_cost_2026_10_07','experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07',
        'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07','literature/source_cache/temporal_cache_primary_2026-10-07']:
        stage|={p for p in (ROOT/folder).rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT.resolve()) for p in stage)
    protected={v['path'] for v in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<100_000_000
    more=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_REAL_SUPPORT_2026-10-07.json',
        ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_REAL_SUPPORT_2026-10-07.json',ROOT/'SESSION_POST_ARCHIVE_REAL_SUPPORT_UPDATE_2026-10-07.md',
        ROOT/'SESSION_CHECKPOINT_RECEIPT_REAL_SUPPORT_2026-10-07.json',ROOT/'SESSION_OBSERVED_EXITS_FINALIZE_REAL_SUPPORT_2026-10-07.json',
        ROOT/'experiments/finalize_real_support_checkpoint_2026_10_07.py'}
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
                q=(Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else p.parent/target.split('#',1)[0]).resolve()
                if q==DEST.resolve():
                    links.append(dict(document=p.relative_to(ROOT).as_posix(),target=DEST.relative_to(ROOT).as_posix(),verified_after_manifest_creation=True));continue
                assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
                if q.is_file():more.add(q)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    c=read(ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/attempt01.json')
    cp=read(ROOT/'experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/independent_disk_rational_attempt01.json')
    r=read(ROOT/'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/attempt01.json')
    rp=read(ROOT/'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/independent_real_input_replay_attempt02.json')
    assert all(d['complete'] and not d['errors'] and not d['prohibited_access_attempts'] for d in (c,cp,r,rp))
    assert cp['checked_series']==rp['checked_series']==16 and cp['checked_method_supports']==rp['checked_candidates']==64
    assert cp['checked_plane_records']==3456 and rp['checked_literal_tile_equalities']==4156
    for doc in (c,r):
        for snapshot in doc['source_snapshots']:
            b=snapshot['snapshot'];assert sha(ROOT/b['path'])==b['sha256']==sha(ROOT/snapshot['source_path'])
    for s in r['series']:
        assert sha(ROOT/s['observed_package']['path'])==s['observed_package']['sha256']
        for m in s['methods'].values():
            p=m['changed_support_package'];assert sha(ROOT/p['path'])==p['sha256']
    failed=read(ROOT/'experiments/mc_rc_observed_roi_cache_cost_2026_10_07/attempt01.json')
    assert not failed['complete'] and failed['cached_prediction_arrays_loaded']==0 and failed['errors']==['AssertionError: ']
    assert sha(ROOT/'experiments/mc_rc_observed_roi_cache_cost_2026_10_07.py')=='aa3610a8ec202ae7d777df53dbb0814ff98c6ebb16b1353848deef744eebb473'
    independent_failure=read(ROOT/'experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/independent_real_input_replay_attempt01.json')
    assert not independent_failure['complete'] and independent_failure['observed_MRI_packages_loaded']==1
    reading=read(ROOT/'literature/temporal_cache_reading_provenance_2026-10-07.json')
    assert reading['complete'] and not reading['errors'] and reading['new_primary_papers_read']==2 and reading['physical_pages_visual_reviewed']==4
    for scope in reading['scopes']:
        for b in [scope['PDF']]+scope['page_texts']+scope['actual_visual_image_files']:assert sha(ROOT/b['path'])==b['sha256']
    assert ledger['actual_observed_MRI_package_array_loads_including_failed_attempt']==33 and ledger['cached_prediction_array_loads']==256
    assert ledger['new_GT_array_loads']==ledger['new_model_forwards']==ledger['new_GPU_forwards']==ledger['new_training_updates']==0
    for v in ledger['root_files_observed']:assert sha(Path(v['path']))==v['sha256']==v['previous_sha256']
    evidence={v['path']:v for v in prior['evidence_files']}
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:evidence[key]=entry(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        prior_manifest_file=PRIOR.relative_to(ROOT).as_posix(),prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=1516,
        stage_files=[entry(p) for p in sorted(stage)],evidence_files=[evidence[k] for k in sorted(evidence)],stage_bytes=sum(p.stat().st_size for p in stage),
        source_bindings_verified=bindings,local_links=links,legacy_failed_V1_snapshot_name_collision_preserved=True,
        successful_source_snapshots_verified=True,failed_versions_preserved=True,previous_real_support_post_appendices_incorporated=True,
        new_primary_papers_read=2,main_and_selected_page_texts_read=17,visual_pages_reviewed=4,actual_observed_MRI_array_loads=33,
        checked_cost_supports=64,checked_cost_plane_records=3456,checked_real_input_candidates=64,checked_literal_tile_equalities=4156,
        new_GT_array_loads=0,new_model_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        live_training_files_excluded=True,full_training_exit_not_claimed=True,publication_claim_confirmed=False,goal_status='active')
    new(DEST,result)
    for b in read(DEST)['evidence_files']:
        p=ROOT/b['path'];assert p.stat().st_size==b['bytes'] and sha(p)==b['sha256']
    assert all((ROOT/v['target']).exists() for v in links)
    new(PROOF,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=DEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(DEST),stage_files_frozen=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],
        previous1516_evidence_hashes_unchanged=True,all_final_evidence_hashes_verified=True,live_training_files_excluded=True,
        full_training_observed_tool_exit=None,publication_claim_confirmed=False,goal_status='active'))
    print(json.dumps(dict(complete=True,new_stage_files=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],
        previous1516_evidence_hashes_unchanged=True,new_primary_papers_read=2,actual_observed_MRI_array_loads=33,goal_status='active',publication_claim_confirmed=False)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
