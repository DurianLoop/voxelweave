"""Record five actual CPU exits and preserve evidence scope without issuing MRI claims."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def new(p,r):
    with p.open('x',encoding='utf-8') as s:json.dump(r,s,ensure_ascii=False,indent=2);s.write('\n')
def entry(path):
    p=ROOT/path;return dict(path=path,sha256=sha(p),bytes=p.stat().st_size)
def main():
    sys.stdout.reconfigure(encoding='utf-8');now=datetime.now(timezone.utc).isoformat()
    items=[
        ('risk_qualification','1f423b','experiments/patient_risk_cost_baseline_executor_qualification_2026_10_07/attempt01.json'),
        ('risk_independent','22c400','experiments/patient_risk_cost_baseline_executor_qualification_2026_10_07/independent_attempt01.json'),
        ('series_qualification','d47af1','experiments/patient_complete_series_panel_qualification_2026_10_07/attempt01.json'),
        ('series_rounding_qualification','cbbf85','experiments/patient_complete_series_panel_rounding_qualification_2026_10_07/attempt01.json'),
        ('series_independent','5e0378','experiments/patient_complete_series_panel_qualification_2026_10_07/independent_attempt01.json')]
    exits={key:dict(observed_tool_exit=0,observed_tool_chunk=chunk,result=entry(path),
        observation_source='Actual current exec_command output with explicit PowerShell exit forwarding.') for key,chunk,path in items}
    for row in exits.values():
        q=read(ROOT/row['result']['path']);assert q['complete'] and not q['errors'] and not q['publication_claim_confirmed']
        assert q['MRI_data_reads']==q['model_forwards']==q['GPU_forwards']==0
    q=read(ROOT/exits['risk_independent']['result']['path']);assert q['independent_selections_replayed']==9 and q['independent_risk_values_checked']==104
    q=read(ROOT/exits['series_independent']['result']['path']);assert q['patient_policy_rows_independently_replayed']==8 and q['panels_independently_replayed']==3
    receipt=dict(created_utc=now,complete=True,errors=[],script_sha256=sha(__file__),observed_exits=exits,
        all_five_actual_tool_exits_zero=True,new_MRI_pixels_or_GT_reads=0,new_model_or_GPU_forwards=0,
        new_training_updates=0,actual_MRI_risk_certificates_issued=0,publication_claim_confirmed=False)
    new(ROOT/'SESSION_OBSERVED_EXITS_PATIENT_BASELINE_2026-10-07.json',receipt)
    progress=dict(created_utc=now,complete=True,errors=[],own_live_runs=[99542],full_training_observed_tool_exit=None,
        latest_actual_training_poll=dict(chunk='ea302f',native_updates=9306,invocation02_new_updates=9207,
            cumulative_wall_seconds=20496.50812969997,returned_session=99542),PCHIP99_is_historical_not_realtime=True,
        latest_GPU_query=dict(chunk='c8850b',timestamp_local='2026/10/07 21:28:37.609',free_MiB=1394,total_MiB=24455,utilization_percent=89),
        GPU_authorized=True,GPU_new_experiment_not_run=True,original_56FOV_not_evaluated=True,
        original_last19998_not_frozen=True,original_direct_ideal_absolute_gate_failure_preserved=True,
        root_files_observed=[dict(path=str(ROOT.parent/name),sha256=sha(ROOT.parent/name)) for name in ('.gitignore','environment.yml')],
        other_processes_modified=False,publication_claim_confirmed=False,goal_status='active')
    new(ROOT/'SESSION_EXECUTION_PROGRESS_PATIENT_BASELINE_2026-10-07.json',progress)
    ledger=dict(created_utc=now,complete=True,errors=[],script_sha256=sha(__file__),
        previous_goal_turn_classification='progress',current_goal_turn_classification='progress',
        classification_evidence='New callable known-method selectors, full-patient aggregation, three executed qualifications and two independent replays.',
        actual_exits=entry('SESSION_OBSERVED_EXITS_PATIENT_BASELINE_2026-10-07.json'),
        progress=entry('SESSION_EXECUTION_PROGRESS_PATIENT_BASELINE_2026-10-07.json'),
        independent_selections=9,independent_risk_pvalues=104,independent_patient_panels=3,independent_patient_policy_rows=8,
        new_primary_papers_read=0,new_MRI_pixels_or_GT_reads=0,new_model_or_GPU_forwards=0,new_training_updates=0,
        entire_original_objective_preserved=True,publication_claim_confirmed=False,goal_status='active',
        known_method_implementation_not_novel_MRI_claim=True,
        limits=['Invalid-input paths independently checked only for recorded consistency',
            'Synthetic panels do not prove patient independence or MRI full-FOV execution',
            'No formal risk certificate without valid fresh calibration; empirical effectiveness still requires frozen unseen confirmation'])
    new(ROOT/'SESSION_EXECUTION_LEDGER_PATIENT_BASELINE_2026-10-07.json',ledger)
    print(json.dumps(dict(complete=True,actual_exit_records=5,independent_selections=9,risk_values=104,patient_panels=3)));return 0
if __name__=='__main__':raise SystemExit(main())
