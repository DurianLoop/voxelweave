# MIRA 主稿修订准备（尚未改写投稿稿件）

目标稿：[CVPR 主文](../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex)。当前文件仍为前一证据阶段的版本；本文件是作者审阅的具体修订清单和可复用措辞，不声称稿件已同步。更新稿件前必须核对目标会议年份、正式参考文献、数据/伦理材料及重新编译。

## 必改的事实与位置

1. **Abstract/Results**：加入事前冻结的 MSValid 外部单配对结果，而不把它计入旧 fastMRI/IXI 的 20 对同时区间。84 名 RRMS brain T2 患者、479 层；HAT phase-0 固定，SwinIR phase-0 与 phase-2 对照；患者等权 `O` 从 2.8428% 至 22.5993%，`delta O=+19.7565` 个百分点，患者 bootstrap 95% CI `[19.3276,20.1605]`，84/84 患者为正。写成**单个预设配对**的新来源确认。详细方法和审计见[外部确认](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)。
2. **Experimental Design**：单列 MSValid 数据源 Zenodo 10875606（CC BY 4.0）、首份 T2 选取、原生 z 间距 3–6 mm、x4 再抽样、phase-0 acquired-only mask、residue 1/3 目标及两侧至少两锚点、各相位 observed-only min/max、CPU float32、患者内 residue 等权和患者 bootstrap。不是既有 fastMRI/IXI 方案的无改动重复；不能把该数值并入旧统计 family。
3. **Discussion p. 现有句** `No authenticated untouched cohort was available for the optional final confirmation.` 已过期。应改为：`A separately sourced MSValid RRMS T2 cohort provided one protocol-frozen HAT-to-SwinIR confirmation; it did not independently replicate the full architecture matrix or influence analysis.` 同时保留跨库患者身份无法认证、疾病/厚层转移及第二次未触及复制缺失。
4. **Related Work**：已有 Hu 2021 引文应保留；新增 Giannakopoulos 等的监督分位数+conformal fastMRI 误差区间、Guo 等的线性逆问题 intrinsic ambiguity/propagated uncertainty 分解，以及[Ribas 与 Oliveras Tous 的响应探针/目标失配审计](literature/2026-09-30_tweedie_target_audit.md)。说明 MIRA 的区别是**固定预测器、同目标真实锚点集合干预、成对误差可观测性与物理 ID 响应审计**，不是首个误差图、扰动探针、校准覆盖或歧义分解。前两篇见[逐节核读](literature/2026-09-30_mira_uncertainty_neighbours.md)。
5. **Limitations/表注**：[反向 HAT2 与线性伙伴](MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md)分别为 +19.50/+14.62 个百分点；[共同归一化](MSVALID_COMMON_NORM_RESULT_2026-09-30.md)为 +19.48 个百分点（相对原结果 -0.28 个百分点）。三者都只能以结果后探索出现，不能叠加为新的独立确认，也不能抹掉 signed geometry、邻层图像内容和相位混杂。需要并列展示伙伴 MAE（139.06 vs 141.68 原始强度单位）和历史可操作 guard 的负结果。
   [MSValid 响应阶段 1](MSVALID_INFLUENCE_STAGE1_RESULT_2026-09-30.md)的简化几何关联在精确上下文固定效应后接近零。若引入本实验，必须并列呈现这一负结果；不能在摘要声称连续影响已经外部复制。
   [误差对齐/质量分解](MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-09-30.md)提示外部主 `Delta O` 主要伴随真实误差余弦下降，伙伴 MSE 失衡的代数贡献很小；这是由同一 O/MSE 恒等式得到的结果后描述，不能当独立机制验证。[原稿响应错配负对照](ACQUIRED_RESPONSE_ID_PLACEBO_RESULT_2026-09-30.md)在四个内部层为正，但[外部精确上下文留出](INFLUENCE_EXACT_CONTEXT_AUDIT_2026-09-30.md)无增量；若加进正文或补充材料，必须把二者并列报告并明确同架构与跨架构合同不同。
   [旧队列 HAT→SwinIR 跨架构复核](CROSS_ARCH_ACQUIRED_RESPONSE_RESULT_2026-09-30.md)在 fastMRI/IXI 的真实锚点响应错配对照上仍为正，但 IXI 病例留出预测增量不稳；不能再用“跨架构本身使响应机制消失”解释 MSValid 阶段性负结果。MSValid 与旧队列同时改变来源、相位/上下文和层距，具体原因未分离。
   [MSValid P25–P84 冻结剩余患者结果](MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md)在精确类别几何基线上误差余弦/O 的 MAE 均轻微变差、目标内排序不变；连续影响量不能列作外部预测或选择器贡献。若保留响应材料，必须并列旧队列内部正机制、SAINT 混合错配和新队列严格负结果，正文摘要只聚焦事前外部 `Delta O` 现象。
6. **数据合规/构建**：fastMRI 本地 release/刊图许可，NingXia 来源、伦理与同意资料仍见[已有数据台账](../design/paper/FINAL_SUBMISSION_PREPARATION/DATA_ETHICS_CITATION_AUDIT.md)，不能凭 MSValid 的公开许可代填。增改后须重建 PDF，核表、页数、图版和引用，不能引用本轮旧构建日志作为新版本通过证据。

## 建议的英文 claim 句

`In a protocol-frozen, separately sourced cohort of 84 RRMS brain T2 patients, one prespecified HAT-to-SwinIR comparison reproduced the loss of paired-error observability under shared real slice anchors (patient-weighted disjoint-minus-shared difference: 19.76 percentage points, 95% patient-bootstrap interval 19.33 to 20.16). This corroborates a conditional measurement-dependence audit, not a calibrated per-case error detector or an identity-only causal effect.`

结果后控制另起句：`Exploratory phase reversal, a linear companion, and shared anchor-derived normalization yield disjoint-minus-shared observability differences of 19.50, 14.62, and 19.48 percentage points, respectively; none constitutes a second independent confirmation or isolates anchor identity from the full companion context.`

## 投稿前停止条件

本轮可审稿的最强主张是**有边界的审计机制候选**。共同归一化已通过结果后敏感性检查；外部响应影响、稿件同步、数据/伦理证据和构建核验仍未完成，因此不标记“投稿就绪”。任何会议年份、引用出版状态都按真实投稿时点核定。
