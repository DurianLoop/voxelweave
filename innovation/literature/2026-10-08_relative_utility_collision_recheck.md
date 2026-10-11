# 本阶段对相对收益先例的有限复核

新增论文获取／全文计数0；复读已有两份method页和一份SafeRestore已提取原文范围。不重计旧learning-to-defer32页或SafeRestore全文。新文字／视觉范围之外的内容仍以旧读记为历史证据。

- Madras等 *Predict Responsibly* arXiv1711.06664v3，**physical3**全文字实际复读：Eq(3)用(1−s)模型loss+s外部决策器loss优化整个系统；原文明确gate“rather than just an expression of uncertainty”，预测两者谁在给定样本loss更低。没有新视觉检查。
- Mozannar／Sontag *Consistent Estimators for Learning to Defer to an Expert*，PMLR119，**physical2**全文字实际复读：Eq(1)一般classifier与expert成本；区分constant-cost reject和依赖x、y、m的defer。当前没有重新复读第3页的一致性proposition；其此前核读记录仍保留，不称新证明。
- SafeRestore arXiv2609.03475v1，已有[TXT](extracted/SafeRestore_2026.txt) **1-based347–401及1265–1277行**完整字面复读：六候选固定、同detectorcheckpoint、六deployment可见特征、两action-specific class-balanced logistic ranking；其candidate生成和所有detector输出先发生，明确不假设efficiency、后文明确不作latency／energy claim。其回投影MSE、entropy、raw/action差异与本轮heldout误差功能相近，需要实质匹配强对照，不以影像模态不同躲开。

两旧method页保存为[bounded复读准备](source_cache/downstream_feature_cost_primary_2026-10-08/old_deferral_method_reread_attempt01.json)，准备时text_actually_reread=false保持；88e05b实际输出完整两页后已核读，provenance另记。90d225实际输出上述SafeRestore范围；4862a1的合并SafeRestore／MoEDiff摘录和f08ac7的搜索输出截断，仅用定位，不声称这些截断原文已读完。MoEDiff本阶段不新计全文或图页。

实质决定：对于合法observed O生成的固定有限动作f_a(O)，训练成本C_a(O,Y)，G_a=C_0−C_a，则argmax_a E[G_a|O]=argmin_a E[C_a|O]是已有相对cost选择。仅换成完整体积Dice、MRI缺层、收益头或条件阈值不构成算法首创；局部联合动作需按实际当前state测，但non-additivity本身亦不是贡献证明。

后续两路径条件cost头、cost-sensitive/defer与SafeRestore六特征双风险排序加入同信息／总head容量／监督／实测预算矩阵。固定评估器与联合适配分开；head-only LOPO不能把task网训练见过的患者说成整个pipeline患者外。方法目标如为期望ΔQ，不用gain>0分类胜负悄悄换目标。候选现在是待验证的MRI机制／应用研究：强适配后同观测及总预算是否仍有可重复净病灶改善；无稳定余量则保留负结果。
