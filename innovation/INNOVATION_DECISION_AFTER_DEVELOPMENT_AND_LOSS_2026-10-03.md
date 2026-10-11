# 本轮创新判断：先把完整任务能力与最小拟合分开

本轮实质进展：19开发完整FOV诊断/57plane复核；Unified Focal作者源码语义与原缩进失败登记、CPU24梯度证明；新两篇原始正文157块+Appendix A；两配方各4000步/4000draw+6plane复核；固定单plane1000步/完整tile覆盖和独立重放。科学确认0，当前没有可发表且独立确认的新claim，goal active。

| 证据 | 本轮实际结果 | 允许的判断 |
|---|---|---|
| 冻结20k模型全部11训练人/19系列 | full Dice .127947、8系列TP=0（仅2空预测）；四验证人此前.127522 | 现有模型不能作重建评价器；训练内亦低，不将验证失败解释为重建损害 |
| 单012同初权重/采样/4000预算loss配方 | BCE+Dice .865312，Unified .823786；后者recall+.038639、FP+31340、absRVE+.200659 | 更重FN在本case提高recall但整体/边界恶化；换loss未解决完整拟合。单case/seed不推广为损失优劣规律 |
| 单012固定z38/全部16tile/无augmentation | Dice .984110、recall .969313、面积误差.030074，预写plane gate通过 | 该实现能拟合这一监督切面；完整病例/多患者仍未过门槛。曝光、覆盖与增强同时改变，不能定位单一因果 |
| 新原始近邻 | 2024已有patch与完整volume偏差/同seedloss；2019已有Tversky、前景patch、样条中心融合和端点取舍 | 换loss、加窗、patch高分/volume低分、召回保护均不作为宽创新 |

最值得保留的研究问题仍是：**在同observed信息、同统计和充分适应的任务网络下，具体稀疏重建是否仍留下可从observed数据识别、且能优于强PCHIP/直接任务修复的缺层病灶残差？** 它可形成明确可否证的实证claim，或在有实际可观测策略增益时形成方法贡献；当前两种都尚无最终证据。

优先推进顺序：先按[覆盖×增强准备](DEVELOPMENT_AND_LOSS_NEXT_FACTORIAL_2026-10-03.md)把训练失败拆开，再证明整个开发/四验证的完整FOV能力；随后native与6×5公平矩阵/直接任务/分辨率随机化，最后冻结具体修正和八未开患者/第二任务网络确认。不把本轮plane成功替代这些门槛。

历史反证继续有效：完整45CISS HAT−pipelinePCHIP平均Dice+.036381704，原平均恶化claim已停止；与rawPCHIP的负差受输入处理和冻结任务响应影响，待公平适配控制。旧残差相加仅2/6过、风险排序/anchor带宽/QDA配置失败。当前拟合诊断不重启这些失败候选，也不把“先例+两种模块组合”改名为创新。

证据：[训练内诊断](MC_RC_FROZEN_GLOBAL_LOCAL_DEVELOPMENT_DIAGNOSIS_CPU_RESULT_2026-10-03.md)、[两配方完整结果](MC_RC_GLOBAL_LOCAL_SINGLE_CASE_LOSS_CPU_RESULT_2026-10-03.md)、[单plane结果](MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_RESULT_2026-10-03.md)、[新论文阅读](literature/2026-10-03_loss_sampling_bias_fulltext_reading.md)、[作者源码审计](literature/2026-10-03_unified_focal_author_code_audit.md)。
