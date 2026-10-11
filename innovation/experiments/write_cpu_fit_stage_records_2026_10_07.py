"""Record observed terminal exits and completed image review without changing old provenance."""
import hashlib,json,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_new(p,x):
    with p.open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    inherited='SESSION_INHERITED_CPU_FINAL_RESULT_HANDOFF_VERBATIM_2026-10-07.md'
    runs=[]
    for command,code,session,status in [
        ('run_mc_rc_3d_cpu_fixed_fit_2026_10_07.py',0,38045,'complete_1024_updates'),
        ('audit_mc_rc_3d_development_supervision_2026_10_07.py',0,None,'complete_608_draws'),
        ('summarize_mc_rc_3d_supervision_density_2026_10_07.py',0,None,'complete'),
        ('plot_mc_rc_3d_supervision_density_2026_10_07.py',0,None,'complete'),
        ('plan_mc_rc_3d_19series_resources_2026_10_07.py',0,None,'complete_metadata_only'),
        ('probe_mc_rc_3d_tiny_gpu_numerical_2026_10_07.py',1,None,'failed_cuda_visibility_zero_updates'),
        ('probe_mc_rc_3d_tiny_gpu_numerical_v2_2026_10_07.py',1,None,'failed_resource_after_one_synthetic_update'),
        ('probe_mc_rc_3d_tiny_gpu_numerical_v3_2026_10_07.py',1,None,'failed_resource_after_one_synthetic_update'),
        ('probe_mc_rc_3d_tiny_gpu_numerical_v4_2026_10_07.py',1,None,'failed_resource_after_one_synthetic_update')]:
        runs.append(dict(command=command,tool_exit=code,session_id=session,status=status,terminal=True,
                         observed_exit_provenance='Inherited user-provided handoff; do not re-run',
                         provenance_file=inherited,provenance_sha256=sha(ROOT/inherited)))
    for command,code,session,status in [
        ('verify_mc_rc_3d_cpu_fixed_fit_2026_10_07.py',0,75652,'complete_independent_replay'),
        ('diagnose_mc_rc_3d_final_patch_2026_10_07.py',0,91627,'complete_four_variants_all_heads'),
        ('report_mc_rc_3d_cpu_fixed_fit_2026_10_07.py',0,None,'complete_report_and_original_figure'),
        ('plot_mc_rc_3d_cpu_fixed_fit_v2_2026_10_07.py',0,None,'complete_separate_absRVE_figure'),
        ('fetch_feature_normalization_primary_2026_10_07.py',0,None,'acquisition_complete_next_stage_reading_not_yet_claimed')]:
        runs.append(dict(command=command,tool_exit=code,session_id=session,status=status,terminal=True,
                         observed_exit_provenance='Direct tool return in current continuation'))
    cmd=['nvidia-smi','--query-gpu=timestamp,name,memory.total,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits']
    observed=subprocess.run(cmd,capture_output=True,text=True,timeout=20,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    assert observed.returncode==0
    ledger=dict(created_utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
                all_own_runs_terminal_from_observed_tool_exits=True,runs=runs,live_own_runs=[],
                actual_patient_cpu_updates=1024,actual_synthetic_gpu_updates=3,actual_patient_gpu_updates=0,
                latest_totals_only_gpu_observation=dict(command=cmd,stdout=observed.stdout.strip(),exit_code=observed.returncode,pids_requested=False),
                complete_gpu_totals_v2_entry_started=False,complete_gpu_startup_floor_bytes=8_000_000_000,
                tool_read_failures=[dict(kind='rg_literal_glob_os123',exit_code=1,files_changed=False),
                                    dict(kind='python_inline_windows_quoting_NameError',exit_code=1,files_changed=False),
                                    dict(kind='powershell_foreach_pipeline_parse_error',exit_code=1,files_changed=False)],
                confirmation_patients_opened=False,scientific_confirmation_patients=0,publication_claim_confirmed=False,
                goal_status='active',user_processes_enumerated_or_modified=False,root_environment_modified=False)
    write_new(ROOT/'SESSION_EXECUTION_LEDGER_CPU_FIT_FOLLOWUP_2026-10-07.json',ledger)
    paths=['figures/mc_rc_3d_supervision_density_2026_10_07/supervision_density.png',
           'figures/mc_rc_3d_cpu_fixed_fit_2026_10_07/fixed_fit_results_v2.png']
    visual=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
                script_sha256=sha(Path(__file__)),method='Actual tools.view_image in current continuation',
                figures=[dict(path=p,sha256=sha(ROOT/p),visual_review_completed=True,
                              findings='Axes, labels and ranges readable; no clipping or overlap observed') for p in paths],
                original_fit_figure=dict(path='figures/mc_rc_3d_cpu_fixed_fit_2026_10_07/fixed_fit_results.png',
                    sha256=sha(ROOT/'figures/mc_rc_3d_cpu_fixed_fit_2026_10_07/fixed_fit_results.png'),
                    visual_review_completed=True,findings='Readable but absRVE compresses overlap metrics; original retained and new v2 separates axes'),
                historical_provenance_visual_flags_preserved=True,metric_values_and_fit_gates_unchanged=True)
    write_new(ROOT/'SESSION_CPU_FIT_FIGURE_VISUAL_REVIEW_2026-10-07.json',visual)
    print(json.dumps(dict(complete=True,runs=len(runs),gpu_totals=observed.stdout.strip()),ensure_ascii=False))
if __name__=='__main__':main()
