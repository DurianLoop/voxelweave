"""Append two direct primaries and all fixed toy cases after immutable prior6515."""
import sys,time,json,re,gzip,hashlib,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
PREV=ROOT/'synthsr_psacnn_followup_2026_10_09';SPATIAL=ROOT/'spatial_adaptation_matched_2026_10_08';FULL=ROOT/'full_real_intensity_v2_2026_10_09'

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    prev=PREV/'APPEND_INDEX.json';prevproof=PREV/'APPEND_PROOF.json'
    assert sha(prev)=='f975b6febd911bc10985eafcb85d79ebf241895c02ea98376214cb38970c0b67'
    assert sha(prevproof)=='855e082d2ffdc7493c6c05fbc36e911c7a4346a4a6b7ca2d75fdd6bb86c08815'
    q=read(prev);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6515
    chain=q['prior_chain']+[entry(prev)];prior=[]
    for b in chain:
        v=read(bind(b));assert v['complete'] and not v['errors'];prior.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6515
    training_done=(SPATIAL/'ACTUAL_TRAINING_EXIT.json').is_file()
    evaluation_done=(SPATIAL/'ACTUAL_EVALUATION_EXIT.json').is_file()
    full_done=(FULL/'full_real_terminal_audit_attempt01/receipt.json').is_file()
    if training_done:
        t=read(SPATIAL/'ACTUAL_TRAINING_EXIT.json');term=read(SPATIAL/'ACTUAL_TRAINING_TERMINAL_TOOL.json')
        assert t['observed_tool_exit']==0 and t['observed_tool_session']==29823 and t['all11968_history_rows_verified']
        assert term['exit_code']==0 and 'session_id' not in term and term['observed_unified_exec_session']==29823
        assert t['result_sha256']==sha(ROOT/t['result_file'])
    if evaluation_done:
        assert training_done;e=read(SPATIAL/'ACTUAL_EVALUATION_EXIT.json')
        assert e['observed_tool_exit']==0 and e['all36_strict_numeric_gates_passed']
        assert e['result_sha256']==sha(ROOT/e['result_file'])
        comparison=read(SPATIAL/'FINAL_MATCHED_COMPARISON.json');assert comparison['complete'] and not comparison['errors']
    # Unfinished scientific stage outputs must never become immutable evidence prematurely.
    closed={SPATIAL/'training_attempt01':training_done,SPATIAL/'evaluation_attempt01':evaluation_done,
        FULL/'full_real_pipeline_attempt01':full_done}
    def allowed(p):return all(done or not p.is_relative_to(folder) or p==folder/'frozen_config.json' for folder,done in closed.items())
    def keep(p):return p.is_file() and allowed(p) and '__pycache__' not in p.parts and not p.name.endswith('.raw.json')
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_frozen_hashes_verified=i)),flush=True)
    r=read(HERE/'READING_PROVENANCE.json');assert r['complete'] and not r['errors'] and r['new_distinct_primary_maintexts_actually_read']==2
    assert r['all39_HTML_nodes_independently_audited'] and r['piecewise_cases']==1080 and r['sphere_groups']==384
    sources={p for folder in [HERE,SPATIAL,FULL] for p in folder.rglob('*') if keep(p) and p not in [index,proof]}
    sources.update(p for p in PREV.iterdir() if p.is_file())
    sources.update(ROOT/b['path'] for b in chain);sources.add(prevproof)
    opaque={ROOT/b['path'] for b in chain}|{prevproof};pending=set(sources);scanned=set();binding_count=0;link_count=0
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
                target=Path(raw.strip('<>').split('#',1)[0])
                if not target.is_absolute():target=p.parent/target
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT) and allowed(target),raw
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                link_count+=1
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    for b in r['root_file_bindings']:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='two_acquisition_primaries_and_fixed_measurement_contract_after6515',
        prior_chain=chain,previous6515_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=6515+len(new),
        new_source_binding_checks=binding_count,new_local_link_checks=link_count,new_distinct_primary_maintexts_actually_read=2,
        nonformula_tables_read=8,formula_HTML_nodes_text_read=31,piecewise_toy_cases=1080,continuous_sphere_toy_groups=384,
        original_training_terminal_observed_and_audited=training_done,matched_medical_evaluation_completed=evaluation_done,
        all_new_branches_medical_gates_passed=e['all_four_medical_gates_passed'] if evaluation_done else None,
        full35904_actual_terminal_independently_audited=full_done,remaining_rolling_outputs_excluded_except_frozen_configs=True,
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+100000<3_000_000
    resources=resource_guard();assert resources['workspace_free_bytes']-estimate-100000-3_000_000-2_000_000>=8_000_000_000
    dump(index,result)
    outcome=dict(complete=True,errors=[],append_index=entry(index),previous6515_frozen_hashes_verified=True,new_frozen_hashes_verified=True,
        newly_bound_files=len(new),cumulative_frozen_evidence_files=6515+len(new),new_primary_maintexts=2,nonformula_tables=8,
        piecewise_toy_cases=1080,continuous_sphere_toy_groups=384,matched_training_terminal_audited=training_done,
        matched_medical_evaluation_completed=evaluation_done,all_new_branches_medical_gates_passed=result['all_new_branches_medical_gates_passed'],
        unfinished_full_replay_excluded=not full_done,root_files_unchanged=True,publication_claim_confirmed=False,
        goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,outcome);print(json.dumps(outcome),flush=True)
if __name__=='__main__':main()
