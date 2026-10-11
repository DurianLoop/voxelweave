"""Freeze this stage and verify all 845 inherited evidence hashes; exclude live training files."""
import hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/incremental_inference_stage_manifest_2026-10-07.json'
MANIFEST=ROOT/'literature/action_composition_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_ACTION_COMPOSITION_2026-10-07.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def new(p,r):assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not PROOF.exists()
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==845
    protected={r['path'] for r in prior['evidence_files']}
    for r in prior['evidence_files']:
        p=ROOT/r['path'];assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    rootnames=[
        'RESEARCH_SCOPE_CLARIFICATION_2026-10-07.md','SESSION_VISIBLE_DIALOGUE_ACTION_INTERACTION_2026-10-07.md',
        'SESSION_IMPORTED_HANDOFF_ACTION_INTERACTION_2026-10-07.md','SESSION_OBSERVED_EXITS_ACTION_COMPOSITION_2026-10-07.json',
        'SESSION_OBSERVED_EXITS_ACTION_COMPOSITION_EVIDENCE_2026-10-07.json',
        'MC_RC_3D_ACTION_COMPOSITION_PROBE_PROTOCOL_2026-10-07.md','MC_RC_3D_ACTION_COST_INTERPRETATION_ADDENDUM_2026-10-07.md',
        'MC_RC_3D_ACTION_COMPOSITION_RESULT_2026-10-07.md','INNOVATION_DECISION_AFTER_ACTION_COMPOSITION_2026-10-07.md',
        'SESSION_RESULT_ACTION_COMPOSITION_2026-10-07.md','SESSION_HANDOFF_ACTION_COMPOSITION_LIVE_2026-10-07.md',
        'SESSION_EXECUTION_LEDGER_ACTION_COMPOSITION_2026-10-07.json','SESSION_EXECUTION_PROGRESS_ACTION_COMPOSITION_2026-10-07.json',
        'SESSION_FINAL_REPLY_ACTION_COMPOSITION_2026-10-07.md',
        'literature/2026-10-07_action_interaction_primary_selection.md','literature/2026-10-07_action_interaction_primary_reading.md',
        'literature/fetch_action_interaction_primary_2026_10_07.py','literature/extract_action_interaction_primary_attempt02_2026_10_07.py',
        'literature/resolve_mri_sampling_identity_attempt03_2026_10_07.py','literature/fetch_verified_mri_sampling_attempt04_2026_10_07.py',
        'literature/render_action_interaction_primary_2026_10_07.py',
        'experiments/probe_mc_rc_3d_action_composition_2026_10_07.py','experiments/verify_action_composition_and_metric_control_2026_10_07.py',
        'experiments/record_action_composition_evidence_2026_10_07.py']
    stage={ROOT/p for p in rootnames}|{Path(__file__)}
    for directory in ('literature/source_cache/action_interaction_primary_2026-10-07','experiments/mc_rc_3d_action_composition_2026_10_07'):
        stage|={p for p in (ROOT/directory).rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT) for p in stage)
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<100_000_000
    newevidence=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_INCREMENTAL_INFERENCE_2026-10-07.json',ROOT/'SESSION_CHECKPOINT_RECEIPT_INCREMENTAL_INFERENCE_2026-10-07.json'}
    old_audits=[ROOT/p for p in ('MIRA_CLAIM_AUDIT_2026-09-30.md','PUBLIC_ONLY_CLAIM_REVIEW_STRESS_TEST_2026-10-01.md',
        'CLAIM_PUBLICATION_GATE_2026-09-30.md','MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md','MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md',
        'literature/2026-10-01_kuestner_fulltext_access_audit.md','literature/2026-10-02_author_code_ensure_long_and_mslesseg_reading.md')]
    assert all(p.is_file() for p in old_audits);newevidence.update(old_audits)
    links=[];source_bindings=[]
    for p in sorted(stage):
        if p.suffix=='.json':
            data=read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[]):
                    target=ROOT/(b.get('path') or b['file']);assert target.is_file() and sha(target)==b['sha256']
                    newevidence.add(target);source_bindings.append(dict(document=p.relative_to(ROOT).as_posix(),source=target.relative_to(ROOT).as_posix(),sha256=b['sha256']))
        elif p.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                url=url.strip('<>')
                if re.match(r'https?://|app://',url):continue
                target=Path(url.split('#',1)[0]) if re.match(r'^[A-Za-z]:[/\\]',url) else p.parent/url.split('#',1)[0]
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT),(p,url)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
                if target.is_file():newevidence.add(target)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in newevidence)
    ledger=read(ROOT/'SESSION_EXECUTION_LEDGER_ACTION_COMPOSITION_2026-10-07.json')
    for row in ledger['observed_exits'].values():assert sha(ROOT/row['result']['path'])==row['result']['sha256']
    assert ledger['observed_exits']['real_MRI_8subset_probe']['observed_tool_exit']==0
    assert ledger['observed_exits']['independent_tile_and_exact_metric_control']['observed_tool_exit']==0
    assert read(ROOT/'SESSION_OBSERVED_EXITS_ACTION_COMPOSITION_EVIDENCE_2026-10-07.json')['observed_tool_exit']==0
    progress=read(ROOT/'SESSION_EXECUTION_PROGRESS_ACTION_COMPOSITION_2026-10-07.json')
    assert progress['own_live_runs']==[99542] and progress['full_training_observed_tool_exit'] is None
    assert progress['rolling_histories']['raw_pchip']['last_update_observed']==99
    provenance=read(ROOT/'literature/source_cache/action_interaction_primary_2026-10-07/reading_provenance.json')
    assert provenance['new_primary_papers_method_and_main_results_read']==3 and provenance['selected_complete_text_pages_actually_read']==29
    assert all(r['actual_view_image_executed'] for r in provenance['actual_source_visual_reviews'])
    records={r['path']:r for r in prior['evidence_files']}
    for p in sorted(newevidence):
        key=p.relative_to(ROOT).as_posix()
        if key not in records:records[key]=entry(p)
    stage_records=[records[p.relative_to(ROOT).as_posix()] for p in sorted(stage)]
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),stage_files=stage_records,
        evidence_files=[records[k] for k in sorted(records)],stage_bytes=sum(r['bytes'] for r in stage_records),
        prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=845,local_links=links,source_bindings_verified=source_bindings,
        old_MIRA_scope_audits_bound=[entry(p) for p in old_audits],new_primary_papers_method_results_read=3,successful_primary_PDF_pages=86,
        selected_complete_pages_read=29,actual_source_visual_pages_reviewed=3,real_MRI_probe_8subset_qualification=True,
        real_MRI_probe_forward_calls=116,real_MRI_probe_tiles=232,new_real_MRI_task_effect_scores=0,exact_synthetic_Dice_counterexample=True,
        other_processes_modified=False,new_experiment_training_updates=0,new_GPU_forwards=0,
        current_3D_lesion_confirmation_patients=0,whole_project_external_confirmation_zero_not_claimed=True,
        own_live_runs_at_checkpoint=[99542],full_training_observed_tool_exit=None,final_execution_closed=False,publication_claim_confirmed=False,goal_status='active')
    new(MANIFEST,result)
    proof=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=MANIFEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(MANIFEST),stage_files=len(stage_records),evidence_files=len(records),stage_bytes=result['stage_bytes'],
        previous_frozen_evidence_files_verified=845,own_live_runs_at_checkpoint=[99542],full_training_observed_tool_exit=None,
        final_execution_closed=False,current_3D_lesion_confirmation_patients=0,whole_project_external_confirmation_zero_not_claimed=True,
        publication_claim_confirmed=False,goal_status='active')
    new(PROOF,proof)
    print(json.dumps({k:proof[k] for k in ('complete','stage_files','evidence_files','stage_bytes','previous_frozen_evidence_files_verified','own_live_runs_at_checkpoint')},ensure_ascii=False))
    return 0
if __name__=='__main__':raise SystemExit(main())
