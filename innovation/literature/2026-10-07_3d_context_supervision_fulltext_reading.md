# 3D U-Net / DeepMedic 原文核读与监督诊断

实际核读两篇原始公开HTML的全部提取文字：3d_unet_sparse_annotation blocks0–52（53块），deepmedic_multiscale blocks0–220（221块），合计274提取块，正文、公式文字、所有主表/附表、图注及参考文献均包括。此是文字提取块，不是274独立段落。没有核原图像素、独立补充文件、作者代码，没有复现作者实验；提取/获取reading=false保留为历史，阅读另登记。

## 3D U-Net: Learning Dense Volumetric Segmentation from Sparse Annotation

[arXiv:1606.06650](https://arxiv.org/abs/1606.06650)，MICCAI2016，按本次HTML读。

关键区分：作者的“sparse”是标签不完整；完整3D观测图像仍输入网络（块1、5、16、19）。本项目stride4只保留MRI观测层，而开发监督label完整；不能把本文当成同observed信息重建的验证，更不能将未标注位置当已知背景。作者将unlabelled标签3的loss权重置0，正是为避免这一混淆。

结构与context：块13为四级3D encoder/decoder、3³conv/2³pool/upconv、skip；19,069,955参数。块14输入132×132×116、输出44×44×28，使用valid context的中心输出，体素1.76×1.76×2.04µm，物理感受野约155×155×180µm。不能拿这些microscopy尺寸当人脑MRI毫米尺度，也不能因为本项目140万参数3D网络能前后向就称复现本文的能力。块15使用batch1但在测试仍当前批次统计，区别于一般BN running-stat推断，也不同于本项目InstanceNorm。

数据/训练：三个Xenopus kidney confocal体积、三染色channel；作者下采样2倍后的shape约248×244×64、245×244×56、246×244×59，orthogonal sparse annotated slices每volume不同（块19）。rotation/scale/gray/elastic、weighted CE、SGD、70k iterations、TitanX约三天（块21）。本项目单T2、512固定两patch CPU拟合不是作者多样增强或训练预算的等价实现。

验证边界：semi-automated setup的77 annotated slices在同三个volume内分3fold，测未使用annotation slice IoU；不是按独立患者隔离的确认。块29报告average IoU .842无BN / .863有BN / .796 2D有BN。Fully automated setup训练两个volume、测第三个，块30 average IoU .723无BN / .704有BN / .547 2D；第三fold BN由.779降至.554。原文块33承认数据差异导致BN反效果。不能简化成“3D+BN在所有fold都更好”，也不把IoU数值直接当Dice或本项目临床肿瘤准确率。

对应本项目：有效监督、valid input context与输出支持、坐标一致性和批统计策略都已有技术依据。增加3D/只标部分label/改变normalization不是剩余新贡献。

## Efficient Multi-Scale 3D CNN with fully connected CRF for Accurate Brain Lesion Segmentation

[arXiv:1603.05959](https://arxiv.org/abs/1603.05959)，按本次获得的当前HTML版本；正文引用包含2017文献，不声称读的是2016v1或某个未核对的最终期刊版。

核心：11层3D CNN、normal/lowres两路径、small3³kernels、larger physical context、dense image-segment training、foreground/background采样。块43说明一半中心前景、一半背景，但segment内部的真实前景比例仍随病灶大小/segment体积变化；不能把“半前景patch”说成“半体素都是病灶”。块68–70对比uniform voxel中心会欠分、均衡class中心patch会过分、dense segment折中，并把segment size列为hyperparameter。该采样/类别平衡方向已有明确先例。

上下文/容量：块76–78 lowres factor3，localRF17³、实际lowres context51³；同参数更宽single-scale BigDeep+并未达到dual-pathway，说明必须分离context和capacity，不能以参数量替代充分基线。附表B.1（块143）single-scale Deep+64.9%/BigDeep+65.2%/DeepMedic66.6%是在固定TBI验证fold，不能直接拿这些分数或结论与本项目单T2不同队列比较。附录A空间对应与upsampling步骤是关键合同，不只是拼两个分支。

数据条件：TBI原66，2 FLAIR坏图+2无病灶+1扫描伪影排除后61；MPRAGE/FLAIR/T2/PD/GE多序列、brain mask、affine MNI registration、resample1mm、逐image z-score（块86）。本项目不据此筛掉TP0/空预测/难系列，也没有这些额外模态与脑mask。TBI5fold共享划分，但CRF先用15subjects调参后又混回fold（块88–90），不把其全部指标视为严格独立超参确认。

BRATS274train/110hidden-test，四modalities/skull-stripped/registered/1mm；TBI、BRATS、ISLES的正则/augmentation并不完全相同。作者BRATS test单netwhole/core/enhDice83.6/67.4/62.9，CRF后84.7/67.0/62.9；core平均下降。TBI单netDice62.3→CRF63.0，但recall64.4→63.2；因此不能宣称后处理改善全部端点（块92、107）。三网络ensemble额外推断预算也不能与本项目单网公平混算。

ISLES28train/36test，T1/T1ce/FLAIR/DWI、brain masks/resample；CRF在整个训练集random search配置，作者块117承认训练集增益可能部分过拟合。测试ensemble+CRF Dice59±31%，测试中心差异使所有方法下降（块111–120）。本文Haussdorf不是本项目HD95；未说明的表面定义/空间轴不能直接搬用。

计算与解释：块123网络训练约一天TitanX，train可3GB、whole-volume inference需12GB，3GB tiled推断<3分钟；不能将旧GPU或作者数值当本机当前显存/速度预测。正文的BN/internal covariate shift解释保留为作者解释，不把它作为本项目失败的因果证据。块133强调softmax并非校准Bayesian概率，块134将data-acquisition-generative augmentation列作future方向；uncertainty/采集随机化也不是本项目可直接首创的大方向。

## 本轮实际监督检查与决定

冻结32draw×19开发series=608 draws；每个draw三尺度GT与独立stride坐标oracle比较，总1,454,374,912重复patch GT值核对。主/半/quarter监督下forced-FG与whole-batch归零均0。最小series VS-MC-RC-011物理foreground76；quarter强制前景patch只1–2voxel，仍非0。不能把重复draw当患者，不能以这些非零GT证明已学会病灶；这轮不支持“coarse GT完全抹除造成失败”的解释。

当前另有相同尺寸/初始权重/监督/primitive的native/PCHIP两CPU臂各512更新正在进行。两checkpoint全部冻结后才评分完整FOV；512固定batch拟合仍只是一个开发series，不是充分19系列训练或泛化确认。Loss下降不作为门槛通过或方法优势。

上述两篇进一步排除：只加3D、增加context或低分辨率分支、改采样/foreground loss、修标签坐标、加CRF/uncertainty本身就是新贡献。仍须标准化或充分配置任务baseline、同observed直接任务、公平输入/统计/监督/容量/预算矩阵；稳定残余成立才开发预测action gain的修正。科学确认0，八确认关闭，没有已独立确认可发表claim。

来源：[获取日志](source_cache/3d_context_supervision_2026-10-07/retrieval_attempt01.json)、[提取与SHA](source_cache/3d_context_supervision_2026-10-07/extraction_attempt01.json)；监督实测：[608draw结果](../experiments/mc_rc_3d_development_supervision_2026_10_07/attempt_01.json)。
