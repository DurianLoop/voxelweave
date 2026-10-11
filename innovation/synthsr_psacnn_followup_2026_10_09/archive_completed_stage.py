"""Verify prior6441 and append completed reading/repair; exclude two live stages."""
import sys,time,json,re,gzip,hashlib,importlib.util
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('immutable_archive_helpers',ROOT/'final_training_medical_execution_2026_10_08/archive_completed_stage.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
read,sha,entry,bind,bindings,dump,resource_guard=[getattr(h,k) for k in ['read','sha','entry','bind','bindings','dump','resource_guard']]
REPAIR=ROOT/'intensity_precision_failure_diagnosis_2026_10_09'
NEWFULL=ROOT/'full_real_intensity_v2_2026_10_09'
OLD=ROOT/'resolution_degradation_controls_2026_10_08'
LIVE=[ROOT/'spatial_adaptation_matched_2026_10_08/training_attempt01',NEWFULL/'full_real_pipeline_attempt01']
def allowed(p):return all(not p.is_relative_to(d) or p==d/'frozen_config.json' for d in LIVE)
def keep(p):return p.is_file() and allowed(p) and '__pycache__' not in p.parts and not p.name.endswith('.raw.json')
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resource_guard()
    index=HERE/'APPEND_INDEX.json';proof=HERE/'APPEND_PROOF.json';assert not index.exists() and not proof.exists()
    prev=ROOT/'resolution_and_lesion_primary_completion_2026_10_09/APPEND_INDEX.json';prevproof=prev.parent/'APPEND_PROOF.json'
    assert sha(prev)=='6c480a23fc223f1e7bdccae5c2f8831c52e5e25defe22bb8b9e2ab0bca7f8d75'
    assert sha(prevproof)=='87c1bb27f2929b762a791dd7e16f65f6c2a9bbd57ba39f88c9404fa6bbd0df95'
    q=read(prev);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6441
    chain=q['prior_chain']+[entry(prev)];prior=[]
    for b in chain:
        v=read(bind(b));assert v['complete'] and not v['errors'];prior.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in prior};assert len(prior)==len(existing)==6441
    for i,b in enumerate(prior,1):
        assert allowed(ROOT/b['path']);bind(b)
        if i%2000==0:resource_guard();print(json.dumps(dict(previous_frozen_hashes_verified=i)),flush=True)
    rp=read(HERE/'READING_PROVENANCE.json');assert rp['complete'] and not rp['errors'] and rp['new_distinct_primary_maintexts_actually_read']==2
    repaired=read(REPAIR/'ACTUAL_REPAIRED_STRESS_TERMINAL_TOOL.json');assert repaired['exit_code']==0 and 'session_id' not in repaired and repaired['observed_unified_exec_session']==47298
    ra=read(REPAIR/'repaired_terminal_audit_attempt01/receipt.json');assert ra['complete'] and not ra['errors'] and ra['all271_exact_identity_sets_and_numeric_gates_verified']
    failed=read(OLD/'ACTUAL_FULL_REAL_PIPELINE_TERMINAL_TOOL.json');assert failed['exit_code']==1 and 'session_id' not in failed and failed['observed_unified_exec_session']==74234
    fa=read(REPAIR/'failed_terminal_audit_attempt01/receipt.json');assert fa['complete'] and not fa['errors'] and not fa['original_full_qualification_passed']
    sources={p for folder in [HERE,REPAIR,NEWFULL,OLD] for p in folder.rglob('*') if keep(p) and p not in [index,proof]}
    sources.update(ROOT/b['path'] for b in chain);sources.add(prevproof)
    sources.add(LIVE[0]/'frozen_config.json')
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
    for b in rp['root_file_bindings']:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='two_primary_readings_completed_repair_and_failed_full_stage_after6441',
        prior_chain=chain,previous6441_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),cumulative_frozen_evidence_files=6441+len(new),
        new_source_binding_checks=binding_count,new_local_link_checks=link_count,new_distinct_primary_maintexts_actually_read=2,original_tables_read=5,
        old_full_real_pipeline_actual_exit=1,repaired271_actual_exit=0,repaired271_independent_audit_complete=True,
        original_training_session=29823,new_full_real_pipeline_session=90446,both_current_stages_actual_terminal_not_observed=True,
        current_rolling_outputs_excluded_except_frozen_configs=True,new_patient_medical_effects=0,confirmation_patients_opened=False,
        publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+100000<4_000_000
    resources=resource_guard();assert resources['workspace_free_bytes']-estimate-100000-3_000_000-2_000_000>=8_000_000_000
    dump(index,result)
    outcome=dict(complete=True,errors=[],append_index=entry(index),previous6441_frozen_hashes_verified=True,new_frozen_hashes_verified=True,
        newly_bound_files=len(new),cumulative_frozen_evidence_files=6441+len(new),new_primary_maintexts=2,original_tables_read=5,
        repaired271_completed_and_independently_audited=True,old_failed_full_stage_retained=True,live_training_and_full_replay_excluded=True,
        new_patient_medical_effects=0,root_files_unchanged=True,publication_claim_confirmed=False,goal_status='active',resources=resource_guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proof,outcome);print(json.dumps(outcome),flush=True)
if __name__=='__main__':main()
