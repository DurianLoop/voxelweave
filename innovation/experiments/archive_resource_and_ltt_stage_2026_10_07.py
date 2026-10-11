"""Verify previous 1240 immutable evidence, then freeze selected new stage without live state."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/paired_and_calibration_stage_manifest_2026-10-07.json'
DEST=ROOT/'literature/resource_and_ltt_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_RESOURCE_AND_LTT_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as s:
        for b in iter(lambda:s.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,r):
    with p.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not DEST.exists() and not PROOF.exists()
    k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p
    k.SetPriorityClass.argtypes=[ctypes.c_void_p,ctypes.c_ulong];assert k.SetPriorityClass(k.GetCurrentProcess(),0x4000)
    receipt=ROOT/'SESSION_OBSERVED_EXITS_RESOURCE_AND_LTT_RECORD_2026-10-07.json'
    ledger=ROOT/'SESSION_EXECUTION_LEDGER_RESOURCE_AND_LTT_2026-10-07.json'
    assert read(ledger)['complete']
    new(receipt,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        metadata_record_observed_tool_exit=0,metadata_record_observed_tool_chunk='6e2c64',
        metadata_record_result_file=ledger.relative_to(ROOT).as_posix(),metadata_record_result_sha256=sha(ledger),
        observation_source='Actual exec_command result, not inferred from JSON complete.'))
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1240
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.is_file() and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    protected={v['path'] for v in prior['evidence_files']}
    names=[
        'MC_RC_3D_PAIRED_REAL_RESOURCE_ENTRY_PROTOCOL_2026-10-07.md',
        'PAIRED_RESOURCE_WORKFLOW_INDEPENDENT_PROTOCOL_2026-10-07.md',
        'MC_RC_3D_PAIRED_RESOURCE_CUDA_TELEMETRY_AMENDMENT_2026-10-07.md',
        'LTT_ORDERING_COUNTEREXAMPLE_CPU_PROTOCOL_2026-10-07.md','RISK_COST_FULL_POLICY_FOLLOWUP_2026-10-07.md',
        'SESSION_OBSERVED_EXITS_PAIRED_RESOURCE_WORKFLOW_2026-10-07.json','SESSION_OBSERVED_EXITS_RESOURCE_AND_LTT_RECORD_2026-10-07.json',
        'SESSION_IMPORTED_SUMMARY_RESOURCE_AND_LTT_VERBATIM_2026-10-07.md','SESSION_VISIBLE_DIALOGUE_RESOURCE_AND_LTT_2026-10-07.md',
        'SESSION_VISIBLE_DIALOGUE_RESOURCE_AND_LTT_ARCHIVING_2026-10-07.md','SESSION_RESULT_RESOURCE_AND_LTT_2026-10-07.md',
        'SESSION_HANDOFF_RESOURCE_AND_LTT_LIVE_2026-10-07.md','SESSION_EXECUTION_LEDGER_RESOURCE_AND_LTT_2026-10-07.json',
        'SESSION_EXECUTION_PROGRESS_RESOURCE_AND_LTT_2026-10-07.json',
        'experiments/mc_rc_3d_paired_resource_worker_2026_10_07.py','experiments/run_mc_rc_3d_paired_real_resource_2026_10_07.py',
        'experiments/qualify_mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07.py',
        'experiments/verify_mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07.py',
        'experiments/receipt_paired_resource_workflow_exits_2026_10_07.py',
        'experiments/prepare_mc_rc_3d_paired_resource_cuda_telemetry_v2_2026_10_07.py',
        'experiments/run_mc_rc_3d_paired_real_resource_v2_2026_10_07.py',
        'experiments/audit_ltt_ordering_counterexample_2026_10_07.py','experiments/verify_ltt_ordering_counterexample_2026_10_07.py',
        'experiments/record_resource_and_ltt_evidence_2026_10_07.py',
        'literature/2026-10-07_learn_then_test_primary_protocol.md','literature/fetch_learn_then_test_primary_2026_10_07.py',
        'literature/render_learn_then_test_primary_2026_10_07.py','literature/2026-10-07_learn_then_test_primary_reading.md',
        'literature/2026-10-07_pareto_testing_primary_protocol.md','literature/2026-10-07_pareto_testing_identity_recovery_protocol.md',
        'literature/fetch_pareto_testing_primary_2026_10_07.py','literature/recover_pareto_testing_primary_2026_10_07.py',
        'literature/search_pareto_testing_official_identity_2026_10_07.py','literature/prepare_verified_pareto_acquisition_2026_10_07.py',
        'literature/fetch_verified_pareto_testing_primary_2026_10_07.py','literature/render_pareto_testing_primary_2026_10_07.py',
        'literature/2026-10-07_pareto_testing_primary_reading.md','literature/resource_and_ltt_reading_provenance_2026-10-07.json']
    stage={ROOT/name for name in names}|{Path(__file__)}
    dirs=[
        'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07',
        'experiments/mc_rc_3d_paired_real_resource_2026_10_07_cpu_attempt01',
        'experiments/mc_rc_3d_paired_real_resource_v2_2026_10_07_gpu_attempt01',
        'experiments/mc_rc_3d_paired_resource_cuda_telemetry_v2_preparation_2026_10_07',
        'experiments/ltt_ordering_counterexample_cpu_2026_10_07',
        'literature/source_cache/learn_then_test_primary_2026-10-07',
        'literature/source_cache/learn_then_test_render_2026-10-07',
        'literature/source_cache/pareto_testing_primary_2026-10-07',
        'literature/source_cache/pareto_testing_primary_recovery_2026-10-07',
        'literature/source_cache/pareto_testing_official_search_2026-10-07',
        'literature/source_cache/pareto_testing_verified_primary_2026-10-07',
        'literature/source_cache/pareto_testing_render_2026-10-07']
    for name in dirs:
        d=ROOT/name;assert d.is_dir();stage|={p for p in d.rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT) for p in stage)
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<100_000_000
    more=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_PAIRED_AND_CALIBRATION_2026-10-07.json',
        ROOT/'SESSION_CHECKPOINT_RECEIPT_PAIRED_AND_CALIBRATION_2026-10-07.json',
        ROOT/'SESSION_FINAL_REPLY_PAIRED_AND_CALIBRATION_ACTUAL_2026-10-07.md',
        ROOT/'SESSION_POST_ARCHIVE_PUBLIC_UPDATE_PAIRED_AND_CALIBRATION_2026-10-07.md',
        ROOT/'experiments/finalize_paired_and_calibration_checkpoint_2026_10_07.py'}
    bindings=[];links=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            q=read(p)
            if isinstance(q,dict):
                for b in q.get('source_bindings',[]):
                    s=(ROOT/b['path']).resolve();assert s.is_file() and s.is_relative_to(ROOT) and sha(s)==b['sha256'],(p,b)
                    more.add(s);bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target=target.strip('<>')
                if re.match(r'https?://|app://',target):continue
                s=(p.parent/target.split('#',1)[0]).resolve()
                assert s.exists() and s.is_relative_to(ROOT),(p,target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=s.relative_to(ROOT).as_posix()))
                if s.is_file():more.add(s)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    l=read(ledger)
    for observed in l['observed_exits'].values():assert sha(ROOT/observed['result']['path'])==observed['result']['sha256']
    scope=read(ROOT/l['reading_scope']['path']);assert scope['primary_papers_selected_read']==2
    assert scope['successful_PDF_pages']==58 and scope['complete_selected_unique_pages_read']==27 and scope['actual_visual_pages_reviewed']==10
    for paper in scope['papers']:
        assert sha(ROOT/paper['pdf']['path'])==paper['pdf']['sha256']
        for t in paper['selected_page_files']:assert sha(ROOT/t['path'])==t['sha256']
    assert all(v['actual_view_image_executed'] and sha(ROOT/v['file'])==v['sha256'] for v in scope['actual_source_visual_reviews'])
    progress=read(ROOT/l['progress']['path']);assert progress['own_live_runs']==[99542] and progress['full_training_observed_tool_exit'] is None
    for f in progress['root_files_observed']:assert sha(f['path'])==f['sha256']
    v=read(ROOT/'experiments/mc_rc_3d_paired_resource_workflow_synthetic_2026_10_07/independent_attempt01.json')
    assert v['complete'] and not v['errors'] and v['independent_coverage_SHA_exact'] and len(v['independent_training_batch_replays'])==6
    c=read(ROOT/'experiments/ltt_ordering_counterexample_cpu_2026_10_07/independent_attempt01.json')
    assert c['complete'] and c['exact_rational_results_match'] and c['independent_binary_outcomes_enumerated']==65536
    evidence={r['path']:r for r in prior['evidence_files']}
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:evidence[key]=entry(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        prior_manifest_file=PRIOR.relative_to(ROOT).as_posix(),prior_manifest_sha256=sha(PRIOR),
        previous_frozen_evidence_files_verified=1240,stage_files=[entry(p) for p in sorted(stage)],
        evidence_files=[evidence[k] for k in sorted(evidence)],stage_bytes=sum(p.stat().st_size for p in stage),
        source_bindings_verified=bindings,local_links=links,
        primary_papers_selected_read=2,successful_PDF_pages=58,complete_selected_unique_pages_read=27,actual_visual_pages_reviewed=10,
        stage_synthetic_workflow_updates=8,new_MRI_data_reads=0,new_MRI_forwards=0,new_GPU_forwards=0,
        live_session=99542,live_training_files_excluded=True,full_training_exit_not_claimed=True,
        real19series_resource_qualification_completed=False,original_direct_ideal_gate_failure_preserved=True,
        preserved_failed_acquisition_attempts=2,publication_claim_confirmed=False,goal_status='active')
    new(DEST,result)
    # Reopen and verify all final evidence bytes, without inspecting live training.
    saved=read(DEST)
    for f in saved['evidence_files']:
        p=ROOT/f['path'];assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256']
    new(PROOF,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest_file=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),
        stage_files_frozen=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],
        previous1240_evidence_hashes_unchanged=True,all_final_evidence_hashes_verified=True,
        live_training_files_excluded=True,publication_claim_confirmed=False,goal_status='active'))
    print(json.dumps(dict(complete=True,stage_files=len(stage),cumulative_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],previous1240_verified=True)));return 0
if __name__=='__main__':raise SystemExit(main())
