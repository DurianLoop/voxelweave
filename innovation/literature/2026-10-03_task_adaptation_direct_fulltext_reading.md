# 任务适应与病灶任务：三篇新原始研究的定向正文核读

本次新读三篇原始研究。TumorSynth 使用公开 HTML，另两篇使用 PMC JATS body；均已验证题名、DOI 和正文方法/结果。原始文件、分块文本、来源和 SHA256 保存在 [本批正文目录](source_cache/task_adaptation_direct_fulltexts_2026-10-03)。这是定向正文阅读，未查看图片像素、未读独立补充材料，也未复现作者网络。段落锚点见该目录 reading_provenance.json；不把所有提取块算作已读，不把重复 Autoencoder TTA / SynthSeg / FeTA 算新增。

## 1. TumorSynth（2026）

Wu 等，*TumorSynth: Integrated Brain Tumor and Tissue Segmentation on Brain MRI Scans of Any Resolution and Contrast*，DOI [10.1148/rycan.250222](https://doi.org/10.1148/rycan.250222)，[公开正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13036690/)。关键方法锚点 HTML 49–59、63–75；结果 84、88、95、99–119。

方法是级联 nnU-Net 分割，并非 MRI 超分辨率网络。以训练患者标签为模板，空间形变后按类别随机 Gaussian mixture 强度生成图像，加入模糊、轴向/矢状/冠状方向、层厚、层距、bias field、亮度随机化；直接训练任务网络。第一网络找正常组织和肿瘤外边界，第二网络分肿瘤内区；采用 average top-K 损失保护少数类、Dice+CE。单序列可以推断，多模态可按层级权重组合概率图，T2/FLAIR 优先外轮廓、增强 T1 优先内部结构。

作者报告 351 名 BraTS 训练患者、1,620 名评估患者，其中同一患者的完整/缺模态条件重复使用，不能把表中条件人数相加当独立人数。正文表 4：完整模态 WT/TC/ET Dice 为 .90/.90/.81，sparsified-trained 为 .92/.92/.86；ET 明确较差。缺模态时相应为 .91/.89/.80 vs .90/.84/.76。无肿瘤 160 人中 7 个误报，原文约称 4%；这不是零误报。跨模态 ADC/DWI/SWI/FA 报 .88/.85/.80/.79，但该段和图注指脑组织/脑加肿瘤评价，不能改述为各模态小肿瘤缺层检出率。

对本项目最直接的限制：层厚/层距随机化的直接分割、模拟低分辨率训练、少数类损失和级联病灶网络均有先例。文中“missing sequences”是缺模态，不是本项目沿 z 轴固定抽层。本文主正文没有证明在我们的同一稀疏观测、同一 SR 和训练预算合同下重建修正是否仍有增益；也没有证明适用于 CISS/FIESTA 前庭神经鞘瘤。补充材料中的超参数、具体层厚抽样范围和 real/synthetic 混合比例尚未核读。不能借题名宣称已经独立验证任意层距，也不能借其成绩宣布本项目任务模型会合格。

## 2. 多平面子宫肌瘤 FGAS（2026）

*Reconstruction from multi-planar MRI with foundation models for uterine fibroid analysis*，DOI [10.1038/s41746-026-02780-6](https://doi.org/10.1038/s41746-026-02780-6)，[正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13385847/)。重点 JATS 12–28、41–58、61–94。

题名的 reconstruction 主要涉及分割后的 3D 形态呈现，不应直接当像素 SR 同类方法。来源 300 名单平面 T2（270 train/30 source test），临床 620 人、1,853 多平面扫描；文中另外描述 100 人/300 扫描独立评估，fine-tuning 67 人/201 扫描。nnU-Net 生成伪标签，由 nnInteractive 用预测框、连通分量质心及随机正点修正；修正与初始 Dice<.5 时过滤，取最大连通分量。各平面 resample 至 .8 mm 并对齐世界坐标，概率图之间均方差作多视图一致性，另加 TV/compactness 与按前景质心的 Gaussian 权重正则。σ=5 是该文经验值，不能未经物理 spacing 换算抄到本项目。

作者报告 FGAS mDSC 70.6%，IPLC 68.3%、target-only 73.5%；<5 mm 小肌瘤子集从全部肌瘤79.7降到67.8。多视图一致性、基础模型自动修正伪标签、连通性约束、预测框和点提示均是直接先例。多平面真实扫描与同一稀疏体的三个重切视图信息量不同，不能把重切后的 views 当成新增观测。

核读发现应保留的定义疑点：表1部分 mDSC 不能由三视图均值简单重算（PseudoSeg 三列32.3/50.3/34.8的等权均值39.133，表报45.8）；表3部分也存在类似差异，可能涉及不同加权或聚合，但正文不足以确定。消融称30 epochs，方法称20 epochs达到最佳；201训练扫描如何从620人中选取、如何与独立测试隔离仍需精确名单。正文同时描述统一世界坐标与实际扫描运动差异，因此物理配准不是可省略的前提。我们保存原表与计算，不把定义疑点断言为作者错误，也不直接借30.8点提升作本项目预期值。

## 3. 高分辨率/组织学辅助颈动脉斑块分割（2023）

*Carotid atherosclerotic plaque segmentation in multi-weighted MRI using a two-stage neural network: advantages of training with high-resolution imaging and histology*，DOI [10.3389/fcvm.2023.1127653](https://doi.org/10.3389/fcvm.2023.1127653)，[正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC10244753/)。重点 JATS 5–31、32–41、44–73。

9名患者、84组in-vivo/ex-vivo/组织切片，7人70层训练、2人14层测试；翻转/旋转到420层仍只有7个训练患者。in vivo 层厚3mm、ex vivo 1mm，后者与组织学用于改善低分辨率图上的人工标签，并非部署时输入隐藏高分辨率 MR。Stage I 用T1估血管边界，Stage II Bayesian 网络接四通道 TOF/T1/PD/T2 与血管mask分斑块；有CLAHE、BM3D和跨模态配准。外部测试23人445层来自同厂商另一3T系统，单中心限制仍在。

表3三类Dice .78/.62/.74；无高分辨率辅助标签对照 .76/.56/.64。表6外部任务 .70/.60/.73。外部标签为人工MR标注，不是该23人的组织学；模型Dice不能直接代表斑块易损性或患者结局。文中明确局限一像素一类，可扩展部分容积估计，并引用PET/SPECT先例；因此不能把“用高分辨率标签训练低分辨率任务”“级联局部任务保护”或部分容积估计宽首创作为我们的新意。

## 对本项目的决策

| 研究想法 | 本次正文证据 | 处理 |
| --- | --- | --- |
| 训练任务模型适应层厚、对比度 | TumorSynth/SynthSeg 的直接分割与域随机化 | 必要强对照，不能单独报创新 |
| 预测区域引导/基础模型修正/跨视图一致性 | FGAS 已明确实现 | 不以换器官或命名作为方法新意 |
| 高分辨率标签/两阶段病灶训练 | 斑块论文已经做 | 区分训练额外监督和部署额外信息 |
| 任务适应后同观测 SR 是否还有可修正缺层损失 | 三文未在本项目合同下回答 | 保留为窄研究问题，尚未验证、未证明文献空白 |
| 基于真正可观测表征保护局部病灶、其余缺层获益 | 旧8开发人QDA/native/联合线性政策失败；三文不能抹去反例 | 先证明新任务表征能力，才开放修正训练 |

下一轮必须把直接稀疏分割、合成分辨率训练、相同曝光的任务适应以及旧raw PCHIP列入可比较基线。既有6任务模型×5输入矩阵仍需真实split、输入流水线、训练实现和GPU，当前0训练。只有适应后仍存在稳定缺层损失，再寻找具体修正方法；若差距消失，应报告对任务训练分布的依赖，停止“必然病灶恢复”的方法故事。

检索覆盖只有 PMC 四个窄查询，共27题名行含重复；不是穷尽全领域 novelty search。三篇新正文都没有给出本项目的独立科学确认，当前新claim为0。

失败保留：TumorSynth EFetch仅front（出版方不提供XML body）；普通公开HTML下载成功，但bs4未安装导致提取attempt02失败；attempt03用标准库解析同一保存响应成功，0新请求、0安装。未变更项目环境。
