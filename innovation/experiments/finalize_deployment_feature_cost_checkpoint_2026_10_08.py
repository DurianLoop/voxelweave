"""Record observed archive completion and latest live training, without future exit claims."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,d):
    with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest=ROOT/'literature/deployment_feature_cost_stage_manifest_2026-10-08.json'
    proof=ROOT/'SESSION_ARCHIVE_VERIFICATION_DEPLOYMENT_FEATURE_COST_2026-10-08.json'
    m,p=read(manifest),read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors']
    assert sha(manifest)==p['manifest_sha256'] and len(m['stage_files'])==62 and len(m['evidence_files'])==3759
    assert m['stage_bytes']==4696633 and p['new_evidence_bytes']==5806235 and p['newly_bound_files']==72
    assert p['previous3687_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified'] and p['local_links_verified']
    for name,digest in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        assert sha(ROOT.parent/name)==digest
    observed=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        archive=dict(actual_observed_tool_chunk='0af306',actual_observed_tool_exit=0,stage_files=62,
            stage_bytes=4696633,newly_bound_files=72,new_evidence_bytes=5806235,cumulative_frozen_files=3759),
        metadata_record=dict(actual_observed_tool_chunk='121a19',actual_observed_tool_exit=0),
        training=dict(actual_observed_tool_chunk='463c63',session_id=99542,returned_same_live_session=True,
            native_updates=18414,invocation02_new_updates=18315,cumulative_wall_seconds=41897.80044349993,
            full_training_observed_tool_exit=None,training_restarted=False,training_migrated=False),
        latest_GPU=dict(actual_observed_tool_chunk='aa5bc1',actual_observed_tool_exit=0,timestamp='2026/10/08 03:28:04.333',
            free_MiB=1394,total_MiB=24455,utilization_percent=88,new_GPU8GB_margin_met=False),
        root_hashes_again_unchanged=True,automatic_approval_review_rejections_received=0,
        user_terminal_processes_controlled=False,new_agents_delegated=False,goal_status='active',publication_claim_confirmed=False)
    obs=ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_DEPLOYMENT_FEATURE_COST_2026-10-08.json';new(obs,observed)
    receipt=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(x) for x in (Path(__file__),manifest,proof,obs,
            ROOT/'SESSION_POST_ARCHIVE_DEPLOYMENT_FEATURE_COST_UPDATE_2026-10-08.md',
            ROOT/'SESSION_PREPARED_FINAL_REPLY_DEPLOYMENT_FEATURE_COST_2026-10-08.md')],
        archive_actual_tool_exit=0,archive_actual_tool_chunk='0af306',new_stage_files_frozen=62,
        cumulative_frozen_evidence_files=3759,stage_bytes=4696633,new_evidence_bytes=5806235,
        previous3687_evidence_hashes_unchanged=True,production_actual_tool_exit=0,metadata_independent_actual_tool_exit=0,
        unique_development_patients=11,unique_development_series=19,observed_package_load_events=19,real_folds_executed=38,
        feature_rows_exact=19,feature_count=17,cold_child_end_to_end_seconds=23.848797200014815,
        measured_production_phase_subset_seconds=19.37797900068108,independent_timing_repeated=False,
        new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        new_primary_papers_read=1,new_supplemental_documents_read=1,new_text_pages_read=9,visual_pages_reviewed=4,
        old_method_pages_reread=2,conditional_variance_step_check_passed=True,complete_Noise2Same_theorem1_disproved=False,
        relative_utility_is_known_cost_sensitive_selection=True,two_path_cost_sensitive_defer_control_required=True,
        live_training=observed['training'],latest_GPU=observed['latest_GPU'],formal_final_budget_completed=False,
        original56FOV_evaluated=False,all6_final_capability_gates_completed=False,actual_MRI_risk_certificates_issued=0,
        actual_MRI_task_benefit_measured=False,full_action_cost_measured=False,real_task_latency_measured=False,
        confirmation_patients_opened=False,validation_data_read=False,locked_IXI_opened=False,
        old_MIRA_MSValid84_confirmation_preserved=True,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',this_receipt_is_post_manifest_appendix=True)
    dest=ROOT/'SESSION_CHECKPOINT_RECEIPT_DEPLOYMENT_FEATURE_COST_2026-10-08.json';new(dest,receipt)
    print(json.dumps(dict(complete=True,receipt=entry(dest),archive_actual_tool_exit=0,stage_files=62,
        cumulative_frozen_files=3759,native_updates=18414,full_training_exit=None,goal_status='active',
        publication_claim_confirmed=False),ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
