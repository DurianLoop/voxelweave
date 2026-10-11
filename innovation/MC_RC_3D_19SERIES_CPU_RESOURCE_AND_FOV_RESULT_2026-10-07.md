# 19开发series真实CPU资源与完整推断成本

真实训练资源资格和完整FOV无评分计时均已完成并实际exit0，独立batch重建和metadata聚合核验也实际exit0。19series/11患者没有删样本。两臂每臂33资源更新全部丢弃；当前正式训练更新0。原单001 low-LR最后模型只用于计时，不是19series充分适配的模型。

| 输入 | 缓存 s | 更新 median/max s | 全19 FOV s | 构造+hash s | 1139 tiles |
|---|---:|---:|---:|---:|---:|
| native_reference | 31.61 | 1.71855/1.86293 | 358.20 | 10.74 | 1139 |
| raw_pchip | 59.28 | 1.70218/1.83966 | 395.83 | 39.23 | 1139 |

每臂 image+float32 GT 缓存1,909,712,000 bytes。实际4 intra-op/1 interop、below-normal、无CUDA；原资源JSON的内嵌cpu_threads=1为遗留guard常量，顶层4为实际设置。完整FOV计时不读GT，不评分，不保存体积；输出概率SHA证明生产记录，独立核验只核tile覆盖/时间聚合/来源，不是独立神经像素重放。计时总墙钟807.47s。

按新准备的每臂19,998更新（1818完整患者轮，每患者1818步）计算，两臂纯更新中位数估算19.00小时；按本次样本最大更新耗时估算20.57小时。后者也不是未来上界。两臂一次开发完整FOV另约12.57分钟。还需加入输入构造、正式随机初始模型的实际速度、checkpoint/核验，以及未实测的四验证推断；不得把纸面20k情景当完工保证或充分能力。

下一科学实验需另立正式协议：共同随机初始化、完全相同患者/series/GT/增强流、同容量和更新数、同最后checkpoint规则。低LR单001两臂从不同初始模型出发，不能取代此控制。正式预算冻结后再启动，能力门槛不调低；只在两臂最终权重冻结后读开发/已见验证效果。八确认和locked IXI test继续关闭，科学确认0。

[资源资格](experiments/mc_rc_3d_19series_cpu_low_lr_qualification_2026_10_07/attempt01.json) · [完整FOV计时](experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07/attempt01.json) · [metadata核验](experiments/mc_rc_3d_19series_fov_cpu_timing_2026_10_07/independent_metadata_and_time_aggregation_attempt01.json) · [预算计算](SESSION_LOW_LR_19SERIES_TRAINING_BUDGET_PREPARATION_2026-10-07.json)。
