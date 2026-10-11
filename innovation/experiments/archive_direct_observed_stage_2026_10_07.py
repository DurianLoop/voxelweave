"""Freeze new evidence, check all 1032 prior hashes, and exclude mutable live training."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/action_composition_stage_manifest_2026-10-07.json'
MANIFEST=ROOT/'literature/direct_observed_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_OBSERVED_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not PROOF.exists()
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000)
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1032
    for r in prior['evidence_files']:
        p=ROOT/r['path'];assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    protected={r['path'] for r in prior['evidence_files']}
    names=['MC_RC_3D_DIRECT_OBSERVED_REPRESENTATION_PROTOCOL_2026-10-07.md',
        'MC_RC_3D_DIRECT_OBSERVED_INDEPENDENT_REPLAY_PROTOCOL_2026-10-07.md','MC_RC_3D_MATCHED_OBSERVED_BASELINE_NEXT_RUN_2026-10-07.md',
        'SESSION_USER_HANDOFF_DIRECT_OBSERVED_2026-10-07.md','SESSION_VISIBLE_DIALOGUE_DIRECT_OBSERVED_2026-10-07.md',
        'SESSION_RESULT_DIRECT_OBSERVED_2026-10-07.md','SESSION_HANDOFF_DIRECT_OBSERVED_LIVE_2026-10-07.md',
        'SESSION_OBSERVED_EXITS_DIRECT_OBSERVED_2026-10-07.json','SESSION_OBSERVED_EXITS_DIRECT_OBSERVED_EVIDENCE_2026-10-07.json',
        'SESSION_EXECUTION_PROGRESS_DIRECT_OBSERVED_2026-10-07.json','SESSION_EXECUTION_LEDGER_DIRECT_OBSERVED_2026-10-07.json',
        'literature/2026-10-07_direct_observed_primary_selection.md','literature/2026-10-07_direct_observed_primary_reading.md',
        'literature/2026-10-07_sparse_dense_counterpoint_reading.md','literature/resolve_direct_observed_primary_2026_10_07.py',
        'literature/fetch_direct_observed_primary_2026_10_07.py','literature/extract_direct_observed_primary_attempt02_2026_10_07.py',
        'literature/render_direct_observed_primary_2026_10_07.py','literature/resolve_sparse_dense_counterpoint_2026_10_07.py',
        'literature/fetch_sparse_dense_counterpoint_2026_10_07.py','literature/render_sparse_dense_counterpoint_2026_10_07.py',
        'experiments/mc_rc_3d_direct_observed_2026_10_07.py','experiments/qualify_mc_rc_3d_direct_observed_2026_10_07.py',
        'experiments/verify_mc_rc_3d_direct_observed_2026_10_07.py','experiments/record_direct_observed_evidence_2026_10_07.py',
        'experiments/receipt_direct_observed_record_exit_2026_10_07.py','SESSION_FINAL_REPLY_DIRECT_OBSERVED_2026-10-07.md',
        'SESSION_VISIBLE_DIALOGUE_DIRECT_OBSERVED_ARCHIVING_2026-10-07.md']
    stage={ROOT/n for n in names}|{Path(__file__)}
    for directory in ('literature/source_cache/direct_observed_primary_2026-10-07','literature/source_cache/sparse_dense_counterpoint_2026-10-07',
                      'experiments/mc_rc_3d_direct_observed_qualification_2026_10_07','experiments/mc_rc_3d_direct_observed_independent_2026_10_07'):
        stage|={p for p in (ROOT/directory).rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT) for p in stage)
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<100_000_000
    more=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_ACTION_COMPOSITION_2026-10-07.json',
        ROOT/'SESSION_CHECKPOINT_RECEIPT_ACTION_COMPOSITION_2026-10-07.json',
        ROOT/'SESSION_FINAL_REPLY_ACTION_COMPOSITION_ACTUAL_2026-10-07.md'}
    links=[];bindings=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            data=read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[]):
                    s=ROOT/b['path'];assert s.is_file() and s.resolve().is_relative_to(ROOT) and sha(s)==b['sha256']
                    more.add(s);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                url=url.strip('<>')
                if re.match(r'https?://|app://',url):continue
                s=(p.parent/url.split('#',1)[0]).resolve();assert s.exists() and s.is_relative_to(ROOT),(p,url)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=s.relative_to(ROOT).as_posix()))
                if s.is_file():more.add(s)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    ledger=read(ROOT/'SESSION_EXECUTION_LEDGER_DIRECT_OBSERVED_2026-10-07.json')
    for e in ledger['observed_exits'].values():assert sha(ROOT/e['result']['path'])==e['result']['sha256']
    assert ledger['observed_exits']['all19_observed_and_synthetic_qualification']['observed_tool_exit']==0
    assert ledger['observed_exits']['independent_coordinates_and_functional_updates']['observed_tool_exit']==0
    progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_DIRECT_OBSERVED_2026-10-07.json')
    assert progress['own_live_runs']==[99542] and progress['full_training_observed_tool_exit'] is None
    for row in progress['root_files_observed']:assert sha(row['path'])==row['sha256']
    for paper in ledger['reading_scope']['papers']:
        assert sha(ROOT/paper['pdf']['path'])==paper['pdf']['sha256']
        for row in paper['text_page_files']:assert sha(ROOT/row['file'])==row['sha256']
    assert all(row['actual_view_image_executed'] for row in ledger['reading_scope']['actual_source_visual_reviews'])
    records={r['path']:r for r in prior['evidence_files']}
    for p in sorted(more):
        k=p.relative_to(ROOT).as_posix()
        if k not in records:records[k]=entry(p)
    stage_records=[records[p.relative_to(ROOT).as_posix()] for p in sorted(stage)]
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=1032,
        stage_files=stage_records,evidence_files=[records[k] for k in sorted(records)],stage_bytes=sum(x['bytes'] for x in stage_records),
        local_links=links,source_bindings_verified=bindings,new_primary_papers_method_results_read=3,successful_primary_PDF_pages=39,
        selected_complete_pages_actually_read=29,actual_visual_pages_reviewed=6,qualified_development_series=19,
        actual_MRI_task_effect_scores=0,new_stage_MRI_training_updates=0,new_stage_synthetic_updates=8,new_stage_GPU_forwards=0,
        own_live_runs_at_checkpoint=[99542],full_training_observed_tool_exit=None,final_execution_closed=False,
        publication_claim_confirmed=False,current_3D_lesion_confirmation_patients=0,whole_project_confirmation_zero_not_claimed=True,goal_status='active')
    new(MANIFEST,r)
    for row in read(MANIFEST)['evidence_files']:assert sha(ROOT/row['path'])==row['sha256']
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=MANIFEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(MANIFEST),stage_files=len(stage_records),evidence_files=len(records),stage_bytes=r['stage_bytes'],
        previous_frozen_evidence_files_verified=1032,own_live_runs_at_checkpoint=[99542],full_training_observed_tool_exit=None,
        final_execution_closed=False,publication_claim_confirmed=False,goal_status='active')
    new(PROOF,receipt)
    print(json.dumps(receipt,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
