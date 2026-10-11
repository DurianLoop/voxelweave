# 联合MRI重建与分割：原文核读、碰撞与局限

新增两篇独立原文：SegNetMRI 1805.02165v1、Joint Calibrationless Reconstruction and Segmentation of Parallel MRI 2105.09220v1。完整文字页分别1–6和1–9，合计15个物理页；实际查看10个不同物理页渲染图。下载/提取18页不等于完整读18页；SegNetMRI7–8、calibrationless10参考文献/结论尾段未完整核读。没有读作者代码、补充文件或复现网络。索引9记录去重8题名摘要，SERANet缩写仍未命中；19总命中只返回首8，非系统综述。

## SegNetMRI

Liyan Sun、Zhiwen Fan、Yue Huang、Xinghao Ding、John Paisley，[arXiv1805.02165v1](https://arxiv.org/abs/1805.02165v1)，2018-05-06。核读[8页作者PDF](primary_attempt01/segnetmri.pdf)，SHA df04eafceaab5264a8d8811be667f46f897c4984b4ca273fefe99700707c4389。完整文字1–6；视觉1/3/4/5/6。后文calibrationless引用将其列为IPMI2019，但本轮未下载或核对那个最终版；不把v1自动等同最终发表内容。

方法p3–4：MRN为N个encoder-decoder+Fourier data-fidelity级联，MSN分割网使用同类encoder-decoder；先分别预训练，再保留MSN decoder、接入各MRN encoder，共享重建encoder，N个分割结果经1×1卷积融合，全部联合微调。损失L_MRN+λL_OMSN，λ=.01；L_OMSN是merged及各block分割CE的N+1项均值。这直接覆盖共享表示、多深度分割融合、深监督、重建+分割联合损失和预训练后任务适配，不能作为本项目的新模块概念。

观测p2–3是人工20% Cartesian k-space采样及Fourier DF，不是本项目z方向每四层的固定CISS真实plane合同。p5采用MRBrainS的T1、240²、五个datasets，四train/192slices，一个test/48slices，三组织GM/WM/CSF的manual labels。所读正文没有明确独立患者ID清单；不把192/48当患者，不补造多中心病灶确认。

训练p4：MSN60,000次、16个64²patch/次；MRN30,000次、4个整图/次；联合再8,000次、4整图/次，Adam初始lr.0005、1080Ti11GB。三种训练unit不同，不把98,000次加总换成等量整病例曝光或完整训练费用。MSN预训练只看fully-sampled图。MRN5+MSN明确no fine-tuning；Liu对照只微调重建部分、分割部分固定，均不是每个输入独立充分适配的最终任务路径。已读正文没有总容量或额外训练量逐项匹配证明。

p5–6原表实际视觉核+Decimal [CPU复核](table_audit_attempt01/receipt.json)：SegNetMRI5相对MRN5+MSN，GM/WM/CSF Dice提高7.02/15.73/.80个百分点；相对只微调恢复器的Liu，2.97/3.44/1.42个百分点。不是“相对充分适配的强任务网15.73点”。PSNR相对MRN5+.33dB，相对Liu+.80dB；它們是不同分母。FS+MSN是使用full image的经验参照，manual label才是seg真值；正文所称upper bound不构成所有任务模型的数学性能上界。

保留字面范围问题：p5的测试48slices，而Table2及p6正文写37 test MRI。两处已视觉确认；不自行解释为剔除负slice、37患者或勘误。训练硬件、block变多较慢不等于完整患者deploy latency；本文未提供本项目全部九阶段费用或病灶缺层端点。Table1 HD是95th percentile，不换成本项目已冻结的其他boundary定义。未取患者配对值/CI，不独立建立显著性。

## Joint Calibrationless Reconstruction and Segmentation of Parallel MRI

Aniket Pramanik、Xiaodong Wu、Mathews Jacob，[arXiv2105.09220v1](https://arxiv.org/abs/2105.09220v1)，2021-05-19。[10页PDF](primary_attempt01/calibrationless.pdf)，SHA 8a34ce19f51fef69ee3db58f427e796517b79bcc3f8d7407c88e2bc8f641b889。完整文字1–9，视觉1/5/6/8/9。页眉TMI2020/XX/XXXX是模板内容，不能作为本轮已核发表日期/卷期。第10页结论尾段与引用未完整读。

观测p2–5为真实CCP raw12coil T1 GRE，117subjects来源中的40train/7validation/15test子集，GE3T，slice thickness1mm。六/八倍retrospective variable-density Cartesian k-space；2D Fourier，文中的“3D volume”在p2/p3许多公式是两维空间+coil channel堆叠，不等同本项目完整3D z上下文网络。其本轮分割任务只CSF/GM/WM，没有肿瘤标签。CCP无手工seg真值，所有reference segmentation由FAST在full image生成，作者明确这是技术可行性演示；Dice是对伪标签，不直接支持真实病灶医学效应。

方法p3–6：IDSLR以U-Net替代空间局部低秩/annihilation投影，reconstruction与DC交替5次，权重跨迭代共享；最后迭代encoder接单个seg decoder，训练L=(1−α)Lrec+αLseg。sixfold α=1e−4、eightfold1e−6，不能从同一名称推断loss各自数值尺度一致。所有迭代DL对照均K=5，Cascade joint明确共同训练且匹配learnable parameter数量（p6），这是实质强控制；正文没给精确参数数值/完整费用，本轮没有代码复核匹配。

p5训练“1000 epochs”，同时写每epoch一次只用一个subject的数据，不把它当40patients的1000完整遍或40,000患者曝光。Adamlr1e−4、Xavier；任务标签4/40的few-shot仍对全部40subjects使用**有fully-sampled重建真值的监督MSE**。它减少的是seg标注覆盖，不是总MRI使用量、全部监督或训练计算降到10%。4个subject具体选择、多subset重复/不确定性在所读正文未明确，不据均值声称4患者已足够任意病灶任务。

p8表II相对full-image-trained frozen SEG，shared joint的Dice六fold增量CSF/GM/WM=.055/.090/.057，八fold=.063/.077/.086。表III相对匹配容量且joint-trained的Cascade，六fold变成−.002/+.003/+.007，八fold+.006/+.008/−.004：六个相关端点4正2负；不是六个独立患者或显著性证据。SNR六fold+.01dB、八fold−.03dB。该结果明确约束“共享encoder/联合网络一定胜过强适配级联”的泛称；也不能由其中负值判定整个作者研究失败。

few-shot shared相对fully-labelled，六fold Dice−.013/−.013/−.003，八fold−.006/−.009/−.003；相对few-shot Cascade则全六指标更高。这支持该伪标签、数据、结构下有限seg监督的经验结果，不可直接迁移为本项目4患者/确认4组的预算规则。表III按15subjects均值；未提供本轮可用逐患者值/CI，不重算p值。SNR是20log10(||xref||/||error||)，不是PSNR，不与前篇dB直接合并。正文orders of magnitude faster描述未给完整本机费用，不能外推部署加速比。

p7图5图注将(d)/(e)写成few-shot，与panel(d)/(f)图像标签不一致；本轮完整读到图注字面，但未视觉核第7页，故仅记文本范围疑点，不作为视觉确认勘误。p9“lower Dice scores”措辞与表中较高Dice优越方向不符，已实际查看第9页；不猜代码loss/指标符号、不推翻结果，比较使用表III的明确数值及表头。

## 对项目的决策

两篇继续排除“联合MRI重建/分割、共享编码器、深监督、重建任务辅助低标注、先预训练后共同适配”本身是新机制。直接任务表示和充分适配矩阵已有Adler/TACKLE等先例；新文支持更强控制而不生成MRI收益。不能仅改成CISS、增加分割loss就声称原创。

窄候选仍是：固定真实观测、强且充分适配的任务模型下，合法缺层修正是否仍留下可重复的完整患者病灶余量；存在余量后，可见状态能否在全部实测费用下选择动作并超过最强静态/条件cost/defer/DC等已有控制。若充分适配后差异消失，记录训练失配解释及负结果；不换端点或开启未见患者来救假设。

新准备 [监督曝光与joint控制](SUPERVISION_EXPOSURE_AND_JOINT_CONTROL_PREPARATION.md)用于后续预算/方法设计，不改当前训练配方、不在原final与资源资格前启动新的医学任务。只有资源实测和预先冻结预算才能实现/资格化正式医学长runner；本轮没有完成这部分，没有读取MRI数组或确认患者。

