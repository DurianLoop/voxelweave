# 作者代码、ENSURE 长稿和 MSLesSeg：新增证据与创新边界

本阶段取得两份正文（ENSURE 长稿 HTML 和 MSLesSeg JATS），并核一份作者仓库。没有新增 PDF；论文 PDF 数仍为 29。索引搜索返回条目不是全文阅读数量。与[上一轮三篇风险方法核读](2026-10-02_risk_action_fulltext_collision_matrix.md)衔接，不替换旧报告。

| 工作 | 本轮实际读取 | 对本项目的约束 | 可继续的具体问题 |
| --- | --- | --- | --- |
| Aggarwal 等，ENSURE，TMI 正式卷期 2023，DOI 10.1109/TMI.2022.3224359 | arXiv:2010.10631v4 的背景、Lemma 1、风险/散度推导、实现、实验表/图注、讨论和 Appendix。正文段 [000]–[260]；未逐图检查或运行作者实现；原 v1 PDF 请求 406 | 原文已明确忽略误差的 mask 依赖，不能包装成首次揭露。随机算子/逆概率加权/无真值训练已有先例；固定抽层与 magnitude 数据不能直接使用其完整风险保证 | 两固定动作的排序是否受 mask 依赖偏差影响；实际独立评价信息和噪声模型能否满足条件 |
| Küstner 等，Predictive uncertainty … deep ensembles，DOI 10.1002/mrm.30030 | 作者公开 README、train_ensemble.py、三个 dataset 文件、losses.py 和四个模型配置的相关段落；按提交固定。论文正文仍未取得，未运行作者代码 | 同观测的模型 ensemble、异方差 NLL、OOD/病理不确定性已有直接先例。不能把多模型输出分歧、像素误差相关性或病理 UQ 泛称创新 | 固定信息和预算下预测动作的收益差，能否胜过绝对误差头、分歧阈值和常数混合 |
| MSLesSeg，Scientific Data 2025，DOI 10.1038/s41597-025-05250-y | DOI 认证 JATS 的全部 23 段正文/表图文字；官方 README、预处理代码、全部 ZIP 目录/4 CSV、117 个 RAW T2 有界头部尝试 | 处理图是 1 mm MNI 网格；标签在注册 FLAIR 标注，不能作为原生薄层 T2 真值。共享形状偏差的叙述亦已出现 | 可作为以后厚层真实应用域候选；必须核原图标签变换及评价任务。当前不能提供所需薄层 T2 独立确认 |

## ENSURE 长稿核读

