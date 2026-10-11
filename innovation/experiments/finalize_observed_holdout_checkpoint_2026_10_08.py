"""Bind observed archive exit and still-live original training; no future exit claims."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def new(p,d):
    with p.open('x',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    manifest = ROOT/'literature/observed_holdout_stage_manifest_2026-10-08.json'
    proof = ROOT/'SESSION_ARCHIVE_VERIFICATION_OBSERVED_HOLDOUT_2026-10-08.json'
    m,p = read(manifest),read(proof)
    assert m['complete'] and p['complete'] and not m['errors'] and not p['errors']
    assert sha(manifest)==p['manifest_sha256'] and len(m['stage_files'])==270 and len(m['evidence_files'])==3687
    assert m['stage_bytes']==38653845 and p['new_evidence_bytes']==39514062 and p['newly_bound_files']==278
    assert p['previous3409_evidence_hashes_unchanged'] and p['all_final_evidence_hashes_verified'] and p['local_links_verified']
    for name,digest in (('.gitignore','7ecc6ec4f2bebbd8e96ad38f4fa76810a9db5254312f392ba49fd39b8f622524'),
                        ('environment.yml','dfdae9bfd34dd605be9dd8a488107fa56863bd99fc1f5835af8cbb8113905257')):
        assert sha(ROOT.parent/name)==digest
    observed = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        metadata_record=dict(actual_observed_tool_chunk='fe5dd7',actual_observed_tool_exit=0),
        archive=dict(actual_observed_tool_chunk='d3d033',actual_observed_tool_exit=0,
            stage_files=270,stage_bytes=38653845,newly_bound_files=278,new_evidence_bytes=39514062,cumulative_frozen_files=3687),
        training=dict(actual_observed_tool_chunk='41270d',session_id=99542,returned_same_live_session=True,
            native_updates=17523,invocation02_new_updates=17424,cumulative_wall_seconds=39814.882034900016,
            full_training_observed_tool_exit=None,training_restarted=False,training_migrated=False),
        latest_GPU=dict(actual_observed_tool_chunk='d7f937',actual_observed_tool_exit=0,timestamp='2026/10/08 02:53:52.109',
            free_MiB=1394,total_MiB=24455,utilization_percent=95,new_GPU8GB_margin_met=False),
        root_hashes_again_unchanged=True,automatic_approval_review_rejections_received=0,
        user_terminal_processes_controlled=False,new_agents_delegated=False,
        goal_status='active',publication_claim_confirmed=False)
    obsfile = ROOT/'SESSION_FINAL_TOOL_OBSERVATIONS_OBSERVED_HOLDOUT_2026-10-08.json'
    new(obsfile,observed)
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(x) for x in (Path(__file__),manifest,proof,obsfile,
            ROOT/'SESSION_POST_ARCHIVE_OBSERVED_HOLDOUT_UPDATE_2026-10-08.md',
            ROOT/'SESSION_PREPARED_FINAL_REPLY_OBSERVED_HOLDOUT_2026-10-08.md')],
        archive_actual_tool_exit=0,archive_actual_tool_chunk='d3d033',new_stage_files_frozen=270,
        cumulative_frozen_evidence_files=3687,stage_bytes=38653845,new_evidence_bytes=39514062,
        previous3409_evidence_hashes_unchanged=True,production_actual_tool_exit=0,
        original_independent_actual_tool_exit=1,original_failed_attempt_retained=True,
        v2_independent_actual_tool_exit=0,unique_development_patients=11,unique_development_series=19,
        observed_package_load_events=41,unique_real_folds=38,counterfactual_check_events=81,
        new_neural_forwards=0,new_GPU_forwards=0,new_training_updates=0,
        feature_rows=19,feature_names=17,real_action_utility_labels_available=False,no_tolerance_widening=True,
        patient_equal_observed_MSE=dict(linear=0.2847022968272982,pchip=0.2865475078664227),
        positive_pchip_minus_linear_series=18,positive_pchip_minus_linear_patients=10,
        new_primary_papers_read=2,related_physical_pages_acquired=20,text_pages_read=19,visual_pages_reviewed=5,
        wrong_identity28_page_paper_excluded=True,separate_supplementary_not_acquired_or_read=True,
        portable_runtime_verified_and_bound=True,original_MRI_environment_modified=False,
        live_training=observed['training'],latest_GPU=observed['latest_GPU'],formal_final_budget_completed=False,
        original56FOV_evaluated=False,all6_final_capability_gates_completed=False,
        actual_MRI_risk_certificates_issued=0,actual_MRI_task_benefit_measured=False,real_task_latency_measured=False,
        confirmation_patients_opened=False,validation_data_read=False,locked_IXI_opened=False,
        old_MIRA_MSValid84_confirmation_preserved=True,publication_claim_confirmed=False,goal_status='active',
        current_goal_turn_classification='progress',this_receipt_is_post_manifest_appendix=True)
    dest = ROOT/'SESSION_CHECKPOINT_RECEIPT_OBSERVED_HOLDOUT_2026-10-08.json'
    new(dest,receipt)
    print(json.dumps(dict(complete=True,receipt=entry(dest),archive_actual_tool_exit=0,stage_files=270,
        cumulative_frozen_files=3687,native_updates=17523,full_training_exit=None,
        goal_status='active',publication_claim_confirmed=False),ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
