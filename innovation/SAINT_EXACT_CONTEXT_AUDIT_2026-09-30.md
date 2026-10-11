# SAINT acquired-only 影响量的精确上下文复核

这是看过旧原稿和新 HAT/SwinIR 结果后的探索性复核，只读 [SAINT 原逐行 CSV](../design/paper/ARCHITECTURE_COVERAGE_CLOSURE/outputs/saint_acquired_observations.csv)，不运行网络或接触 GPU。脚本、SHA-256、病例留出逐行预测和全部数值在[结果目录](experiments/saint_exact_context_audit/summary.json)。

原稿对 SAINT 恰好一共享锚点的固定 count 关联只调整 span/asymmetry 与检查对象：fastMRI +0.3798、IXI +0.4174。按本轮更严口径，同时消除**目标与精确上下文固定效应**后，主幅度 `.01` 分别为 **+0.2563**（24 检查对象、72 目标，探索性检查对象区间 `[+0.1179,+0.4001]`）和 **+0.3831**（115 对象、345 目标，`[+0.3268,+0.4355]`）。`.005/.01/.02/-.01` 四幅度在两队列的八个点估计均为正，范围 +0.2013 至 +0.4060；幅度结果没有同时区间，也没有逐响应锚点错配检验。

按检查对象五折留出、精确上下文 one-hot 岭回归 `alpha=1`，加入影响量后的误差余弦 MAE 在 fastMRI 从 `0.024257` 降至 `0.022506`（增益 `+0.001752`，探索性病例区间 `[+0.000689,+0.002832]`），IXI 从 `0.026369` 降至 `0.023780`（`+0.002588`，`[+0.001456,+0.003807]`）。然而每目标四候选的平均 Spearman 排序在 fastMRI **0.753→0.708**、IXI **0.857→0.849**，均退化。较低 MAE 只表示该监督映射对成对余弦的数值预测有帮助，不能替代实际上下文选择、病灶保护或部署正确性评分。

这使旧队列的严格几何后正关联从 HAT/SwinIR 延伸到第三种可兼容架构，但所有区间是结果后探索，且 SAINT 在[原稿适格审计](../design/paper/ARCHITECTURE_COVERAGE_CLOSURE/FIVE_ARCH_ACQUIRED_ONLY_INFLUENCE.md)中的接口/精度合同与外部 MSValid 不同。不能以 SAINT 的内部结果覆盖 [MSValid 跨架构严格基线负结果](INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md)。

**更严格的原始响应错配负对照削弱了 SAINT 身份特异性结论。** 按[已写方案](SAINT_RESPONSE_ID_PLACEBO_PLAN_2026-09-30.md)逐一核验 417 份 SAINT NPZ 的 SHA-256，原影响分数最大复算差 `<1e-16`。[逐行分数与汇总](experiments/saint_response_id_placebo/summary.json)如下：

| 队列 | 正确配对偏相关 | 错配 A | 错配 B | 正确减错配均值；探索性病例区间 |
|---|---:|---:|---:|---:|
| fastMRI | +0.2563 | +0.2501 | +0.1517 | +0.0554 `[-0.1004,+0.2275]` |
| IXI | +0.3831 | -0.0556 | +0.3871 | +0.2173 `[+0.1663,+0.2680]` |

结果后拆开两种错配的[敏感性区间](experiments/saint_placebo_component_sensitivity/summary.json)更清楚：fastMRI 正确减错配 A 仅 `+0.0062`，区间跨零；IXI 正确减错配 B 为 `-0.0040`，区间也跨零。即使 IXI 的**平均错配**对照为正，不能说正确配对稳定优于**每一种**错配。SAINT 对锚点响应可能有位置耦合/空间平滑，因此这里只保留“精确几何后条件关联”和数值 MAE 观察，不把它列为 HAT/SwinIR 等级的物理 ID 特异性复制，也不据此推广可部署评分。
