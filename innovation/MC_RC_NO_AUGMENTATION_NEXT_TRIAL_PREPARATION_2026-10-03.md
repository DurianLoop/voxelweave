# 后续尝试准备与运行边界

[四臂结果](MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_RESULT_2026-10-03.md)和[19系列零前向采样预检](experiments/mc_rc_no_augmentation_development_cpu_preflight/attempt_01.json)已完成。新11开发固定20000步无增强训练的[协议](MC_RC_NO_AUGMENTATION_ALL_DEVELOPMENT_CPU_PROTOCOL_2026-10-03.md)、[运行器](experiments/run_mc_rc_no_augmentation_all_development_cpu.py)已实现；配方准备的历史状态见[准备记录](experiments/no_augmentation_all_development_preparation_2026-10-03.json)。它不是新确认或重建方法训练。

运行状态以[启动观测](literature/source_cache/no_augmentation_training_launch_observation_2026-10-03.json)和[动态训练结果](experiments/mc_rc_no_augmentation_all_development_cpu/attempt_01.json)为准。若该任务live或已完成，不重跑该入口；exist_ok=False用于防覆盖。接续只能用当前session轮询，不按估计时间重启。原factorial25480、verifier53787、输入预检31096都已经实际exit0。

| 尚不能完成的科学检验 | 已准备的具体条件 | 仍缺的工作 |
|---|---|---|
| 多患者完整任务能力 | 11开发19series固定20k无增强；冻结后19开发诊断、四验证9series raw PCHIP/linear；沿用原患者均值能力门槛 | 当前训练完成、独立20000draw/checkpoint核验、新评价binding/所有预测与完整plane复核 |
| 原生与稀疏能力对照 | 只允许开发/验证；完整MR在单独native分支；不进入observed分支 | 独立native loader、身份/统计证明、同预算native训练/评价 |
| 原6×5公平矩阵 | 同patient/series/draw/容量/统计/监督/20000更新，最后权重；全部条件保存 | 新完整任务能力通过、输入/协议和具体训练运行器冻结；不是可直接运行的矩阵 |
| 直接任务/随机分辨率 | 两篇新原文的采样/模糊/CarveMix是近邻；直接从同observed输入预测，区分真实隔层与模糊 | 公平容量/预算版本实现，物理位置/目标合同、独立预检；不得用额外模态或五模型集成作同预算 |
| observable缺层修正 | 不读隐藏MR/GT ROI，输入只能observed像素/spacing/位置及允许预测；锚点/尾部保留 | 适配后残余证据、具体非线性政策与随机/固定/同容量强对照、冻结后的患者级确认 |
| 最终可发表claim | 八确认患者/十二series不提前开；第二独立训练任务网络；患者聚合与bootstrap | 前面所有能力/公平门槛；当前科学确认0，不能填入预期收益 |

GPU忙的期间这些准备和训练均CPU单线程，资源守卫和below-normal只作用于自身。用户已有终端训练、IXI锁定test和根环境不操作。训练/验证失败会保留，不以总Dice过门槛忽略tail FP、空GT或边界指标。
