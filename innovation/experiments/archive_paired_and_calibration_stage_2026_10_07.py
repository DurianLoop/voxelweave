"""Verify prior1130, then freeze paired and calibration evidence, excluding live state."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/direct_observed_stage_manifest_2026-10-07.json'
MANIFEST=ROOT/'literature/paired_and_calibration_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_PAIRED_AND_CALIBRATION_2026-10-07.json'
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
    kernel.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];assert kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000)
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1130
    for r in prior['evidence_files']:
        p=ROOT/r['path'];assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    protected={r['path'] for r in prior['evidence_files']}
    names=[
        'SESSION_CONTINUATION_PAIRED_SAMPLING_CONTEXT_2026-10-07.md',
        'MC_RC_3D_PAIRED_SAMPLING_FOV_PROTOCOL_2026-10-07.md','MC_RC_3D_TWO_CHANNEL_COORDINATE_DIAGNOSTIC_PROTOCOL_2026-10-07.md',
        'MC_RC_3D_PAIRED_RESOURCE_READINESS_PROTOCOL_2026-10-07.md','MC_RC_3D_PAIRED_SAMPLING_FOV_RESULT_2026-10-07.md',
        'SESSION_OBSERVED_EXITS_PAIRED_SAMPLING_FOV_2026-10-07.json',
        'experiments/mc_rc_3d_paired_sampling_fov_2026_10_07.py','experiments/qualify_mc_rc_3d_paired_sampling_fov_2026_10_07.py',
        'experiments/diagnose_mc_rc_3d_two_channel_coordinates_2026_10_07.py',
        'experiments/check_mc_rc_3d_paired_resource_readiness_2026_10_07.py','experiments/receipt_paired_sampling_fov_exits_2026_10_07.py',
        'CALIBRATED_RISK_VS_ACTION_GAIN_CPU_PROTOCOL_2026-10-07.md','CALIBRATED_RISK_VS_ACTION_GAIN_CPU_RESULT_2026-10-07.md',
        'CALIBRATION_POSITION_CPU_PROTOCOL_2026-10-07.md','CALIBRATION_AND_ACTION_GAIN_FOLLOWUP_2026-10-07.md',
        'literature/2026-10-07_calibration_selection_primary_protocol.md','literature/2026-10-07_calibration_selection_primary_reading.md',
        'literature/fetch_calibration_selection_primary_2026_10_07.py','literature/recover_calibration_selection_pmlr_attempt02_2026_10_07.py',
        'literature/render_calibration_selection_primary_2026_10_07.py',
        'experiments/audit_calibrated_risk_vs_action_gain_2026_10_07.py','experiments/verify_calibrated_risk_vs_action_gain_2026_10_07.py',
        'experiments/audit_calibration_position_2026_10_07.py','experiments/record_paired_and_calibration_evidence_2026_10_07.py',
        'experiments/receipt_paired_and_calibration_record_exit_2026_10_07.py',
        'SESSION_OBSERVED_EXITS_PAIRED_AND_CALIBRATION_RECORD_2026-10-07.json',
        'SESSION_USER_HANDOFF_PAIRED_AND_CALIBRATION_2026-10-07.md','SESSION_IMPORTED_SUMMARY_PAIRED_AND_CALIBRATION_VERBATIM_2026-10-07.md',
        'SESSION_VISIBLE_DIALOGUE_PAIRED_AND_CALIBRATION_2026-10-07.md','SESSION_VISIBLE_DIALOGUE_PAIRED_AND_CALIBRATION_ARCHIVING_2026-10-07.md',
        'SESSION_RESULT_PAIRED_AND_CALIBRATION_2026-10-07.md','SESSION_HANDOFF_PAIRED_AND_CALIBRATION_LIVE_2026-10-07.md',
        'SESSION_EXECUTION_LEDGER_PAIRED_AND_CALIBRATION_2026-10-07.json','SESSION_EXECUTION_PROGRESS_PAIRED_AND_CALIBRATION_2026-10-07.json',
        'SESSION_FINAL_REPLY_PAIRED_AND_CALIBRATION_DRAFT_2026-10-07.md']
    stage={ROOT/n for n in names}|{Path(__file__)}
    directories=[
        'experiments/mc_rc_3d_paired_sampling_fov_qualification_2026_10_07',
        'experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07',
        'experiments/mc_rc_3d_paired_resource_readiness_2026_10_07',
        'experiments/calibrated_risk_vs_action_gain_2026_10_07','experiments/calibration_position_cpu_2026_10_07',
        'literature/source_cache/calibration_selection_primary_2026-10-07',
        'literature/source_cache/calibration_selection_pmlr_attempt02_2026-10-07',
        'literature/source_cache/calibration_selection_render_2026-10-07']
    for directory in directories:
        d=ROOT/directory;assert d.is_dir();stage|={p for p in d.rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT) for p in stage)
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<100_000_000
    more=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_DIRECT_OBSERVED_2026-10-07.json',
        ROOT/'SESSION_CHECKPOINT_RECEIPT_DIRECT_OBSERVED_2026-10-07.json',
        ROOT/'SESSION_FINAL_REPLY_DIRECT_OBSERVED_ACTUAL_2026-10-07.md',
        ROOT/'experiments/finalize_direct_observed_checkpoint_receipt_2026_10_07.py'}
    links=[];bindings=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            data=read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[]):
                    s=ROOT/b['path'];assert s.is_file() and s.resolve().is_relative_to(ROOT) and sha(s)==b['sha256'],(p,b)
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
    ledger=read(ROOT/'SESSION_EXECUTION_LEDGER_PAIRED_AND_CALIBRATION_2026-10-07.json')
    for e in ledger['observed_exits'].values():assert sha(ROOT/e['result']['path'])==e['result']['sha256']
    scope=ledger['reading_scope'];assert scope['new_primary_papers_method_and_results_read']==3
    assert scope['successful_PDF_pages']==38 and scope['selected_complete_pages_actually_read']==23 and scope['actual_visual_pages_reviewed']==7
    for paper in scope['papers']:
        assert sha(ROOT/paper['pdf']['path'])==paper['pdf']['sha256']
        for t in paper['text_page_files']:assert sha(ROOT/t['file'])==t['sha256']
    assert all(v['actual_view_image_executed'] and sha(ROOT/v['file'])==v['sha256'] for v in scope['actual_source_visual_reviews'])
    progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_PAIRED_AND_CALIBRATION_2026-10-07.json')
    assert progress['own_live_runs']==[99542] and progress['full_training_observed_tool_exit'] is None
    for r in progress['root_files_observed']:assert sha(r['path'])==r['sha256']
    coord=read(ROOT/'experiments/mc_rc_3d_two_channel_coordinate_diagnostic_2026_10_07/attempt01.json')
    assert coord['all_float32_and_float64_coordinate_replays_passed'] and not coord['all_original_ideal_absolute_gates_passed']
    assert ledger['observed_exits']['inherited_readiness_exit_forwarding_failed']['observed_tool_exit']==1
    assert ledger['observed_exits']['inherited_readiness_expected_deferred']['observed_tool_exit']==3
    evidence={r['path']:r for r in prior['evidence_files']}
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:evidence[key]=entry(p)
    records=[evidence[p.relative_to(ROOT).as_posix()] for p in sorted(stage)]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        prior_manifest_file=PRIOR.relative_to(ROOT).as_posix(),prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=1130,
        stage_files=records,evidence_files=[evidence[k] for k in sorted(evidence)],stage_bytes=sum(r['bytes'] for r in records),
        local_links=links,source_bindings_verified=bindings,new_primary_papers_method_results_read=3,successful_primary_PDF_pages=38,
        selected_complete_pages_actually_read=23,actual_visual_pages_reviewed=7,
        inherited_synthetic_updates_now_archived=6,new_continuation_synthetic_training_updates=0,
        new_continuation_MRI_data_reads=0,new_continuation_MRI_forwards=0,new_continuation_GPU_forwards=0,
        original_direct_ideal_absolute_gate_still_false=True,original56FOV_code_and_gates_unchanged=True,
        own_live_runs_at_checkpoint=[99542],full_training_observed_tool_exit=None,final_execution_closed=False,
        publication_claim_confirmed=False,current_3D_lesion_confirmation_patients=0,whole_project_confirmation_zero_not_claimed=True,goal_status='active')
    new(MANIFEST,result)
    for r in read(MANIFEST)['evidence_files']:assert sha(ROOT/r['path'])==r['sha256']
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest_file=MANIFEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(MANIFEST),stage_files=len(records),
        evidence_files=len(evidence),stage_bytes=result['stage_bytes'],previous_frozen_evidence_files_verified=1130,
        own_live_runs_at_checkpoint=[99542],full_training_observed_tool_exit=None,final_execution_closed=False,
        publication_claim_confirmed=False,goal_status='active')
    new(PROOF,proof);print(json.dumps(proof));return 0
if __name__=='__main__':raise SystemExit(main())
