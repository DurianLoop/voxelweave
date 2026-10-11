# 11开发患者无增强完整任务能力：固定20000更新

这是能力开发，不是新重建方法或确认实验。选择legacy_none基于已见单012完整病例拟合及尽量保持原20k前景采样合同；在因子最后一臂结果取得前写下这个下一实验配方。不开“挑四臂最优者”的隐含规则；完整四臂仍逐一保留。新训练必须等因子全部完成/独立核验、legacy_none原fit gate通过、19系列608draw/1216完整patch预检通过，才能启动。

患者固定001/002/004/005/006/007/009/010/011/012/013，共11人19系列；同人所有时点一角色。只读已核observed-only包的每4层观测，raw PCHIP + observed_shared统计，native监督标签和physical area target。没有完整隐藏MR训练输入。原稀疏输入、physical .5mm、5平面±2/±1/0mm上下文、256全局视野、128局部patch均沿用。

981602参数GlobalLocalUNet，seed20261004，初权重SHA需等于原20k模型的初权重（不加载其已训练权重）；BCE+两patch整体Dice+.5global，同AdamW wd=.0001、cosine .001→.0001/19999，20000步，最后checkpoint，不看验证改预算/阈值/checkpoint。不加预训练/ensemble/GT裁剪或后处理。

患者均匀、再患者内series均匀；原.5foreground-z/.5all-z及一个前景patch/一个全FOV随机patch外生随机数不改。每步保留冻结legacy增强primitive并在原空间逆映射patch，关闭整个几何+强度bundle。每次实际训练draw另用克隆rng运行旧training_example，核对结束rng状态和原增强example SHA；记录新/旧SHA与primitive SHA，20000项全部保留，可后续独立种子重放。不将随机stream一致误称处理输入相同。

资源守卫：CPU单线程/自身below-normal、磁盘≥15GB/内存≥8GB；首10真实updates平均≤2秒仅作资源预检，不按loss早停。非有限loss/梯度停止并保留失败attempt。只在前一真实训练任务已实际exit后启动，不并行两个新训练。训练每100步保存状态/历史/采样计数；目录<100MB。

训练期间验证模型前向0，确认效果0。新checkpoint冻结后先完整19开发FOV训练内诊断，再四验证020/022/025/024的9系列，raw PCHIP为主、raw linear为对照，完整原生网格/全部z/.5，无GT crop。开发诊断失败也保留全部结果；四验证是已用过的验证，绝不称独立确认。

沿用原能力门槛：四患者先各自series平均、再患者平均；raw PCHIP full Dice≥.70、missing Dice≥.65、full recall≥.70、full absRVE≤.50；四患者full/missing Dice均正，9系列无TP=0完全漏检。额外报告full/missing/anchors/tail、TP/FP/FN、precision/recall、signed/absRVE、full affine ASSD/HD95与空/undefined计数。不能将单患者fit≥.90门槛混成四验证门槛或事后降低原门槛。

后续每预测独立label/bincount/完整affine距离及首/中/末完整plane重放；训练20000draw/最后checkpoint/源SHA独立核验。原冻结20k的失败结果继续保留，本训练也可能失败，不能只报告高分。

八确认030/029/019/028/031/026/027/015保持效果关闭。只有能力充分后再具体实施native/6×5公平矩阵、直接任务/随机分辨率、observable缺层修正与第二任务网络/八患者确认。GPU、用户终端训练与locked IXI test不操作。科学确认0、goal active。
