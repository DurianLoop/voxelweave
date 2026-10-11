"""Append a directly cited primary and pinned implementation after immutable6580."""
import sys,time,json,re,gzip,hashlib,importlib.util,posixpath
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
PREV=ROOT/'pulse_sequence_and_forward_model_2026_10_09';SPATIAL=ROOT/'spatial_adaptation_matched_2026_10_08';FULL=ROOT/'full_real_intensity_v2_2026_10_09';DEV=ROOT/'development_capacity_after_matched_2026_10_09'
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    prev=PREV/'APPEND_INDEX.json';prevproof=PREV/'APPEND_PROOF.json'
    assert sha(prev)=='cf8b0189ccfae0d3162e9035d0e1c744b95381efc9cf0a02ce12a11deb179834'
    assert sha(prevproof)=='6d50040627f559a73f6d0e80c204d7c306f0d6bfb1c2ea6d64de9bd0fbc36695'
    q=read(prev);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6580
    chain=q['prior_chain']+[entry(prev)];prior=[]
    for b in chain:
        v=read(bind(b));assert v['complete'] and not v['errors'];prior.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6580
    medical_done=(SPATIAL/'ACTUAL_EVALUATION_EXIT.json').exists()
    full_done=(FULL/'full_real_terminal_audit_attempt01/receipt.json').exists()
    if medical_done:
        e=read(SPATIAL/'ACTUAL_EVALUATION_EXIT.json');tool=read(SPATIAL/'ACTUAL_EVALUATION_TERMINAL_TOOL.json')
        assert e['observed_tool_exit']==0 and e['observed_tool_session']==78123 and e['all36_strict_numeric_gates_passed']
        assert tool['exit_code']==0 and 'session_id' not in tool and tool['observed_unified_exec_session']==78123
        assert e['result_sha256']==sha(ROOT/e['result_file'])
        cmp=read(SPATIAL/'FINAL_MATCHED_COMPARISON.json');assert cmp['complete'] and not cmp['errors']
    # Only development preparation and its immutable config are included here.
    # A later index must capture the genuinely completed development evaluation.
    closed={SPATIAL/'evaluation_attempt01':medical_done,FULL/'full_real_pipeline_attempt01':full_done,DEV/'evaluation_attempt01':False}
    def allowed(p):return all(done or not p.is_relative_to(folder) or p==folder/'frozen_config.json' for folder,done in closed.items())
    def keep(p):return p.is_file() and allowed(p) and '__pycache__' not in p.parts and not p.name.endswith('.raw.json')
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_frozen_hashes_verified=i)),flush=True)
    r=read(HERE/'READING_PROVENANCE.json');assert r['complete'] and not r['errors'] and r['new_distinct_primary_maintexts_actually_read']==1
    assert r['author_repository_files_actually_read']==5 and r['author_source_and_document_lines']==914 and r['result_data_tables']==0
    author={bind(a['source_binding']):a['author_path'] for a in r['author_sources']}
    tree=read(HERE/'author_tree_attempt01/receipt.json');repo_paths={v['path'] for v in tree['files']}
    sources={p for folder in [HERE,SPATIAL,FULL] for p in folder.rglob('*') if keep(p) and p not in [index,proof]}
    sources.update(p for p in DEV.iterdir() if keep(p))
    sources.add(DEV/'evaluation_attempt01/frozen_config.json')
    sources.update(p for p in PREV.iterdir() if p.is_file());sources.update(ROOT/b['path'] for b in chain);sources.add(prevproof)
    opaque={ROOT/b['path'] for b in chain}|{prevproof};pending=set(sources);scanned=set();binding_count=0;link_count=0;repo_link_count=0
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file() and allowed(p)
        if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
        if p.suffix=='.json':
            v=read(p)
            if p.name.startswith('OBSERVATION_COMPRESSION_RECEIPT_'):
                for b in v['records']:
                    local=Path(b['path']);assert not local.is_absolute() and local.name==b['path']
                    target=(p.parent/local).resolve();assert target.parent==HERE
                    assert target.stat().st_size==b['bytes'] and sha(target)==b['sha256']
                    with gzip.open(target,'rb') as f:data=f.read()
                    assert len(data)==b['uncompressed_bytes'] and hashlib.sha256(data).hexdigest()==b['uncompressed_sha256']
                    if target not in sources:sources.add(target);pending.add(target)
                    binding_count+=1
            else:
                for b in bindings(v):
                    target=bind(b);assert allowed(target)
                    if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
                    binding_count+=1
        elif p.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):continue
                if p in author:
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(author[p]),raw.split('#',1)[0]));assert target in repo_paths,raw
                    repo_link_count+=1;continue
                target=Path(raw.strip('<>').split('#',1)[0])
                if not target.is_absolute():target=p.parent/target
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT) and allowed(target),raw
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                link_count+=1
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    for b in r['root_file_bindings']:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='one_original_sampling_mask_primary_and_pinned_author_source_after6580',
        prior_chain=chain,previous6580_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=6580+len(new),
        new_source_binding_checks=binding_count,new_local_link_checks=link_count,new_author_repo_relative_link_checks=repo_link_count,
        new_distinct_primary_maintexts_actually_read=1,new_author_files_wholly_read=5,new_author_file_lines=914,formula_layout_nodes_text_read=25,result_data_tables=0,
        original_matched_medical_evaluation_completed_and_audited=medical_done,all_new_branches_medical_gates_passed=e['all_four_medical_gates_passed'] if medical_done else None,
        full35904_actual_terminal_independently_audited=full_done,unfinished_rolling_outputs_excluded_except_frozen_configs=True,
        development_preparation_and_frozen_config_included=True,development_rolling_receipt_and_predictions_excluded=True,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+100000<2_000_000
    res=resource_guard();assert res['workspace_free_bytes']-estimate-100000-3_000_000-2_000_000-2_800_000>=8_000_000_000
    dump(index,result)
    outcome=dict(complete=True,errors=[],append_index=entry(index),previous6580_frozen_hashes_verified=True,new_frozen_hashes_verified=True,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6580+len(new),new_distinct_primary_maintexts=1,new_author_files=5,new_author_lines=914,author_implementation_executed=False,
        original_matched_medical_evaluation_completed_and_audited=medical_done,all_new_branches_medical_gates_passed=result['all_new_branches_medical_gates_passed'],
        unfinished_full_replay_excluded=not full_done,root_files_unchanged=True,publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,outcome);print(json.dumps(outcome),flush=True)
if __name__=='__main__':main()
