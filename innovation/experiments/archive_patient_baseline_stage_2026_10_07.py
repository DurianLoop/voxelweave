"""Freeze patient baseline evidence, preserving previous1386 and excluding running state."""
import ctypes,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'literature/resource_and_ltt_stage_manifest_2026-10-07.json'
DEST=ROOT/'literature/patient_baseline_stage_manifest_2026-10-07.json'
PROOF=ROOT/'SESSION_ARCHIVE_VERIFICATION_PATIENT_BASELINE_2026-10-07.json'
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
    prior=read(PRIOR);assert prior['complete'] and not prior['errors'] and len(prior['evidence_files'])==1386
    for v in prior['evidence_files']:
        p=ROOT/v['path'];assert p.is_file() and p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    protected={v['path'] for v in prior['evidence_files']}
    record=ROOT/'SESSION_EXECUTION_LEDGER_PATIENT_BASELINE_2026-10-07.json';assert read(record)['complete']
    record_receipt=ROOT/'SESSION_OBSERVED_EXITS_PATIENT_BASELINE_RECORD_2026-10-07.json'
    new(record_receipt,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        metadata_record_observed_tool_exit=0,metadata_record_observed_tool_chunk='20138e',
        metadata_record_result_file=record.relative_to(ROOT).as_posix(),metadata_record_result_sha256=sha(record)))
    names=[
        'PATIENT_RISK_COST_BASELINE_EXECUTOR_PROTOCOL_2026-10-07.md','PATIENT_RISK_COST_BASELINE_NUMERICAL_AMENDMENT_2026-10-07.md',
        'PATIENT_COMPLETE_SERIES_PANEL_PROTOCOL_2026-10-07.md','PATIENT_RISK_COST_REAL_INPUT_TEMPLATE_2026-10-07.json',
        'RISK_COST_BASELINE_AND_CLAIM_SCOPE_FOLLOWUP_2026-10-07.md',
        'SESSION_GOAL_CONTINUATION_BASELINE_VERBATIM_2026-10-07.md','SESSION_VISIBLE_DIALOGUE_PATIENT_BASELINE_2026-10-07.md',
        'SESSION_RESULT_PATIENT_BASELINE_2026-10-07.md','SESSION_HANDOFF_PATIENT_BASELINE_LIVE_2026-10-07.md',
        'SESSION_OBSERVED_EXITS_PATIENT_BASELINE_2026-10-07.json','SESSION_EXECUTION_PROGRESS_PATIENT_BASELINE_2026-10-07.json',
        'SESSION_EXECUTION_LEDGER_PATIENT_BASELINE_2026-10-07.json','SESSION_OBSERVED_EXITS_PATIENT_BASELINE_RECORD_2026-10-07.json',
        'experiments/patient_risk_cost_baseline_executor_2026_10_07.py','experiments/qualify_patient_risk_cost_baseline_executor_2026_10_07.py',
        'experiments/verify_patient_risk_cost_baseline_executor_2026_10_07.py','experiments/patient_complete_series_panel_2026_10_07.py',
        'experiments/qualify_patient_complete_series_panel_2026_10_07.py','experiments/qualify_patient_complete_series_rounding_2026_10_07.py',
        'experiments/verify_patient_complete_series_panel_2026_10_07.py','experiments/record_patient_baseline_evidence_2026_10_07.py']
    stage={ROOT/name for name in names}|{Path(__file__)}
    for name in ('patient_risk_cost_baseline_executor_qualification_2026_10_07',
        'patient_complete_series_panel_qualification_2026_10_07','patient_complete_series_panel_rounding_qualification_2026_10_07'):
        d=ROOT/'experiments'/name;assert d.is_dir();stage|={p for p in d.rglob('*') if p.is_file()}
    assert all(p.is_file() and p.resolve().is_relative_to(ROOT) for p in stage)
    assert not any(p.relative_to(ROOT).as_posix() in protected for p in stage)
    assert sum(p.stat().st_size for p in stage)<5_000_000
    more=stage|{PRIOR,ROOT/'SESSION_ARCHIVE_VERIFICATION_RESOURCE_AND_LTT_2026-10-07.json',
        ROOT/'SESSION_CHECKPOINT_RECEIPT_RESOURCE_AND_LTT_2026-10-07.json',
        ROOT/'SESSION_FINAL_REPLY_RESOURCE_AND_LTT_ACTUAL_2026-10-07.md',ROOT/'SESSION_POST_ARCHIVE_RESOURCE_AND_LTT_UPDATE_2026-10-07.md',
        ROOT/'experiments/finalize_resource_and_ltt_checkpoint_2026_10_07.py'}
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
                s=(p.parent/target.split('#',1)[0]).resolve();assert s.exists() and s.is_relative_to(ROOT),(p,target)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=s.relative_to(ROOT).as_posix()))
                if s.is_file():more.add(s)
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt','native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    ledger=read(record);receipt=read(ROOT/ledger['actual_exits']['path'])
    for observed in receipt['observed_exits'].values():
        assert observed['observed_tool_exit']==0 and sha(ROOT/observed['result']['path'])==observed['result']['sha256']
    progress=read(ROOT/ledger['progress']['path']);assert progress['own_live_runs']==[99542] and progress['full_training_observed_tool_exit'] is None
    for f in progress['root_files_observed']:assert sha(f['path'])==f['sha256']
    assert ledger['current_goal_turn_classification']==ledger['previous_goal_turn_classification']=='progress'
    assert ledger['independent_selections']==9 and ledger['independent_risk_pvalues']==104
    assert ledger['independent_patient_panels']==3 and ledger['independent_patient_policy_rows']==8
    assert ledger['new_primary_papers_read']==ledger['new_MRI_pixels_or_GT_reads']==ledger['new_model_or_GPU_forwards']==0
    for name in ('patient_risk_cost_baseline_executor_qualification_2026_10_07','patient_complete_series_panel_qualification_2026_10_07',
        'patient_complete_series_panel_rounding_qualification_2026_10_07'):
        d=ROOT/'experiments'/name;q=read(d/'attempt01.json')
        assert q['complete'] and not q['errors'] and q['synthetic_only']
        for b in q['source_bindings']:assert sha(d/((ROOT/b['path']).name+'.source_snapshot'))==b['sha256']
    template=read(ROOT/'PATIENT_RISK_COST_REAL_INPUT_TEMPLATE_2026-10-07.json')
    assert template['template_only'] and template['not_real_MRI_results'] and not template['fixed_policy_ids'] and not template['expected_series']
    evidence={r['path']:r for r in prior['evidence_files']}
    for p in sorted(more):
        key=p.relative_to(ROOT).as_posix()
        if key not in evidence:evidence[key]=entry(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        prior_manifest_file=PRIOR.relative_to(ROOT).as_posix(),prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=1386,
        stage_files=[entry(p) for p in sorted(stage)],evidence_files=[evidence[k] for k in sorted(evidence)],
        stage_bytes=sum(p.stat().st_size for p in stage),source_bindings_verified=bindings,local_links=links,
        synthetic_qualifications=3,independent_verifiers=2,independent_selections=9,independent_risk_pvalues=104,
        independent_patient_panels=3,independent_patient_policy_rows=8,
        new_primary_papers_read=0,new_MRI_pixels_or_GT_reads=0,new_model_or_GPU_forwards=0,new_training_updates=0,
        live_training_files_excluded=True,full_training_exit_not_claimed=True,
        actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False,goal_status='active')
    new(DEST,result)
    for f in read(DEST)['evidence_files']:
        p=ROOT/f['path'];assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256']
    new(PROOF,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=DEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(DEST),stage_files_frozen=len(stage),cumulative_frozen_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],
        previous1386_evidence_hashes_unchanged=True,all_final_evidence_hashes_verified=True,
        live_training_files_excluded=True,publication_claim_confirmed=False,goal_status='active'))
    print(json.dumps(dict(complete=True,stage_files=len(stage),cumulative_evidence_files=len(evidence),stage_bytes=result['stage_bytes'],previous1386_verified=True)));return 0
if __name__=='__main__':raise SystemExit(main())
