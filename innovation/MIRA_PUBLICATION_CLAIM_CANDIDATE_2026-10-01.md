# MIRA 候选可发表主张：证据与边界

状态：**可审稿的科学主张候选，不等于投稿就绪。** 本文档在 P25–P84 剩余响应结果打开前写成。现有 CVPR 主文尚未同步 MSValid，fastMRI 使用/刊图与 NingXia 来源/伦理资料仍需作者真实原件；不能因本文件存在就通过[投稿门槛](CLAIM_PUBLICATION_GATE_2026-09-30.md)。

**时序更新（2026-10-01）：** 下文保留当时的 fastMRI 权重 MSValid 主张和历史选择记录，不能直接当成现行公开来源稿摘要。[现行公开来源草稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)使用同一 IXI 训练 HAT/SwinIR 对：MSValid 同患者结果后权重跟进 +24.1856 点、[共同缩放/反向](MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) +24.0358/+24.0681；ReMIND 后续冻结新来源 +26.3999 点、[共同缩放/反向](REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) +26.3236/+26.3049。后两类控制均在看过各自主结果后设计。最强句子是**固定模型对在两个发布层来源中的上下文依赖与成对误差对齐**，仍非纯锚点身份因果。ReMIND 的 `MPR` 标志必须随结果报告；稿件及许可门槛见[公开来源路线](PUBLIC_ONLY_MIRA_MANUSCRIPT_ROUTE_2026-10-01.md)。

## 一句话主张

在所测试的冻结 x4 脑 MRI 层间重建器中，**共享真实观测切片的两种估计可在仍有明显错误时高度一致；改变伙伴的真实锚点集合会显著提高同目标成对误差在输出分歧中的可观测比例**。旧 fastMRI/IXI 的 acquired-only 响应审计显示，正确物理锚点的响应配对含有超出精确上下文类别与错配响应的误差对齐信息；一个方案先于目标打开而固定的 HAT→SwinIR 主对照在不同来源 MSValid RRMS T2 队列复制了可观测性现象。这个句子是**有条件的经验审计**，不是“仅改变 ID 的因果效应”、新网络或可部署误差证书。

可用于摘要的英文核心句：`For frozen through-plane MRI interpolators, sharing observed slice anchors can make substantial paired error nearly invisible to prediction disagreement. A prespecified HAT-to-SwinIR comparison reproduced a 19.76-percentage-point disjoint-minus-shared increase in paired-error observability across 84 separately sourced RRMS examinations (95% patient-bootstrap interval 19.33–20.16), while acquired-only response audits on the original brain cohorts showed specificity to correctly matched physical anchors beyond exact context categories. These findings characterize a bounded measurement-dependence failure, not an identity-only causal effect or a calibrated per-case error detector.`

## 证据层级

| 层级 | 可以写什么 | 关键依据 | 不能跨越的边界 |
|---|---|---|---|
| 外部现象 | 单个预设 HAT→SwinIR 对照在新来源 84 人、479 目标中 `Delta O=+19.7565` 百分点，84/84 人为正；共同缩放、相位反向和线性伙伴仍同向。 | [事前 MSValid 主结果](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)、[结果后控制](MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md)、[共同缩放](MSVALID_COMMON_NORM_RESULT_2026-09-30.md) | 只是一对模型的外部确认；相位几何与完整邻层内容共变。 |
| 误差结构 | 该 `Delta O` 的代数对齐项 +19.6110 百分点、MSE 失衡项 +0.1456；近质量匹配目标仍同向。 | [误差分解](MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-09-30.md) | 同一 O/MSE 恒等式的结果后解释，不是独立机制实验。 |
| 内部响应机制 | HAT/SwinIR 正确锚点响应相对错配在四个同架构层和两个旧跨架构层均有精确上下文残余优势；[六项结果后同时区间](RESPONSE_PLACEBO_SIX_FAMILY_RESULT_2026-10-01.md)下界均正，但 fastMRI 跨架构几乎贴零。SAINT 的严格几何后关联为正，**但其一种错配可与正确配对相当**。 | [四层错配](ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md)、[旧跨架构](CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md)、[SAINT 混合负对照](SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md) | 全是结果后旧队列分析；六项 family 不能补偿历史选择；错配响应不等于真实图像/物理 ID 随机化；不能称三架构均有身份特异性复制。 |
| 可行动评分 | **不主张成功。** 原 guard 的 AP 同时区间跨零；MSValid P13–P24 精确上下文留出无影响量增益。 | [严格留出审计](INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md) | 无需真值的逐患者正确性评分、病灶安全性和真实薄层恢复均未验证。 |

与成熟先例的区别需落在**真实观测切片身份、冻结估计器、同目标成对比较、acquired-only 响应归档与失败边界**的组合；不能把共同误差、基本能量恒等式、MRI 不确定性图、有限扰动或互补采集各自称为首创。[Hu 2021](literature/2026-09-30_hu_mira_overlap.md)已明确指出预测变动会漏掉系统 MRI 误差，[相关工作核查](../design/paper/FINAL_SCIENTIFIC_STRENGTHENING/NOVELTY_LITERATURE_AUDIT.md)及[2026 近邻审计](literature/2026-09-30_mira_uncertainty_neighbours.md)给出更详细边界。建议以机制/审计论文而非性能领先的重建方法定位；具体投稿场合仍需按当期要求和作者数据权利确定。

## 决定下一版摘要的负结果

[已冻结的 P25–P84 方案](MSVALID_INFLUENCE_P25_P84_FROZEN_ANALYSIS_2026-09-30.md)已经在完整性/源影像 SHA-256 全通过后执行。[60 人留出结果](MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md)中，精确上下文基线加入影响量使误差余弦 MAE 由 `0.027280` 升到 `0.027448`，患者等权差 `-0.000168`（探索性区间跨零），目标内排序完全不变。因此**下一版摘要不得暗示影响量跨来源预测或部署有效**；内部响应结果只放在受限机制解释或补充材料。现有事前主 `Delta O` 现象 claim 不依赖这项探索的正值，也不能以该负结果抹去。

投稿前仍要：同步真实主文、表/图/限制与参考文献并重新构建核页；从作者原始材料核实 fastMRI release/图像使用和 NingXia 来源、去标识、伦理与发表许可，或重构不使用未认证材料的稿件；核查实际会议年份与数据政策。缺其中任何一项都不能标记整个投稿任务完成。
