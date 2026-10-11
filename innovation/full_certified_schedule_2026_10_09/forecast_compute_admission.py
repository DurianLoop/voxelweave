"""Require actual ended qualification before prespecified bounded CPU cost admission."""
import sys,time,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'final_training_medical_execution_2026_10_08'))
from archive_completed_stage import resource_guard,read,entry,bind,dump

def main():
    sys.stdout.reconfigure(encoding='utf-8');started=time.perf_counter();resources=resource_guard();stage=ROOT/'direct_oracle_efficiency_2026_10_09'
    terminalpath=stage/'ACTUAL_ALL_PATIENT_STRESS_TERMINAL_TOOL.json';terminal=read(terminalpath)
    assert terminal['exit_code']==0 and 'session_id' not in terminal
    path=stage/'all_patient_stress_attempt01/receipt.json';r=read(path);auditpath=stage/'all_patient_terminal_audit_attempt01/receipt.json';a=read(auditpath)
    assert r['complete'] and r['all542_full_fields_verified'] and a['complete'] and a['all542_unique_field_identities_verified']
    for b in r['source_bindings']:bind(b)
    fields=[f for f in r['fields'] if f['identity']['scope']=='real_stress'];assert len(fields)==228
    # Numerator includes synthetic/regression overhead conservatively; only real fields in denominator.
    seconds_per_active=(r['cost_seconds']['candidate']+r['cost_seconds']['direct_oracle'])/228
    estimate=10710*seconds_per_active;with_margin=estimate*1.25+1200
    disk=resources['workspace_free_bytes']-8_000_000_000>=15_800_000
    result=dict(complete=True,errors=[],forecast_only=True,expected_total_fields=35904,expected_active_fields=10710,
        conservative_seconds_per_active_field=seconds_per_active,point_forecast_seconds=estimate,with25percent_and1200seconds_allowance=with_margin,
        prespecified_wall_seconds=64800,compute_admitted=with_margin<=64800,disk_stage_admitted=disk,admitted=with_margin<=64800 and disk,
        source_bindings=[entry(p) for p in [Path(__file__),HERE/'FULL_REAL_PIPELINE_PROTOCOL.md',terminalpath,path,auditpath]],
        resources=resources,elapsed_seconds=time.perf_counter()-started,full35904_qualification_passed=False,training_ready=False,publication_claim_confirmed=False,goal_status='active')
    out=HERE/'compute_admission_attempt01';out.mkdir(exist_ok=False);dump(out/'receipt.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':main()
