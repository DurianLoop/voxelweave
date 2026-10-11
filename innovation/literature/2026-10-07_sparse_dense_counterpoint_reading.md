# Jaritz原文：普通CNN及训练配方的必要对照

基于Eldesokey实际p13参考文献[7]及p2的mask-saturation讨论，再核题名索引，得到Maximilian Jaritz、Raoul de Charette、Émilie Wirbel、Xavier Perrotton、Fawzi Nashashibi的 [Sparse and Dense Data with CNNs: Depth Completion and Semantic Segmentation](https://doi.org/10.1109/3dv.2018.00017)，3DV2018。本轮实际下载 [arXiv1808.00769v2](https://arxiv.org/abs/1808.00769v2)，页首31Aug2018，9物理页。完整选读p1-8，p9参考文献未读；不是作者代码/实验复现。

这篇论文提供与Uhrig及Eldesokey不同的经验结果，必须一起解释。p2/p3 §3.1-3.2采用更强NASNet-mobile encoder/custom decoder，省去sparse输入首次strided conv后的BatchNorm，理由是缺失zero干扰mean。p3 Fig3分析maxpool传播的mask很快饱和；p3-4声称小网络拼mask可能改善、大网络未观察额外改善。因此本文并未证明“mask永远没用”，也没有与同结构同训练的全部sparse-normalized方法形成完全因果匹配。

p4 §3.3通过每image从(0,1]采density训练来增强变化稀疏度鲁棒性；p6 Fig6普通网络在固定density时会对更高density失效，varying-density训练可避免这一现象。p6同时明确其他同train/test-density实验仍用fixed-density以求较佳效果。鲁棒训练策略已有；本项目不能因加入mask或改变采样密度就声称新机制。

p4的depth completion loss只监督有GT的**未观测depth点**，p5Kitti输入下采样用maxpool避免零参与resize。这些均有场景条件：depth是非负距离且输入常为输出GT子集。我们的归一化MRI有正负值，task标签是病灶类别，不能把zero-maxpool或只监督缺层病灶机械迁移。原3D任务仍保留全标签的既有BCE+Dice，不借此更换主要endpoint。

p6 Table2报告depth-only iMAE.98/iRMSE2.60、RGB+sparse .95/2.17，是作者KITTI benchmark结果，不是MRI实测；作者讨论LiDAR-derived GT给depth输入天然优势，且LiDAR FOV以外未受监督。我们必须保留完整MRI FOV及统一label mask，不能按动作位置缩评价范围。

p7 §4.3：只更改末层为classes及softmax/CE就从稀疏depth直接做semantic segmentation；Synthia13类IoU depth-only57.10%、RGB-only63.47%、late fusion70.74%；Cityscapes19类depth-only44.18%、RGB-only50.13%、late fusion57.82%。p8明确“无需先生成dense depth map”及train/test sparsity类型不变的适用条件。因此不仅mask方法已有，普通CNN直接稀疏task也有先例。多模态融合带来的增益不能充当同MRI观测源的SR增益。

接续决定：现有one-channel-PCHIP能力参考仍保留；本轮两通道direct与dense是**已知类型的公平基线准备**。不能预设普通direct必然弱、mask-normalized必然强。若实际直接基线弱，先核其训练能力/观测编码/增强，必要时另立已知NConv/partial-conv对照；通过资格前不给SR正向claim。一个可发表命题只能来自充分适配后、患者级确认的可预测task修正余量或受控负结果，不能来自这三篇对同一问题互不相同的作者配置。

本轮累计新原文：Uhrig16页、Eldesokey14页、Jaritz9页，共39成功PDF页；完整选读8+13+8=29页。渲染与实际view证据另存reading_provenance.json。
