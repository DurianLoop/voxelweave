# 联合动作、greedy与成本：三篇原文方法/主要结果核读

实际取得并核读三份作者预印本，成功PDF共86物理页，选定完整文本页29页；三个关键页已经Poppler渲染并实际view_image。并未完整通读60页理论稿全部证明，也未运行作者代码/复现作者实验。所有获取的reading=false历史保留，阅读另登记。此前错误1710.09336实际是数学逻辑论文Properly Ergodic Structures，排除，不计MRI论文或29页阅读；本地缺fitz导致首次提取exit1，之后用既有Poppler恢复。最初Europe PMC宽查询返回2771匹配、仅取5条，均不是目标论文，不拿它当系统综述。

## Gözcü等：Learning-Based Compressive MRI

[正确作者稿](https://arxiv.org/abs/1805.01266)，v1，2018-05-03，13物理页；正式DOI10.1109/TMI.2018.2832540只用来定位，不冒称核对过正式期刊版差异。核读完整物理页1、3–10，共9页，Algorithm1物理页5另实际视觉检查。

方法：`b=P_Omega Psi x+w`，固定decoder可以是任意非线性重建器；代表性fully-sampled训练数据上的目标性能eta可以是PSNR/SSIM。候选S允许整条horizontal/vertical读出线，不只单频率点。成本c(Omega)假设随集合包含单调，作者明确可用真正scan time，而不是只用样本数（p3–4）。Algorithm1每次真实重建Omega union S并评分，选择 `(eta(Omega union S)-eta(Omega))/(c(Omega union S)-c(Omega))`；这已经是联合收益/联合成本增量选择，不能被本项目宽泛首创。

理论边界：Proposition1是有界eta、独立同分布代表训练信号、有限可行mask族A下的uniform empirical-vs-population bound，依赖log|A|和m。它没有给任意decoder/任意性能目标的greedy全局(1-1/e)近似保证。不能把统计泛化保证写成优化最优保证，更不能把本项目11患者/多相关slice计成独立大量m。噪声Proposition2额外要求Gaussian同方差及对真值的Lipschitz条件，不能直接套到未知采集slice profile或病灶Dice。

主要实验：7健康T1扫描中实际用5人各20slice，2人/40slice训练、3人/60slice测试；不是60独立患者。另5人TOF，2训练/3测试。TableI 25%下TV/BP/BM3D/NN，各mask交叉decoder性能，匹配NN-greedy/NN PSNR36.36；这些是作者图像指标，不是本项目任务收益。TableIII部分匹配目标行没有最高分，原文p10明确提出有限训练数据/greedy次优的解释，不能简化成“匹配目标必定最优”。p6 NN与mask做交替训练至多三轮，每次7000epochs；本项目固定task模型/observed生成输入与其算法条件不同。

作者p8–9离线mask优化使用256 CPU nodes或40 GPU nodes，时间不可当本机预算；离线label/teacher生成也不能在本项目总预算里免费。本文改变实际Fourier采集子集；本项目已经观察到的层集合固定，修正动作只能使用observed信息，不能通过新采集/隐藏GT增强输入。

## Golovin/Krause：Adaptive Submodularity

[作者当前稿](https://arxiv.org/abs/1003.3967)，v5，2017-12-06，60物理页；首页注明原工作JAIR2011/COLT2010。核读完整物理页1、3–11、29、30、41，共13页；p6定义/可加成本另实际视觉检查。这不是2026新文，也不是核完全部定理证明。

p4–8设定：ground-set items状态由先验p(phi)产生，选择一个item后可看到其状态Phi(e)，条件边际收益在partial realization psi上取期望。Adaptive monotonicity要求条件边际>=0；adaptive submodularity要求增加已选item和反馈后任一未选item的条件边际不能增大。性质依赖分布，不由“用了greedy”或“神经网络连续”成立。p9还明确不直接覆盖选择item会改变底层realization的普通POMDP；MRI修正改变整幅模型输入，不应生硬等同作者的传感器故障反馈。

Theorem5的(1-1/e)类保证需要adaptive monotone/submodular和合格approximate greedy条件；Appendix15.1 p41成本为 `sum c(e)` 的modular item cost。窗口重算的`|union R_e|`属于coverage集合成本，通常不可加；不得直接套作者可加成本定理。真实病灶GT收益部署时不可观察，不能把开发GT评分当合法运行反馈psi。

Lazy evaluations p10–11依赖旧边际值能作为当前上界，即边际递减。没有证明或充分实测实际任务效益具有该性质时，不能缓存旧单动作收益并把lazy pruning称精确。经验上的有限集合检验也不会证明全部患者/动作自适应子模性。

主要实验p29–30：Gaussian空间场/已知噪声、条件独立观测和独立失败传感器；46温度传感器、357交通传感器。文中lazy速度收益约3.5–7和30–38，是该特定传感器任务，非MRI病灶或本机速度复现。可用作方法基线/假设检查先例，不能借其保证本项目。

## Sanchez等：Scalable Learning-Based Sampling Optimization for Compressive Dynamic MRI

[作者稿](https://arxiv.org/abs/1902.00386)，v5，2020-03-16，13物理页（主文及内附补充）；正式定位DOI10.1109/ICASSP40776.2020.9053345。完整核读物理页1–4、6–8，共7页；补充Table1/p8实际视觉检查，未完整读其余补充和引用页。

已知机制：随机候选phase-encode line minibatch与训练image minibatch、按frame轮流增加读出线，降低完整greedy的候选/训练样本评价量。主文k38、l1，补充成本表另l3；不能混成完全相同配方。每个candidate仍评分真实Omega union S，不是只加初始singleton收益。作者称方法灵感来自submodular优化，但正文p3自己承认问题lack of structure，未给任意MRIdecoder/metric统一子模保证。

Proposition1/2是在固定cardinality、无放回mask采样/经验目标中存在紧支持最优分布，可退化为确定mask的优化。它不证明greedy找到最优mask，也不证明个体按observed选择动作的策略不需学习。不能把其概率/确定性结论从一个population-fixed采集mask搬到每患者修正组合。

主要实验：7健康成人心脏cine，3volume训练/4测试；256²×25×34 coil经复杂coil组合后crop152²×17；retrospective undersampling，不是prospective病灶采集验证。fastMRI膝PD训练12649中心slice，验证2587slice是slice数量，不是患者数；无本项目CISS病灶Dice。补充p6–8还记4vocal scans、self-calibrated4coil设置、SSIM初始4低频phase encodes，2.5%时SSIM低分反例保留。

成本表：作者速度比按 `time_G*nprocs_G/(time_SG*nprocs_SG)`，是并行资源量而非单纯墙钟，部分G时间带星号为外推。本次由印出的四行time/nprocs机械复算与印出的Speedup数不全部相等；不推定差异原因、不当作者原始日志复核，也不据此重算其论文结论。它进一步提醒本项目需保存实际calls/tiles/wall/backend和候选/teacher成本，不能引用“近200倍”当本机预测。

## 对本项目的排重和剩余问题

这些原文进一步排除“首次联合增量收益/成本greedy”“首次MRI采样候选minibatch”“任意局部动作自动有子模保证”。本轮新增研究证据限单开发MRI合成干预的输出/成本结构，0真实病灶效益评分；精确Dice反例是解析/合成控制，不是患者收益发现。

下一步仍先等19series两个最终模型冻结与原完整56FOV资格。剩余可能研究的是：公平且充分适配后确有修正余量时，真实可部署候选的联合病灶收益是否可预测，并在同端到端预算下超过强PCHIP/同observed直接task/既有defer与真实union-greedy。要分别排除Dice分式耦合、二值threshold/动作支持碰撞、神经/后续数值耦合和成本并集；只有临床端点剩余交互可预测且带来独立收益时才推进方法claim。当前可发表claim未确认。

原文/获取/SHA：`source_cache/action_interaction_primary_2026-10-07/`；实测入口：`../experiments/probe_mc_rc_3d_action_composition_2026_10_07.py`；独立窗口与Dice控制：`../experiments/verify_action_composition_and_metric_control_2026_10_07.py`。
