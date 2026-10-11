# 实际观测特征路径成本：一次CPU全19series

实际19个observed包／11开发患者，两fold合计38，17特征及完整fold scores与原冻结资格19/19严格相同。一次CPU1／interop1／BLAS1、CUDA不可见、below-normal，无warmup／重复；cold child从创建到全部输出并退出=23.848797200s，launcher自身receipt写出未包含。

显式生产相位合计19.377979001s；逐series含资格检查／GC／审计总时21.491694601s。生产相位是子集，fold-plan等少量生产开销与验证开销混在未分配部分，不将19.378s说成完整端到端cost。cold缓存没有控制，原用户训练／系统负载在场。

| 显式相位 | 全19series秒数 |
|---|---:|
| observed_package_hash_verification_seconds | 0.122158000 |
| observed_IO_decode_seconds | 1.161220800 |
| input_array_metadata_verification_seconds | 0.205005600 |
| source_construct_seconds | 2.488275100 |
| two_interpolation_predictions_seconds | 11.861229200 |
| reference_projection_seconds | 1.288525500 |
| full_plane_scores_seconds | 2.577501600 |
| feature_reduce_seconds | 0.001226800 |
| feature_equality_verification_seconds | 0.000661700 |

独立元数据作业只读receipt和上一特征表，重新核所有17特征、nonnegative时间、timing边界与fsum患者聚合，无新MRI加载；不是独立测第二组墙时或重新独立插值数学。

| 患者 | series数 | 显式生产相位合计秒 | series含检查合计秒 |
|---|---:|---:|---:|
| VS-MC-RC-001 | 2 | 0.186396400 | 0.330570800 |
| VS-MC-RC-002 | 2 | 3.571557600 | 3.872299300 |
| VS-MC-RC-004 | 1 | 0.887263600 | 1.029940900 |
| VS-MC-RC-005 | 2 | 6.635758100 | 6.888620900 |
| VS-MC-RC-006 | 3 | 2.214798300 | 2.500560400 |
| VS-MC-RC-007 | 1 | 0.572715400 | 0.642178300 |
| VS-MC-RC-009 | 2 | 1.156593100 | 1.359794800 |
| VS-MC-RC-010 | 3 | 2.311181400 | 2.672797800 |
| VS-MC-RC-011 | 1 | 0.587007800 | 0.697482100 |
| VS-MC-RC-012 | 1 | 0.667550500 | 0.804118700 |
| VS-MC-RC-013 | 1 | 0.587156800 | 0.693330600 |

患者内全部series合并后、患者等权相位均值=1.761634455s；范围0.186396400–6.635758100s。共享启动／输出／审计等费用保持单列；此均值不是完整患者deployment延迟。

本阶段新医学observed加载19、模型／native GT／缺失MR／验证／确认／lockedIXI数组0、神经／GPUforward／训练更新0；未重复counterfactual或Hermite资格。原108.467s是上一阶段生产＋失败＋独立资格总时，不作为部署feature cost。

费用用途：后续动作收益实验把真实feature计算加入总预算，和cost-only／random／risk／error强控制匹配。现在没有任务网／修正／定位／transfer／组合／后处理的完整费用，也没有ΔQ标签、临床效果或可发表收益claim；不推GPU速度或成本优势。

[源码](experiments/measure_deployment_observed_feature_cost_2026_10_08.py)；[执行前协议](DEPLOYMENT_FEATURE_COST_AND_DOWNSTREAM_PROTOCOL_2026-10-08.md)；[真实child结果](experiments/deployment_observed_feature_cost_2026_10_08/attempt01.json)；[cold launcher receipt](experiments/deployment_observed_feature_cost_launch_2026_10_08/launch_attempt01.json)；[独立metadata核验](experiments/deployment_observed_feature_cost_metadata_2026_10_08/attempt01.json)；[汇总JSON](experiments/deployment_feature_cost_summary_2026_10_08.json)。
