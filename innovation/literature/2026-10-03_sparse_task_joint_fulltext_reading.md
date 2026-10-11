# 联合任务、软标签、分辨率随机化与适应后 SR：四篇原始正文核读

本批四个PMC查询返回31题名行（含重复，命中数5/52/15/2）；取得三篇JATS正文后，发现joint_scar不是SR，另补取一篇直接LGE SR正文。后者efetch仅给front，原失败不覆盖；用标准库读取公开PMC HTML成功。实际阅读正文/方法/结果/限制和表格文字，登记393个非空定向块：joint_scar39、soft_spinal160、DRIPS113、LGE81。块数包含标题、图注和表格，不能当393页或393独立证据；未视觉复核图像、未读单独补充材料、未复现作者训练。

来源、实际block ID、原始块文字与SHA见 [阅读登记](source_cache/sparse_task_joint_fulltexts_2026-10-03/reading_provenance.json)。公开正文可分别查 [JDL](https://pmc.ncbi.nlm.nih.gov/articles/PMC10959501/)、[Soft spinal](https://pmc.ncbi.nlm.nih.gov/articles/PMC13110827/)、[DRIPS](https://pmc.ncbi.nlm.nih.gov/articles/PMC12633610/)、[LGE SR](https://pmc.ncbi.nlm.nih.gov/articles/PMC10206514/)。

| 原始论文 | 数据与实际方法 | 与MRI项目有关的先例 | 必须保留的限制 |
| --- | --- | --- | --- |
| Joint Deep Learning for Improved Myocardial Scar Detection from Cardiac MRI，ISBI 2023，DOI 10.1109/ISBI53787.2023.10230541 | 168患者，140训练/28测试；心肌/瘢痕两个分割网络，以预测心肌概率mask乘MRI，message passing和联合反传 | 预测区域指导病灶任务、两任务联合优化已有直接先例 | **不是超分辨率+分割**；两阶段训练使用人工心肌mask而测试使用预测mask，存在曝光差异；并非所有任务改善 |
| Towards contrast-agnostic soft segmentation of the spinal cord，Medical Image Analysis 2025，DOI 10.1016/j.media.2025.103473 | 243患者、6模态，145/49/49患者划分；六个hard mask对齐T2按FOV平均成soft GT，逆变换回原生；3D nnUNet模板、NormReLU、adaptive wing loss及重增强 | 跨模态软监督、直接分割、低分辨率增强和下游体积稳定性已有先例 | soft GT是配准/标注汇总，不能直接称物理组织占比gold standard；center crop假设目标居中；nnUNet对照1000epochs，主模型200epochs，不假定同预算 |
| DRIPS: Domain Randomisation for Image-based Perivascular spaces Segmentation，所读为medRxiv预印本，DOI 10.1101/2025.10.22.25337423 | 840 atlas合成曲折PVS，随机0.5–4mm voxel、形变、运动、Rician噪声、bias；3D U-Net，50×5000updates；165人五队列评价 | 细小结构直接分割、物理启发模拟和分辨率域随机化已做，不能将这些宽概念当首创 | 原段46在评价PR曲线上选最大Dice阈值；这是有评价标签辅助的operating point，不是部署冻结阈值；训练atlas和评价均有ADNI，身份交叉未在本批证明 |
| Deep learning architecture for 3D image super-resolution of late gadolinium enhanced cardiac MRI，JMI 2023，DOI 10.1117/1.JMI.10.5.051808 | 154体积来自60患者，80/20/54按体积描述；傅里叶/高斯模拟×2/4/8；DBPN/EDSR+3D梯度支路；另30个LAScarQS高分辨率体积 | **分别在各重建方法输入上训练U-Net后再比较任务收益**已经做过；3D梯度指导SR/边界结构也已有先例 | 本文段34/49未明确患者级分配，不能推定无同人跨split，也不能断言实际泄漏；center crop224×224×88，任务输入resize96×96×64；模拟LR；增支路同时增容量 |

JDL 原段30公式precision=TP/(TP+FP)、recall=TP/(TP+FN)正确，文字将“少漏检”和“少误报”的解释颠倒。按公式解释：高recall关联较少FN，高precision关联较少FP；不要复制该段反向解释。原段32心肌Dice分别.894/.900/.891（two-step/MTL/JDL），不足以支持“联合后所有任务都改善”，与结论部分较强用词的差异要保留。瘢痕效果主要在图中，本批不编造未从图视觉读取的精确值。

Soft spinal 段88/89说明跨模态CSA差异减小但没有完全消失；段157/158/159保留全部表格。主模型内部Dice约.95–.96，CSA绝对误差1.64±1.42mm²（段97），但主模型并非所有RVE/ASD最优。在外部sci-t2w，soft_all Dice .86±.07、RVE −16.14±9.80%，而nnUNet3D Dice .87±.05、RVE −15.20±8.59%；不能用“总冠军”描述全部任务。段104不报告DeepSeg2D外部Dice，因为GT由其预测再人工修正，明确标注来源偏向。段127/133中心裁剪是其有效性条件，我们的病灶推断不能沿用人工真值中心crop。NormReLU也引入输出最大值归一化，不能自动把任何软输出当校准概率。

DRIPS 段62可变voxel在EBBIVD BG median AUPRC .325→.459、voxel Dice .397→.499、lesion Dice .508→.635；是有价值的随机分辨率对照。段64运动增强并非所有指标更好：CSO AUPRC .390→.363，而lesion Dice .493→.532。段66/107增加Laplacian强度符号约束减少假阳性，提示contrast-agnostic形状学习还会误识其他管状组织；这不是任意去除病灶ROI的依据。段99明确合成几何/朝向简化、未比较新架构、扫描协议/病程范围与纵向效度局限。最大Dice阈值选择与多队列结果不能替代我们事前冻结阈值和患者身份证明。

LGE 段51/76/95是最接近“适应后任务评价”的证据：各SR方法分别训练3D U-Net，100epochs，监督LA chamber，并非把一个native冻结分割器直接用在所有重建输入上，也不是本文joint_scar意义的两分割任务联合梯度。表3在×4条件bicubic/DBPN/DBPN+gradient Dice=88.52/91.96/93.47%：gradient相对bicubic +4.95百分点，相对DBPN +1.51百分点。其任务适应后仍有收益，所以“所有SR差异都只是分割器曝光失配”同样是未获支持的宽结论。

LGE 表4仅图像loss+梯度loss（不增branch）PSNR25.36→25.35、SSIM.730→.729；增branch到all levels为26.63/.763，但参数1.13M→5.41M，约4.79倍，不能把全部收益归于梯度信息本身。表2外部×8时EDSR+gradient PSNR21.57/SSIM.424，DBPN+gradient21.03/.423，主框架并非每个表项最佳。其native0.625mm与外部1.4mm、模拟LR、任务resize等条件与本项目真实observed层/完整缺层端点不同，应明确对照差别。

对当前项目的判断：加入边界/梯度loss、联合训练、预测mask指导、soft标签、直接稀疏分割、分辨率随机化、适应后评价这些单项均已有先例。优先验证具体的**训练曝光×输入统计×重建方法交互**，以及同容量/预算、完整缺层和病灶边界/体积守卫下的残余收益。实验合同的严谨性本身不证明方法首创；必须有具体可观测方法与真正未见患者结果。

本轮训练pilot只检查数据和从头任务网络的能力，不能当上述矩阵已执行。任务适应如果消除差异，可报告原评价结论依赖训练曝光；若保留差异，才值得训练局部可观测修正，并与raw PCHIP、直接分割、随机分辨率、同容量taskloss和无条件修正比较。所有发表结论仍待后续验证。
