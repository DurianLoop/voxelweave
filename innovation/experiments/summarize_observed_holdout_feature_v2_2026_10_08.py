"""Metadata-only summary and deployable feature table; no new MRI array reads."""
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def entry(p):
    return dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def new(p, data):
    with p.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    paths = [ROOT/('experiments/'+d+'/attempt01.json') for d in (
        'observed_holdout_feature_qualification_2026_10_08',
        'observed_holdout_feature_independent_2026_10_08',
        'observed_holdout_feature_independent_layout_v2_2026_10_08')]
    prod, failed, checked = map(read, paths)
    assert prod['complete'] and checked['complete'] and not prod['errors'] and not checked['errors']
    assert not failed['complete'] and failed['errors'] and len(failed['series']) == 2
    assert len(prod['series']) == len(checked['series']) == 19
    assert [s['patient'] for s in prod['series']] == [s['patient'] for s in checked['series']]
    assert prod['actual_real_folds_completed'] == prod['real_counterfactuals_completed'] == 38
    assert failed['medical_observed_packages_loaded'] == 3
    assert failed['real_folds_verified'] == failed['real_counterfactuals_verified'] == 5
    assert checked['real_folds_verified'] == checked['real_counterfactuals_verified'] == 38
    assert checked['medical_observed_packages_loaded'] == 19
    assert all(checked['gate'].values())
    patients = []
    table = []
    for s in prod['series']:
        linear, pchip = (s['merged_scores'][k]['MSE'] for k in ('linear','pchip'))
        retained_gaps = [b-a for f in s['folds'] for a,b in zip(f['retained_positions_mm'],f['retained_positions_mm'][1:])]
        values = dict(observed_adjacent_spacing_mm=s['observed_adjacent_spacing_mm'],
            retained_adjacent_spacing_min_mm=min(retained_gaps),
            retained_adjacent_spacing_max_mm=max(retained_gaps),
            observed_anchor_count=len(s['observed_indices']),
            heldout_observed_plane_count=sum(len(f['heldout_ordinals']) for f in s['folds']),
            target_rows=s['target_rc'][0], target_cols=s['target_rc'][1],
            heldout_observed_pixel_count=s['merged_scores']['linear']['elements'],
            heldout_linear_MSE=linear, heldout_pchip_MSE=pchip,
            heldout_MSE_pchip_minus_linear=pchip-linear,
            heldout_linear_MAE=s['merged_scores']['linear']['MAE'],
            heldout_pchip_MAE=s['merged_scores']['pchip']['MAE'],
            retained_mean_min=min(f['retained_statistics']['mean'] for f in s['folds']),
            retained_mean_max=max(f['retained_statistics']['mean'] for f in s['folds']),
            retained_population_std_min=min(f['retained_statistics']['population_std'] for f in s['folds']),
            retained_population_std_max=max(f['retained_statistics']['population_std'] for f in s['folds']))
        assert all(math.isfinite(v) for v in values.values())
        table.append(dict(patient=s['patient'], series_uid=s['uid'],
            observed_package_sha256=s['observed_package_sha256'], features=values,
            observed_reference_is_available_at_deployment=True,
            MRI_task_labels=None, action_utility_labels=None, full_action_cost=None))
    for patient in sorted({s['patient'] for s in prod['series']}):
        series = [s for s in prod['series'] if s['patient']==patient]
        means = {k:math.fsum(s['merged_scores'][k]['MSE'] for s in series)/len(series) for k in ('linear','pchip')}
        patients.append(dict(patient=patient, series=len(series), series_equal_mean_MSE=means,
            MSE_difference_pchip_minus_linear=means['pchip']-means['linear']))
    totals = {k:math.fsum(p['series_equal_mean_MSE'][k] for p in patients)/len(patients) for k in ('linear','pchip')}
    assert len(patients) == 11
    for k in totals:
        assert math.isclose(totals[k], prod['patient_equal_observed_MSE'][k], rel_tol=1e-14, abs_tol=1e-14)
        assert math.isclose(totals[k], checked['independent_patient_equal_observed_MSE'][k], rel_tol=1e-14, abs_tol=1e-14)
    projection = [f['source_projection_check']['max_abs_error'] for s in checked['series'] for f in s['folds']]
    mathematics = [c for s in checked['series'] for f in s['folds'] for c in f['independent_full_heldout_checks']]
    layouts = [dict(patient=s['patient'],uid=prod['series'][i]['uid'],fold=f['fold'],**f['previous_layout_diagnostic'])
               for i,s in enumerate(checked['series']) for f in s['folds']]
    difference = totals['pchip']-totals['linear']
    common = dict(created_utc=datetime.now(timezone.utc).isoformat(), complete=True, errors=[],
        source_bindings=[entry(Path(__file__))]+[entry(p) for p in paths],
        unique_development_patients=11, unique_development_series=19,
        medical_array_load_events_in_this_summary=0, neural_forwards=0, GPU_forwards=0, training_updates=0,
        actual_MRI_task_benefit_measured=False, interpolation_method_selected=False,
        theoretical_risk_certificate_issued=False, publication_claim_confirmed=False, goal_status='active')
    feature = dict(common, schema_version=1, rows=table,
        feature_names=list(table[0]['features']), aggregation='fold pixels -> series; series equal within patient; patients equal',
        use='ordinary empirical predictors from legally observed planes, not clean-image risk certificates',
        required_future_label='paired actual task Q(current state + action) - Q(current state)',
        cross_fitting_group='patient', preselected_route_or_threshold=None,
        independent_pixels_are_not_independent_patients=True)
    table_path = ROOT/'experiments/observed_holdout_feature_table_2026_10_08.json'
    new(table_path, feature)
    summary = dict(common, source_bindings=common['source_bindings']+[entry(table_path)],
        stage_medical_observed_package_load_events=41, production_observed_load_events=19,
        failed_independent_observed_load_events=3, v2_independent_observed_load_events=19,
        unique_real_folds=38, counterfactual_check_events=81,
        successful_production_counterfactuals=38, failed_attempt_completed_counterfactuals=5,
        successful_independent_v2_counterfactuals=38,
        production_seconds=prod['elapsed_seconds'], failed_attempt_seconds=failed['elapsed_seconds'],
        independent_v2_seconds=checked['elapsed_seconds'],
        total_measured_job_body_seconds=math.fsum(d['elapsed_seconds'] for d in (prod,failed,checked)),
        original_independent_failed=True, original_failure='series3 fold1 retained_statistics exact equality',
        old_layout_difference_folds=[v for v in layouts if not v['previous_layout_matches_production']],
        independent_sampled_bilinear_max_abs_error=max(projection),
        independent_full_heldout_max_abs_error={k:max(c['max_abs_error'] for c in mathematics if c['name']=='full_nonuniform_'+k) for k in ('linear','pchip')},
        independent_full_heldout_elements=sum(c['elements'] for c in mathematics),
        atol=3e-5, rtol=3e-5, tolerance_widened=False,
        patient_features=patients, patient_equal_observed_MSE=totals,
        patient_equal_observed_MSE_difference_pchip_minus_linear=difference,
        relative_observed_MSE_difference_percent=100*difference/totals['linear'],
        positive_difference_series=sum(s['observed_MSE_difference_pchip_minus_linear']>0 for s in prod['series']),
        negative_difference_series=sum(s['observed_MSE_difference_pchip_minus_linear']<0 for s in prod['series']),
        positive_difference_patients=sum(p['MSE_difference_pchip_minus_linear']>0 for p in patients),
        negative_difference_patients=sum(p['MSE_difference_pchip_minus_linear']<0 for p in patients),
        negative_series=[dict(patient=s['patient'],uid=s['uid'],difference=s['observed_MSE_difference_pchip_minus_linear'])
            for s in prod['series'] if s['observed_MSE_difference_pchip_minus_linear']<0],
        geometry_ranges_mm={k:dict(min=min(row['features'][k] for row in table),max=max(row['features'][k] for row in table))
            for k in ('observed_adjacent_spacing_mm','retained_adjacent_spacing_min_mm','retained_adjacent_spacing_max_mm')},
        future_action_labels_available=False, patient_level_inference_from_pixels_prohibited=True,
        baseline_deployment_using_all_observed_statistics_is_legal=True,
        original_live_training_excluded_from_new_array_and_compute_counts=True)
    assert summary['positive_difference_series']==18 and summary['negative_difference_series']==1
    new(ROOT/'experiments/observed_holdout_feature_summary_2026_10_08.json',summary)
    rows=['# 真实19系列的观测留出特征与独立核验结果', '',
        '本阶段完成11开发患者／19系列／38固定fold的普通可观测特征资格。没有MRI病灶任务评分；这不是新的去噪算法、插值方法或理论风险证书。', '',
        f'患者等权（患者内series等权）normalized MSE：linear={totals["linear"]:.12g}，PCHIP={totals["pchip"]:.12g}；差={difference:.12g}（{summary["relative_observed_MSE_difference_percent"]:.6g}%）。18/19系列、10/11患者差为正，VS-MC-RC-007是保留的负差。', '',
        '| 患者 | series数 | linear MSE | PCHIP MSE | PCHIP−linear |',
        '|---|---:|---:|---:|---:|']
    rows.extend(f'| {p["patient"]} | {p["series"]} | {p["series_equal_mean_MSE"]["linear"]:.9g} | {p["series_equal_mean_MSE"]["pchip"]:.9g} | {p["MSE_difference_pchip_minus_linear"]:.9g} |' for p in patients)
    rows.extend(['', '先mask再用retained层统计／投影／预测，完成预测后才加入同retained统计的heldout reference；首末observed保留，奇偶内部层各留出一次。每fold仅改变heldout值+10000，source／两种完整预测SHA不变，而reference／scores改变。生产38和独立v2的38次完整检查均通过；原失败attempt另有5次已完成检查。81是检查事件，只有38个唯一真实fold。', '',
        '生产19包，原独立失败3包，新v2独立19包，共41次加载、唯一19包；原失败只完成2完整series／5fold，第3series fold1的统计严格相等失败保留。生产C-copy与fancy-index数组布局的浮点归约顺序不同；另冻v2指定C-copy，未改原生产结果和3e-5容差，另用1e-12独立中心矩核统计。', '',
        f'完整source／prediction／reference及score共享库重放exact；独立float32坐标bilinear是样点检查，最大绝对误差{max(projection):.9g}；独立非均匀Hermite覆盖完整heldout数组，linear/PCHIP最大绝对误差分别{summary["independent_full_heldout_max_abs_error"]["linear"]:.9g}/{summary["independent_full_heldout_max_abs_error"]["pchip"]:.9g}。共享库SHA重放与独立数学核验分开记录。', '',
        '留出将每4层observed中的一部分去掉，改变间距和输入量；首末保留亦会产生非均匀间距。本误差包括完整面内背景，且归一化统计随fold变化；不能推出原x4缺层恢复、病灶分割或线性部署更好，不据此选winner。MRI magnitude无偏与噪声条件独立未证明；原部署从全部合法observed计算统计本来合法，只有heldout诊断的预测需要先mask。', '',
        '已导出[19行可观测特征表](experiments/observed_holdout_feature_table_2026_10_08.json)，其中任务标签、动作收益、完整成本明确为null。后续必须与真实患者配对动作收益和实测成本连接，整患者cross-fitting；本表不含模型、native GT、验证、确认、lockedIXI或缺失MR。没有新增神经／GPUforward／训练更新。', '',
        '[科学JSON](experiments/observed_holdout_feature_summary_2026_10_08.json)；[原协议](OBSERVED_HOLDOUT_FEATURE_PROTOCOL_2026-10-08.md)；[原失败](experiments/observed_holdout_feature_independent_2026_10_08/attempt01.json)；[v2布局协议](OBSERVED_HOLDOUT_FEATURE_LAYOUT_V2_PROTOCOL_2026-10-08.md)；[v2结果](experiments/observed_holdout_feature_independent_layout_v2_2026_10_08/attempt01.json)。', ''])
    with (ROOT/'OBSERVED_HOLDOUT_FEATURE_RESULT_2026-10-08.md').open('x',encoding='utf-8') as f:
        f.write('\n'.join(rows))
    print(json.dumps({k:summary[k] for k in ('complete','stage_medical_observed_package_load_events','counterfactual_check_events',
        'patient_equal_observed_MSE','relative_observed_MSE_difference_percent','positive_difference_series',
        'positive_difference_patients','independent_sampled_bilinear_max_abs_error','independent_full_heldout_max_abs_error')},ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
