"""Write measured phase and patient costs from frozen receipts, no new MRI arrays."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def entry(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    paths=[ROOT/p for p in ('experiments/deployment_observed_feature_cost_2026_10_08/attempt01.json',
        'experiments/deployment_observed_feature_cost_launch_2026_10_08/launch_attempt01.json',
        'experiments/deployment_observed_feature_cost_metadata_2026_10_08/attempt01.json')]
    body,launch,checked=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
    assert all(v['complete'] and not v['errors'] for v in (body,launch,checked))
    r=dict(created_utc=datetime.now(timezone.utc).isoformat(),complete=True,errors=[],
        source_bindings=[entry(Path(__file__))]+[entry(p) for p in paths],
        stage_medical_observed_package_load_events=19,unique_development_patients=11,unique_development_series=19,
        real_folds_executed=38,feature_names=17,series_features_and_fold_scores_exact=19,
        metadata_verifier_new_medical_array_loads=0,summary_new_medical_array_loads=0,
        neural_forwards=0,GPU_forwards=0,training_updates=0,model_arrays_loaded=0,
        measured_cold_child_end_to_end_seconds=launch['cold_child_end_to_end_wall_seconds'],
        measured_production_phase_subset_seconds=body['total_production_phase_seconds'],
        measured_series_with_qualification_total_seconds=body['total_series_with_qualification_seconds'],
        phase_totals_seconds=body['phase_totals_seconds'],patient_costs=body['patient_costs'],
        patient_equal_production_phase_subset_seconds=body['patient_equal_production_phase_seconds'],
        patient_phase_subset_range_seconds=dict(min=min(v['production_phases_sum_seconds'] for v in body['patient_costs']),
            max=max(v['production_phases_sum_seconds'] for v in body['patient_costs'])),
        repeats=1,warmups=0,cache_state_controlled=False,independent_timing_repeated=False,
        independent_metadata_aggregation_passed=True,full_action_cost_measured=False,
        actual_MRI_task_benefit_measured=False,real_task_latency_measured=False,
        publication_claim_confirmed=False,goal_status='active')
    path=ROOT/'experiments/deployment_feature_cost_summary_2026_10_08.json'
    with path.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    rows=['# 实际观测特征路径成本：一次CPU全19series', '',
        f'实际19个observed包／11开发患者，两fold合计38，17特征及完整fold scores与原冻结资格19/19严格相同。一次CPU1／interop1／BLAS1、CUDA不可见、below-normal，无warmup／重复；cold child从创建到全部输出并退出={r["measured_cold_child_end_to_end_seconds"]:.9f}s，launcher自身receipt写出未包含。', '',
        f'显式生产相位合计{r["measured_production_phase_subset_seconds"]:.9f}s；逐series含资格检查／GC／审计总时{r["measured_series_with_qualification_total_seconds"]:.9f}s。生产相位是子集，fold-plan等少量生产开销与验证开销混在未分配部分，不将19.378s说成完整端到端cost。cold缓存没有控制，原用户训练／系统负载在场。', '',
        '| 显式相位 | 全19series秒数 |', '|---|---:|']
    rows.extend(f'| {key} | {value:.9f} |' for key,value in r['phase_totals_seconds'].items())
    rows.extend(['', '独立元数据作业只读receipt和上一特征表，重新核所有17特征、nonnegative时间、timing边界与fsum患者聚合，无新MRI加载；不是独立测第二组墙时或重新独立插值数学。', '',
        '| 患者 | series数 | 显式生产相位合计秒 | series含检查合计秒 |', '|---|---:|---:|---:|'])
    rows.extend(f'| {v["patient"]} | {v["series"]} | {v["production_phases_sum_seconds"]:.9f} | {v["measured_series_with_qualification_sum_seconds"]:.9f} |' for v in r['patient_costs'])
    rows.extend(['', f'患者内全部series合并后、患者等权相位均值={r["patient_equal_production_phase_subset_seconds"]:.9f}s；范围{r["patient_phase_subset_range_seconds"]["min"]:.9f}–{r["patient_phase_subset_range_seconds"]["max"]:.9f}s。共享启动／输出／审计等费用保持单列；此均值不是完整患者deployment延迟。', '',
        '本阶段新医学observed加载19、模型／native GT／缺失MR／验证／确认／lockedIXI数组0、神经／GPUforward／训练更新0；未重复counterfactual或Hermite资格。原108.467s是上一阶段生产＋失败＋独立资格总时，不作为部署feature cost。', '',
        '费用用途：后续动作收益实验把真实feature计算加入总预算，和cost-only／random／risk／error强控制匹配。现在没有任务网／修正／定位／transfer／组合／后处理的完整费用，也没有ΔQ标签、临床效果或可发表收益claim；不推GPU速度或成本优势。', '',
        '[源码](experiments/measure_deployment_observed_feature_cost_2026_10_08.py)；[执行前协议](DEPLOYMENT_FEATURE_COST_AND_DOWNSTREAM_PROTOCOL_2026-10-08.md)；[真实child结果](experiments/deployment_observed_feature_cost_2026_10_08/attempt01.json)；[cold launcher receipt](experiments/deployment_observed_feature_cost_launch_2026_10_08/launch_attempt01.json)；[独立metadata核验](experiments/deployment_observed_feature_cost_metadata_2026_10_08/attempt01.json)；[汇总JSON](experiments/deployment_feature_cost_summary_2026_10_08.json)。', ''])
    with (ROOT/'DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md').open('x',encoding='utf-8') as f:f.write('\n'.join(rows))
    print(json.dumps({k:r[k] for k in ('complete','stage_medical_observed_package_load_events',
        'measured_cold_child_end_to_end_seconds','measured_production_phase_subset_seconds',
        'patient_equal_production_phase_subset_seconds','patient_phase_subset_range_seconds')},ensure_ascii=False),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
