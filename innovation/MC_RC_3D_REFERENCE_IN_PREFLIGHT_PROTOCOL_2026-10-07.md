# PCHIP参照内部IN统计：实现资格预检

本项在执行前冻结，目的仅实现核验/准备未来机制诊断，不验证分割或恢复增益。采用001开发系列原raw_PCHIP最后512checkpoint（未通过任务能力门槛）；不切换到新head分支挑选有利输出。

双流定义：reference分支按原InstanceNorm逐层运行；candidate分支在每层pre-IN卷积特征a处执行`gamma*(a-mu(reference))/sqrt(var(reference)+1e-5)+beta`，mu/var按该样本、该channel空间D,H,W计算、population variance。reference逐层独立按原流程传播；不从candidate重新计算参照。14处IN全部固定，并保持conv/skip/pool/affine/activation/head权重。与AdaIN的candidate自身标准化后施加style统计明确不同，不主张新颖性。

资格控制：seed20261007、标准正态synthetic batch2×16³以及batch1×32³；每项在candidate=reference时，三个head概率与原functional实现最大绝对误差<=3e-6且0.5预测0差异。再用001只由observed NPZ生成的PCHIP首个完整tile（起点0,0,0）作同输入自重放。tile位置不使用GT。

再从同observed生成raw_linear，输入z-score完全共享observed统计；重建native lattice中两者anchors逐值一致。只对首tile比较ordinary linear与PCHIP参照统计linear的输出差异，记录全部head与14层统计差异。没有任何GT、native隐藏缺层像素读取，没有Dice/收益评价、阈值挑选或候选策略选择。physical resampling会混合邻层，不能将native anchors一致解释为物理grid对应位置/任务预测必然一致。

自重放须先成功再运行不同输入。输出差异仅说明这个实现控制产生了不同输出，不证明统计污染致害、修正有效或机制因果量可加。后续科学效果需合格checkpoint、全部患者/四域、同预算及第二独立训练网络，本项不可代替。

CPU单线程、自身below-normal、RAM/磁盘各8GBreserve、<=360秒、不初始化CUDA。禁止NIfTI load和原MR ZIP读取以证明运行路径只使用observed NPZ；验证/八确认继续关闭。新输出只JSON（不存MR/GT/概率体积），<=2MB，任何失败原样保留。

先例：[三篇原始论文核读](literature/2026-10-07_feature_normalization_primary_reading.md)、[候选边界](INNOVATION_CANDIDATES_AFTER_3D_LOSS_READING_2026-10-07.md)。
