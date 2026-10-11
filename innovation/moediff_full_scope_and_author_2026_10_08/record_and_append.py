"""Verify the 5460-file prior chain and append this scientific reading/source audit."""
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FULL = ROOT/'lossless_final_evaluation_entry_2026_10_08'
PREVIOUS = ROOT/'task_routing_author_source_2026_10_08'
WATCH = ROOT/'training_finalization_watch_2026_10_08'
sys.path.insert(0, str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def entry(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size, sha256=sha(path))


def binding_path(binding):
    path = (ROOT/binding['path']).resolve()
    allowed_roots = {(ROOT.parent/'.gitignore').resolve(), (ROOT.parent/'environment.yml').resolve()}
    assert path.is_relative_to(ROOT.resolve()) or path in allowed_roots, binding['path']
    assert path.is_file() and sha(path)==binding['sha256'], binding['path']
    if 'bytes' in binding:
        assert path.stat().st_size==binding['bytes'], binding['path']
    return path


def bindings(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            yield value
        for child in value.values():
            yield from bindings(child)
    elif isinstance(value, list):
        for child in value:
            yield from bindings(child)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    client.base.own_priority()
    started = time.perf_counter()
    resources = client.resource_guard()
    index_path, proof_path, ledger_path = [HERE/n for n in ['APPEND_INDEX.json','APPEND_PROOF.json','EXECUTION_LEDGER.json']]
    assert not any(p.exists() for p in [index_path, proof_path, ledger_path])
    full_manifest, full_proof = FULL/'ARCHIVE_MANIFEST.json', FULL/'ARCHIVE_PROOF.json'
    old_index, old_proof = PREVIOUS/'APPEND_INDEX.json', PREVIOUS/'APPEND_PROOF.json'
    assert sha(full_manifest)=='d6481cf77e2e46303c4433969ac37804034ba0f70fbfa487570378abb696658e'
    assert sha(full_proof)=='258d257d14079cd721004cfe90d9fdf25c2e1373163d2a44c51147fe33d05241'
    assert sha(old_index)=='274c0f1c5713e45f38d3e57a3b4b2d19bb9ffb90b3a121d6f81c6acf60ca7d39'
    assert sha(old_proof)=='97dc7cd533cb0d4d589727a8244834665d0d6a42774c09b76384af6aab0e9141'
    prior_full, prior_delta = read(full_manifest), read(old_index)
    for q in [prior_full, prior_delta, read(full_proof), read(old_proof)]:
        assert q['complete'] and not q['errors']
    assert len(prior_full['evidence_files'])==5430 and len(prior_delta['new_evidence_files'])==30
    previous = prior_full['evidence_files']+prior_delta['new_evidence_files']
    existing = {b['path']: b for b in previous}
    assert len(previous)==len(existing)==5460
    for number, binding in enumerate(previous, 1):
        binding_path(binding)
        if number%1500==0:
            print(json.dumps(dict(prior_evidence_hashes_verified=number)), flush=True)
            client.resource_guard()
    provenance = read(HERE/'READING_PROVENANCE.json')
    cpu = read(HERE/'cpu_audit_attempt01/receipt.json')
    extraction = read(HERE/'primary_attempt02/receipt.json')
    author = read(HERE/'sources_attempt01/receipt.json')
    for q in [cpu, extraction, author]:
        assert q['complete'] and not q['errors']
    assert provenance['actual_text_pages_this_stage']==list(range(1,11))
    assert provenance['actual_visual_pages_this_stage']==[1,4,6,7,8,9]
    assert len(provenance['actual_author_implementation_files_completely_read'])==5
    assert cpu['printed_table_rows_audited']==15 and cpu['printed_weight_vectors_audited']==1
    assert cpu['author_implementation_files_AST_parsed']==5 and not cpu['author_code_executed']
    assert len(author['records'])==5 and all(r['HTTP_status']==200 for r in author['records'])
    roots=[]
    for name, expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        assert sha(ROOT.parent/name)==expected
        roots.append(dict(absolute_path=str(ROOT.parent/name), sha256=expected))
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        previous_goal_turn_classification='verified_wait', current_goal_turn_classification='progress',
        new_independent_papers_read=0, existing_papers_full_scope_completed=1,
        text_pages_actually_read_this_stage=10, newly_completed_main_pages=[7,8], newly_completed_reference_pages=[10],
        visual_pages_actually_reviewed=6, author_README_files_read=1,
        author_implementation_files_read=5, author_implementation_files_AST_parsed=5,
        public_table_rows_audited=15, public_weight_vectors_audited=1,
        author_code_executed=False, medical_arrays_loaded=0, model_checkpoint_arrays_loaded=0,
        neural_forwards=0, GPU_forwards=0, new_medical_training_jobs=0, head_fits=0, new_action_labels=0,
        original_training_modified=False, new_agents_delegated=0, other_processes_modified=False,
        previous_evidence_hashes_verified=5460, root_files_observed=roots,
        confirmation_patients_opened=False, lockedIXI_opened=False,
        GPU_user_authorization_present=True, latest_GPU_free_MiB=1394,
        latest_actual_raw_updates=11880, actual_original_terminal_exit=None,
        original_contract=dict(per_arm_updates=19998,total_updates=39996,cumulative_wall_limit_hours=30),
        automatic_approval_review_rejections_received=0, publication_claim_confirmed=False, goal_status='active',
        source_bindings=[entry(p) for p in [Path(__file__), HERE/'PROTOCOL.md', HERE/'READING_PROVENANCE.json',
            HERE/'OBSERVED_TOOL_RESULTS.json', HERE/'VISIBLE_DIALOGUE.md', HERE/'PRIMARY_AND_SOURCE_READING.md',
            HERE/'FULL_FLOW_DENSE_ENSEMBLE_CONTROL_PREPARATION.md', HERE/'RESULT.md', HERE/'prepare_primary_v2.py',
            HERE/'cpu_audit_attempt01/receipt.json']], resource_snapshot=resources)
    client.base.new(ledger_path, ledger)
    stage={p for p in HERE.rglob('*') if p.is_file() and p not in [index_path,proof_path]}
    assert not any(p.suffix=='.pyc' for p in stage)
    assert sum(p.stat().st_size for p in stage)<6_000_000
    post={PREVIOUS/n for n in ['APPEND_INDEX.json','APPEND_PROOF.json','POST_APPEND_TOOL_OBSERVATIONS.json','NEXT_STAGE_HANDOFF.md']}
    watch={p for p in WATCH.rglob('*') if p.is_file()}
    assert len(list(WATCH.glob('turn_*_input.json')))==8
    more=stage|post|watch
    verified=[]
    links=[]
    for path in sorted(more):
        if path.suffix=='.json':
            for binding in bindings(read(path)):
                target=binding_path(binding)
                if target.is_relative_to(ROOT.resolve()):
                    more.add(target)
                verified.append(dict(document=path.relative_to(ROOT).as_posix(), **binding))
        elif path.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):
                    continue
                target=(path.parent/raw.split('#',1)[0]).resolve()
                assert target.exists() and target.is_relative_to(ROOT.resolve()), raw
                if target.is_file():
                    more.add(target)
                links.append(dict(document=path.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()))
    forbidden={'invocation02.json','native_reference_resume.pt','raw_pchip_resume.pt',
        'native_reference_history.jsonl','raw_pchip_history.jsonl'}
    assert not any(p.name in forbidden for p in more)
    additions=[entry(p) for p in sorted(more) if p.relative_to(ROOT).as_posix() not in existing]
    index=dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        index_kind='immutable_delta_after_full5430_and_prior_delta30',
        prior_full_manifest=entry(full_manifest), prior_full_proof=entry(full_proof),
        prior_append_index=entry(old_index), prior_append_proof=entry(old_proof),
        previous_frozen_evidence_files_verified=5460, new_evidence_files=additions,
        newly_bound_files=len(additions), cumulative_frozen_evidence_files=5460+len(additions),
        stage_files=[entry(p) for p in sorted(stage)], source_bindings_verified=verified,
        local_links_verified=links, prior_post_four_files_incorporated=True,
        watch_turns4_through8_incorporated=True, live_training_files_excluded=True,
        publication_claim_confirmed=False, goal_status='active')
    client.base.new(index_path,index)
    for binding in additions:
        binding_path(binding)
    output=dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        append_index=entry(index_path), previous5460_evidence_hashes_unchanged=True,
        all_new_evidence_hashes_verified=True, all_source_bindings_verified=True, all_local_links_verified=True,
        prior_post_four_files_incorporated=True, watch_turns4_through8_incorporated=True,
        newly_bound_files=len(additions), cumulative_frozen_evidence_files=5460+len(additions),
        new_independent_papers_read=0, existing_papers_full_scope_completed=1,
        text_pages_actually_read_this_stage=10, visual_pages_actually_reviewed=6,
        author_source_files_read=5, public_table_rows_audited=15, author_code_executed=False,
        actual_medical_evaluation_started=False, original_training_modified=False,
        publication_claim_confirmed=False, goal_status='active',
        resource_snapshot=client.resource_guard(), elapsed_seconds=time.perf_counter()-started)
    client.base.new(proof_path,output)
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<6_000_000
    print(json.dumps(output,ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
