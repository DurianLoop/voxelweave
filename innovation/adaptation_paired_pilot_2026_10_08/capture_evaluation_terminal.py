"""Actual 80828 terminal evidence, all36 numerical result and sources; medical pass stays separate."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    resource_guard();tool=HERE/'ACTUAL_EVALUATION_TERMINAL_TOOL.json';obs=json.loads(tool.read_text());assert obs['exit_code']==0 and 'session_id' not in obs
    p=HERE/'evaluation_attempt01/receipt.json';r=json.loads(p.read_text());assert r['complete'] and not r['errors'] and r['all36_strict_gates_passed']
    assert len(r['arms'])==4 and all(a['complete'] and len(a['series'])==9 for a in r['arms'])
    assert not r['cross_process_independent_reexecution'] and not r['all_four_branches_medical_gates_passed']
    for b in r['source_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],observed_tool_exit=0,observed_tool_session=80828,
        observed_tool_chunk=obs['chunk_id'],result_file=p.relative_to(ROOT).as_posix(),result_sha256=sha(p),
        complete_production_and_independent_FOVs=36,all36_strict_numeric_gates_passed=True,all_four_medical_gates_passed=False,
        single_entry_two_implementations=True,cross_process_independent_reexecution=False,elapsed_seconds=r['elapsed_seconds'],
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        source_bindings=[dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in [Path(__file__),tool,p]])
    with (HERE/'ACTUAL_EVALUATION_EXIT.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='source_bindings'}),flush=True)
if __name__=='__main__':main()
