"""Verify previous6923 logical hashes and append substantive reading and ended-failure evidence."""
import importlib.util,json,re,sys,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(helper,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    indexpath=HERE/'APPEND_INDEX.json';proofpath=HERE/'APPEND_PROOF.json';assert not indexpath.exists() and not proofpath.exists()
    prev=ROOT/'uncertainty_dmri_primary_completion_2026_10_09'
    previous=prev/'APPEND_CAPACITY_INDEX.json';previous_proof=prev/'APPEND_CAPACITY_PROOF.json'
    assert sha(previous)=='3d4514b07456ea239c7f91ba20af3f36902362613f50ff72fe5ddb5cb07f2a96'
    assert sha(previous_proof)=='399977a77f7f76132d15a84e75f8623e85baa1dae7c727e6709d9c99a8461197'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6923
    chain=q['prior_chain']+[entry(previous)];old=[]
    for b in chain:
        v=read(bind(b));assert v['complete'] and not v['errors'];old.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in old};assert len(old)==len(existing)==6923
    for i,b in enumerate(old,1):
        bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_frozen_hashes_verified=i)),flush=True)
        assert time.perf_counter()-started<1200
    reading=read(HERE/'READING_PROVENANCE.json');assert reading['complete'] and not reading['errors'] and reading['new_distinct_primary_maintexts_actually_read']==3 and reading['blocks_actually_read']==414
    primary=read(HERE/'primary_xml_attempt01/receipt.json');assert primary['complete'] and len(primary['records'])==3
    for paper in primary['records']:
        assert paper['identity_verified'];bind(paper['source'])
        for b in paper['extraction_sources']:bind(b)
    compression=read(HERE/'compression_attempt01/receipt.json');assert compression['complete'] and not compression['errors'] and compression['all40_frozen_logical_bytes_and_hashes_verified']
    for row in compression['files']:assert row['logical_bytes_and_SHA_unchanged'];bind(row['source_binding'])
    diagnostic=read(HERE/'cpu_diagnostics_attempt01/receipt.json');assert diagnostic['complete'] and not diagnostic['errors'] and diagnostic['diagnostics_completed']==5
    audit=read(HERE/'failed_v2_terminal_audit_attempt01/receipt.json');assert audit['complete'] and audit['actual_exit']==1 and audit['all14673_unique_journal_rows_exact_prefix_verified']
    replay=read(HERE/'failed_v2_field_diagnostic_attempt01/receipt.json');assert replay['complete'] and replay['failed_v2_field_reproduced'] and replay['observed_errors']['full']>3e-6
    exact=read(HERE/'exact_interpolation_witness_attempt01/receipt.json');assert exact['complete'] and exact['exact_round_restored_matches_production'] and not exact['full_pipeline_repaired']
    failed=ROOT/'full_real_intensity_v2_2026_10_09';terminal=read(failed/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json')
    assert terminal['exit_code']==1 and 'session_id' not in terminal and terminal['observed_unified_exec_session']==90446
    sources={p for folder in [HERE,failed] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [indexpath,proofpath]}
    sources.update(p for p in prev.iterdir() if p.is_file());sources.update(ROOT/b['path'] for b in chain);sources.add(previous_proof)
    opaque={ROOT/b['path'] for b in chain}|{previous_proof};pending=set(sources);scanned=set();binding_count=link_count=0
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        scanned.add(p);assert p.is_file()
        if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=bind(b)
                if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
                binding_count+=1
        elif p.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):continue
                target=Path(raw.strip('<>').split('#',1)[0])
                if not target.is_absolute():target=p.parent/target
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT),raw
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                link_count+=1
        assert time.perf_counter()-started<1200
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='three_generalization_primaries_and_actual_failed14673_pipeline_after6923',
        prior_chain=chain,previous6923_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6923+len(new),source_binding_checks=binding_count,local_link_checks=link_count,
        new_distinct_primary_maintexts_actually_read=3,maintext_blocks_actually_read=414,data_tables_read=16,
        synthetic_CPU_diagnostics=5,transparent_compression_frozen_files=40,all40_logical_SHA_unchanged=True,
        complete_six_branch_forecast_admitted=False,actual_full_qualification_terminal_exit=1,failed_prefix_fields=14673,
        exact_prefix_audited=True,failed_field_reproduced=True,single_exact_halfULP_witness_verified=True,
        full35904_numeric_qualification_passed=False,new_training_launched=False,former_rolling_outputs_now_terminal_frozen=True,
        confirmation_patients_opened=False,lockedIXI_opened=False,independent_medical_confirmation=False,
        publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+20_000<2_000_000
    res=resource_guard();assert res['workspace_free_bytes']-estimate-20_000-2_000_000-3_000_000-2_800_000>=8_000_000_000
    dump(indexpath,result)
    out=dict(complete=True,errors=[],append_index=entry(indexpath),previous6923_frozen_hashes_verified=True,
        new_frozen_hashes_verified=True,newly_bound_files=len(new),cumulative_frozen_evidence_files=6923+len(new),
        new_primary_maintexts=3,maintext_blocks=414,actual_full_qualification_exit=1,failed_prefix_fields=14673,
        full_qualification_passed=False,new_training_launched=False,publication_claim_confirmed=False,goal_status='active',
        resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proofpath,out);print(json.dumps(out,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
