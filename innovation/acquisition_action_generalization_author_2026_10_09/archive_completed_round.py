"""Append only ended/frozen evidence after independently hashing the old6997 chain."""
import sys,time,json,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import read,sha,entry,bind,bindings,dump,resource_guard
LIVE=ROOT/'full_certified_schedule_2026_10_09/full_real_pipeline_attempt01'
def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter()
    def guard():
        res=resource_guard();assert time.perf_counter()-started<1200
        assert res['workspace_free_bytes']-16_800_000-20_000>=8_000_000_000
        assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())<2_000_000;return res
    guard();indexpath=HERE/'APPEND_INDEX.json';proofpath=HERE/'APPEND_PROOF.json'
    assert not indexpath.exists() and not proofpath.exists()
    previous=ROOT/'resource_recovery_and_generalization_controls_2026_10_09/APPEND_INDEX.json'
    prevproof=previous.with_name('APPEND_PROOF.json')
    assert sha(previous)=='af51442f0daab1459e40de7a17ca6c0332ca1aa206a7a05f0def71a9a016a4bf'
    assert sha(prevproof)=='6b3d95d59b2eb8ee6075c5db04b16101808b2eb69c5540b26a8207a9f13614d2'
    q=read(previous);assert q['complete'] and not q['errors'] and q['cumulative_frozen_evidence_files']==6997
    chain=q['prior_chain']+[entry(previous)];old=[]
    for b in chain:
        v=read(bind(b));assert v['complete'] and not v['errors'];old.extend(v.get('evidence_files',v.get('new_evidence_files',[])))
    existing={b['path']:b for b in old};assert len(old)==len(existing)==6997
    for i,b in enumerate(old,1):
        bind(b)
        if i%1000==0:guard();print(json.dumps(dict(previous6997_hashes_verified=i)),flush=True)
    reading=read(HERE/'READING_PROVENANCE.json')
    assert reading['complete'] and reading['new_distinct_primary_maintexts_actually_read']==3 and reading['blocks_actually_read']==341
    for stage,session in [('certified_resolution_rounding_2026_10_09',43633),('direct_oracle_efficiency_2026_10_09',31883)]:
        t=read(ROOT/stage/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json');assert t['exit_code']==0 and 'session_id' not in t and t['observed_unified_exec_session']==session
        r=read(ROOT/stage/'all_patient_stress_attempt01/receipt.json');a=read(ROOT/stage/'all_patient_terminal_audit_attempt01/receipt.json')
        assert r['complete'] and r['all542_full_fields_verified'] and a['complete'] and a['all542_unique_field_identities_verified']
    gpu=ROOT/'gpu_graph_cost_smoke_2026_10_09'
    t=read(gpu/'ACTUAL_GPU_SMOKE_V3_TERMINAL_TOOL.json');assert t['exit_code']==0 and 'session_id' not in t
    assert read(gpu/'terminal_audit_attempt01/receipt.json')['all_six_unique_branch_identities_verified']
    recovery=read(ROOT/'frozen_text_resource_recovery_v2_2026_10_09/compression_attempt01/receipt.json')
    assert recovery['complete'] and recovery['files_processed']==1000 and recovery['all_selected_logical_SHA_unchanged']
    roots=[HERE,ROOT/'certified_resolution_rounding_2026_10_09',ROOT/'direct_oracle_efficiency_2026_10_09',
        ROOT/'frozen_text_resource_recovery_v2_2026_10_09',ROOT/'gpu_graph_cost_smoke_2026_10_09',ROOT/'intensity_precision_failure_diagnosis_2026_10_09']
    sources={p for folder in roots for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [indexpath,proofpath]}
    for folder in [ROOT/'full_certified_schedule_2026_10_09',previous.parent]:sources.update(p for p in folder.iterdir() if p.is_file())
    sources.update(ROOT/b['path'] for b in chain);sources.add(prevproof)
    opaque={ROOT/b['path'] for b in chain}|{prevproof}
    pending=set(sources);scanned=set();binding_count=link_count=0;live_refs=[]
    while pending:
        p=sorted(pending)[0];pending.remove(p)
        if p in scanned:continue
        assert p.is_file() and p.resolve().is_relative_to(ROOT) and not p.is_relative_to(LIVE)
        scanned.add(p)
        if p.relative_to(ROOT).as_posix() in existing or p in opaque:continue
        if p.suffix=='.json':
            for b in bindings(read(p)):
                target=(ROOT/b['path']).resolve();assert not target.is_relative_to(LIVE),'A frozen JSON must not bind live output'
                target=bind(b);binding_count+=1
                if target.is_relative_to(ROOT) and target not in sources:sources.add(target);pending.add(target)
        elif p.suffix=='.md':
            for raw in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                if re.match(r'https?://|app://',raw):continue
                target=Path(raw.strip('<>').split('#',1)[0])
                if not target.is_absolute():target=p.parent/target
                target=target.resolve();assert target.exists() and target.is_relative_to(ROOT),raw
                if target.is_relative_to(LIVE):live_refs.append(dict(document=p.relative_to(ROOT).as_posix(),target=target.relative_to(ROOT).as_posix()));continue
                if target.is_file() and target not in sources:sources.add(target);pending.add(target)
                link_count+=1
        guard()
    assert not any(p.is_relative_to(LIVE) for p in sources)
    new=[entry(p) for p in sorted(sources) if p.relative_to(ROOT).as_posix() not in existing]
    for b in new:bind(b)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],index_kind='three_primaries_two542_qualifications_checkpointed_GPU_and_live35904_preparation_after6997',
        prior_chain=chain,previous6997_frozen_hashes_verified=True,new_evidence_files=new,newly_bound_files=len(new),
        cumulative_frozen_evidence_files=6997+len(new),source_binding_checks=binding_count,local_link_checks=link_count,live_link_targets_excluded=live_refs,
        live_full35904_outputs_excluded=True,full35904_qualification_passed=False,complete_six_branch_training_ready=False,
        new_primary_maintexts=3,maintext_blocks=341,data_tables=11,new_synthetic_diagnostics=4,
        old_and_optimized_full542_actual_terminal_exit=0,GPU_checkpointed_graph_actual_terminal_exit=0,
        optimizer_updates=0,independent_medical_confirmation=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        publication_claim_confirmed=False,goal_status='active')
    estimate=len((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    assert sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())+estimate+20_000<2_000_000
    guard();dump(indexpath,result)
    for b in new:bind(b)
    proof=dict(complete=True,errors=[],append_index=entry(indexpath),previous6997_frozen_hashes_verified=True,new_frozen_hashes_verified=True,
        newly_bound_files=len(new),cumulative_frozen_evidence_files=6997+len(new),live_full35904_outputs_excluded=True,
        full35904_qualification_passed=False,checkpointed_GPU_graph_passed=True,training_ready=False,
        publication_claim_confirmed=False,goal_status='active',resources=guard(),elapsed_seconds=time.perf_counter()-started)
    dump(proofpath,proof);print(json.dumps(proof,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
