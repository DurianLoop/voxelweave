# 新完整任务能力训练期间：TTA不确定性与采集增强原文核读

两篇原始 JATS 正文/floats 图注表格文字共185提取块实际读完：tta_uncertainty 0–90（91块），kspace_motion 0–93（94块）。嵌套正文/算法/公式有重复，不称185独立段落。没有查看原论文图像像素、单独补充材料、作者代码或独立复现作者实验。选择在新20k训练仍live、无新完整效果时确定，不改变训练配方。

## Aleatoric uncertainty estimation with test-time augmentation for medical image segmentation with convolutional neural networks

2019，Neurocomputing，DOI [10.1016/j.neucom.2019.01.103](https://doi.org/10.1016/j.neucom.2019.01.103)，[PMC6783308](https://pmc.ncbi.nlm.nih.gov/articles/PMC6783308/)。

核心不是仅对单次softmax计算entropy，而是对同模型的多次变换输入预测逆变换回同一空间，再以标签投票频率计算像素entropy；结构级不确定性用预测体积的变异系数VVC=std/mean。作者区分MC dropout模型不确定性与输入变换/噪声不确定性，并提供采集隐藏参数的Monte Carlo表述（块14–39）。空间逆变换/坐标一致性、边界和结构体积的uncertainty都有直接先例。本文主要建模可逆空间变换和噪声，块16将模糊/降采样留在当前建模之外；不能引用它作为本项目隔层缺失信息的完整后验或错误保证。

2D任务是60胎儿T2 SSFSE，40/4/16患者训练/验证/测试，原in-plane .63–1.58mm、3–6mm层厚，重采样in-plane 1mm；有三个采集视图。FCN/U-Net/P-Net各训练10k，flip、0–2π旋转、.8–1.2scale和高斯噪声均用于train/TTA；测试20次采样开始趋于平台（块49–58）。3D任务BraTS2017的285 studies，20验证、50测试、其余训练；T1/T1ce/T2/FLAIR四模态已注册/skull-stripped/1mm各向同性，20k训练，40次TTA/TTD，另有2.5D三视图W-Net集成（块65–72）。这些额外模态、三模型/视图与20/40倍推理预算不同于我们的单T2/单模型原生完整FOV，不直接用作者分数比较方法。

表1无训练增强U-Net baseline Dice90.26%，TTA91.64%；有训练增强baseline91.93%，TTA92.88%。表2 3D U-Net无训练增强baseline87.26%，TTA88.58%；有训练增强baseline88.43%，TTA89.41%（块89–90）。作者同时检查error与entropy、VVC与1−Dice的关系，并展示MC dropout可能在误分区过度自信（块53、60–61、71–72）。它是特定队列上的误差关联和预测改进，不是跨域患者级校准、缺层误差上界或统一临床安全保证。我们的模型没有训练dropout，不能临时加dropout就声称复现其TTD。

正文块69写“improvement is not significant (p-value <0.05)”前后矛盾；本记录保留该原文问题，不擅自改为>0.05，也不依此推导TTA+TTD的显著性。作者讨论N随应用而变，建议验证集平台选择（块77）；若本项目要加TTA，必须提前定义样本数/允许变换，并把额外前向预算与固定策略公平比较，不能照抄40次并称无需额外计算。

对应本项目：未来observable策略可把input perturbation disagreement作为候选特征，但必须在患者隔离的开发中检验它是否预测“修正带来的增益”，不能只证明其与分割错误相关。对增强变化敏感也可能是任务网络缺少方向/强度适应；应先完成当前能力评价。任何选择性修正不能宣称TTA/entropy本身首创，或把same-model多次预测当第二独立训练网络。

## A k-Space Model of Movement Artefacts: Application to Segmentation Augmentation and Artefact Removal

2020，IEEE TMI，DOI [10.1109/TMI.2020.2972547](https://doi.org/10.1109/TMI.2020.2972547)，[PMC7116018](https://pmc.ncbi.nlm.nih.gov/articles/PMC7116018/)。

作者从干净magnitude MR生成随机3D刚体运动，log-Euclidean累计/去均值，从原始图像分别重采样后做3D FFT，按采集时段拼接k-space，再逆FFT生成运动伪影（块7–15、16–39算法）。去均值旨在保留标签对应的大致位置；该模型不是本项目真实隔4层抽取，也不是完整层面PSF模型，不能借“k-space”名称就视为真实数据一致性约束。作者报约30秒CPU生成一个256³模拟体积，额外生成/存储与训练预算须计入。

模拟实验为272 ADNI MPRAGE，各15伪影体积；80/10/10 train/validation/test。HighRes3DNet、80³ patch、batch1、Dice、Adam1e-4；Gaussian-blurred GT前景加权采样，各模型训练至观察overfitting或100k。五配方clean/classical/25%/40%/50%motion augmentation，bias field增强默认开启（块41–46）。该终止/最优选择与我们固定20k最后权重不同；正文该段没有充分说明所有生成版本患者分配细则，本记录不补造与本项目同合同的隔离证明。

真实实验是106对经专家QC选择的MPRAGE test-retest：一张差一张干净，group-wise刚体配准，两输入的同算法分割相互比较，以clean-image分割为reference，而非逐例独立manual GT（块48–50）。因此高Dice首先说明test-retest预测一致性，不能等同于病灶真值准确率，更不是单T2原始薄层同平面来源。该数据还需权限，本轮不下载/请求患者数据。

直接end-to-end分割对运动伪影鲁棒性，以及先恢复图像再做分割之间的取舍已经在本文明确讨论（块5、57、68、80–81）。在真实伪影去除中，模型有时主要模糊图像、恢复不了丢失细节；真实MAE .00302→.00297、SSIM .98566→.98604，改善不显著。计算前剔除before-correction error最高分位且视觉确认错配的配对，最终98个，并用膨胀TIV mask评分（块66、93）；不引用其图像结果作全106患者结论或与本项目不筛除/完整FOV端点直接比较。

不确定性用训练dropout和100次前向，比较clean/artifact输出KLD。作者指出只训练clean/classical模型可“低std、高KLD”自信给出不同预测，motion augmentation改变这类行为（块53–55、68）。这不是同真实病灶标签的定量校准证明；caption块89写highKLD/highvariance，与正文的风险组合表述不一致，需回到实际原图/数据才能判断。本轮只读文字，不把其中一种写成独立已证事实。

局限包括缺少phase、magnitude模拟只是近似；重运动可能没有单一空间标签；参数受内存限制可能牺牲clean任务表现；真实运动不完全独立随机且未含非刚体，scanner/coil/trajectory等未完整建模（块74–78）。因此“物理真实增强一定最好”或“先去伪影总是损害任务”均过强。本文部分目标/边界指标中classical更好，也必须保留（块46、70）。

对应本项目：直接任务适应与图像预恢复的比较是必须做的强对照，不是新贡献；经过registered clean reference的输出一致性不能替代我们的native label/完整affine验证。若当前无增强训练内好但四验证失败，后续可单因子区分方向/强度/采集分辨率适应，不用它改动这轮正在运行的预算或提前开确认。

## 精确创新问题与准备

| 剩余候选 | 本文先例与缺口 | 本项目判据 |
|---|---|---|
| TTA disagreement选择修正区域 | TTA/entropy/VVC/error关联已有；没有检验我们同observed信息的“修正增益”目标 | 在患者隔离开发中预测实际action gain；对照随机、固定、同容量及无条件；计全部推理预算；无增益则停止 |
| 直接任务或采集增强胜过图像恢复 | 2020正文明确做过该方向，且不同目标/边界结论不统一 | 公平输入/统计/容量/监督/最后权重；不能用弱冻结评价器负差称新方法危害 |
| 适配后仍有可观测、可修复缺层病灶残余 | 当前两篇不回答精确合同，但其他近邻仍需一并核 | 当前37条件能力/111plane实现核验→native/6×5公平矩阵→冻结具体修正/八保留患者/第二任务网络；尚未验证 |

阅读原件与SHA：[获取记录](source_cache/no_augmentation_task_fulltexts_2026-10-03/attempt_01.json)、[逐块阅读登记](source_cache/no_augmentation_task_fulltexts_2026-10-03/reading_provenance.json)。当前科学确认0，暂无已独立确认可发表claim。
