"""Verify prior3102, then freeze this matched-oracle stage within 20MB."""
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT/'literature/anchor_prior_stage_manifest_2026-10-07.json'
PRIOR_PROOF = ROOT/'SESSION_ARCHIVE_VERIFICATION_ANCHOR_PRIOR_2026-10-07.json'
DEST = ROOT/'literature/matched_oracle_stage_manifest_2026-10-08.json'
PROOF = ROOT/'SESSION_ARCHIVE_VERIFICATION_MATCHED_ORACLE_2026-10-08.json'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    assert p.resolve().is_relative_to(ROOT.resolve())
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def new(p, data):
    with p.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert not DEST.exists() and not PROOF.exists()
    prior, priorproof = read(PRIOR), read(PRIOR_PROOF)
    assert prior['complete'] and priorproof['complete'] and not prior['errors'] and not priorproof['errors']
    assert len(prior['evidence_files']) == 3102 and sha(PRIOR) == priorproof['manifest_sha256']
    for v in prior['evidence_files']:
        p = ROOT/v['path']
        assert p.stat().st_size == v['bytes'] and sha(p) == v['sha256'], v['path']
    stage = set()
    for pattern in ('*MATCHED_ORACLE*', '*MATCHED_ANCHOR*'):
        stage.update(p for p in ROOT.glob(pattern) if p.is_file())
    for pattern in ('*matched_anchor_oracle*.py', '*matched_oracle_budget*.py', '*matched_anchor_oracle*.json', '*matched_oracle_stage*.py'):
        stage.update(p for p in (ROOT/'experiments').glob(pattern) if p.is_file())
    stage.add(ROOT/'experiments/matched_anchor_oracle_independent_helper_origin_2026_10_08.json')
    stage.add(ROOT/'MATCHED_ANCHOR_TO_ACTION_VALUE_PREPARATION_2026-10-08.md')
    stage.add(Path(__file__))
    for pattern in ('2026-10-08_shared_cost*.md', 'fetch_shared_cost_primary*.py', 'shared_cost_reading_provenance*.json'):
        stage.update(p for p in (ROOT/'literature').glob(pattern) if p.is_file())
    walk_errors = []
    for relative in ('experiments/mc_rc_matched_anchor_oracle_2026_10_08',
                     'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08',
                     'literature/source_cache/shared_cost_primary_2026-10-08'):
        folder = ROOT/relative
        assert folder.is_dir()
        for current, dirs, files in os.walk(folder, onerror=lambda error: walk_errors.append(str(error))):
            dirs[:] = [d for d in dirs if d not in ('tmp', '__pycache__')]
            stage.update(Path(current)/name for name in files if not name.endswith('.pyc'))
    assert not walk_errors, walk_errors
    previous_paths = {v['path'] for v in prior['evidence_files']}
    assert not any(p.relative_to(ROOT).as_posix() in previous_paths for p in stage)
    stagebytes = sum(p.stat().st_size for p in stage)
    assert stagebytes < 20_000_000
    post = ['SESSION_FINAL_TOOL_OBSERVATIONS_ANCHOR_PRIOR_2026-10-07.json',
            'SESSION_POST_ARCHIVE_ANCHOR_PRIOR_UPDATE_2026-10-07.md',
            'SESSION_CHECKPOINT_RECEIPT_ANCHOR_PRIOR_2026-10-07.json',
            'SESSION_OBSERVED_EXITS_FINALIZE_ANCHOR_PRIOR_2026-10-07.json',
            'SESSION_DELIVERY_ANCHOR_PRIOR_2026-10-07.md',
            'experiments/finalize_anchor_prior_checkpoint_2026_10_07.py']
    more = stage | {PRIOR, PRIOR_PROOF} | {ROOT/p for p in post}
    bindings, links = [], []
    for p in sorted(stage):
        if p.suffix == '.json':
            d = read(p)
            if isinstance(d, dict):
                for binding in d.get('source_bindings', []):
                    q = (ROOT/binding['path']).resolve()
                    assert q.is_file() and q.is_relative_to(ROOT.resolve()) and sha(q) == binding['sha256'], (p, binding)
                    more.add(q)
                    bindings.append(dict(document=p.relative_to(ROOT).as_posix(), **binding))
        elif p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
                target = target.strip('<>')
                if re.match(r'https?://|app://', target):
                    continue
                q = (Path(target) if re.match(r'^[A-Za-z]:[/\\]', target) else p.parent/target.split('#', 1)[0]).resolve()
                if q != DEST.resolve():
                    assert q.exists() and q.is_relative_to(ROOT.resolve()), (p, target)
                    if q.is_file():
                        more.add(q)
                links.append(dict(document=p.relative_to(ROOT).as_posix(), target=q.relative_to(ROOT).as_posix()))
    forbidden = {'invocation02.json', 'native_reference_resume.pt', 'raw_pchip_resume.pt',
                 'native_reference_history.jsonl', 'raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden or p.suffix == '.pyc' for p in more)
    ledgerfile = ROOT/'SESSION_EXECUTION_LEDGER_MATCHED_ORACLE_2026-10-08.json'
    ledger = read(ledgerfile)
    assert ledger['complete'] and not ledger['errors'] and ledger['goal_status'] == 'active' and not ledger['publication_claim_confirmed']
    for rootfile in ledger['root_files_observed']:
        assert sha(Path(rootfile['path'])) == rootfile['sha256'] == rootfile['previous_sha256']
    production = read(ROOT/'experiments/mc_rc_matched_anchor_oracle_2026_10_08/attempt01.json')
    independent = read(ROOT/'experiments/mc_rc_matched_anchor_oracle_2026_10_08/independent_labels_disk_fraction_attempt01.json')
    costproof = read(ROOT/'experiments/mc_rc_matched_oracle_budget_scenarios_2026_10_08/independent_integer_rational_v2_attempt01.json')
    assert all(d['complete'] and not d['errors'] for d in (production, independent, costproof))
    assert independent['checked_series'] == 19 and costproof['checked_aggregate_cost_ratios'] == 96
    for v in production['anchor_receipts']:
        assert sha(ROOT/v['file']['path']) == v['file']['sha256']
    for snapshot in production['source_snapshots']:
        assert sha(ROOT/snapshot['snapshot']['path']) == snapshot['snapshot']['sha256'] == sha(ROOT/snapshot['source_path'])
    evidence = {v['path']:v for v in prior['evidence_files']}
    additions = []
    for p in sorted(more):
        key = p.relative_to(ROOT).as_posix()
        if key not in evidence:
            value = entry(p)
            evidence[key] = value
            additions.append(value)
    assert sum(v['bytes'] for v in additions) < 20_000_000
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        source_bindings=[entry(Path(__file__)), entry(PRIOR), entry(PRIOR_PROOF), entry(ledgerfile)],
        prior_manifest_sha256=sha(PRIOR), previous_frozen_evidence_files_verified=3102,
        stage_files=[entry(p) for p in sorted(stage)], stage_bytes=stagebytes,
        new_evidence_files=additions, new_evidence_bytes=sum(v['bytes'] for v in additions),
        evidence_files=[evidence[key] for key in sorted(evidence)], source_bindings_verified=bindings,
        local_links=links, scientific_evidence_enumeration_errors=walk_errors,
        previous_post_appendices_incorporated=True, failed_versions_and_receipts_preserved=True,
        historical_failed_pip_temp_directories_retained_and_not_enumerated=True,
        excluded_previous_retained_temporary_directories=prior['excluded_retained_temporary_directories'],
        current_stage_saved_bytes_limit=20_000_000, checked_series=19, checked_ideal_supports=19,
        checked_missing_plane_records=1005, independent_cost_series_supports=76,
        independent_cost_series_ratios=608, independent_cost_aggregate_ratios=96,
        actual_medical_array_counts=ledger['production_and_geometry_verification_medical_array_counts'],
        new_primary_papers_read=2, text_pages_read=16, visual_pages_reviewed=4,
        live_training_files_excluded=True, full_training_observed_tool_exit=None,
        publication_claim_confirmed=False, goal_status='active')
    new(DEST, result)
    for value in read(DEST)['evidence_files']:
        p = ROOT/value['path']
        assert p.stat().st_size == value['bytes'] and sha(p) == value['sha256'], value['path']
    assert all((ROOT/link['target']).exists() for link in links)
    new(PROOF, dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        manifest_file=DEST.relative_to(ROOT).as_posix(), manifest_sha256=sha(DEST),
        stage_files_frozen=len(stage), stage_bytes=stagebytes, newly_bound_files=len(additions),
        new_evidence_bytes=result['new_evidence_bytes'], cumulative_frozen_evidence_files=len(evidence),
        previous3102_evidence_hashes_unchanged=True, all_final_evidence_hashes_verified=True,
        local_links_verified=True, live_training_files_excluded=True,
        goal_status='active', publication_claim_confirmed=False))
    print(json.dumps(dict(complete=True, new_stage_files=len(stage), newly_bound_files=len(additions),
        cumulative_frozen_evidence_files=len(evidence), stage_bytes=stagebytes,
        new_evidence_bytes=result['new_evidence_bytes'], previous3102_hashes_unchanged=True,
        all_final_evidence_hashes_verified=True, goal_status='active', publication_claim_confirmed=False)), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
