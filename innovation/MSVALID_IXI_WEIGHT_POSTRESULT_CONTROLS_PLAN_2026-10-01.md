# MSValid IXI 权重对：共同缩放与反向相位（结果后探索）

制定时间：已看到同一 84 名 MSValid 患者上的 fastMRI/IXI 两对权重主结果及 ReMIND 的 IXI 权重对主结果。此计划用于使“只用公开训练来源”路线的两个患者来源有**同模型对**敏感性，而非创造新独立队列或新事前检验。ReMIND 同类结果即使先打开，也不改本方案；全部 84 人及固定 479 目标完整报告。

输入固定为[IXI 权重 MSValid 次级协议](MSVALID_IXI_WEIGHTS_SECONDARY_PROTOCOL_2026-10-01.md)中的 84 人、`literature/msvalid_geometry_qualification.json` 的全部 residue 1/3 合格目标、原提取 NIfTI 的 SHA-256 清单和相同 IXI HAT/SwinIR checkpoint。不得读取锁定 IXI test 或调用 GPU。CPU float32、两条 torch 线程、模型原 256x256 条件接口。两相位所有真实发布层锚点计算一个并集 min/max；各相位只把自己的图像送给模型。前向固定 HAT0，SwinIR0 共享与 SwinIR2 不相交，评分支撑来自 phase-0 最近真锚点。反向固定 HAT2，SwinIR2 共享与 SwinIR0 不相交，支撑来自 phase-2 最近真锚点。两方向预测同一固定目标；目标像素不参与输入缩放、mask 或病例筛选。

每目标 `O=mean((a-b)^2)/(4T)`、`T=(MSE(a,y)+MSE(b,y))/2`，记录两方向共享/不相交 `O`、差、伙伴/参考 MAE/MSE、支撑像素。每患者先在 residue 1/3 内平均，再双 residue 等权，之后患者等权。两方向同一患者 bootstrap 抽样 5,000 次、种子 `20261005`，分别报告区间、正负患者和与原 IXI 权重结果的前向配对差。把前向共同缩放主差仍为正、区间下界 >0 且至少保留原效果一半作为**探索性**的“独立 min/max 非唯一解释”门槛；反向结果按方向完整报告，不用另找替代模型。

共同缩放让共享组获得不相交组锚点的两个极值，因此只是机制敏感性，不是可部署单条件输入。反向仍改变全部邻层图像内容和 signed geometry。两个来源同向也不能估计疾病因果差异、独立原始采集身份或临床可靠性；本试验保持结果后探索标签。输出路径固定 `innovation/experiments/msvalid_ixi_weight_postresult_controls/`，拒绝覆盖；保存方案/脚本/源/权重哈希、逐目标及逐患者结果、全部失败与只读复算。
