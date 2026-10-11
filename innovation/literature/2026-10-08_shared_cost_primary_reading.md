# 共享提取成本与条件路由：两篇原文及 MRI 创新边界

本轮补读两篇关于测试成本的原文，共取得 17 个物理 PDF 页，实际文字阅读 16 页、视觉核看 4 页。取得、文字阅读、渲染、看图分别记录；取得时的 `new_paper_read=false` 和渲染时的 `visually_reviewed=false` 不覆盖，阅读完成的范围另见 [reading provenance](shared_cost_reading_provenance_2026-10-08.json)。不声称作者训练复现、MRI 实验复现或未读补充材料。

## The Greedy Miser: Learning under Test-time Budgets

Xu、Weinberger、Chapelle，ICML 2012。本轮使用作者 [arXiv 1206.6451](https://arxiv.org/abs/1206.6451) 的 [PDF 缓存](source_cache/shared_cost_primary_2026-10-08/greedy.pdf)，实际文字阅读物理页 1–8，视觉核看页 3、7。

| 原文位置（物理 PDF 页） | 读到的具体内容 | 对当前 MRI 项目的含义 |
|---|---|---|
| 2，式 3 | 成本包含弱学习器求值与所用特征首次提取；同一输入后续复用该特征免费或仅付很小的常数成本 | 首次支付、缓存共享及集合成本已有明确先例 |
| 3，算法 1、式 5 | 特征一旦使用，其后续成本标记置零；普通 L1 会对已共享的特征重复罚费 | 窗口费用应该按实际需要重算的集合计，但集合计费本身不足以创新 |
| 4，式 7–9 | capped L1 与树/特征预算分解；推导依赖各树坐标只增加一次等条件，采用局部/近似优化 | 不可移植成 MRI 每患者硬预算保证或全局最优声明 |
| 5–6，Yahoo 实验 | 特征费用为相对近似单位；irrelevant 样本复制 10 次，验证集选择最佳迭代 | 该曲线不是 MRI 同实测延迟对照，不同采样不能与下一篇混比 |
| 7，Scene15 | descriptor、kernel、SVM 费用在 CPU 上测量；15 个 one-vs-all 分类器共享 descriptor，首用之后主要再付 SVM 求值 | 共享计算和实际提取费用都已有实验先例，不能只靠 cache 申报贡献 |
| 7–8，实验与结论 | 多随机划分和验证选迭代；任务为分类/排序 | 不能将其准确率或预算曲线当成 MRI 缺层修复的净任务收益 |

本项目可借用“首次支付后复用”的严谨计费习惯；还需实测初始化、定位、动作生成、候选探索、传输、推理和后处理。静态特征共享不能证明连续 MRI 编辑下缓存输出等价，更不能证明具体修正会改善分割端点。

## Cost-Sensitive Tree of Classifiers

Xu、Kusner、Weinberger、Chen，ICML 2013。取得 [PMLR 官方页面](https://proceedings.mlr.press/v28/xu13.html) 及 [PDF 缓存](source_cache/shared_cost_primary_2026-10-08/cstc.pdf)。实际文字阅读物理页 1–8，页 9 参考文献未逐页阅读；视觉核看页 4、5。

| 原文位置（物理 PDF 页） | 读到的具体内容 | 对当前 MRI 项目的含义 |
|---|---|---|
| 3，式 2 | 弱学习器和特征提取首次计费，缓存后可复用 | 条件成本与共享费用是已有设计 |
| 4–5，路径费用和训练目标 | 每条路径的特征 union 只计一次；用软路径概率加权 expected cost，mixed norm 作松弛 | 期望成本不等同每患者硬成本，也不等同最终硬路径安全证书 |
| 5，优化与剪枝 | 非凸初始化、验证集 pruning | 需要报告选择过程，不能拿被调过的验证集称独立确认 |
| 6，fine tuning | 固定所选特征支持后调整分类器 | 可借用“先定支持，再调模型”的分离思路，仍须按本项目验证 |
| 7，Yahoo 实验 | 没有 Greedy Miser 的 irrelevant 复制；费用单位为弱学习器求值 | 两文设置不同，不能跨文曲线计算受控改善；训练 3h/fine tuning 10min 不是测试端到端延迟 |
| 8，结果解释 | fine tuning 对 MSE 可有改善，对 NDCG 改善很小；端点响应不同 | MRI 重建误差、病灶 Dice 和边界指标不可互相替代 |

样本相关路由、成本感知模型选择、特征复用都不能单独作为本项目新意。当前要证明的是：在足够强、充分适配的 MRI 基线之后，合法可观测信息能否预测**某个具体修正的整患者任务增益**，并在计入全部成本的同预算强对照中取得可复现优势。

## 与本轮证据的连接

[19 系列匹配 oracle](../MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md) 展示理想定位的几何空间，[两种费用流程](../MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md) 显示初始化如何影响结论。二者都没有证明部署定位、MRI 修复收益或实测加速。ROI、类别平衡、共享 union 成本和 budget routing 已有先例；后续候选与强控制见 [执行准备](../MATCHED_ANCHOR_TO_ACTION_VALUE_PREPARATION_2026-10-08.md)。
