"""Freeze new reading/qualification evidence; hash prior stage once and exclude live training."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/incremental_inference_stage_manifest_2026-10-07.json'
ARCHIVE=ROOT/'SESSION_ARCHIVE_VERIFICATION_INCREMENTAL_INFERENCE_2026-10-07.json'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for data in iter(lambda:f.read(1048576),b''):h.update(data)
    return h.hexdigest()
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))

def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not ARCHIVE.exists()
    kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
    assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000)
    previous=ROOT/'literature/final_eval_preparation_stage_manifest_2026-10-07.json'
    prior=read(previous);receipt=ROOT/'SESSION_CHECKPOINT_RECEIPT_FINAL_EVAL_PREPARATION_2026-10-07.json';p=read(receipt)
    assert prior['complete'] and p['complete'] and p['preparation_archive_observed_tool_exit']==0
    assert p['manifest_sha256']==sha(previous) and p['archive_sha256']==sha(ROOT/p['archive_file'])
    for record in prior['evidence_files']:
        assert sha(ROOT/record['path'])==record['sha256'],'Frozen evidence changed: '+record['path']
    protected={r['path'] for r in prior['evidence_files']}
    stage={ROOT/name for name in (
        'MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_PROTOCOL_2026-10-07.md',
        'MC_RC_3D_LOCAL_EDIT_CACHE_QUALIFICATION_RESULT_2026-10-07.md',
        'INNOVATION_DECISION_AFTER_INCREMENTAL_INFERENCE_READING_2026-10-07.md',
        'SESSION_IMPORTED_HANDOFF_INCREMENTAL_INFERENCE_VERBATIM_2026-10-07.md',
        'SESSION_VISIBLE_DIALOGUE_INCREMENTAL_INFERENCE_2026-10-07.md',
        'SESSION_RESULT_INCREMENTAL_INFERENCE_2026-10-07.md',
        'SESSION_HANDOFF_INCREMENTAL_INFERENCE_LIVE_2026-10-07.md',
        'SESSION_EXECUTION_LEDGER_INCREMENTAL_INFERENCE_2026-10-07.json',
        'SESSION_EXECUTION_PROGRESS_INCREMENTAL_INFERENCE_2026-10-07.json',
        'literature/2026-10-07_incremental_inference_primary_reading.md',
        'literature/fetch_incremental_inference_primary_2026_10_07.py',
        'literature/fetch_deepcache_cvpr_alternate_2026_10_07.py',
        'literature/render_incremental_inference_key_pages_2026_10_07.py',
        'experiments/qualify_mc_rc_3d_local_edit_cache_2026_10_07.py',
        'experiments/plan_mc_rc_3d_local_edit_cache_development_cost_2026_10_07.py',
        'experiments/record_incremental_inference_stage_evidence_2026_10_07.py')}
    stage.add(Path(__file__))
    for name in (
        'literature/source_cache/incremental_inference_primary_2026-10-07',
        'literature/source_cache/deepcache_cvpr_alternate_2026-10-07',
        'literature/source_cache/incremental_inference_key_page_renders_2026-10-07',
        'experiments/mc_rc_3d_local_edit_cache_2026_10_07'):
        stage|={p for p in (ROOT/name).rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT) for p in stage)
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<=100_000_000
    evidence={ROOT/r['path'] for r in prior['evidence_files']}|stage|{previous,receipt,ROOT/p['archive_file']}
    links=[];bindings=[]
    for path in sorted(stage):
        if path.suffix=='.json':
            d=read(path)
            for b in d.get('source_bindings',[]):
                target=ROOT/b['path'];assert target.is_file() and sha(target)==b['sha256']
                evidence.add(target);bindings.append(dict(document=path.relative_to(ROOT).as_posix(),**b))
        elif path.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                url=url.strip('<>')
                if re.match(r'https?://|app://',url):continue
                target=(path.parent/url.split('#',1)[0]).resolve()
                assert target.exists() and target.is_relative_to(ROOT),(str(path),url)
                links.append(dict(document=path.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
                if target.is_file():evidence.add(target)
    assert not any(p.name in ('invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt',
        'native_reference_history.jsonl','raw_pchip_history.jsonl') for p in evidence)
    ledger=read(ROOT/'SESSION_EXECUTION_LEDGER_INCREMENTAL_INFERENCE_2026-10-07.json')
    progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_INCREMENTAL_INFERENCE_2026-10-07.json')
    for observation in ledger['observed_exits'].values():
        b=observation['result'];assert sha(ROOT/b['path'])==b['sha256']
    assert ledger['observed_exits']['MRI_cache_qualification']['observed_tool_exit']==0
    assert progress['own_live_runs']==[99542] and progress['last_tool_poll_observed_exit'] is None
    provenance=read(ROOT/'literature/source_cache/incremental_inference_key_page_renders_2026-10-07/reading_provenance.json')
    assert provenance['new_primary_papers_method_results_read']==3 and provenance['complete_text_pages_read']==29
    assert all(v['actual_view_image_executed'] for v in provenance['source_visual_review'])
    # Reuse already verified old entries; hash each new/linked file once.
    oldentries={r['path']:r for r in prior['evidence_files']}
    evidence_records=[oldentries.get(p.relative_to(ROOT).as_posix()) or entry(p) for p in sorted(evidence)]
    stage_records=[next(r for r in evidence_records if r['path']==p.relative_to(ROOT).as_posix()) for p in sorted(stage)]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        stage_files=stage_records,evidence_files=evidence_records,stage_bytes=sum(r['bytes'] for r in stage_records),
        previous_frozen_evidence_files_verified=len(prior['evidence_files']),prior_manifest_sha256=sha(previous),
        local_links=links,source_bindings_verified=bindings,new_primary_papers_method_results_read=3,new_abstracts_read=0,
        primary_PDF_pages_acquired=42,selected_complete_page_texts_read=29,source_visual_pages_reviewed=3,
        real_MRI_structure_qualification_passed=True,real_MRI_task_effects_scored=False,
        development_series_metadata_cost_prepared=19,actual_new_training_updates_in_stage=0,new_GPU_updates=0,
        failures_preserved=True,own_live_runs_at_checkpoint=[99542],full_training_exit=None,final_execution_closed=False,
        scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    new(MANIFEST,result)
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest_file=MANIFEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(MANIFEST),
        stage_files=len(stage_records),evidence_files=len(evidence_records),stage_bytes=result['stage_bytes'],
        previous_frozen_evidence_files_verified=len(prior['evidence_files']),own_live_runs_at_checkpoint=[99542],
        full_training_exit=None,final_execution_closed=False,scientific_confirmation_patients=0,
        publication_claim_confirmed=False,goal_status='active')
    new(ARCHIVE,proof)
    print(json.dumps({k:proof[k] for k in ('complete','stage_files','evidence_files','stage_bytes',
        'previous_frozen_evidence_files_verified','own_live_runs_at_checkpoint')}),flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
