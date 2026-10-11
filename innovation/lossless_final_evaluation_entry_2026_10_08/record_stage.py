"""Record actual lossless-storage qualification and deferred medical entry evidence."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'seranet_identity_prior_art_2026_10_08'))
import query_seranet_stdlib_v3 as client
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sys.stdout.reconfigure(encoding='utf-8');resources=client.resource_guard()
    qualification=read(HERE/'compression_qualification_v3/receipt.json');probe=read(HERE/'readiness_probe_v3/receipt.json')
    for q in [qualification,probe,read(HERE/'BUILD_RECEIPT.json'),read(HERE/'BUILD_RECEIPT_V3.json')]:assert q['complete'] and not q['errors']
    assert qualification['synthetic_payloads']==14 and qualification['total_cross_reader_checks']==56
    assert qualification['all_lossless_interoperability_checks_passed']
    for b in qualification['production_bindings']:assert sha(ROOT/b['path'])==b['sha256']
    assert probe['actual_subprocess_exit']==3 and not probe['actual_subprocess_status']['ready']
    assert probe['actual_subprocess_status']['MR_or_GT_arrays_loaded']==0 and not probe['actual_subprocess_status']['CUDA_initialized']
    assert not (HERE/'medical_attempt03').exists()
    obs=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        previous_turn_classification='progress',current_turn_classification='progress',
        actual_executions=[dict(chunk_id='113721',session_id=99542,terminal_exit=None,raw_updates=7623,invocation_new_updates=27423,cumulative_wall_seconds=63439.549753700034),
            dict(chunk_id='e80cef',exit_code=0,GPU_free_MiB=1394,GPU_utilization_percent=85),
            dict(chunk_id='955223',exit_code=1,error='rg Windows123: path wildcard not expanded',repaired_with_glob_root_search=True),
            dict(chunk_id='e5978f',exit_code=0,kind='build_V2_entries'),
            dict(chunk_id='1a864d',exit_code=1,kind='V2_actual_standalone_readiness',error='ModuleNotFoundError for experiments dependency'),
            dict(chunk_id='8c1855',exit_code=0,kind='build_V3_entries'),
            dict(chunk_id='e54f9e',exit_code=0,kind='lossless_storage_qualification',synthetic_payloads=14,cross_reads=56),
            dict(chunk_id='482af5',exit_code=0,kind='actual_CLI_probe_and_storage_audit',child_CLI_exit=3,medical_arrays_loaded=0),
            dict(chunk_id='a5372d',session_id=99542,terminal_exit=None,raw_updates=7920,invocation_new_updates=27720,cumulative_wall_seconds=64132.80965880002),
            dict(chunk_id='fe6f95',session_id=99542,terminal_exit=None,output_empty=True,not_a_terminal_observation=True),
            dict(chunk_id='c69eea',exit_code=0,GPU_free_MiB=1394,GPU_utilization_percent=65,root_hashes_unchanged=True),
            dict(chunk_id='d47c12',exit_code=0,kind='V3_diff_actual_review')],
        source_bindings=[client.base.entry(p) for p in [Path(__file__),HERE/'VISIBLE_DIALOGUE.md',HERE/'FAILED_V2_READINESS.txt']],
        original_training_modified=False,all_failures_preserved=True,automatic_approval_review_rejections_received=0)
    client.base.new(HERE/'ACTUAL_OBSERVATIONS.json',obs)
    roots=[]
    for path,expected in [('D:/MRI/.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('D:/MRI/environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')]:
        assert sha(Path(path))==expected;roots.append(dict(path=path,sha256=expected,previous_sha256=expected))
    docs=[Path(__file__)]+[HERE/n for n in ['PROTOCOL.md','REPAIR_V3.md','RESULT.md','MEDICAL_EXECUTION.md','NEXT_STAGE_HANDOFF.md',
        'VISIBLE_DIALOGUE.md','ACTUAL_OBSERVATIONS.json','BUILD_RECEIPT.json','BUILD_RECEIPT_V3.json',
        'compression_qualification_v3/receipt.json','readiness_probe_v3/receipt.json']]
    zeros={k:0 for k in ['new_primary_papers_read','new_full_text_pages_read','visual_pages_reviewed','public_table_rows_checked',
        'medical_arrays_loaded','model_checkpoint_arrays_loaded_from_disk','neural_forwards','MRI_neural_forwards','GPU_forwards',
        'real_medical_training_updates','head_fits','new_action_labels_generated','new_agents_delegated']}
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],**zeros,
        source_bindings=[client.base.entry(p) for p in docs]+qualification['production_bindings'],
        qualified_synthetic_payloads=14,cross_reader_checks=56,qualified_lossless_medical_entry_version='V3',
        actual_entry_readiness_exit=3,actual_medical_evaluation_started=False,
        AST_scientific_function_comparisons=len(qualification['AST_scientific_functions_unchanged']),
        root_files_observed=roots,resource_snapshot=resources,storage_planning=probe['storage_planning'],
        original_terminal_exit=None,latest_raw_arm_updates=7920,latest_invocation_new_updates=27720,
        original_training_modified=False,new_GPU_job_started=False,GPU_user_authorization_present=True,latest_GPU_free_MiB=1394,
        current_original_contract=dict(per_arm_updates=19998,total_updates=39996,cumulative_wall_limit_hours=30),
        confirmation_patients_opened=False,lockedIXI_opened=False,publication_claim_confirmed=False,goal_status='active',
        previous_frozen_evidence_files_expected=5392,automatic_approval_review_rejections_received=0,
        software_storage_qualification_is_not_MRI_effect_or_speed_evidence=True,actual_observations=obs)
    client.base.new(HERE/'EXECUTION_LEDGER.json',ledger)
    print(json.dumps(dict(complete=True,qualified_synthetic_payloads=14,cross_reader_checks=56,actual_readiness_exit=3,
        AST_scientific_function_comparisons=ledger['AST_scientific_function_comparisons'],
        resource_snapshot=resources,publication_claim_confirmed=False,goal_status='active')),flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
