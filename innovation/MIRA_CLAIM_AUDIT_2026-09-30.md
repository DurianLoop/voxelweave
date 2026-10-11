# MIRA 候选论文 claim 与外部确认边界

本文先对**现有** CVPR [主稿](../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex)和[连续影响扩展](../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/FINAL_REPORT_ZH.md)作研究审计，再记录本轮新增的单配对外部确认；不取代原作者的投稿决策。它与本轮[修正动作诊断](experiments/LOCAL_ACTION_STUDY_2026-09-30.md)是不同研究线。当前尚未证明“可发表的正向新重建方法”；最接近的是下述有边界的机制/审计 claim。

## 可守住的候选主张

> 在已测试的冻结 MRI 重建器及稀疏采样合同下，两个预测共用相同真实锚点时，模型间分歧可只显示成对重建误差的一小部分；保持缺失目标和参考预测不变、改用不相交真实锚点后，局部误差可观测比例系统上升。局部响应影响量在数值稳定的实现中，提供超出共享锚点数量的误差对齐关联。该框架用于审计分歧失明，不提供单个重建的校准正确性分数。

新意应落在**同目标物理测量身份干预、响应空间影响与分离报告卡**，而非误差代数恒等式或“共同错误存在”本身。[Hu 等 MICCAI 2021](https://miccai2021.org/openaccess/paperlinks/2021/09/01/280-Paper1009.html)已讨论 MRI 的随机/系统误差；标准协方差传播也不是新定理。若稿件只称“预测一致性会失效”，会与已有工作直接相撞。

| 要素 | 现有证据 | 可写边界 |
|---|---|---|
| 同目标物理共享控制 | 两个脑队列、五种冻结实现的全部 20 个有序跨架构配对，分离锚点后局部可观测比例增益的队列内同时区间均高于零；fastMRI 为 6.2–16.0、IXI 为 13.1–28.5 个百分点。见[当前主稿](../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex) §5。 | 参考 A 固定，但伴随 B 的完整上下文、相位和可能的归一化变化；不能称纯粹随机化锚点身份。 |
| 信息访问敏感性 | [补充中的支撑检查](../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/submission_sensitivity.tex)显示 target-derived 1% mask、acquired-only anchor-union mask、全有限图像三种支撑下，两个队列各 20 对效果及同时区间均保持正；此为事后敏感性。 | 不等于真实部署评分无目标依赖；`O` 本身在回顾性评价中仍需要目标误差。 |
| 连续影响 | [扩展大表](../design/paper/CONTINUOUS_INFLUENCE_EXPANSION/CONTINUOUS_INFLUENCE_BIG_TABLE.md)实测 8 个实现、16 个模型/队列单元，其中 14 个同时通过预定数值门槛和 beyond-count 同时区间；另有数值失败、fixed-count 负/空结果。 | 8 个实现含 Linear 控制，不是 8 个独立神经架构的因果复制；相关优势不能升级为单样本错误预测能力。 |
| 可行动评分 | [Plan17 证据矩阵](../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/claim_evidence_matrix.md)的唯一 acquired-only guard：fastMRI 内评没有阳性，IXI 两配对各仅 2 个阳性，全部 12 个与基线的同时 AP 对照跨零。 | 不可主张可靠筛查、校准不确定性、临床安全保证或新风险证书。 |
| 研究独立性 | [来源审计](../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_audit.md)指出队列反复用于分析、部分早期掩膜含目标、主要端点层级曾事后变化；后续统计纠正没有重置历史。 | 现有 bootstrap 是病例/患者重复测量推断，不消除整个研究过程的选择偏倚。 |
| 外部单配对确认 | [MSValid 预定试验](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)在 84 名新来源 RRMS T2 患者、479 个目标上，冻结 HAT→SwinIR 的 `ΔO` 为 +19.76 个百分点，患者 95% CI +19.33 至 +20.16，84/84 患者正；不相交伙伴总体 MAE 未更差。 | 只确认这个模型配对和原生 3–6 mm 域的机制现象，不复制全部 20 配对或连续影响分析；相位、完整上下文与归一化仍共变。 |

## 当前判定

这是一个**可以围绕现有数据写成有边界机制论文的候选 claim**，且主文和补充材料已构建；其发表性并未由本轮核验保证。原有两脑队列/20 对架构的局部结果与 acquired-only 支撑敏感性，现在得到一个先冻结规则、后打开目标的新来源 MSValid 患者队列上的单配对确认。最强拒稿风险仍是已有共同误差先例、身份与完整上下文未完全解耦、旧队列反复使用，以及新确认只覆盖一个配对和一种疾病/厚层域。把失败 guard 隐藏或改称方法成功会削弱而非增强稿件。

新确认使用公开 MSValid 而非现有 `dataset/` 内的 fastMRI、IXI、NingXia 等家族；它来自不同医院，但匿名 ID 不提供跨库同人排除证明。[结果后反向/线性控制](MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md)和[共同 min/max 控制](MSVALID_COMMON_NORM_RESULT_2026-09-30.md)均保持正效应，说明独立缩放差异不是唯一解释；但相位几何、邻层图像内容与锚点身份仍共变。[近邻文献全文核读](literature/2026-09-30_mira_uncertainty_neighbours.md)进一步排除宽泛的误差图、校准不确定性和内在歧义首创措辞。既有 IXI wavelet full 训练及其锁定测试未被用于 MIRA 新分析。

## 原执行前草案与已执行协议

1. 选一个此前未进入模型训练、checkpoint 选择、MIRA 探索或结果查看的患者独立、致密 3D 脑 T2 队列。逐例核 patient ID、原生层间距、体积深度、许可及可发布结果范围；用训练侧旧数据做样本量规划，在新队列任何目标结果打开前固定纳入数与排除条件。若只能取得 T1，需明确这是更强分布转移试验，不能与 T2 同合同合并。
2. 固定 fastMRI HAT checkpoint `842c1b7415cfa5a2a3c7b50ecf5ded6a0003872ae8ae2d2362220b9f58c6c094` 和 SwinIR checkpoint `a7f8883a4f19d695bd9f0cb0c2c082a44e0060ddbe8ab5d8575e7d4ce702efa5`；原路径和哈希见[Plan17 台账](../design/paper/PLAN17_MEASUREMENT_INFLUENCE_FRAMEWORK/research_ledger.json)。冻结模型代码、归一化、×4 两个真实采样相位、同一目标选择、acquired-only anchor-union 支撑和失败处理；不可用新队列挑权重或 mask。
3. 预定单一主要对照为固定 HAT phase-0 参考与 SwinIR phase-0 共享、SwinIR phase-2 不相交伙伴。两个条件保持目标及 HAT 输出相同，目标限两相位都缺失且满足真实四锚点支持的 residue 1/3；病例内两 residue 先等权，再以患者为独立单位比较 `O=||h||²/T` 的不相交减共享变化。注意这仍改变 SwinIR 完整上下文，不能宣传纯身份因果效应。
4. 用同一患者的配对 bootstrap 和预先固定随机种子检验平均 `ΔO>0`，报告点估计、95% CI、阳/阴患者数、两条件的成对误差与各自误差。成功标准为主端点 CI 下界大于零且数据/模型/几何审计通过；否则保留负结果。其余模型配对、连续影响与 guard 只能作为预标记次要端点，不用其阳性代替主端点。

以上四点保留为执行前的决策脉络；实际数据源、模型、目标和检验规则在打开 MSValid 像素前写入[正式本地协议](MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md)，完整结果见[外部确认报告](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)。这不是第三方注册。当前 CVPR 主文 SHA-256 为 `396c7f3dfeac1329444e0770fd8129f7e74a29dffc155b171395c8b904b7d03a`；MIRA 参考 API SHA-256 为 `7852b196aa7c5ee7c0b8ca02542ce50ee998f065d2dfa1a6905c0d2d88961fc1`，只作之前审计的快照；新结果的权重、协议和实际代码哈希登记在主结果 JSON 中。
