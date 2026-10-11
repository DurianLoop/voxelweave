"""Independent metadata aggregation and exact feature replay; no new medical arrays."""
import hashlib,json,math,sys
from datetime import datetime,timezone
from pathlib import Path
from mc_rc_reference_resources_2026_10_07 import resource_guard
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/deployment_observed_feature_cost_metadata_2026_10_08'


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(exist_ok=False)
    paths=[ROOT/p for p in ('experiments/deployment_observed_feature_cost_2026_10_08/attempt01.json',
        'experiments/deployment_observed_feature_cost_launch_2026_10_08/launch_attempt01.json',
        'experiments/observed_holdout_feature_table_2026_10_08.json')]
    body,launch,table=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
    assert all(v['complete'] and not v['errors'] for v in (body,launch,table))
    assert launch['child_actual_subprocess_exit']==0
    before=resource_guard()
    expected={(v['patient'],v['series_uid']):v['features'] for v in table['rows']}
    assert len(body['series'])==19 and len(expected)==19
    assert body['medical_observed_packages_loaded']==19 and body['real_folds_completed']==38
    assert all(body[k]==0 for k in ('model_arrays_loaded','neural_forwards','GPU_forwards','training_updates','counterfactuals_run','warmups'))
    for v in body['series']:
        assert v['features']==expected[(v['patient'],v['uid'])] and len(v['features'])==17
        assert all(math.isfinite(t) and t>=0 for t in v['phase_seconds'].values())
        assert v['measured_series_total_with_qualification_seconds']>=math.fsum(v['phase_seconds'].values())
        assert v['features_and_fold_scores_exactly_equal_to_frozen_qualification']
    totals={key:math.fsum(v['phase_seconds'][key] for v in body['series']) for key in body['series'][0]['phase_seconds']}
    assert totals==body['phase_totals_seconds']
    core=math.fsum(v['summed_production_phases_seconds'] for v in body['series'])
    assert core==body['total_production_phase_seconds']
    assert launch['cold_child_end_to_end_wall_seconds']>=body['child_elapsed_before_final_output_seconds']>=body['total_series_with_qualification_seconds']>=core
    patients=[]
    for patient in sorted({v['patient'] for v in body['series']}):
        cases=[v for v in body['series'] if v['patient']==patient]
        patients.append(dict(patient=patient,series=len(cases),
            production_phases_sum_seconds=math.fsum(v['summed_production_phases_seconds'] for v in cases),
            measured_series_with_qualification_sum_seconds=math.fsum(v['measured_series_total_with_qualification_seconds'] for v in cases)))
    assert patients==body['patient_costs'] and len(patients)==11
    equal=math.fsum(v['production_phases_sum_seconds'] for v in patients)/11
    assert equal==body['patient_equal_production_phase_seconds']
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__))]+[entry(p) for p in paths],resources_before=before,
        resources_after=resource_guard(),medical_arrays_loaded=0,model_arrays_loaded=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,series_exact_features=19,
        independent_patient_aggregation=True,phase_totals_exact=True,timing_boundaries_checked=True,
        production_phase_seconds=core,cold_child_end_to_end_seconds=launch['cold_child_end_to_end_wall_seconds'],
        patient_equal_production_phase_seconds=equal,phase_totals_seconds=totals,patient_costs=patients,
        full_action_cost_measured=False,task_latency_measured=False,publication_claim_confirmed=False,goal_status='active')
    with (OUT/'attempt01.json').open('x',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:r[k] for k in ('complete','series_exact_features','production_phase_seconds',
        'cold_child_end_to_end_seconds','patient_equal_production_phase_seconds','full_action_cost_measured')},ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
