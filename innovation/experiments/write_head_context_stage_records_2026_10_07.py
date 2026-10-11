"""Save observed exits, final totals-only GPU reading and actual image review for this new stage."""
import json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from mc_rc_observed_only_training_input import ROOT,sha
def write_new(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    runs=[]
    for command,code,session,status in [
        ('run_mc_rc_3d_frozen_feature_head_fit_2026_10_07.py',0,4611,'complete_4096_head_updates'),
        ('verify_mc_rc_3d_frozen_feature_head_fit_2026_10_07.py',0,47610,'complete_all_four_module_replays'),
        ('report_mc_rc_3d_frozen_feature_head_fit_2026_10_07.py',0,None,'complete'),
        ('render_feature_normalization_formula_pages_2026_10_07.py',0,None,'complete_three_formula_pages'),
        ('write_feature_normalization_reading_provenance_2026_10_07.py',0,None,'complete_three_primary_texts_33_pages'),
        ('preflight_mc_rc_3d_reference_in_2026_10_07.py',1,None,'failed_numerical_self_replay_zero_updates'),
        ('diagnose_mc_rc_3d_reference_in_self_replay_2026_10_07.py',0,None,'complete_failed_preflight_measurements'),
        ('prepare_reference_in_preflight_v2_2026_10_07.py',0,None,'complete_new_entry'),
        ('preflight_mc_rc_3d_reference_in_v2_2026_10_07.py',1,None,'failed_observed_npz_zip_guard_after_synthetic_pass'),
        ('prepare_reference_in_preflight_v3_2026_10_07.py',0,None,'complete_new_entry'),
        ('preflight_mc_rc_3d_reference_in_v3_2026_10_07.py',0,24427,'complete_label_native_free_preflight'),
        ('run_mc_rc_3d_all_tile_head_fit_2026_10_07.py',0,13677,'complete_2048_head_updates'),
        ('verify_mc_rc_3d_all_tile_head_fit_2026_10_07.py',0,83967,'complete_feature_label_sha_and_full_fov_replays'),
        ('report_mc_rc_3d_all_tile_head_fit_2026_10_07.py',0,None,'complete'),
        ('audit_mc_rc_3d_label_roundtrip_2026_10_07.py',1,48529,'failed_float32_probability_tolerance_at_series_6'),
        ('prepare_mc_rc_3d_label_roundtrip_v2_2026_10_07.py',0,None,'complete_new_entry'),
        ('audit_mc_rc_3d_label_roundtrip_v2_2026_10_07.py',1,None,'failed_certificate_path_JSONDecodeError_zero_series'),
        ('prepare_mc_rc_3d_label_roundtrip_v3_2026_10_07.py',0,None,'complete_new_entry'),
        ('audit_mc_rc_3d_label_roundtrip_v3_2026_10_07.py',0,37599,'complete_all19_coordinate_and_original_float32_reporting'),
        ('report_mc_rc_3d_label_roundtrip_2026_10_07.py',0,None,'complete')]:
        runs.append(dict(command=command,tool_exit=code,session_id=session,status=status,terminal=True,
                         observed_exit_provenance='Actual tool exit in current continuation'))
    command=['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits']
    run=subprocess.run(command,capture_output=True,text=True,timeout=20,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));assert run.returncode==0
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(Path(__file__)),
                all_own_runs_terminal_from_observed_tool_exits=True,runs=runs,live_own_runs=[],
                new_patient_cpu_head_parameter_updates=6144,new_patient_gpu_updates=0,new_synthetic_gpu_updates=0,
                inherited_full_network_cpu_updates=1024,inherited_synthetic_gpu_updates=3,
                latest_totals_only_gpu_observation=dict(command=command,stdout=run.stdout.strip(),exit_code=run.returncode,pids_requested=False),
                complete_gpu_attempt02_started=False,complete_gpu_startup_floor_bytes=8_000_000_000,
                confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,
                goal_status='active',user_processes_enumerated_or_modified=False,root_environment_modified=False,
                artifacts_only_under_innovation=True)
    write_new(ROOT/'SESSION_EXECUTION_LEDGER_HEAD_CONTEXT_2026-10-07.json',ledger)
    figures=['figures/mc_rc_3d_frozen_feature_head_fit_2026_10_07/head_fit_results.png',
             'figures/mc_rc_3d_all_tile_head_fit_2026_10_07/all_tile_head_fit_results.png']
    visual=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],script_sha256=sha(Path(__file__)),
                figures=[dict(path=p,sha256=sha(ROOT/p),actual_view_image_completed=True,
                              observations='All panels and labels readable; no clipping/overlap observed; gate lines and failed status retained') for p in figures],
                original_provenance_visual_flags_preserved=True,formula_pages_documented_in_reading_provenance=True)
    write_new(ROOT/'SESSION_HEAD_CONTEXT_FIGURE_VISUAL_REVIEW_2026-10-07.json',visual)
    print(json.dumps(dict(complete=True,runs=len(runs),head_updates=6144,gpu_totals=run.stdout.strip()),ensure_ascii=False))
if __name__=='__main__':main()
