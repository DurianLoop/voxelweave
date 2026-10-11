"""Freeze current actual exits/resources and verify source closure without MRI IO."""
import hashlib,json,sys,time,subprocess,shutil
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PROJECT=ROOT.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    sys.stdout.reconfigure(encoding='utf-8');tick=time.perf_counter()
    q=read(HERE/'synthetic_attempt01/receipt.json');v=read(HERE/'independent_attempt01/receipt.json')
    e=read(HERE/'SYNTHETIC_OBSERVED_EXITS.json');real=read(HERE/'real_resource_cpu_attempt01/attempt01.json')
    ready=read(HERE/'real_resource_cpu_attempt01/prerequisite_readiness.json');gen=read(HERE/'RESOURCE_ENTRY_GENERATION.json')
    assert all(d['complete'] and not d['errors'] for d in (q,v,e,real,ready,gen))
    assert q['actual_resource_updates']==12 and q['completed_model_forward_calls']==36 and v['independent_batch_count']==9
    assert real['status']=='prerequisite_deferred' and real['readiness_process_exit']==3 and not ready['ready']
    assert real['MRI_observed_packages_loaded']==real['development_GT_loaded']==real['actual_resource_updates']==0
    assert not real['neural_modules_imported'] and not real['CUDA_initialized'] and not real['torch_in_sys_modules'] and not real['numpy_in_sys_modules']
    sources=[]
    for p,d in [(HERE/'synthetic_attempt01/receipt.json',q),(HERE/'independent_attempt01/receipt.json',v),
            (HERE/'SYNTHETIC_OBSERVED_EXITS.json',e),(HERE/'real_resource_cpu_attempt01/attempt01.json',real),
            (HERE/'real_resource_cpu_attempt01/prerequisite_readiness.json',ready),(HERE/'RESOURCE_ENTRY_GENERATION.json',gen)]:
        for b in d.get('source_bindings',[])+d.get('output_bindings',[]):
            target=ROOT/b['path'];assert sha(target)==b['sha256']
            if 'bytes' in b:assert target.stat().st_size==b['bytes']
            sources.append(dict(document=p.relative_to(ROOT).as_posix(),**b))
    roots=[]
    for name,expected in [('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        p=PROJECT/name;assert sha(p)==expected;roots.append(dict(path=str(p),sha256=expected,previous_sha256=expected))
    gpu=subprocess.run(['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader'],
        capture_output=True,text=True,timeout=15);assert gpu.returncode==0
    livepath=ROOT/'experiments/mc_rc_3d_19series_common_init_cpu_2026_10_07/invocation02.json'
    payload=livepath.read_bytes();live=json.loads(payload)
    obs=dict(observed_utc=datetime.now(timezone.utc).isoformat(),training_session_id=99542,
        original_training_terminal_exit=None,training_status=live.get('status'),training_complete=live.get('complete'),training_errors=live.get('errors'),
        arms=[dict(kind=a.get('kind'),updates_completed=a.get('updates_completed'),complete=a.get('complete')) for a in live.get('arms',[])],
        invocation02_new_updates=live.get('new_cpu_backbone_updates'),new_updates_not_raw_arm_count=True,
        live_bytes_sha256_observation_not_frozen=hashlib.sha256(payload).hexdigest(),
        gpu_csv=gpu.stdout.strip(),gpu_query_exit=0,gpu_authorization_retained=True,new_GPU_job_started=False,
        workspace_free_bytes=shutil.disk_usage(ROOT).free,disk_reserve_bytes=8_000_000_000,
        root_files_observed=roots,original_terminal_training_modified=False,other_processes_enumerated=False,other_processes_modified=False)
    new(HERE/'TRAINING_RESOURCE_OBSERVATION.json',obs)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__)),entry(HERE/'PROTOCOL.md'),entry(HERE/'RESULT.md'),entry(HERE/'VISIBLE_DIALOGUE.md'),
            entry(HERE/'USER_GOAL_REQUEST.md'),entry(HERE/'DELIVERY.md'),entry(HERE/'NEXT_STAGE_HANDOFF.md'),entry(HERE/'TRAINING_RESOURCE_OBSERVATION.json')]+
            [entry(HERE/s) for s in ('synthetic_attempt01/receipt.json','independent_attempt01/receipt.json','SYNTHETIC_OBSERVED_EXITS.json',
                'RESOURCE_ENTRY_GENERATION.json','real_resource_cpu_attempt01/attempt01.json','real_resource_cpu_attempt01/prerequisite_readiness.json')],
        actual_exits=[dict(chunk='84810c',session_id=64443,exit_code=0,job='synthetic_three_arm'),
            dict(chunk='6c8fd2',exit_code=0,job='independent_batch_replay'),dict(chunk='a5488f',exit_code=0,job='generate_gated_resource_entry'),
            dict(chunk='518698',exit_code=0,job='source_and_exit_receipt'),dict(chunk='3fcdfe',exit_code=3,job='real_entry_cpu_attempt01',
                expected_prerequisite_defer=True,medical_arrays_loaded=0,neural_modules_imported=False)],
        original_live_polls=[dict(chunk='903714',session_id=99542,returned_session_id=99542,terminal_exit=None,new_output_empty=True),
            dict(chunk='dc53d2',session_id=99542,terminal_exit=None,raw_pchip_updates=891,invocation02_new_updates=20691,cumulative_wall_seconds=47555.260539299925),
            dict(chunk='90f348',session_id=99542,terminal_exit=None,raw_pchip_updates=1188,invocation02_new_updates=20988,cumulative_wall_seconds=48267.897887800005)],
        source_bindings_verified=sources,all_source_bindings_verified=True,source_originals_not_overwritten=True,
        synthetic_resource_updates=12,synthetic_neural_forwards=36,independent_batches_reconstructed=9,
        independent_neural_forwards=0,independent_training_updates=0,
        independent_resume_or_FOV_network_reexecution=False,representative_synthetic_FOV_passes=6,
        real_medical_resource_updates=0,real_medical_formal_training_updates=0,medical_arrays_loaded=0,
        prediction_arrays_loaded_from_medical_files=0,model_checkpoint_arrays_loaded_from_disk=0,
        MRI_neural_forwards=0,GPU_forwards=0,head_fits=0,new_final_action_labels_generated=0,
        new_primary_papers_read=0,new_full_text_pages_read=0,visual_pages_reviewed=0,
        actual_new_MRI_task_benefit_measured=False,real19series_resource_qualification_completed=False,
        formal_three_arm_training_implemented_and_qualified=False,full_action_cost_measured=False,
        original56FOV_evaluation_launched=False,confirmation_patients_opened=False,lockedIXI_opened=False,
        original_terminal_training_modified=False,new_agents_delegated=0,automatic_approval_review_rejections_received=0,
        root_files_observed=roots,publication_claim_confirmed=False,goal_status='active',
        previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
        current_progress='Implemented and executed the previously missing third representation resource workflow; independently certified9input/label batches.',
        completion_audit=dict(original_two_arm_final_not_complete=True,original_task_capability_not_yet_evaluated=True,
            strong_matched_three_arm_task_effects_not_measured=True,full_action_cost_unknown=True,
            novel_MRI_effect_not_confirmed=True,eight_unseen_patient_confirmation_not_opened=True),
        ancillary_read_failure='Broad rg included inaccessible retained tools/tmp paths; bounded explicit-file reads used thereafter.',
        elapsed_seconds=time.perf_counter()-tick)
    new(HERE/'EXECUTION_LEDGER.json',result)
    print(json.dumps(dict(complete=True,synthetic_resource_updates=12,synthetic_neural_forwards=36,independent_batches=9,
        medical_arrays_loaded=0,real_medical_training_updates=0,real_entry_exit=3,training_resource_observation=obs),ensure_ascii=False),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())
