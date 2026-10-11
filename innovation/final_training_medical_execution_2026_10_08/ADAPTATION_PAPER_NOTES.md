# 基础分割能力失败后的论文核读与创新判断

本批四篇不同论文的原文文字已实际核读，阅读范围各不相同，见 READING_PROVENANCE.json。未视觉检查论文图像，未执行作者代码，未下载新预训练权重。BigAug 目前只有身份与他文引用，正文获取 429，不能计入原文已读数量。所有数字是论文自身任务的指标，不能换成当前 CISS/前庭神经鞘瘤实验的预期结果。

| 论文与原始来源 | 实际关键证据 | 对项目的决定 |
| --- | --- | --- |
| [Models Genesis](https://doi.org/10.1016/j.media.2020.101840)，PMC7726094 | 623 个未标注胸部 CT；明确排除测试影像泄漏。目标任务全层适配。BraTS FLAIR 肿瘤任务 Table 3 的 63.00±1.73 → 67.96±1.29 是 IoU。作者承认不同公开模型比较的架构、参数、平台不对称。恢复 MSE 不是表示质量充分证据。 | 自监督恢复、跨模态迁移已有先例，不能作为新意。若后续采用，必须独立核对权重身份、预训练病人重叠与输入合同，设置同架构 scratch 控制，报告预训练和适配费用。不能把 FLAIR 结果外推到 CISS。DOI 身份可信；BioC front 的 year=2022 与索引卷期 2021 冲突保留。 |
| [Head and Neck Tumor Segmentation for MRI-Guided Radiation Therapy Using Pre-trained STU-Net Models](https://doi.org/10.1007/978-3-031-83274-1_4)，PMC11983000 | 120/30 单次训练/内部验证拆分。Table 3 DSCagg-mean：nnU-Net .77、STU-B scratch .81、pretrained B .83；最终 challenge .81。聚合 Dice 与当前患者先均值不同。正文将 .77→.74 称为 improved，与表矛盾。 | 已经存在 CT 监督预训练到 MRI 肿瘤适配，不能把“预训练+MRI肿瘤”当创新。其正文 transformer 解释不采用，原始 STU-Net 是残差 CNN。更大架构的收益须与预训练收益分开。 |
| [STU-Net 原始论文](https://arxiv.org/html/2304.06716v1) | 六级残差 CNN，nearest interpolation + 1×1×1 上采样，TotalSegmentator CT 监督预训练。Table 5 AMOS-MR STU-B scratch 86.92 → fine-tune 87.49，nnU-Net 87.39，并非普遍巨大提升。原始预训练 4000×250 更新、默认适配 1000×250，设备 A100 80GB。direct inference 的标签合并会并入器官/肿瘤。 | 新病灶标签需要替换 head 并做适配；不能直接 zero-shot 得到 VS 肿瘤。不能用器官/病灶合并结果证明肿瘤保持，也不能以“大模型”本身当新意。本机先做同容量增强对照，迁移实验等待真实资源和来源核对。 |
| [Colormap augmentation](https://doi.org/10.1007/s11548-025-03559-y)，PMC13035743 | 2D 肝脏 CT↔MRI，训练/验证/测试均转 RGB 三通道。Table 4 T2：单 Cmap .5%，BigAug 72.2%，BigAug+Style 78.5%，ExAug+Cmap 41.0%。block 31 逐 map 测试后选 gnuplot2，与 block 40 target 完全未见的表述需要澄清。 | 不能称色图增强普遍提升；当前单通道合同不能直接挪用它。仅变换不用 GPU 不等于网络推断免费。其更有价值的启示是同容量增强消融和真实采集差异，采用标准增强作控制，绝不按确认集选择增强。 |

纠正的 BigAug 身份：[Generalizing deep learning for medical image segmentation to unseen domains via deep stacked transformation](https://doi.org/10.1109/TMI.2020.2973595)，PMC7393676。此前错误短题名检索无结果、Crossref 500 和正文 429 均保留。未复核其原文的数值，不以 Colormap 引文代替阅读。

MC-RC 作者论文 PMC11111906 只属于复读。其五 fold、约 25 万更新及丰富增强与本项目 11 名开发患者、每输入臂 19998 更新不同，因此已有训练结束不能直接称“充分任务适配”。

## 当前证据与可发表主张之间的差距

原始 native/raw 训练各 19998 更新真实完成。开发患者先均值 full Dice 为 .890639/.859645；已见四名验证患者为 .506632/.445159，六项医学能力门槛未全部通过。错误同时影响 anchors 与 missing，主要是漏检和低估；4.1 ml 和 1.2 ml 病例亦失败，不能只用微小残余解释。坐标 float64 修复是工程修复，必须完成全部 56 FOV 核验后判断，不能把严格数值通过等同医学成功。

官方 CSV、标签 ZIP 和 56 个首尾 DICOM header 的 UID/去标识 StudyDate 相符。同患者多个体积属于不同纵向时间点，不应要求相等，日期不能推断治疗。事后数学方向审计：开发 6 人/8 区间两臂均 0 错，已见验证 3 人/5 区间两臂均 2 错、涉及 2 人，患者先均值错误比例 .5。它可启发后续纵向终点，但不是独立确认、临床复发/增长判断，也不能将 native 同样存在的错误归因于 PCHIP。

主候选仍是：在任务模型具备足够医学能力后，从同一合法 observed 输入预测具体缺层修正对真实病灶的净收益，并在完整成本下超过强 raw、直接任务、两路径 error-cost/defer、随机和静态匹配控制。训练收益头、ROI、3D 模型、预训练、增强、两路径路由本身均已有先例。现阶段尚无正面的可发表 claim。

下一实验先检验基础泛化：同输入、同 frozen 起始权重、同患者/series 顺序、同标签、同 crop/flip、同更新和学习率，只改变训练增强。原始最后权重另立分支，原证据不回改。短 pilot 只能验证变换与训练可执行性；医学能力仍需固定最终权重、完整 FOV 和原门槛评价。增强成功后也还须完成 observed 直接任务和动作真实成本控制，再考虑未见确认。

资源快照 NEXT_EXPERIMENT_RESOURCE_READINESS.json：GPU free 1394 MiB，未达既有 8192 MiB 启动门槛；磁盘在十进制 8GB 储备外仅 90,775,552 bytes。两份 STU-S/Genesis FP32 权重的参数估算分别 116.8/130.56 MB，未计 optimizer/history/下载且未测实际 checkpoint，当前不满足。用户 GPU 授权仍有效，资源恢复后可以使用，不操作其他 PID。
