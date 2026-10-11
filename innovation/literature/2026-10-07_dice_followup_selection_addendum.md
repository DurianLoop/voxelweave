# 区域偏置核读后的补充选文

新增定向核读两个原始loss先例，目标是准备尚未训练的更强能力对照，不在当前512更新实验中改配方：

- Sudre et al., *Generalised Dice overlap as a deep learning loss function for highly unbalanced segmentations*，arXiv1707.03237：检查经典不平衡loss的学习率/前景比例边界，不能将改Dice当贡献。
- Wang et al., *Dice Semimetric Losses: Optimizing the Dice Score with Soft Labels*，MICCAI2023：仅为后续软/占比监督查新；先从arXiv精确题名metadata确定公开原文版本，不猜identifier。

二者来自已读区域偏置论文references（blocks134/140），与既有Unified Focal、nnU-Net区分。只有实际阅读成功的部分才登记，无法访问的论文只记录准备。
