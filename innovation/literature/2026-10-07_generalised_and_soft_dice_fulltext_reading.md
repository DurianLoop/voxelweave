# 经典不平衡Dice与软标签Dice：两个原始先例

实际核读两篇原始公开HTML的全部可提取文字：Generalised Dice blocks0–65（66块），Dice Semimetric blocks0–181（182块，含附录0.A–0.E）。公式保留LaTeX；获取/提取不算阅读，登记另存。**Generalised Dice的三张数值表是外链SVG路径图形，HTML仅含表题；已下载SVG但没有可提取text节点，也未渲染核图，表内数值未读。**其曲线/示例像素也未读。不声称视觉核表或复现作者网络。Dice Semimetric主表/附表的HTML数值实际均已读，原图像素与作者代码未核。

## Generalised Dice overlap as a deep learning loss function for highly unbalanced segmentations

[arXiv1707.03237v3](https://arxiv.org/html/1707.03237v3)，2017，DOI10.1007/978-3-319-67558-9_28。四种loss：WCE、二类Dice、sensitivity-specificity、inverse-squared-GT-volume加权GDL；与当前foreground-only BCE+Dice不是同一配方。块10 WCE的w写成预测P之比，块9缺外层括号等形式细节，没有作者代码核对时不能默默将它改成GT权重后称复现。

块34–37同时改变patch size和batch size，学习率10^-3/10^-4/10^-5，无训练增强，**所有训练patch必须含至少一个前景**。因此其“较小patch更好”不能排除batch/梯度与前景比例的混杂。2D为BRATS，3D为524subjects的白质病灶队列；T1/T2/FLAIR并以WM统计z-score，不等于本项目单T2/同observed统计。2D1000/3D3000更新看训练末200步，另3D10%留出；不能将其训练曲线当本项目跨患者最终能力。

块36说最不平衡patch“median0.2%”，块52又说最不平衡情形0.02%，可能涉及中位数/更极端样本，三张表尚未视觉读取，不能合并成唯一统一比例。高/低学习率失败说明优化预算影响结果，不证明本项目当前loss必定失败或GDL必定有效。

inverse-volume权重在某类GT为0时无定义；作者只采非空patch是重要适用条件。本项目明确保留uniform采样的空背景patch和全部空评价域，不能为套GDL筛去它们。后续若实施已知GDL对照，需显式冻结empty-class、batch聚合和epsilon规则。

## Dice Semimetric Losses: Optimizing the Dice Score with Soft Labels

[arXiv2303.16296v4](https://arxiv.org/html/2303.16296v4)，标MICCAI2023，本次为2024-03-20更新v4；不等同未经核对的会议最后稿。块12/17：普通L1 soft-Dice直接吃软标签时，最优预测不一定等于软标签，例如标量GT=.5时loss最小在prediction1。这与“soft Dice”名字里的soft（预测可微）是两件事。L2形式和其公式3文字/平方记法需对照实现，当前不端口代码。

块32定义：`DML1=|x-y|_1/(|x|_1+|y|_1)`，`DML2=1-2<x,y>/(2<x,y>+|x-y|_1)`。在硬GT上它们与普通L1 soft-Dice等价（未加平滑的理论式）。**当前三个head的GT都是hard，直接换DML不构成新的不同loss干预。**若未来换coarse area-average/占比GT，须明确该GT是几何占比，不是本队列并不存在的多标注者概率。x=y=全0时理论分式为0/0，需要实际empty/epsilon约定；不能在空case使用未经声明的“零距离”数值。

块35–39/附录0.A证明的是semimetric，Dice并非通常metric；弱三角常数作者给上界黄金比约1.62、下界1.5，最紧值留为开放问题。不能说具有原始三角不等式或已解决最紧常数。

数据和训练：QUBIQ7任务含55/39/32/24cases，多rater；LiTS和KiTS为CT，只用有公开GT的训练病例作5fold CV。模型2D、ImageNet预训练ResNet/EfficientNet/MobileNet+UNet/DeepLab，batch8、SGD.01、150/60epochs、CE/DML权重.25/.75。不是当前3Dfrom-scratch、无教师或无额外数据的公平同容量基线。

评价：Dice/ECE对majority-vote GT，BDice对soft标签按.1–.9九个阈值平均。QUBIQ Brain Tumor T2在表2中uniform BDice55.11/weighted44.23，但Dice分别52.42/61.01，说明“更好”随端点变化。表3按这项任务用uniform、其余用weighted，是任务特定的选择；不能将表3整体BDice78.14与表2纯weighted76.59当完全同规则或独立新增信息优势。五fold CV不等于本项目已反复开发的四验证独立确认。

块64/附录0.B的校准界为`abs(E[p*-f]) <= E[abs(E[y|f]-f)]`：左边是平均有符号偏差的绝对值，**不是E|p*-f|、单voxel误差或个体病灶修正收益的界**。系统偏差可能抵消，不能据此称低ECE能识别有益修正。KDE教师校准本身已是先例；其训练使用key-point标签及额外教师容量/计算预算，部署阶段不能读取隐藏GT或native缺层像素。

附录0.E需按类采keypoints、避免某类被忽略，否则预测该类校准值为0；还限制到错分/边界像素以控制O(n*n_key)成本。h在两CT任务最优1e-3来自该实验，不能把它当MRI最优参数。本文已占位“软标签+Dice兼容”“校准教师蒸馏”“区域比例/校准改进”等大方向，不作为独立创新。

## 对项目的实际改变

新增对已认证608draw审计JSON的数值汇总（不读取新MR或GT，不新增前向）：强制前景fine-patch前景比例范围**0.0072479%–20.0832%**、中位数0.553417%；整batch最小0.003624%，中位数0.276709%。本轮固定001的forced crop1662/1048576=0.158501%，另一crop为0，所以整batch仅0.0792503%前景；“半patch强制前景”不是50%前景体素。

原审计forced-FG和whole-batch三尺度非0的结论仍成立。新增更窄计数：608个uniform crops中167个fine_GT>0，这些在half/quarter分别有11/17个GT归0；其余441个fine空crop保留，比例误差undefined不补0。coarse最近邻FG数乘2^3/4^3后，与同fine-crop体积的相对误差可达到−100%至+152.63%（half）、−100%至+95.12%（quarter）。这些是重复crop的离散误差，不是独立患者风险率、物理真体积测量或拟合失败因果证据。当前固定batch的forced前景在全部head仍非0，新增计数不证明这个batch因GT抹除失败。

因此准备两个**已有方法的能力对照**：充分更新预算及前景采样/权重；若以后实际发现coarse监督问题，再冻结体积守恒软GT与兼容Dice/CE，保留空patch。当前512实验保持原样；不以换loss或soft-GT包装发表点。

剩余问题仍需充分任务能力、同observed直接任务和强PCHIP之后的稳定可修正残余。八确认关闭，科学确认0，无已确认可发表claim。

来源：[原文缓存](source_cache/dice_followup_fulltexts_2026-10-07/)、[SVG获取状态](source_cache/dice_followup_fulltexts_2026-10-07/table_svg_acquisition_attempt01.json)、[监督密度结果](../experiments/mc_rc_3d_supervision_density_2026_10_07/attempt01.json)。
