"""Append the pinned README audit while verifying prior immutable evidence.

No training control, tensor/model/data loading, author-code execution, or network.
This delta index references the prior full manifest without copying it.
"""
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREVIOUS = ROOT / 'lossless_final_evaluation_entry_2026_10_08'
WATCH = ROOT / 'training_finalization_watch_2026_10_08'
sys.path.insert(0, str(ROOT / 'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1_048_576), b''):
            h.update(block)
    return h.hexdigest()


def entry(path):
    return dict(path=path.relative_to(ROOT).as_posix(),
                bytes=path.stat().st_size, sha256=sha(path))


def check_binding(binding):
    path = (ROOT / binding['path']).resolve()
    assert path.is_relative_to(ROOT.resolve()) and path.is_file(), binding['path']
    assert sha(path) == binding['sha256'], binding['path']
    if 'bytes' in binding:
        assert path.stat().st_size == binding['bytes'], binding['path']


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    client.base.own_priority()
    resources_before = client.resource_guard()
    started = time.perf_counter()
    ledger_path = HERE / 'EXECUTION_LEDGER.json'
    index_path = HERE / 'APPEND_INDEX.json'
    proof_path = HERE / 'APPEND_PROOF.json'
    assert not any(p.exists() for p in (ledger_path, index_path, proof_path))
    prior_manifest = PREVIOUS / 'ARCHIVE_MANIFEST.json'
    prior_proof = PREVIOUS / 'ARCHIVE_PROOF.json'
    before = read(prior_manifest)
    proof = read(prior_proof)
    assert before['complete'] and not before['errors']
    assert proof['complete'] and not proof['errors']
    assert len(before['evidence_files']) == proof['cumulative_frozen_evidence_files'] == 5430
    assert sha(prior_manifest) == proof['manifest_sha256'] == 'd6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e'
    assert sha(prior_proof) == '258d257d14079cd721004cfe90d9fdf25c2e1373163d2a44c51147fe33d05241'
    for index, binding in enumerate(before['evidence_files'], 1):
        check_binding(binding)
        if index % 1500 == 0:
            print(json.dumps(dict(prior_evidence_hashes_verified=index)), flush=True)
            client.resource_guard()
    fetch_receipt = read(HERE / 'identity_attempt01/receipt.json')
    identity = read(HERE / 'identity_attempt01/visible_identity.json')
    assert fetch_receipt['complete'] and not fetch_receipt['errors']
    assert identity['current_commit'] == '74138572a1a0ac625927478d03db0f6d8036cc53'
    assert identity['root_tree_items'] == [dict(name='README.md', path='README.md', contentType='file')]
    assert identity['complete_recursive_tree_verified'] is False
    for binding in fetch_receipt['source_bindings']:
        check_binding(binding)
    for record in fetch_receipt['records']:
        assert record['complete'] and not record['errors'] and record['HTTP_status'] == 200
        check_binding(record['response_binding'])
    author_readme = HERE / 'identity_attempt01/README.source.txt'
    assert author_readme.stat().st_size == 282
    assert sha(author_readme) == '957bb0fad35f6a28ad712ef0699aa272f788eb0bd57bc243881991883a6410e4'
    assert 'Coming soon!' in author_readme.read_text(encoding='utf-8')
    actual = read(HERE / 'OBSERVED_TOOL_RESULTS.json')
    final = read(HERE / 'FINAL_READINESS_AND_WATCH.json')
    assert actual['actual_README_complete_read']['exit_code'] == 0
    assert actual['author_README_files_read'] == 1 and actual['author_implementation_files_read'] == 0
    assert final['actual_poll']['session_id'] == 99542
    assert final['actual_poll']['tool_confirmed_live'] and final['actual_poll']['terminal_exit'] is None
    assert final['actual_readiness']['exit_code'] == 3
    assert final['actual_readiness']['MR_or_GT_arrays_loaded'] == 0
    assert not final['actual_readiness']['CUDA_initialized']
    assert not (PREVIOUS / 'medical_attempt03').exists()
    for binding in read(PREVIOUS / 'compression_qualification_v3/receipt.json')['production_bindings']:
        check_binding(binding)
    root_hashes = []
    for name, expected in [
        ('.gitignore', '7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml', 'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')
    ]:
        path = ROOT.parent / name
        assert sha(path) == expected
        root_hashes.append(dict(path=str(path), sha256=expected))
    zeros = {key: 0 for key in [
        'new_primary_papers_read', 'new_full_text_pages_read', 'new_visual_pages_reviewed',
        'author_implementation_files_read', 'medical_arrays_loaded',
        'model_checkpoint_arrays_loaded_from_disk', 'neural_forwards', 'GPU_forwards',
        'new_medical_training_updates', 'head_fits', 'new_action_labels_generated', 'new_agents_delegated'
    ]}
    ledger = dict(
        created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[], **zeros,
        author_README_files_completely_read=1, author_README_bytes=282,
        author_code_executed=False, complete_recursive_tree_verified=False,
        original_training_modified=False, other_processes_modified=False,
        author_implementation_availability_beyond_observed_files='unknown',
        latest_actual_poll=final['actual_poll'], actual_readiness=final['actual_readiness'],
        GPU_user_authorization_present=True, actual_GPU_snapshot=actual['GPU_query'],
        new_GPU_job_started=False, current_original_contract=dict(
            per_arm_updates=19998, total_updates=39996, cumulative_wall_limit_hours=30),
        root_files_observed=root_hashes, confirmation_patients_opened=False,
        lockedIXI_opened=False, publication_claim_confirmed=False, goal_status='active',
        stage_classification='author_source_availability_audit_and_verified_wait',
        original_actual_terminal_exit=None, previous_frozen_evidence_files_verified=5430,
        automatic_approval_review_rejections_received=0,
        source_bindings=[entry(p) for p in [Path(__file__), HERE/'SOURCE_AUDIT.md',
            HERE/'NEXT_MEDICAL_STEP.md', HERE/'OBSERVED_TOOL_RESULTS.json',
            HERE/'FINAL_READINESS_AND_WATCH.json', HERE/'VISIBLE_DIALOGUE_CONTINUED.md',
            HERE/'RECEIVED_HANDOFF.md', HERE/'RESULT.md', author_readme]],
        resource_snapshot=resources_before)
    client.base.new(ledger_path, ledger)
    stage = {p for p in HERE.rglob('*') if p.is_file() and p not in (index_path, proof_path)}
    assert not any(p.suffix == '.pyc' for p in stage)
    assert sum(p.stat().st_size for p in stage) < 3_000_000
    prior_post_files = {PREVIOUS / name for name in [
        'ARCHIVE_MANIFEST.json', 'ARCHIVE_PROOF.json', 'record_post_archive.py',
        'POST_ARCHIVE_INPUT.json', 'POST_ARCHIVE_OBSERVATIONS.json'
    ]}
    watch_files = {p for p in WATCH.rglob('*') if p.is_file()}
    assert len(list(WATCH.glob('turn_*_input.json'))) == 3
    assert len(list(WATCH.glob('turn_*_observation.json'))) == 3
    for path in WATCH.glob('turn_*_observation.json'):
        watch = read(path)
        assert watch['complete'] and not watch['errors']
        assert watch['turn_classification'] == 'verified_wait'
        for binding in watch['source_bindings']:
            check_binding(binding)
    more = stage | prior_post_files | watch_files
    verified_source_bindings = []
    local_links = []
    for path in sorted(stage):
        if path.suffix == '.json':
            payload = read(path)
            if isinstance(payload, dict):
                for binding in payload.get('source_bindings', []) + payload.get('production_bindings', []):
                    check_binding(binding)
                    more.add(ROOT / binding['path'])
                    verified_source_bindings.append(dict(document=path.relative_to(ROOT).as_posix(), **binding))
        elif path.suffix == '.md':
            for raw in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://', raw):
                    continue
                target = (path.parent / raw.split('#', 1)[0]).resolve()
                assert target.is_relative_to(ROOT.resolve()) and target.exists(), raw
                if target.is_file():
                    more.add(target)
                local_links.append(dict(document=path.relative_to(ROOT).as_posix(), target=target.relative_to(ROOT).as_posix()))
    forbidden = {'invocation02.json', 'native_reference_resume.pt', 'raw_pchip_resume.pt',
                 'native_reference_history.jsonl', 'raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    prior_names = {binding['path'] for binding in before['evidence_files']}
    additions = [entry(p) for p in sorted(more) if p.relative_to(ROOT).as_posix() not in prior_names]
    index = dict(
        created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        index_kind='immutable_delta_to_prior_full_manifest',
        prior_full_manifest=entry(prior_manifest), prior_full_proof=entry(prior_proof),
        previous_frozen_evidence_files_verified=5430,
        new_evidence_files=additions, newly_bound_files=len(additions),
        cumulative_frozen_evidence_files=5430+len(additions),
        prior_post_five_files=[entry(p) for p in sorted(prior_post_files)],
        training_watch_files=[entry(p) for p in sorted(watch_files)],
        stage_files=[entry(p) for p in sorted(stage)],
        source_bindings_verified=verified_source_bindings, local_links_verified=local_links,
        live_training_files_excluded=True, publication_claim_confirmed=False, goal_status='active')
    client.base.new(index_path, index)
    for binding in additions:
        check_binding(binding)
    result = dict(
        created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        append_index=entry(index_path), previous5430_evidence_hashes_unchanged=True,
        all_new_evidence_hashes_verified=True, all_source_bindings_verified=True,
        all_local_links_verified=True, prior_post_five_files_incorporated=True,
        first_three_watch_turns_incorporated=True, newly_bound_files=len(additions),
        cumulative_frozen_evidence_files=5430+len(additions),
        author_README_files_completely_read=1, author_implementation_files_read=0,
        actual_medical_evaluation_started=False, original_training_modified=False,
        medical_arrays_loaded=0, neural_forwards=0, GPU_forwards=0,
        automatic_approval_review_rejections_received=0,
        publication_claim_confirmed=False, goal_status='active',
        resource_snapshot=client.resource_guard(), elapsed_seconds=time.perf_counter()-started)
    client.base.new(proof_path, result)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file()) < 3_000_000
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
