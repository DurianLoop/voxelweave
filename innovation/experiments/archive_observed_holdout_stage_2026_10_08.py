"""Verify prior3409 and archive the observed-feature and primary-reading stage."""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT/'literature/common_projected_stage_manifest_2026-10-08.json'
PRIOR_PROOF = ROOT/'SESSION_ARCHIVE_VERIFICATION_COMMON_PROJECTED_2026-10-08.json'
DEST = ROOT/'literature/observed_holdout_stage_manifest_2026-10-08.json'
PROOF = ROOT/'SESSION_ARCHIVE_VERIFICATION_OBSERVED_HOLDOUT_2026-10-08.json'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not DEST.exists() and not PROOF.exists()
    prior, priorproof = read(PRIOR), read(PRIOR_PROOF)
    assert prior['complete'] and priorproof['complete'] and not prior['errors'] and not priorproof['errors']
    assert len(prior['evidence_files'])==3409 and sha(PRIOR)==priorproof['manifest_sha256']
    for v in prior['evidence_files']:
        p = ROOT/v['path']
        assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],v['path']
    stage = set()
    for pattern in ('*OBSERVED_HOLDOUT*','OBSERVED_FEATURE_TO_ACTION*'):
        stage.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in ('*observed_holdout*.py','observed_holdout*.json'):
        stage.update(p for p in (ROOT/'experiments').glob(pattern) if p.is_file())
    for pattern in ('2026-10-08_blindspot*.md','*blindspot*.py','*noise2same*.py',
                    'BLINDSPOT*.md','blindspot_dependence_reading*.json'):
        stage.update(p for p in (ROOT/'literature').glob(pattern) if p.is_file())
    walk_errors = []
    for rel in ('experiments/observed_holdout_feature_qualification_2026_10_08',
                'experiments/observed_holdout_feature_independent_2026_10_08',
                'experiments/observed_holdout_feature_independent_layout_v2_2026_10_08',
                'literature/source_cache/blindspot_dependence_primary_2026-10-08',
                'tools/blindspot_pdf_reader_2026_10_08',
                'tools/blindspot_pdf_reader_v2_2026_10_08',
                'tools/blindspot_pdf_reader_v3_2026_10_08'):
        folder = ROOT/rel
        assert folder.is_dir(),rel
        for current,dirs,files in os.walk(folder,onerror=lambda e:walk_errors.append(str(e))):
            dirs[:] = [d for d in dirs if d not in ('tmp','__pycache__')]
            stage.update(Path(current)/name for name in files if not name.endswith('.pyc'))
    assert not walk_errors
    stage.discard(PROOF)
    stage.discard(DEST)
    previous = {v['path'] for v in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in previous for p in stage)
    stagebytes = sum(p.stat().st_size for p in stage)
    assert stagebytes < 50_000_000,stagebytes
    post = ['SESSION_FINAL_TOOL_OBSERVATIONS_COMMON_PROJECTED_2026-10-08.json',
        'SESSION_POST_ARCHIVE_COMMON_PROJECTED_UPDATE_2026-10-08.md',
        'SESSION_CHECKPOINT_RECEIPT_COMMON_PROJECTED_2026-10-08.json',
        'SESSION_OBSERVED_EXITS_FINALIZE_COMMON_PROJECTED_2026-10-08.json',
        'SESSION_DELIVERY_COMMON_PROJECTED_2026-10-08.md',
        'experiments/finalize_common_projected_checkpoint_2026_10_08.py']
    more = stage | {PRIOR,PRIOR_PROOF} | {ROOT/p for p in post}
    bindings = []
    links = []
    for p in sorted(stage):
        if p.suffix=='.json':
            data = read(p)
            if isinstance(data,dict):
                for b in data.get('source_bindings',[]):
                    q = (ROOT/b['path']).resolve()
                    assert q.is_relative_to(ROOT.resolve()) and q.is_file() and sha(q)==b['sha256'],(p,b)
                    more.add(q)
                    bindings.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
        elif p.suffix=='.md' and p.relative_to(ROOT).parts[0]!='tools':
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                target = target.strip('<>')
                if re.match(r'https?://|app://',target):
                    continue
                q = (Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else p.parent/target.split('#',1)[0]).resolve()
                if q!=DEST.resolve():
                    assert q.exists() and q.is_relative_to(ROOT.resolve()),(p,target)
                    if q.is_file():
                        more.add(q)
                links.append(dict(document=p.relative_to(ROOT).as_posix(),target=q.relative_to(ROOT).as_posix()))
    forbidden = {'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt',
        'native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix=='.pyc' for p in more)
    ledgerfile = ROOT/'SESSION_EXECUTION_LEDGER_OBSERVED_HOLDOUT_2026-10-08.json'
    ledger = read(ledgerfile)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status']=='active'
    assert ledger['observed_package_load_events']==41 and ledger['unique_real_folds']==38
    assert ledger['counterfactual_check_events']==81 and ledger['original_independent_failed'] and ledger['layout_v2_passed']
    assert ledger['text_pages_read']==19 and ledger['visual_pages_reviewed']==5
    assert all(ledger[k]==0 for k in ('neural_forwards','GPU_forwards','training_updates','model_arrays_loaded'))
    for v in ledger['root_files_observed']:
        assert sha(Path(v['path']))==v['sha256']==v['previous_sha256']
    runtime = read(ROOT/'tools/blindspot_pdf_reader_v3_2026_10_08/installation_attempt03.json')
    assert runtime['complete'] and not runtime['errors'] and runtime['import_actual_subprocess_exit']==0
    for v in runtime['installed_files']:
        assert sha(ROOT/v['path'])==v['sha256']
    for v in runtime['packages']:
        assert v['official_digest_verified'] and v['wheel_sha256']==v['official_PyPI_sha256']
    evidence = {v['path']:v for v in prior['evidence_files']}
    additions = []
    for p in sorted(more):
        key = p.relative_to(ROOT).as_posix()
        if key not in evidence:
            value = entry(p)
            evidence[key] = value
            additions.append(value)
    newbytes = sum(v['bytes'] for v in additions)
    assert newbytes < 50_000_000,newbytes
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(PRIOR),entry(PRIOR_PROOF),entry(ledgerfile)],
        prior_manifest_sha256=sha(PRIOR),previous_frozen_evidence_files_verified=3409,
        stage_files=[entry(p) for p in sorted(stage)],stage_bytes=stagebytes,
        new_evidence_files=additions,new_evidence_bytes=newbytes,
        evidence_files=[evidence[k] for k in sorted(evidence)],source_bindings_verified=bindings,local_links=links,
        scientific_evidence_enumeration_errors=walk_errors,previous_post_appendices_incorporated=True,
        historical_failed_pip_temp_directories_retained_and_not_enumerated=True,
        excluded_previous_retained_temporary_directories=prior['excluded_previous_retained_temporary_directories'],
        original_independent_failed_attempt_and_source_retained=True,layout_v2_pre_execution_protocol_bound=True,
        new_failed_summary_and_stage_writer_sources_retained=True,
        verified_portable_runtime_all_files_bound=True,portable_runtime_existing_MRI_environment_modified=False,
        related_primary_papers_read=2,related_physical_pages_acquired=20,text_pages_read=19,visual_pages_reviewed=5,
        wrong_identity28_pages_excluded=True,separate_supplementary_not_acquired_or_read=True,
        unique_development_patients=11,unique_development_series=19,observed_package_load_events=41,
        unique_real_folds=38,counterfactual_check_events=81,
        new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        actual_MRI_task_benefit_measured=False,actual_MRI_risk_certificates_issued=0,
        stage_max_saved_bytes=50_000_000,medical_job_saved_limit_remains=20_000_000,
        live_training_files_excluded=True,full_training_observed_tool_exit=None,
        goal_status='active',publication_claim_confirmed=False)
    new(DEST,result)
    for v in result['evidence_files']:
        assert (ROOT/v['path']).stat().st_size==v['bytes'] and sha(ROOT/v['path'])==v['sha256'],v['path']
    proof = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        manifest=DEST.relative_to(ROOT).as_posix(),manifest_sha256=sha(DEST),
        previous3409_evidence_hashes_unchanged=True,all_final_evidence_hashes_verified=True,
        stage_files=len(stage),stage_bytes=stagebytes,newly_bound_files=len(additions),new_evidence_bytes=newbytes,
        cumulative_frozen_evidence_files=len(evidence),local_links_verified=True,
        all_source_bindings_verified=True,portable_runtime_official_checksums_verified=True,
        source_binding_count=len(bindings),local_link_count=len(links),
        automatic_approval_review_rejections_received=0,user_terminal_processes_controlled=False,
        actual_MRI_task_benefit_measured=False,goal_status='active',publication_claim_confirmed=False)
    new(PROOF,proof)
    print(json.dumps({k:proof[k] for k in ('complete','stage_files','stage_bytes','newly_bound_files',
        'new_evidence_bytes','cumulative_frozen_evidence_files','previous3409_evidence_hashes_unchanged',
        'local_links_verified','goal_status','publication_claim_confirmed')},ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
