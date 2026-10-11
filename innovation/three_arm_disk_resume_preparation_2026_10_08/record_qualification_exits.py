"""Record actual observed terminal exits, including the partial failed update."""
import sys,time
from pathlib import Path
import disk_resume_core as core
def main():
    sys.stdout.reconfigure(encoding='utf-8'); tick=time.perf_counter()
    first=core.HERE/'attempt01/receipt.json'; partial=core.HERE/'attempt01/continuous/receipt.json'
    success=core.HERE/'attempt02/receipt.json'; proof=core.HERE/'independent_attempt02/receipt.json'
    a,b,c,d=[core.read(p) for p in (first,partial,success,proof)]
    assert not a['complete'] and a['status']=='failed' and a['children'][0]['exit_code']==1
    assert not b['complete'] and b['actual_resource_updates']==b['completed_model_forward_calls']==1
    assert b['synthetic_checkpoint_arrays_loaded_from_disk']==0
    assert c['complete'] and not c['errors'] and c['actual_synthetic_updates']==c['synthetic_neural_forwards']==15
    assert d['complete'] and not d['errors'] and all(d['gate'].values()) and d['neural_forwards']==0
    assert d['synthetic_checkpoint_arrays_loaded_from_disk']==9 and c['synthetic_checkpoint_arrays_loaded_from_disk']==3
    for q in (c,d): core.verify_bindings(q['source_bindings'])
    leftover=core.HERE/'attempt01/continuous/legacy_dense_step001.pt'; assert leftover.is_file()
    root_files=[]
    for name,expected in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                          ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        p=core.ROOT.parent/name; assert core.sha(p)==expected
        root_files.append(dict(path=str(p),sha256=expected,previous_sha256=expected))
    q=dict(created_utc=core.now(),complete=True,errors=[],
        source_bindings=[core.entry(p) for p in (Path(__file__),first,partial,success,proof,leftover)],
        failed_qualification_observed_tool_exit=1,failed_qualification_observed_chunk='3321ac',failed_qualification_session=64668,
        failed_actual_synthetic_updates=1,failed_actual_synthetic_forwards=1,failed_parent_success_summary_not_actual_count=True,
        failed_source_and_partial_checkpoint_retained=True,attempt02_generation_observed_tool_exit=0,
        attempt02_generation_observed_chunk='aa4427',qualification_observed_tool_exit=0,qualification_observed_chunk='a953c9',qualification_session=82922,
        qualification_result_file=success.relative_to(core.ROOT).as_posix(),qualification_result_sha256=core.sha(success),
        verifier_observed_tool_exit=0,verifier_observed_chunk='b27b3a',verifier_result_file=proof.relative_to(core.ROOT).as_posix(),verifier_result_sha256=core.sha(proof),
        qualified_cross_process_disk_resumes=3,actual_attempt02_updates=15,actual_attempt02_forwards=15,
        total_stage_synthetic_updates=16,total_stage_synthetic_neural_forwards=16,FOV_forwards=0,
        synthetic_checkpoint_arrays_loaded_in_training_processes=3,synthetic_checkpoint_arrays_loaded_by_independent_verifier=9,
        total_synthetic_checkpoint_arrays_loaded_from_disk=12,synthetic_checkpoint_byte_hash_reads_are_not_array_loads=True,
        six_fault_probe_child_exits=[3]*6,valid_probe_child_exit=0,neural_imports_at_all_probes=False,
        medical_arrays_loaded=0,old_checkpoint_arrays_loaded=0,MRI_forwards=0,GPU_forwards=0,real_medical_resource_updates=0,
        real_medical_formal_training_updates=0,head_fits=0,new_action_labels=0,new_papers_read=0,root_files_observed=root_files,
        actual_new_MRI_task_benefit_measured=False,full_action_cost_measured=False,formal_long_MRI_training_not_qualified=True,
        original_terminal_training_modified=False,new_agents_delegated=0,publication_claim_confirmed=False,goal_status='active',
        automatic_approval_review_rejections_received=0,resources=core.guard(tick,60))
    core.new_json(core.HERE/'QUALIFICATION_OBSERVED_EXITS.json',q)
    print(core.json.dumps(dict(complete=True,total_stage_synthetic_updates=16,total_synthetic_checkpoint_arrays_loaded_from_disk=12,qualified_disk_resumes=3)),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
