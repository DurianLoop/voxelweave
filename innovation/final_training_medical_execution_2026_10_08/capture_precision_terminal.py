"""Bind an actually observed V4 terminal exit to its immutable numerical/medical result."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    tool=HERE/'ACTUAL_PRECISION_V4_TERMINAL_TOOL.json';obs=json.loads(tool.read_text());assert obs['exit_code']==0 and 'session_id' not in obs
    path=HERE/'precision_v4_attempt01/receipt.json';r=json.loads(path.read_text());assert r['complete'] and not r['errors']
    assert r['all56_production_and_independent_FOVs_completed'] and r['all_strict_numeric_gates_passed']
    assert r['total_old_prediction_threshold_changes']==0 and r['all_old_metrics_identical']
    assert not r['all_arms_validation_gates_passed'] and not r['cross_process_independent_reexecution']
    for b in r['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],observed_tool_exit=0,
        observed_tool_session=70619,observed_tool_chunk=obs['chunk_id'],result_file=path.relative_to(ROOT).as_posix(),result_sha256=sha(path),
        production_and_independent_complete_FOVs=56,all_strict_numeric_gates_passed=True,
        max_probability_error=r['max_probability_error'],old_binary_changes=0,old_medical_metrics_identical=True,
        medical_capability_gates_passed=False,single_entry_two_implementations=True,cross_process_independent_reexecution=False,
        elapsed_seconds=r['elapsed_seconds'],CUDA_initialized=r['CUDA_initialized'],new_training_updates=0,
        publication_claim_confirmed=False,goal_status='active',source_bindings=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
            for p in [Path(__file__),tool,path,HERE/'PRECISION_REPAIR_V4_PROTOCOL.md',HERE/'production_probability_mapping_v4.py']])
    with (HERE/'ACTUAL_PRECISION_V4_EXIT.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='source_bindings'}))
if __name__=='__main__':main()
