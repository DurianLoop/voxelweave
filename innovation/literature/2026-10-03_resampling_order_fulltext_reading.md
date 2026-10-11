# 本批正文：避免插值损失已有先例，顺序效应仍需项目证据

首批检索实际返回27条题名，按大小写与HTML实体规范化后26个不同题名；Brainana的两个公开版本不重复计论文。随后两个窄查询又返回14条，其中PySERA与首批重复。实际重点核读3篇新的公开正文，均为经DOI身份核对的JATS XML，新增PDF为0。VINNA此前读过索引摘要，本次才新增正文。检索题名、重点摘要、正文和自己的实验分别记录，不以返回数量代替阅读量。

来源取得记录：[获取清单](source_cache/resampling_order_fulltexts_2026-10-03/attempt_01.json)。索引记录：[三项检索](source_cache/resampling_order_search_2026-10-03/attempt_01.json)。抽取的公式、表格和图注为展平文字，未视觉核读图像及补充材料；本笔记中的数值均是作者报告，未独立复现其训练或模体实验。

## 1. VINNA for neonates: Orientation independence through latent augmentations

Henschel等，2024，DOI [10.1162/imag_a_00180](https://doi.org/10.1162/imag_a_00180)。[本地正文](source_cache/resampling_order_fulltexts_2026-10-03/vinna_maintext.txt)。关键块：0004、0006、0009–0010、0039、0044、0046、0059、0063、0070、0072、0084、0088、0091、0095、0097、0101–0103、0128–0129、0136–0143。

具体方法并非停止所有插值，而是把分辨率归一化、面内旋转和平移作用在连续特征图上，在最后用逆变换恢复空间；pre-IDB与post-CDB保留原网格输入和非插值特征的路径。相比传统图像/离散标签外部增强，它避免反复插值原图与标签。外部增强同时比较最近邻离散标签和one-hot线性插值soft loss，且有参数相同的CNN、VINN及VINNA对照。

数据身份与边界：dHCP共578人，318训练、90验证、170测试；训练覆盖0.5/0.8/1.0 mm，dHCP本身先经运动校正与SR生成0.5 mm，并非原始高分辨率采集真值。训练/主要测试参考由dHCP pipeline生成；另用10名M-CRIB手工标签做外部验证，需合并/屏蔽不同atlas标签，不能把其指标直接移用于肿瘤二值Dice。消融在验证集、后续比较在测试集，作者明确分开。作者采用Wilcoxon与BH校正；外部10人结果只描述，未宣布显著性。

可用结论：VINNA优于附加外部增强的VINNA；one-hot soft标签增强比最近邻好，但VINNA仍在0.5/1.0 mm较好，0.8 mm未检出与VINN+soft增强差异。0.8 mm较差被作者解释为非整数网格插值的可能效应，不是独立因果证明。M-CRIB比较还修正了nnUNet五人的左右翻转，正文披露这一点。作者承认对未见尺度、扫描器/年龄/强度域的外推不保证。

对MRI项目：原网格特征旁路、物理分辨率感知以及把重采样移到特征域，都不能作为宽首创。“256网格预处理可能影响下游任务”亦已有很近的实证先例。可继续问的窄问题是固定缺层合同中，面内缩放与非线性PCHIP的顺序差异是否达到病灶/任务相关量级，并与面内信息损失和冻结评估器暴露区分。VINNA不直接研究我们的PCHIP算子，也不证明本项目结果。

## 2. MRI预处理、纵向重复性与跨平台重复性

题名：Influence of image preprocessing on reproducibility and longitudinal repeatability analysis of radiomics features in magnetic resonance image-guided accelerator imaging，2026，DOI [10.21037/qims-2025-aw-2151](https://doi.org/10.21037/qims-2025-aw-2151)。[正文](source_cache/resampling_order_fulltexts_2026-10-03/mri_preprocessing_maintext.txt)。关键块0012–0025、0029、0047、0060、0062、0067–0074。

实验是同一ACR模体、两机构的同型1.5T Unity MR-Linac、三序列T1w/T2w/FLAIR。System A有同session重新放置test/retest及30天每日一次扫描；System B一次扫描用于平台比较。五个ROI先在T1w划定，经刚体注册传播，不逐扫描重新勾画。不是患者肿瘤队列，不能把“平台不同”描述为多厂商验证。

处理因素：sitkBSpline、9种各向同性网格0.5–5 mm；BN 8–512或BW 1–100；有/无Z-score。对92项一阶与纹理特征做ICC绝对一致性及CV联合判断，高稳定要求ICC>0.9且CV<10%。部分BW=1、无Z-score、细网格组合提取失败，作者保留计算失败，并未计作高稳定。重采样针对重建网格；作者的表1明确区分采集与重建体素，值得本项目沿用。

表2可核对的反例：T2w test/retest最佳稳定比例89.13%，0.5 mm、BN512；纵向63.04%，不空间重采样、BN512；跨平台50%，1.5 mm或不重采样、BW5/10/25。不同任务的最佳条件不同，不能把同一网格一概说最优。作者只固定一种BSpline核，讨论中的核差异来自既有研究，未在本实验比较PCHIP顺序。两同型系统、同质模体、只一种归一化及未加入denoising/bias-field correction均限制外推。

对项目：已排除“预处理改变指标”宽创新。其可借鉴之处是把不同重复性任务、处理因素、失败和采集/重建网格分开。它没有证明我们的冻结分割Dice变化，也未测我们的插值顺序；不能以其最优BN/网格为项目调参依据。

## 3. A Stability Atlas for IBSI Radiomics Features

完整题名：A Stability Atlas for IBSI Radiomics Features Using Synthetic Digital Phantoms, with Proof-of-Concept Physics-Based Normalisation，2026，DOI [10.3390/jimaging12080392](https://doi.org/10.3390/jimaging12080392)。[正文](source_cache/resampling_order_fulltexts_2026-10-03/stability_atlas_maintext.txt)。关键块0008、0010、0012、0014–0019、0021、0026–0027、0031–0036、0039、0041、0043–0044。

作者把可控高斯随机场纹理/可选椭球病灶、图像域退化、IBSI特征、稳定性和拒绝校正组合为工具。15纹理×9条件；含随机噪声的5条件各5个realisation，总435模拟采集。原136向量的两常数特征排除，余134报告ICC(2,1)，2000次targets及随机realisation共同bootstrap；另报ICC(3,1)、条件组成敏感性和方差分解。482个IBSI数字模体数值匹配并不代表全部预处理配置已标准化。

固定顺序为blur/slice-profile→resampling→noise→quantization；并未比较“PCHIP前/后面内缩放”。这是HU-like图像域合成研究，不能当MRI扫描链或临床验证。作者报告median ICC .13（CI .03–.19）只对应该严苛合成envelope；大部分不稳定不能直接用来支持患者结论。

对本项目最有用的是失败探针：白噪声校准应用到等幅相关噪声，作者报告264%校正误差；noise与blur共变的校准即便R²=.9999，单独noise应用仍错9.5%。已知noise描述符的GLCM contrast校正median误差3.8%，换成图像估计noise则11.1%。因此拟合/软件复核通过，不能代替域外科学验证；模体值应与真实患者证据分开。简单噪声方差减法与合成稳定性工具都有直接先例，不作为新方法claim。

## 本批对创新判断的实际改变

| 候选 | 本文献提供的先例/限制 | 下一步 |
| --- | --- | --- |
| 原网格旁路、特征域重采样 | VINN/VINNA有直接架构先例 | 作为强对照；需更窄任务和未见数据效应 |
| 256处理改变任务排名 | 预处理影响任务/特征早已有结果 | 做具体因素控制，避免只换基线命名创新 |
| PCHIP和面内缩放的顺序 | 这三篇未测相同算子/合同；缺少直接先例不等于首创 | 全45固定CPU解析对照与独立数学复核；先量化，再决定task forward |
| 观测信息预测局部有害修正 | 拟合筛选不能保证域外有效，且旧候选多次失败 | 需部署可得输入、动作/绝对误差强对照及新患者确认 |

正文只收窄查新空间。本批没有因新增3篇或软件复核而成立新的可发表claim；原HAT−pipelinePCHIP负向主张继续停止。

## 两个窄查询和一项正文未取得

[窄查询记录](source_cache/pchip_order_prior_art_2026-10-03/attempt_01.json)分别返回2和12条。PCHIP查询中一篇为发动机压力处理，与MRI缺层无关；另一篇为CEST Z-spectrum稀疏频谱恢复，DOI `10.1002/mrm.30233`，不是空间切片重建。order查询总hit254但仅返回首12，混有fractional-order、first-order及非医疗图像，精度与覆盖都不足。不能据“未找到完全相同算子”宣布首创，仍待signal-processing、image-resampling与医学MRI领域更全面的查新。

其中神经母细胞瘤T2研究 *Reproducibility Analysis of Radiomic Features on T2-weighted MR Images after Processing and Segmentation Alterations in Neuroblastoma Tumors*（2024，DOI `10.1148/ryai.230208`，PMC11294951）直接相关，已登记为优先补读。然而[取得记录](source_cache/t2_tumor_processing_fulltext_2026-10-03/attempt_01.json)只有metadata/abstract，XML明确写明“**The publisher of this article does not allow downloading of the full text in XML form.**”且没有body。保存此次失败，不重复该受限路径，不计第四篇正文、不从摘要补造方法细节。后续只用合法公开作者版本或用户已有全文补读。
