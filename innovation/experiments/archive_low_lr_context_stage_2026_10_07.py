"""Archive completed incremental work while checking every previous frozen evidence hash."""
import hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'literature/low_lr_context_stage_manifest_2026-10-07.json'
RECEIPT=ROOT/'SESSION_ARCHIVE_VERIFICATION_LOW_LR_CONTEXT_2026-10-07.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def write(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8');assert not MANIFEST.exists() and not RECEIPT.exists()
    ledgerpath=ROOT/'SESSION_EXECUTION_LEDGER_LOW_LR_CONTEXT_2026-10-07.json';ledger=read(ledgerpath)
    assert ledger['all_own_runs_terminal_from_observed_tool_exits'] and ledger['own_live_runs']==[]
    assert all(ledger[k]==0 for k in ('training_observed_tool_exit','independent_verifier_observed_tool_exit',
        'resource_qualification_observed_tool_exit','resource_verifier_observed_tool_exit','fov_timing_observed_tool_exit','fov_metadata_verifier_observed_tool_exit'))
    priorpath=ROOT/'literature/backbone_context_stage_manifest_2026-10-07.json';prior=read(priorpath)
    closurepath=ROOT/'SESSION_CLOSING_RECEIPT_BACKBONE_CONTEXT_2026-10-07.json';closure=read(closurepath)
    assert prior['complete'] and closure['complete'] and closure['manifest_sha256']==sha(priorpath)
    assert closure['archive_sha256']==sha(ROOT/closure['archive_file'])
    for row in prior['evidence_files']:assert sha(ROOT/row['path'])==row['sha256'],'Frozen evidence changed: '+row['path']
    protected={row['path'] for key in ('stage_files','evidence_files') for row in prior[key]}
    protected|={priorpath.relative_to(ROOT).as_posix(),closurepath.relative_to(ROOT).as_posix(),closure['archive_file']}
    candidates=set(ROOT.glob('*2026-10-07.md'))|set(ROOT.glob('*LOW_LR*2026-10-07.json'))|set(ROOT.glob('*19SERIES*2026-10-07.json'))
    candidates|=set((ROOT/'experiments').glob('*2026_10_07.py'))|set((ROOT/'experiments').glob('*2026_10_07.json'))
    candidates|=set((ROOT/'experiments').glob('*2026_10_07.py.failed*'))
    candidates|=set((ROOT/'literature').glob('*2026_10_07.py'))|set((ROOT/'literature').glob('2026-10-07*.md'))
    for name in ('mc_rc_3d_backbone_context_low_lr_2026_10_07','mc_rc_3d_finite_context_halo_audit_2026_10_07',
        'mc_rc_3d_19series_cpu_entry_preflight_2026_10_07','mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07',
        'mc_rc_3d_19series_fov_cpu_timing_2026_10_07','task_gain_target_cpu_2026_10_07'):
        candidates|={p for p in (ROOT/'experiments'/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for name in ('action_utility_followup_2026-10-07','agentic_restoration_primary_2026-10-07',
        'hcc_sr_task_primary_2026-10-07','low_lr_followup_reading_2026-10-07','learning_to_defer_primary_2026-10-07',
        'learning_to_defer_title_verification_2026-10-07','learning_to_defer_primary_attempt02_2026-10-07'):
        candidates|={p for p in (ROOT/'literature/source_cache'/name).rglob('*') if p.is_file()}
    candidates|={p for p in (ROOT/'figures/mc_rc_3d_backbone_context_low_lr_2026_10_07').rglob('*') if p.is_file()}
    stage={p for p in candidates if p.relative_to(ROOT).as_posix() not in protected and p not in (MANIFEST,RECEIPT)}
    assert sum(p.stat().st_size for p in stage)<=250_000_000
    evidence={ROOT/r['path'] for r in prior['evidence_files']}|stage|{priorpath,closurepath,ROOT/closure['archive_file']}
    links=[];bindings=[]
    for path in sorted(stage):
        if path.suffix=='.json':
            obj=read(path)
            if not isinstance(obj,dict):continue
            for b in obj.get('source_bindings',[]):
                target=ROOT/b['path'];assert target.is_relative_to(ROOT) and target.is_file() and sha(target)==b['sha256']
                evidence.add(target);bindings.append(dict(document=path.relative_to(ROOT).as_posix(),**b))
        elif path.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                url=url.strip('<>')
                if re.match(r'https?://|app://',url):continue
                target=(path.parent/url.split('#',1)[0]).resolve();assert target.exists() and target.is_relative_to(ROOT)
                links.append(dict(document=path.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
                if target.is_file():evidence.add(target)
    fitpath=ROOT/'experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/attempt01.json';fit=read(fitpath)
    proof=read(fitpath.parent/'independent_both1024_and_full_fov_attempt01.json')
    qualifier=read(ROOT/'experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json')
    timing=read(ROOT/'experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07/attempt01.json')
    assert all(d['complete'] and not d['errors'] and not d['cuda_initialized'] for d in (fit,proof,qualifier,timing))
    assert fit['actual_cpu_backbone_updates']==2048 and fit['both_original_fit_gates_passed'] and proof['result_sha256']==sha(fitpath)
    for a in fit['arms']:
        assert sha(ROOT/a['checkpoint_file'])==a['checkpoint_sha256'] and sha(ROOT/a['prediction_file'])==a['prediction_sha256']
    assert qualifier['actual_resource_test_cpu_updates']==66 and not qualifier['updated_weights_saved'] and not qualifier['task_effects_scored']
    assert timing['GT_files_loaded']==0 and not timing['task_effects_scored'] and all(a['total_tiles']==1139 for a in timing['arms'])
    readings=[read(ROOT/'literature/source_cache/low_lr_followup_reading_2026-10-07/actual_reading_and_visual_review_attempt01.json'),
              read(ROOT/'literature/source_cache/learning_to_defer_primary_attempt02_2026-10-07/actual_reading_and_visual_review_attempt01.json')]
    assert readings[0]['new_primary_papers_completed']==1 and readings[1]['newly_completed_primary_papers']==2
    for d in readings:
        for v in d['visual_reviews']:assert sha(ROOT/v['path'])==v['sha256']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(__file__),
        stage_files=[entry(p) for p in sorted(stage)],evidence_files=[entry(p) for p in sorted(evidence)],
        prior_manifest_sha256=sha(priorpath),prior_closure_sha256=sha(closurepath),previous_frozen_evidence_files_verified=len(prior['evidence_files']),
        stage_bytes=sum(p.stat().st_size for p in stage),local_links=links,source_bindings_verified=bindings,
        new_cpu_backbone_updates=2048,resource_qualification_updates_discarded=66,new_gpu_updates=0,
        new_primary_papers_completed=3,new_primary_abstracts_completed=3,repeated_prior_abstracts=1,
        new_pdf_physical_pages_textually_read=46,new_JATS_extraction_blocks=161,
        original_failures_preserved=True,scientific_confirmation_patients=0,publication_claim_confirmed=False,goal_status='active')
    write(MANIFEST,r);reopened=read(MANIFEST)
    for row in reopened['evidence_files']:assert sha(ROOT/row['path'])==row['sha256']
    write(RECEIPT,dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],manifest_file=MANIFEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(MANIFEST),stage_files=len(r['stage_files']),evidence_files=len(r['evidence_files']),stage_bytes=r['stage_bytes'],
        previous_frozen_evidence_files_verified=len(prior['evidence_files']),own_live_runs=[],publication_claim_confirmed=False,goal_status='active'))
    print(json.dumps({k:read(RECEIPT)[k] for k in ('complete','stage_files','evidence_files','stage_bytes','previous_frozen_evidence_files_verified')}))
    return 0
if __name__=='__main__':raise SystemExit(main())