[原文 HTML](https://arxiv.org/html/2010.10631v4)，[保存正文](source_cache/author_repo_and_mslesseg_2026-10-02/ensure_long_attempt_01_maintext.txt)，[正式 DOI](https://doi.org/10.1109/TMI.2022.3224359)。会议 ICASSP2021 版本和本长稿是同一方法的发展版本，不按独立新方法重复计数。

- [023]–[024] 假定复数 Gaussian 噪声及协方差 C，采样算子随机，且与噪声独立。magnitude CISS 的抽层模型不能直接替代这些实测前提。
- [060] 写 “ignoring its dependence on … s”；[062] Eq.11b 明用近似号。将依赖同一 mask 的误差移出期望需额外条件。[063] 明确 Q=E[P_s]、W²=Q；[075] 的加权完整风险论证沿用该思路。
- [084]–[097] 从加权投影误差，经 LS 解与散度构成训练损失。Appendix [241]–[260] 核 Gaussian sufficient statistic、integration by parts 及 LS 交叉项。已阅读论证，不等于对奇异算子、复数微分或边界项给出完整形式化证明。
- [116]–[130] 实际用 CG 近似 LS/投影、Monte Carlo 输入扰动近似散度、多个采样矩阵近似 W；brain 实验的 Cartesian Bernoulli 密度中心较高且未完全采集中心。没有复现这些步骤；本轮 toy 不包含噪声散度或 multi-coil。
- [164]–[173] brain 来自九名志愿者的 1 mm 3D T2 CUBE，5/2/2 train/test/validation；knee 子集 100 人，43/2/55。这里的 2D random sampling 指 k-space 设置，不能误说成原生二维临床厚层采集。
- [218]–[219] fastMRI 另有 uniform-density / fully sampled center 与 mask shuffling 试验。不同实验采样策略应分别记录。
- [228] 明确 W 不可逆时无法无偏估完整 MSE；[229] 明确总体采样期望与每图固定 mask 训练之间的近似，并讨论噪声估计/扫描器差异。

因此，本轮[动作排序穷举](../MASK_DEPENDENT_ACTION_RANKING_CPU_RESULT_2026-10-02.md)是对本项目使用条件的审计。它不推翻 ENSURE 的训练实验，不提供现有图像可部署的无真值收益标签，也不构成新定理。

## Küstner 作者代码核查

[公开仓库](https://github.com/midas-tum/recon_uncertainty)；提交 `ce0e6ede3682a6901bfdd6ddc85b44ef28e72f3a`。GitHub API ref 请求 403 rate limit 后未重试该 API；匿名仓库 HTML 中 currentOid 唯一并与逐提交 raw URL 一起归档。README 明确题名、五名作者及 DOI，属于身份已核的作者代码证据。

- train_ensemble.py 636–649 行创建一次 data module，然后遍历 checkpoint，用同一 test loader 推断。679–700 行按 subject/slice 堆叠输出。
- transforms.py 221–243 行在测试时由 filename 中的数字设 mask seed，生成后恢复 RNG state。因此同 filename、shape 与采样配置下成员的评价观测一致。训练时 mask 另行随机，不能把训练随机性和测试信息变化混为一谈。
- train_ensemble.py 718–722 行的原代码为 `mean(y)`、`mean(sigma)`、`mean(y ** 2) - mean(y) ** 2` 及两不确定性的和。复数分支已先转换；这里仅抄录实现，没有将无共轭的表达替作者认证为标准复数方差。
- losses.py 的 `loss_l2_heteroscedastic` 用 `sigma=exp(log_sigma)+1e-5`、平方残差/sigma 和 log_sigma。cnn config 1302–1313、unet config 364–376 启用该 loss 和 parameter_estimation。模型内部输出到保存 sigma 的变换尚未全核，不能直接断言保存数组的物理尺度。
- README 的摘要明确研究 undersampling pattern、contrast、orientation、anatomy 和 pathology shifts。该公开摘要已足以否定“首次将 ensemble UQ 用于 MRI 病理/域偏移”的宽泛说法。

尚未取得全文或检查全部评价脚本/模型定义，不能由已读文件没有出现某动作选择逻辑，推断整篇论文/整个仓库不存在它。

## MSLesSeg 核读与来源资格

[论文 DOI](https://doi.org/10.1038/s41597-025-05250-y)，[官方 Figshare v1](https://doi.org/10.6084/m9.figshare.27919209.v1)，[保存正文](source_cache/author_repo_and_mslesseg_2026-10-02/mslesseg_attempt_01_maintext.txt)。官方 CC BY 4.0；本轮目录和 metadata/header 读取未解压像素。

正文 [007] 写 53 train/22 test、总 75 人/115 扫描；[019]/[021] 的 technical-validation 却写 54–77 /24 test。官方 ZIP 实际是 P1–P53 的 93 个 train 时点，P54–P75 的 22 个 test，合计 115；保留正文矛盾，不自行补出 P76/P77 或用平均层厚替逐扫描资格。

[009]/[018] 明确各模态配准至 1 mm MNI152、182×218×182 LAS；[010]–[013] 标签在注册 FLAIR，由 junior rater 标注、两位 senior 审查，T1/T2 辅助。[016]–[017] 的 STAPLE 参考纳入被评价算法及 GT，属于自包含共识；原文已经讨论多个算法相似轮廓偏差。这不支持我们提出首次共同偏差的新意。

官方 RAW/处理包有文件/时点差异，header 部分读取成功、TLS 和 Schannel 失败以及原图逆映射门槛见[独立来源审计结果](../MSLESSEG_SCAN_METADATA_AND_HEADER_RESULT_2026-10-02.md)。
