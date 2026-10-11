# 先验调整与类别平衡：原文核读及对 MRI 定位的约束

新增实际核读两篇原始论文：Menon et al., *Long-Tail Learning via Logit Adjustment*，ICLR 2021 对应作者 arXiv:2007.07314v2（2021-07-09、正文封面日期 2021-07-13）；Cui et al., *Class-Balanced Loss Based on Effective Number of Samples*，CVPR 2019，pp.9268–9277，正式 CVF PDF。

取得共 37 个物理页。实际文字核读：Logit 页 1–11 正文及 17–18 附录 A/B.1；CB 页 1–8 正文，共 **21 页**。Logit 页 12–16 参考文献、19–27 其余附录、CB 页 9–10 参考文献未逐页读；无作者训练复现。实际渲染并视觉核看 **4 页**：Logit5/7、CB4/6。不称读完全部附录。

OpenReview PDF GET 返回 HTTP403（获取工具 e4b57d，实际 exit1；同次 CB 获取成功）。改用作者公开 arXiv PDF，新 attempt02，工具 dfb178 实际 exit0；403 保留，不绕过认证或推断 OpenReview 文件相同。封面明确 v2，引用结论来自该版本。已取得不是已读，获取 JSON 保持 new_primary_papers_read=0，实际阅读另有 provenance。

| 直接证据 | 原文位置 | 项目应如何处理 |
|---|---|---|
| balanced error 的最优决策是 argmax P(x\|y)，与原始 posterior 决策不同 | Logit PDF2 Eq2，5 Eq7–9 | QDA 仅移除类先验是已知决策调整；不能把调整后的分数称部署病灶概率 |
| 后处理减 tau*log prior，训练损失加 tau*log prior，方向不同 | PDF5–7 Eq9/10 | 不能混用符号；QDA 相同类条件只改先验是部署阈值/代价诊断，没有新表征 |
| Fisher consistency 是预期风险最优解性质 | PDF7 Theorem1，17证明、18 B.1 | 不等于有限样本 QDA/forest 的校准、99% coverage 证书、患者级 Dice 或成本保证 |
| 已平衡训练的 logits 再做相同后处理会扭曲目标 | PDF7 Section5.3 | forest 使用平衡 sample_weight，不再盲目移除真实先验；未来神经模型也必须声明 sampling/loss 的有效分布 |
| 有效数量 En=(1-beta^n)/(1-beta)，beta=0 不加权，beta→1 逆频率 | CB PDF3–4 Eq1–6 | class balancing 是已知控制；beta 需开发内选择，本轮不新增调参 |
| 作者明确 effective number 不等于统计 ESS | CB PDF2 Related Work | 不把相邻 MRI 像素数当独立患者数量，不能从 En 获得研究样本量或风险证书 |
| 更强平衡不是普遍更优，超参/训练费用变化须报告 | CB PDF6 Table2/Section5.2，7 Figure5 | 不由 inverse prior 推导 MRI 最佳方法；额外搜索、不同 LR/epochs/模型要进入强对照和预算 |

Logit 页5–6 的 τ=1 对理想 posterior 移除先验；作者强调实际网络常未校准，并允许通过 held-out calibration/tuning 选 τ。本轮 QDA 阈值是冻结的0，不是验证校准值；有两个不同队列的旧/new QDA，也不能把 19 队列与旧16模型直接当纯先验消融。只有当前 19 队列内 empirical/balanced 两臂共享类条件，才隔离先验影响。

页7训练损失+log prior与测试 argmax raw f 对应 balanced target；后处理−log prior适用于原 posterior scorer。正文 Theorem1 的 δ 是任意正向量、α_y=δ_y/π_y、Δ_yy'=log(δ_y'/δ_y)。它在 unrestricted expected loss 层面保证 balanced classification consistency；当前空间相关像素、整患者外推、模型误设和 Dice/99%-boundary 都未由该定理覆盖。附录18作者 σ(z) 定义为 `(1+exp(z))^-1`，若复用 Lemma2 须保留其符号约定，不能换为常用 increasing sigmoid而不改符号。

实验也不是方法处处领先：Logit 页9 Table3，τ*=best possible tuning value，不能误当独立固定校准成功；页11讨论 iNaturalist/ResNet50，DRW32.0% error 优于 vanilla logit33.6%。页10–11更深模型和200epoch改善结果，不能把训练容量/时长差异忽略。正文研究分类 balanced error，不提供 MRI segmentation/SR、cache latency 或患者级确认。

CB 页3的覆盖模型假定新样本完全落入旧区域或完全在外，忽略部分重叠；页4实际令所有类别共享 N/beta。它是一种建模/权重定义，不是在我们 observed MRI 特征空间测得真实独立原型。页6 Table2 的 class-balanced 行按 cross-validation选 best loss/beta/gamma，并不是每格同一固定超参。页7 Figure5，CIFAR100 上较大 beta 可劣化，而 CIFAR10 近 inverse-frequency 更好。页6实现 sigmoid/focal bias 初始化与 loss-specific LR（ImageNet focal2倍、iNat4倍）也变化，需作为充分适配强对照背景。

对当前诊断的直接解释：只改 QDA prior 可以大幅提高 coverage，但此举不获得精确病灶分割；覆盖扩张必须同原ROI/window/cold-start费用一起报告。若已平衡 forest 仍漏某些患者，不由论文推断缺失MRI信息是唯一原因，也不纯归因为非线性容量，因为 forest同时抽样/权重/容量都与QDA不同。

保留的创新候选：充分适配的 dense/direct/SR 基线下，以合法观测预测具体修正的完整任务净收益，用真实窗口 union、冷启动及候选探索费用约束选择；与相同信息/容量/总成本的 risk、固定动作、random、greedy、defer等控制比较，冻结后才8确认。先验调整、loss balancing、森林与缓存分别作为既有方法和执行控制，不申报首次。

- [作者 arXiv 来源](https://arxiv.org/abs/2007.07314)，[本地 Logit PDF](source_cache/prior_balance_primary_attempt02_2026-10-07/logit.pdf)。
- [CVF 正式来源](https://openaccess.thecvf.com/content_CVPR_2019/html/Cui_Class-Balanced_Loss_Based_on_Effective_Number_of_Samples_CVPR_2019_paper.html)，[本地 CB PDF](source_cache/prior_balance_primary_2026-10-07/classbalance.pdf)。
- [首轮获取及403记录](source_cache/prior_balance_primary_2026-10-07/acquisition_attempt01.json)、[arXiv attempt02](source_cache/prior_balance_primary_attempt02_2026-10-07/acquisition_attempt01.json)、[4页渲染记录](source_cache/prior_balance_visual_2026-10-07/render_attempt01.json)。
