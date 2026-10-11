# 内部特征统计：三篇原始论文与候选边界

本项新增实际核读3份公开原始PDF全部可提取页文本：Instance Normalization 6页、AdaIN 10页、Group Normalization 17页，共33页；包括图注、表格和参考文献文本。AdaIN页2–3因首次合并输出截断另读，Group Norm首次输出未显示，随后全部按小组重读。三个关键公式页经Poppler渲染并实际view_image核看；其余示例/曲线像素没有视觉核读。未复现作者代码或网络，不将参考文献列表计作额外已读研究。

## Instance Normalization

Ulyanov、Vedaldi、Lempitsky，*Instance Normalization: The Missing Ingredient for Fast Stylization*，arXiv1607.08022。本次下载是PDF所标1607.08022v3、2017-11-06，不能冒充2016首版本。作者在摘要将它称短文并指向另一份完整论文1701.02096；后者此次未另读。

PDF页4 Eq.3明确对每个sample/channel的空间轴取均值和方差，分母为sqrt(var+epsilon)，并在测试继续使用当前输入统计。它解决的是固定风格快速stylization，相比BN改变训练和测试两端并重新训练；不是将已训练MRI网络的统计换成PCHIP即可获得任务改善的证据。页3同时讨论zero padding边界伪影和训练样本数/早停，不应把边界问题只归因统计。

对本项目：现有InstanceNorm3d(affine=True, track_running_stats=False)的eval仍按当前patch取统计；输入层同observed z-score不能固定后续14个IN的统计。宽“逐图统计改变生成/识别行为”已是先例。3D扩展将空间轴换成D,H,W，不构成新原理。

## Adaptive Instance Normalization

Huang、Belongie，*Arbitrary Style Transfer in Real-time with Adaptive Instance Normalization*，ICCV2017，正文页1501–1510，[CVF原文](https://openaccess.thecvf.com/content_ICCV_2017/papers/Huang_Arbitrary_Style_Transfer_ICCV_2017_paper.pdf)。

PDF页3先区分像素对比度归一化与特征统计：即使训练图像统一contrast，IN仍有效；将输入预先style normalize后IN与BN差距变小。此为自然图像风格实验，不是MRI统计路径因果确认。

页4 Eq.8：`AdaIN(x,y)=sigma(y)*(x-mu(x))/sigma(x)+mu(y)`。它用candidate自身统计标准化，再施加style统计；**不同于本项目拟诊断的 `(candidate-mu(PCHIP))/sqrt(var(PCHIP)+eps)`**。后者固定标准化参照，保留candidate相对参照的均值/方差变化；这一区别可以支持明确控制定义，但不能单凭公式不同宣称新颖或有用。

作者用固定预训练VGG19至relu4_1编码、训练随机decoder，decoder无BN/IN且使用reflection padding。页7实验比较concatenation及BN/IN decoder，提示不能默认给所有层加统计迁移都有效。页5训练COCO与WikiArt各约80k，batch8、256²crop；页7速度表Titan X、100图像平均。512px时间0.065秒不含style encoding、0.098含encoding，不能将56FPS或作者GPU数字当本项目3D速度。页8已支持不同区域各自AdaIN，区域统计/空间控制宽方向也被占位。

## Group Normalization

Wu、He，*Group Normalization*，ECCV2018，[CVF原文](https://openaccess.thecvf.com/content_ECCV_2018/papers/Yuxin_Wu_Group_Normalization_ECCV_2018_paper.pdf)。

页5–6 Eq.1–7与TensorFlow示例清楚区分统计集合：BN含batch轴；IN每样本每channel；GN每样本将相邻channel分组并跨空间取统计。GN的G=1对应论文中的LN，G=C对应IN；并保留每channel affine。**GN仍依赖当前patch的空间内容**，所以换GN不自动阻断candidate改变内部统计或消除tile context差异。当前16起始channels也不能盲目用默认32组。

页7–9 ImageNet ResNet50、8GPU、100epochs、最后5epochs中位数；batch32时BN23.6%/IN28.4%/GN24.1%错误，batch2时BN34.7%/GN24.1%。这10.6是百分点而非相对误差下降。batch变化还按0.1*N/32调整学习率并保持epochs，更新数随之变化；不应冒充仅改变统计集合的纯控制。页8Figure5图注右侧误写LN，图内及对应Table2实际是GN；阅读记录保留该差异。

页11–12 COCO Mask R-CNN区分冻结BN*与GN重新预训练/微调：C4 GN boxAP38.8 vs37.7、maskAP33.6 vs32.8；后续更长训练也影响结果。页13–14 Kinetics为3D视频分类，GN spatial扩展含时间轴，不是MRI病灶3D分割数据。作者明确不同norm的适宜超参可能不同。它排除了“batch2改GN”宽创新，但没有证明本项目当前失败由IN造成。

## 候选修订与下一步

有价值的窄控制仍是：同一部署可见observations、PCHIP参照、固定checkpoint/tile plan，在每个IN中固定参照统计，区分candidate内容路径与统计反馈路径。它是机制诊断，需先通过同输入自重放及label/native屏蔽；部署参照不得来自隐藏native MRI或GT框。由于全部层串联且有卷积、激活和skip，ordinary/ref-stat差值不是全网可加的“统计因果贡献百分比”。

本阶段输出层诊断仅能改善训练crop，完整FOV仍失败；先修充分优化与采样/context覆盖。统计控制若在弱网络上改变输出，也不能当MRI收益或新方法成功。最终贡献仍取决于充分任务适配后可预测的修正收益、同observed直接任务/强PCHIP对照、完整患者端点以及独立确认。

原文与阅读/公式视觉登记：[缓存](source_cache/feature_normalization_primary_2026-10-07/)。已有相关原始先例：[区域统计/掩膜/归一化等变](2026-10-03_masked_normalization_primary_reading.md)、[SegRenorm与MRI任务统计](2026-10-03_task_normalization_context_fulltext_reading.md)。本项新增3篇，不重复计算先前5篇或nnU-Net两篇。
