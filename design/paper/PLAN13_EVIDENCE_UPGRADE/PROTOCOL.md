# Plan 13 补充分析协议

2026-09-08。已阅读 Plan 9–12 既有结果后制定，全部为探索性再分析，不能称为预注册、独立新队列或重新训练结果。新输出不得覆盖既有实验。

## E01：架构效应稳健性

纳入 Plan 9 fastMRI 与 Plan 11 IXI 全部正式五架构、所有病例和冻结平面；排除带 smoke/debug/failure_probe 的技术试运行。原始口径不改，额外在每个队列统一计算病例内均值/中位数、病例间均值/中位数四种口径。两队列分别报告，禁止合并精度。逐病例删除分析和所有五模型共同病例重采样；随机种子 20260908，10,000 次 bootstrap。对五模型 observable gain、ranking gain 分别给出同时区间（bootstrap 最大绝对标准化偏差），不把五模型当五个独立队列。排名另以固定 phase-0 error（若有）或两条件误差平均值为共同端点作敏感性检查；后者仍为探索性、并非纯 phase-0 端点。

## E02：同模型受益的数学耦合与患者影响

纳入 Plan 11 正式 598 行、全部 13 个模型，两队列和三个冻结分数。复核 benefit = MAE_x4 - MAE_x2、支持集、病例簇、有限值和结构性 bank 缺失。计算原始 Spearman、在 MAE_x4 的秩上残差化后的 partial Spearman；控制当前误差使用真实目标，仅用于回顾性混杂诊断，不能变成部署分数。10,000 次 examination/patient cluster bootstrap；NingXia 完整保留患者下所有序列，另给八次 leave-one-patient-out 结果。不得根据相关正负删除 Res-SRDiff 或改分母。补充患者等权聚合（患者内取序列中位数）作为不同 estimand 的敏感性结果。

## E03：源代码与信息可用性审计

逐项区分输入值、归一化、掩膜、错误端点、模型选择可用的信息。GT 生成的输出掩膜必须披露。归一化 disagreement 与 shared fraction 的代数耦合必须推导，不以关联显著性证明独立机制。检查现有 IXI 同模型 x2 数据资格，若缺少完整同支持输出则保留缺口，禁止用跨模型结果替代。

## 构建与保全

修改前逐文件 SHA-256 快照；当前论文仍在原候选目录修订，原始内容可从本阶段 snapshot 恢复。新图表来自机器可读输出，完整置信区间和负结果留在表中。CVPR 保持技术正文不超过 8 页；TMI 目标为含参考文献不超过 10 页，不以缩小正文或把删下的文本冒充期刊补充材料达到页数。

## E04 增补：恢复 IXI I3Net 同架构 x2/x4 共同支持（结果计算前）

文件资格检查发现 `full_test115_x2_fast` 和 `full_test115_stable` 各有 115 个 I3Net 输出。只纳入这两个预先存在且完整的 profile；`full_test115_x2` 无输出，不作候选。x2/x4 是不同的因子专用 checkpoint，因此只能称同架构/同模型标签，不能称固定权重或纯采集效果。读取原始 T2、两个预测并验证 affine、in-plane shape、完整 test-list 身份；使用共同深度内所有奇数 z（两倍率都未采集），相同目标 1% mask，病例等权的逐平面 masked MAE 均值。禁止直接减去不同生成平面集合上的旧摘要。

分数完全由 x4 已采集锚点构成：Anchor-CV、adjacent-anchor MAE，与 Plan 6 float32/float64 运算一致；同时计算无归一化及仅使用 acquired-anchor robust range 的归一化分数。10,000 次 examination bootstrap，报告原始及控制 x4 当前误差后的相关、10/20/30/50% 预算下相对随机收益；不据结果挑病例。Linear 作为同支持解析参照；不将这一单架构补充填入原 13 模型矩阵或旧基准表。保存 checkpoint/输入文件 SHA-256、每病例每平面指标、几何检查和失败清单。明确标记 exploratory recovered-output experiment。
