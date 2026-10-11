# 覆盖×增强实验期间的两篇原始正文阅读

本阶段累计实际阅读两篇原始 JATS 正文，共 205 个提取文字块：brain_weighting 0–97，lesion_augmentation 0–106。交接前已读 103 块，本次接续读完剩余 102 块，并重取被输出截断的图注。文字块包含标题、公式、表格和图注，存在嵌套段落重复，不能称为 205 个独立实验或段落。没有审阅图像像素、独立复现作者实验或阅读单独补充材料。获取记录中的 actual_reading_completed=false 是获取时的历史状态；完成状态另存 reading_provenance.json，不覆盖来源记录。

## 1. Loss Weightings for Improving Imbalanced Brain Structure Segmentation Using Fully Convolutional Networks

2021，Healthcare，DOI [10.3390/healthcare9080938](https://doi.org/10.3390/healthcare9080938)，[PMC 原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC8393549/)。原始 XML、全部正文及哈希见 [获取记录](source_cache/coverage_augmentation_fulltexts_2026-10-03/attempt_01.json)。

数据是 84 位未破裂脑动脉瘤患者的 MRC 与 TOF-MRA，60/4/20 训练/验证/测试；图像 512×512、144–190 层，0.47×0.47×1.00 mm。MRC 分脑实质，MRA 分血管，多类任务使用多模态输入。前景频率 0.096/0.012/0.003/0.001，并非本项目的单序列稀疏层病灶重建。作者选择 2D U-Net 以减少 3D patch 尺寸等额外因素，也指出缩小图像可能损失小结构信息（块 7–9、37–42、93–94）。

比较 CE 与 Dice，各配无加权、inverse frequency、median frequency、focal、distance transform、distance penalty，共 12 个配方。类频率、预测置信度和到标签边界的距离已是明确先例；本文的 focal weighting Dice 不是上一轮的 asymmetric Unified Focal。训练从头 Adam、batch 5、30 epochs；测试模型从三种学习率×10/20/30 epochs 的九种组合中选择（块 16–34、44）。正文这一段没有清楚交代每次最优组合判据，不能替作者断言发生 test leakage，也不能把它当作本项目固定预算/最后 checkpoint 的复现。

关键发现是损失与权重的交互。二分类血管：无权 CE Dice 0.785，inverse CE 0.642，median CE 0.647；无权 Dice 0.704，inverse Dice 0.786，focal Dice 0.785。即使更强调稀有结构，CE 下也可能过提取背景、增加 FP。多类 inverse Dice 对某些稀有血管有利，却能完全漏掉大脑实质（五类表中 cerebrum Dice 0）。边界与整体重叠指标不一定一起改善；focal 或距离权重也不保证在每个目标最好（块 64–79、95–97）。

作者用 DSC、surface DSC、ASD、95HD 和显著性计数排名。排名中的 Wilcoxon p<.05 未作多重校正（块 55–60、88、90、95–97），因此不将排名解释为跨任务普遍最优的统计证明。论文主要限定于 MRC/MRA、2D 模型和默认权重参数，作者明确建议进一步检验别的任务/3D 网络（块 81–84）。

对应本项目：上一轮 Unified 提高 recall 却增加 FP/体积误差有先例，不能把这种取舍本身写成创新。本轮先保持 BCE+Dice、预算和阈值不变，检验采样/增强，避免用后见效果同时改 loss。后续评价必须保留 FP、FN、precision/recall、signed/absolute RVE 与物理边界；仅体积接近或召回提高不足以证明任务能力。

## 2. New lesion segmentation for multiple sclerosis brain images with imaging and lesion-aware augmentation

2022，Frontiers in Neuroscience，DOI [10.3389/fnins.2022.1007453](https://doi.org/10.3389/fnins.2022.1007453)，[PMC 原文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9633994/)。

任务是双时点 FLAIR 的新 MS 病灶分割：MSSEG-2 的 100 位患者、15 台扫描仪、200 图像；40 训练、60 测试。作者主训练排除 11 位没有新病灶的患者，用 29 位训练；测试保留 32 新病灶和 28 无新病灶患者。只标新病灶，没有完整既存/生长病灶监督，不能移植为本项目单时点肿瘤恢复的效果证据（块 42–45、81–84）。

输入为基线与随访两通道，经过脑提取、N4、仿射/非刚性配准并重采样。nnU-Net 3D fullres，128×112×160 patch，67% 随机采样、33% 确保含病灶；CE+Dice、SGD Nesterov、batch 2、1000 epochs、五 fold 各选最高 Dice checkpoint，五模型集成，无后处理（块 20–30）。本项目为一个 2.5D global/local 模型、固定4000更新和最后权重，数据/选择/集成预算不同；这些分数不作直接排行榜比较。

除 nnU-Net 标准几何/强度增强外，作者已有两类任务增强：沿轴向 [1,1,n]、n=2/3/4 的 median filter 模拟模糊，以及用标签距离变换随机阈值产生 ROI 的 CarveMix 跨患者病灶混合。所谓 axial subsampling 的具体操作是中值滤波；它不同于我们的隔4层保留、PCHIP 恢复，不能把两者当作相同采集模型（块 32–39）。但“模拟层分辨率变化增强”或“病灶感知增强”这些宽概念已有直接先例。

消融是 pre-processing、registration、Aug+ 的组合：基础 DSC 0.476/F1 0.533，pre+reg 0.490/0.548，再加 Aug+ 0.510/0.552。Aug+ 同时加入轴向滤波与 CarveMix，不能从表3断言哪一个单独贡献了 +0.020 DSC（块 75–79）。新病灶召回/分割改善伴随无新病灶 FP 小幅增加。无新病灶总体误报只集中在一位患者的14体素，且两位专家也标该区域，而 consensus 未标（块 86–91）；标签分歧不能由论文阅读证明算法发现了真实新病灶。

官方默认评价忽略小于3 mm³ 的病灶；因此其 lesion-level 结果不证明任意微小病灶保护。nnU-Net baseline 的无新病灶 VFP 0.138，proposed 0.192，不能说所有指标均改善（块 45、69）。作者强调 nTP/nFP/nFN 要合并分析，单一指标排名会误导（块 94）。

对应本项目：关闭增强后的训练内 fit 成功不能推导关闭增强提高多患者泛化；这篇论文反而展示任务相关增强可以在另一任务有用。当前因子中的增强是 flip/rot90/scale/shift 的整体 bundle，不能归因到某个单操作。后续可预写“仅强度”“仅几何”“原生方向/物理分辨率随机化”作为能力或直接任务强对照，但不称宽泛首创，也不因本轮结果修改正在执行的四臂。

## 这两篇对创新路线的实际限制

| 想法 | 近邻限制 | 本项目仍须完成的检验 |
|---|---|---|
| 用稀有结构 loss/前景采样改善 recall | 类频率、focal、距离加权及前景 patch 已有 | 保持统计/预算一致，完整 FOV、FP/FN/边界并列；目前只是评价器能力开发 |
| 用轴向分辨率变化增强、病灶混合增强 | 原论文已有 median filter 与 CarveMix | 若采用，应成为强直接任务基线；区别真实采集/隔层抽取/模糊，不能将组合直接命名创新 |
| 从 observed 数据识别重建的缺层病灶误差并做选择性修正 | 这两篇没有检验这个精确合同；此前相关论文仍须一并比较 | 先充分适配任务网络，再与 native、raw PCHIP、输入处理 PCHIP、直接分割/分辨率随机化公平比较；冻结后八患者确认 |

第三项是尚待验证的研究问题，不是已经证实的新颖性或可发表 claim。阅读与当前实验不使用 GPU，不打开确认患者效果，不更改用户终端训练。

记录：[逐块阅读 provenance](source_cache/coverage_augmentation_fulltexts_2026-10-03/reading_provenance.json)、[固定因子协议](../MC_RC_COVERAGE_AUGMENTATION_FACTORIAL_CPU_PROTOCOL_2026-10-03.md)。
