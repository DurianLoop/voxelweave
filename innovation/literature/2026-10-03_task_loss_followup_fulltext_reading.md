# 类别不平衡的原始 loss 先例：任务能力诊断准备

新增原始正文一篇：Unified Focal loss: Generalising Dice and cross entropy-based losses to handle class imbalanced medical image segmentation，2022，DOI [10.1016/j.compmedimag.2021.102026](https://doi.org/10.1016/j.compmedimag.2021.102026)，[PMC8785124](https://pmc.ncbi.nlm.nih.gov/articles/PMC8785124/)。实际读 JATS 正文全部 162 个文字块（含标题、公式、重复表格与图注），不是 162 页或独立实验；未视觉核图、未读单独补充材料、未复现作者训练。[正文](source_cache/task_loss_followup_fulltext_2026-10-03/unified_focal_maintext.txt)与阅读证据保留原文锚点和 SHA。两检索共七条题名、命中 1/17，其他题名只算线索。

正文 24–88 将 CE/focal、Dice/Tversky/focal Tversky 与 compound loss 统一：λ 控两项权重，δ 控类别/错误代价，γ 控 suppress/enhance；asymmetric 版本分别保留前景项、压低易分类背景项、增强稀有类区域项。重点块 48/54/80/86：作者讨论高不平衡下 Dice 梯度不稳定、precision/recall 偏向，以及对所有类别统一 focal 可能同时压低稀有类信号。不能据此判定我们的失败必然由 loss 导致。

作者建议 λ=.5、δ=.6，2D γ 在 .1–.9 搜索，3D 固定 .5；这些是其数据上的启发式，不能直接复制为 MRI 最优参数。提取 Eq.18 的 δ 系数和段 88 的“纠正低 recall”文字需要对照作者实现确认类别顺序及 FP/FN 系数；不能凭扁平化公式把方向默默改掉。Focal Tversky 的 γ 与 1/γ、modified 版本的 γ 与 1−γ 也不能混用。

块 91–114：五数据集，BraTS20 单 T1-CE 的 enhancing tumour 二分类，排除 27 无 enhancing 肿瘤扫描后 342 例；KiTS19 204 例、肿瘤占比约 .2%，均有重采样和随机 patch。2D 数据里 CVC 的 612 帧来自 13 患者的 23 视频，但分配段写随机 dataset 划分，不能推定患者/视频已经隔离。原文“normalised to [0,1] using the z-score”含概念歧义，不能作为准确归一化实现。

作者用 U-Net/3D U-Net、instance norm、softmax、SGD lr .1、batch 2；验证 loss 用于 LR 下降、早停和最终 checkpoint 选择。不同 loss 的早停更新数未证明相同，2D unified 还有多 γ 搜索。因此不能当我们的同初始化、同抽样、同更新预算的损失因果实验已做。

| 原表格端点 | 读到的结果 | 要保留的取舍 |
|---|---|---|
| BraTS20 表 5 | asymmetric Unified Dice .787，CE .716，Dice .620，Combo .686 | precision .795、recall .800；CE precision .826、focal Tversky recall .822，主法并非每个单指标最好 |
| KiTS19 tumour 表 6 | asymmetric Unified Dice .634，CE .336，Dice .536，Combo .554；recall .695 | 增加 recall 与 FP 代价需一起检查；不能迁移为单 T2 VS 预期数值 |
| CVC/DRIVE/BUS 表 2–4 | asymmetric Dice .909/.803/.824，2D 表报搜索后的最好 γ | symmetric/asymmetric 之间无显著差异；普通 focal 在 CVC/BUS 比 CE 更差，不能假定 focal 必然改善 |

块 156/157 的限制：未直接比较 boundary loss，也未证明与 nnU-Net/训练采样方法叠加仍改善。因此“加边界loss”“结合区域与像素loss”“前景优先采样”“降低背景主导”均应作为已有能力基线，不能单独包装创新。

本项目下一项可在 CPU 做的检查是开发标签尺度与冻结采样合同：在没有真实 MRI 像素、没有模型前向的条件下，用真实开发标签和零值 placeholder 图像重放固定数量的采样，测全 FOV 与局部监督 foreground mass、正/负切面比、面积重采样后的目标占比。它只描述这个采样器在既有开发集上的分布，不估计本次训练的真实梯度，也不证明失败原因。若能力失败，先在另写协议下检查同模型单病例可拟合性，再比较同预算 loss/采样；四验证患者始终是验证，八确认患者仍关闭。
