# 全视野模型单开发系列、同预算损失能力诊断

启动依据：冻结20k模型的全部19开发输入已完成；独立计数、完整affine物理距离和57个完整plane重放通过。11患者先聚合full Dice .127947、missing Dice .130587、recall .207787、absRVE 12.445064；8/19系列TP=0，其中有非空假阳性预测，不能全部叫空预测。训练内和此前验证均低，尚不能用该网络判定重建创新。

仅固定开发患者VS-MC-RC-012的唯一合格系列（UID以已核开发清单绑定），随机初始化981,602参数GlobalLocalUNet。两臂依次执行：既有BCE+跨patch前景Dice；已核作者公式的binary asymmetric Unified Focal适配（weight .5、delta .6、gamma .5、epsilon 1e-7）。后一臂同时改变区域项、class/per-image归约和像素项，比较的是完整loss配方，不能将差异归因于单一focal因素或宣称新loss。soft area label为本项目适配，不叫原作者训练复现。

每臂固定4000 updates、seed20261004，同初始state、相同patient/series选择的RNG消耗（单患者/单系列）、相同training_example抽样和augmentation。沿用原architecture、physical resize/.5mm、5通道物理上下文、128patch、一个前景/一个全FOV采样、.5global辅助系数、AdamW wd=.0001和cosine .001→.0001，分母3999。每个真实update对完整输入/target/location生成按序SHA摘要；两臂所有4000个draw及累积hash必须逐项一致。权重与优化器各从头，不继承20k权重，不中途读取验证或调整预算。合成10步分别估时，任一平均>2秒或GPU初始化即停止保留attempt，不基于效果换病例或加步数。

输入只来自已核012 observed-only raw PCHIP/observed_shared；核包、原生输入、physical输入与监督mask SHA。隐藏MR不解码。绑定原20k失败诊断及独立复核、作者源码审计、CPU port scalar/24梯度与输入guards回执；任何已有记录/源码/checkpoint均不修改。

每臂仅保存最后checkpoint。完成4000步后才作012全部原生z/完整FOV预测；固定.5，无GT裁剪、真值侧别、最大成分或后处理。保留full/missing/anchors/tail计数、precision/recall、signed/absRVE、ASSD/HD95、empty/undefined以及完整coverage。另核原生label轴、bincount、独立surface和每臂首/中/末3个完整plane重放；不是第二独立任务网络或独立患者确认。

预写训练内fit gate沿用此前可拟合性诊断：full Dice≥.90、missing Dice≥.90、full recall≥.90、full absRVE≤.10。两臂全部报告，任一失败仍保留，不能在两个结果中选好者冒充对照。通过仅说明该病例可拟合，不能说明泛化/临床能力；失败亦不能证明重建无益。四验证患者始终是验证，八确认保持关闭。

CPU单线程、自身below-normal，磁盘≥15GB、可用内存≥8GB；两臂顺序运行，不并行第二重训练。新增输出限innovation/experiments/mc_rc_global_local_single_case_loss_cpu，exist_ok=False，<100MB。每100updates登记资源/曲线，非有限loss/梯度停止。实际session持续poll，失败以新attempt修复、不原地覆盖、不重启live任务。GPU/用户终端训练/locked IXI test不操作，科学确认0，goal active。
