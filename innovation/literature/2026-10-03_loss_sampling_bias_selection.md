# 本轮损失/采样原始正文选择

三个PMC查询筛查18题名行（总命中40/29/48；不是117篇已阅读）。选择两篇与当前单病例拟合/严重失衡和patch到完整volume差距直接相关的原始研究：

1. An Analysis of Loss Functions for Heavily Imbalanced Lesion Segmentation，2024，DOI 10.3390/s24061981，PMC10976047。核梯度修改、前景漏检及patch/完整image训练效果是否相同。
2. Asymmetric Loss Functions and Deep Densely Connected Networks for Highly Imbalanced Medical Image Segmentation: Application to Multiple Sclerosis Lesion Detection，2019，DOI 10.1109/ACCESS.2018.2886371，PMC6746414。核Tversky系数方向、overlapping patch、召回与FP取舍、实验划分及预算。

准确DOI/题名在既有literature Markdown与reading JSON未命中；这只支持本缓存未登记，不代表全局文献不存在其他先例。Unified Focal已读，跳过，不重复计数。其余题名仅索引线索，包括2026肿瘤采样论文；本轮不说已读正文。不会以这些论文修改正在执行的固定012两臂实验。
