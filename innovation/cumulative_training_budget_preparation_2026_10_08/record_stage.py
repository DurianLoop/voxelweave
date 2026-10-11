"""Record the actual CPU accounting qualification without medical claims."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'experiments'))
from mc_rc_reference_resources_2026_10_07 import resource_guard
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    sys.stdout.reconfigure(encoding='utf-8');resource_guard()
    a=read(HERE/'ACTUAL_OBSERVATIONS.json');q=read(HERE/'attempt01/receipt.json');v=read(HERE/'independent_attempt01/receipt.json')
    assert q['complete'] and v['complete'] and not q['errors'] and not v['errors']
    assert a['actual_qualification']['exit_code']==a['actual_independent_verifier']['value']['exit_code']==0
    assert q['actual_CPU_work_units']==12 and q['actual_total_child_processes_launched']==11
    assert v['cumulative_paid_ns']==q['final_normal_state']['paid_ns']==3246692800
    assert v['actual_recorded_normal_controller_ns']==271998200
    assert a['actual_live_poll']['value']['session_id']==99542 and 'exit_code' not in a['actual_live_poll']['value']
    assert a['actual_goal']['value']['goal']['status']=='active'
    roots=[]
    for p,expected in [(Path('D:/MRI/.gitignore'),'7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        (Path('D:/MRI/environment.yml'),'dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        assert sha(p)==expected;roots.append(dict(path=str(p),sha256=expected,previous_sha256=expected))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
       source_bindings=[entry(p) for p in (Path(__file__),HERE/'PROTOCOL.md',HERE/'RESULT.md',HERE/'ACTUAL_OBSERVATIONS.json',
       HERE/'attempt01/receipt.json',HERE/'independent_attempt01/receipt.json',HERE/'INTEGRATION_PREPARATION.md',
       HERE/'VISIBLE_DIALOGUE.md',HERE/'NEXT_STAGE_HANDOFF.md')],root_files_observed=roots,
       new_primary_papers_read=0,new_full_text_pages_read=0,visual_pages_reviewed=0,CPU_accounting_work_units=12,
       work_child_processes=4,validation_child_processes=7,controlled_nonzero_exit17_count=1,
       independent_verifier_executed_work_units=0,cumulative_controller_charged_ns=3246692800,
       actual_recorded_normal_controller_ns=271998200,conservative_charge_not_exact_actual_wall=True,
       medical_arrays_loaded=0,model_checkpoint_arrays_loaded_from_disk=0,neural_forwards=0,MRI_neural_forwards=0,
       GPU_forwards=0,real_medical_resource_updates=0,real_medical_formal_training_updates=0,
       head_fits=0,new_final_action_labels_generated=0,new_agents_delegated=0,
       confirmation_patients_opened=False,lockedIXI_opened=False,new_GPU_job_started=False,
       original_terminal_training_not_modified=True,original_training_terminal_exit=None,
       formal_medical_budget_frozen=False,formal_medical_long_runner_qualified=False,actual_new_MRI_task_benefit_measured=False,
       full_action_cost_measured=False,publication_claim_confirmed=False,goal_status='active',current_goal_turn_classification='progress',
       previous_goal_turn_classification='progress',automatic_approval_review_rejections_received=0)
    with (HERE/'EXECUTION_LEDGER.json').open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(complete=True,CPU_accounting_work_units=12,neural_forwards=0,goal_status='active')),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())

