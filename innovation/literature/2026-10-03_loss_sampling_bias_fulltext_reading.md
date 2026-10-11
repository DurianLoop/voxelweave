# 两篇病灶失衡原始研究：完整体积能力与loss取舍

本轮三个PMC查询筛查18题名行，选取两篇新原始正文；实际读完69+88=157个body/floats文字块（含公式、表格与图注），并另读2024论文back中的Appendix A全部p/disp-formula。没有新PDF、图像视觉复核或独立复现作者训练。文字提取的数学式可能丢失符号/分式，不据此直接实现新loss。获取记录保留actual_reading_completed=false，另存阅读锚点/SHA。

| 论文 | 原始公开来源 | 对项目的约束 |
|---|---|---|
| An Analysis of Loss Functions for Heavily Imbalanced Lesion Segmentation，2024，DOI 10.3390/s24061981 | [PMC10976047](https://pmc.ncbi.nlm.nih.gov/articles/PMC10976047/)、[正文](source_cache/loss_sampling_bias_fulltexts_2026-10-03/lesion_loss_analysis_maintext.txt) | patch分数与完整image分数分离、严重失衡/梯度饱和、同初始化/批次和多seed已有原始先例 |
| Asymmetric Loss Functions and Deep Densely Connected Networks for Highly Imbalanced Medical Image Segmentation: Application to Multiple Sclerosis Lesion Detection，2019，DOI 10.1109/ACCESS.2018.2886371 | [PMC6746414](https://pmc.ncbi.nlm.nih.gov/articles/PMC6746414/)、[正文](source_cache/loss_sampling_bias_fulltexts_2026-10-03/asymmetric_ms_maintext.txt) | Tversky/Fbeta、前景patch、overlap/按patch中心加权融合及召回/FP平衡已有直接先例 |

## 2024：不能用patch高Dice代替完整image能力

块6–18：WMH为60例，另17名MS新/增大病灶患者（原20人中排除3无活动病例），主要使用处理后的FLAIR等输入，不是本项目稀疏单T2/VS。32³patch、stride16，训练仅含前景patch/batch16；2,906,913参数3D U-Net/GroupNorm8。初权重和batch shuffle同seed，五seed×五fold；并未证明我们的4000/20k步预算复现作者能力。

块31/37/41–45、表2（68）：同时评价training patch、完整training image、完整test image；预测overlap平均后固定.5。LIT中Dice loss的patch/train/test Dice .96/.55/.52；mixed .93/.55/.54。它直接覆盖“patch能拟合但全FOV失败”的宽现象。作者表2使用已知最佳epoch/seed的结果，不是预写最后checkpoint效果；不能把其上界比较当部署可复现均值。表2中patch的CE/focal1 .64/.59，与块54“all methods over .7”文字存在范围不一致，保留表内具体数值，不复述为全部都>.7。

块48–58与Appendix A：Dice接sigmoid时极端错误概率可使logit梯度很小，作者另提出weighted-gradient而非简单loss weighting。正文Eq5的纯文本符号不足以确认实现，不能直接照抄。BCEWithLogits本来有不同梯度；本项目当前loss已包含BCE，因此不能推断Dice饱和就是我们的失败原因。作者自己指出提高TPf通常增加FP、patch位置/padding/pooling和多重计数可能影响完整预测；这是解释候选，不是其逐因素受控因果证明。

块52/58：多seed/epoch的不确定性足以改变loss排序。当前单012单seed两臂只查可拟合性，不能升级为loss泛化结论；将来正式方法需固定多seed/患者划分并对所有重复报告。

## 2019：不对称与加权融合不能包装成新方法

块20–30：Fbeta将FN权重设beta²/(1+beta²)、FP设1/(1+beta²)，beta增大偏召回。不要把这套beta直接当Unified Focal的delta；后者作者源码delta=.6作用于FN，符号语义另行审计。块44“TP为0便无学习”的概括并不适用于所有带smooth/BCE的实现，不能用它合理化删除我们的空前景patch。

块32–46：3D DenseNet大patch、50%overlap，四种rotation，单体素可有32次预测；样条权重降低patch边缘影响。这是既有融合/增强方案，不能把我们加窗或按位置融合称新概念。训练仅选至少10病灶体素patch，每image等量；MSSEG15人五fold，ISBI5人21时点，testing段明确按患者隔离时点，不能把21stacks当21独立人。多个模态、训练epochs与TTA计算量均不同于本项目。

表II（86）：Spline Fusion beta1的Dice70.3高于beta1.5的69.9，但后者recall78.58高于74.49，F2/APR也稍高。正文“最佳”指多端点取舍，不能改写成所有指标一致增益。beta3的Dice64.34说明更重FN不是越大越好。

表III（87）：ISBI focal的Dice58.41、PPV92.07、recall45.58；Fbeta为65.74/71.39/66.77，表面距离4.48→2.88mm，体积差49.72→37.27%。总体challenge排名focal更高，而Fbeta某些临床端点更好；单一排名不能替代任务需求。块84图9图注称focal更少FN/更多FP，与总体表及块67的focal更低FP方向不同；图9是挑选两个Dice近似病例，不能推广。未看图片，不作视觉断言。

## 更新创新判断

同初始化loss对照、Dice饱和、小病灶召回保护、patch/volume评价差异及中心加权融合都有先例；本轮用于诊断，不作为新claim。值得保留的问题仍是：在任务模型具备完整FOV能力、训练曝光与统计均公平后，是否仍存在由稀疏采样/重建引入、能用observed信息修复的缺层残差。需要强PCHIP、直接任务/分辨率随机化、native能力、同预算矩阵和未开患者确认。当前两臂实验不被新阅读更改，八确认关闭，科学确认0。
