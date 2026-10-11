"""Freeze this stage only after observed training/verifier exits; preserve previous immutable evidence."""
import hashlib, json, re, sys
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'literature/backbone_context_stage_manifest_2026-10-07.json'
RECEIPT = ROOT/'SESSION_ARCHIVE_VERIFICATION_BACKBONE_CONTEXT_2026-10-07.json'
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): h.update(chunk)
    return h.hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p, v):
    with p.open('x', encoding='utf-8') as f: json.dump(v, f, ensure_ascii=False, indent=2); f.write('\n')
def entry(p): return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8'); assert not MANIFEST.exists() and not RECEIPT.exists()
    ledger = read(ROOT/'SESSION_EXECUTION_LEDGER_BACKBONE_CONTEXT_2026-10-07.json')
    assert ledger['all_own_runs_terminal_from_observed_tool_exits'] and ledger['own_live_runs'] == []
    assert ledger['training_observed_tool_exit'] == ledger['independent_verifier_observed_tool_exit'] == 0
    fitpath = ROOT/'experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json'
    fit = read(fitpath); verification = read(fitpath.parent/'independent_both1024_and_full_fov_attempt01.json')
    assert all(v['complete'] and not v['errors'] and not v['cuda_initialized'] for v in (fit, verification))
    assert fit['actual_cpu_backbone_updates'] == 2048 and len(fit['arms']) == len(verification['arms']) == 2
    assert verification['result_sha256'] == sha(fitpath)
    for arm in fit['arms']:
        assert arm['updates_completed'] == len(arm['history']) == 1024 and arm['evaluation_complete']
        assert sha(ROOT/arm['checkpoint_file']) == arm['checkpoint_sha256']
        assert sha(ROOT/arm['prediction_file']) == arm['prediction_sha256']
    assert all(a['history_rows_verified'] == 1024 and a['full_tile_stream_and_labels_verified'] and
        a['production_coordinate_replay_threshold_disagreements'] == 0 and
        a['production_coordinate_replay_max_probability_error'] <= 3e-6 and
        a['independent_float64_coordinate']['gate_passed'] for a in verification['arms'])
    oldnorm = read(ROOT/'experiments/mc_rc_3d_local_kernel_normalization_2026_10_07/attempt01.json')
    newnorm = read(ROOT/'experiments/mc_rc_3d_local_kernel_normalization_centered_2026_10_07/attempt01.json')
    assert oldnorm['complete'] and not oldnorm['fp32_qualification_passed'] and oldnorm['fp32_failed_cases'] == ['constant_two', 'offset_1000']
    assert newnorm['complete'] and not newnorm['errors'] and not newnorm['cuda_initialized']
    assert newnorm['float32_qualification_passed'] and newnorm['float64_qualification_passed'] and newnorm['original_failure_preserved']
    priorpath = ROOT/'literature/head_context_stage_manifest_2026-10-07.json'; prior = read(priorpath)
    closurepath = ROOT/'SESSION_CLOSING_RECEIPT_HEAD_CONTEXT_2026-10-07.json'; closure = read(closurepath)
    assert prior['complete'] and closure['complete'] and closure['manifest_sha256'] == sha(priorpath)
    assert closure['archive_sha256'] == sha(ROOT/closure['archive_file'])
    for row in prior['evidence_files'] + closure['closing_files']:
        assert sha(ROOT/row['path']) == row['sha256'], 'Previous immutable evidence changed: '+row['path']
    protected = {row['path'] for key in ('stage_files', 'evidence_files') for row in prior[key]}
    protected |= {row['path'] for row in closure['closing_files']}
    protected |= {priorpath.relative_to(ROOT).as_posix(), closurepath.relative_to(ROOT).as_posix(), closure['archive_file']}
    candidates = set(ROOT.glob('*2026-10-07.md')) | set(ROOT.glob('*BACKBONE_CONTEXT*2026-10-07.json'))
    candidates |= set((ROOT/'experiments').glob('*2026_10_07.py')) | set((ROOT/'experiments').glob('*2026_10_07.json'))
    candidates |= set((ROOT/'literature').glob('*2026_10_07.py')) | set((ROOT/'literature').glob('2026-10-07*.md'))
    stage = {p for p in candidates if p.relative_to(ROOT).as_posix() not in protected and p not in (MANIFEST, RECEIPT)}
    for name in ('mc_rc_3d_cpu_thread_qualification_2026_10_07', 'mc_rc_3d_tile_lattice_audit_2026_10_07',
        'mc_rc_3d_crop_origin_sampling_audit_2026_10_07', 'mc_rc_3d_backbone_context_refit_2026_10_07',
        'mc_rc_3d_backbone_context_refit_v2_2026_10_07', 'mc_rc_3d_local_kernel_normalization_2026_10_07',
        'mc_rc_3d_local_kernel_normalization_centered_2026_10_07', 'mc_rc_3d_backbone_collapse_diagnostic_2026_10_07'):
        stage |= {p for p in (ROOT/'experiments'/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for name in ('tile_context_primary_2026-10-07', 'tile_context_followup_2026-10-07',
        'tile_context_alternates_2026-10-07', 'kernel_normalization_primary_2026-10-07',
        'thumbnail_instance_normalization_2026-10-07', 'thumbnail_instance_normalization_v2_2026-10-07',
        'tile_context_visual_review_2026-10-07', 'kernel_normalization_visual_review_2026-10-07'):
        stage |= {p for p in (ROOT/'literature/source_cache'/name).rglob('*') if p.is_file()}
    stage |= {p for p in (ROOT/'figures/mc_rc_3d_backbone_context_refit_2026_10_07').rglob('*') if p.is_file()}
    assert all(p.is_relative_to(ROOT) for p in stage)
    size = sum(p.stat().st_size for p in stage); assert size <= 250_000_000
    evidence = {ROOT/row['path'] for row in prior['evidence_files']+closure['closing_files']} | stage
    evidence |= {priorpath, closurepath, ROOT/closure['archive_file']}
    scripts = {sha(p) for p in evidence if p.suffix == '.py'}
    for p in stage:
        if p.suffix != '.json': continue
        obj = read(p)
        if not isinstance(obj, dict): continue
        if obj.get('script_sha256'): assert obj['script_sha256'] in scripts, 'Source missing for '+str(p)
        for binding in obj.get('source_bindings', []):
            target = ROOT/binding['path']; assert target.is_relative_to(ROOT) and sha(target) == binding['sha256']; evidence.add(target)
    links = []
    for p in stage:
        if p.suffix != '.md': continue
        for url in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            url = url.strip('<>')
            if re.match(r'https?://|app://', url): continue
            target = (p.parent/url.split('#', 1)[0]).resolve()
            assert target.exists() and target.is_relative_to(ROOT), f'Invalid link in {p.name}: {url}'
            links.append(dict(document=p.relative_to(ROOT).as_posix(), target=target.relative_to(ROOT).as_posix()))
            if target.is_file(): evidence.add(target)
    three = read(ROOT/'literature/source_cache/tile_context_visual_review_2026-10-07/actual_reading_and_visual_review_attempt01.json')
    kn = read(ROOT/'literature/source_cache/kernel_normalization_visual_review_2026-10-07/actual_reading_and_visual_review_attempt01.json')
    assert three['complete'] and three['primary_papers_newly_read'] == 3 and three['pdf_physical_pages_textually_read'] == 34
    assert kn['complete'] and kn['newly_completed_primary_papers'] == 1 and kn['physical_pages_textually_read'] == list(range(1, 22))
    for row in kn['visual_reviews']: assert row['actual_visual_review'] and sha(ROOT/row['image']) == row['sha256']
    assert sha(ROOT/kn['report']) == kn['report_sha256'] and sha(ROOT/kn['source_pdf']) == kn['source_pdf_sha256']
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], script_sha256=sha(__file__),
        stage_files=[entry(p) for p in sorted(stage)], evidence_files=[entry(p) for p in sorted(evidence)], local_links=links,
        prior_manifest_sha256=sha(priorpath), prior_closure_sha256=sha(closurepath), new_cpu_backbone_updates=2048,
        resource_qualification_updates_discarded=12, new_gpu_updates=0, new_primary_papers_completed=4,
        new_pdf_physical_pages_textually_read=55, new_XML_extraction_blocks_textually_read=176,
        new_physical_pdf_pages_visually_read=8, original_failures_preserved=True,
        original_fit_gates_passed_by_arm={a['kind']:a['training_fit_gate_passed'] for a in fit['arms']},
        production_float32_strict_coordinate_failures_retained=sum(not a['production_float32_vs_numpy_coordinate']['original_strict_gate_passed'] for a in verification['arms']),
        numerical_implementation_success_not_MRI_success=True, confirmation_patients_opened=False,
        scientific_confirmation_patients=0, publication_claim_confirmed=False, goal_status='active')
    write(MANIFEST, manifest)
    for key in ('stage_files', 'evidence_files'):
        for row in read(MANIFEST)[key]: assert sha(ROOT/row['path']) == row['sha256']
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], manifest_file=MANIFEST.relative_to(ROOT).as_posix(),
        manifest_sha256=sha(MANIFEST), stage_files=len(stage), evidence_files=len(evidence), stage_saved_bytes=size,
        all_files_rehashed=True, prior_376_immutable_evidence_and_closing_files_rehashed=True,
        local_links_verified=len(links), new_cpu_backbone_updates=2048, new_gpu_updates=0, new_primary_papers_completed=4,
        own_live_runs=[], all_own_runs_terminal_from_observed_tool_exits=True, original_task_capability_gate_changed=False,
        original_failures_preserved=True, confirmation_patients_opened=False, scientific_confirmation_patients=0,
        publication_claim_confirmed=False, goal_status='active')
    write(RECEIPT, receipt); print(json.dumps(receipt, ensure_ascii=False))
if __name__ == '__main__': main()
