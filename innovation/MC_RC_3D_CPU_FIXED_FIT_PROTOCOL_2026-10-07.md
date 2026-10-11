# CPU 同尺寸两臂实际拟合：额外诊断，不替代 GPU 资格

目标继续为可发表且独立确认的MRI claim；本实验是必要任务能力诊断，成功不等于目标达成。上一轮为有进展：全28原生来源/坐标/输入认证、两次真实尺寸CPU更新、两篇全文阅读与归档完成。本轮最新GPU totals为1394MiB空闲、util82%，原GPU拟合入口的8GB启动条件仍不满足，因此不再运行一个已知会延后的GPUattempt。

新CPU实验与原GPU拟合的样本/两输入/架构/统计/监督/初始seed/固定patch/增强primitive/512更新/AdamW cosine/最后checkpoint/完整FOV/阈值均保持一致。第一固定开发系列为 VS-MC-RC-001 / 1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177。真实完整MR仅native reference分支，rawPCHIP仅observed package。只此一个开发series被训练/评分，无验证/确认效果读取。两CPU臂可作训练内描述比较，不拿旧GPU结果作同设备控制。

CPU只一线程、自身below-normal、RAM>=8GB、磁盘保留>=8GB、新增保存<=250MB，不查询/控制用户PID，不更改终端/根环境。沿用上一阶段有限存储合同，MR/physical体积不落盘复制。上一轮同尺寸CPU一步native/PCHIP分别4.496/3.642秒，1024步投影约4167秒，解释新CPU投影上限7200秒与总runtime上限9000秒；此是更慢设备下的新合同，不改变原GPU3600秒门槛或旧失败记录。前32实际更新重新测量，超过7200投影即记录失败停止自己的运行。每16更新检查资源并写进度；不以loss或Dice触发早停/选最优。

每臂冻结512实际更新，保留checkpoint与512 loss历史、实际batch SHA、primitive、初始/最终weights SHA、输入/标签/代码/协议来源SHA。所有训练都在CPU，CUDA不得初始化。patch前景Dice>=.90；完整该训练series Dice>=.90、recall>=.90、absRVE<=.25、TP>0；与原GPU拟合检查一致，失败也完整记录。所有full/anchors/missing/tail端点，空/undefined均保留。两臂checkpoint训练完成后再统一fullFOV评分，避免第一个评分类提前影响第二臂。

独立实现核验应重建相同batch/权重、检查全部训练历史与LR、重放完整FOV及全域计数；这只能验证实现，不作为第二独立训练任务网络的科学证据。完整FOV训练内失败意味着该固定patch诊断没有证明任务能力，不能变成“SR损害病灶”的claim。

下一阶段仍需更多19系列充分训练和原四验证全gate，标准化强baseline/同observed直接任务与resolution-randomization，公平native/6×5矩阵，最终冻结后八确认和第二独立网络。GPU本体显存/数值/速度资格只有真实GPU运行才能证明，CPU试验不会自动通过它。
