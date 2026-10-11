# 512更新失败的解释及下一步隔离诊断

两臂均未通过原拟合门槛。全训练FOV的低Dice主要伴随过多误报；native也失败，不能将native-PCHIP差异作为恢复损害病灶的确认。只有001开发系列、两个固定crop，且训练crop主head也未达到0.9，因此当前既有训练拟合不足，也可能有采样覆盖/推断context差异。不能只归因其中一种。

独立功能网络重放两臂各1,966,080个native体素；最大概率误差分别5.96046448e-7和6.55651093e-7，阈值预测0差异。1024条历史/LR、batch、source、checkpoint、四个域及gate核对通过。此为独立实现核验，不是第二个独立训练任务网络。

四种预冻结crop变体都报告，主head foreground hard-Dice变化不足0.00022。去掉这组flip/intensity增强没有将训练crop救过原门槛；这不能推断其他增强配方都无效。

| 原训练增强/输出 | native soft Dice | PCHIP soft Dice | native背景平均概率 | PCHIP背景平均概率 |
|---|---:|---:|---:|---:|
| 主head | 0.0116103 | 0.0115151 | 0.1304028 | 0.1298025 |
| 半尺度 | 0.0796281 | 0.0789981 | 0.0184907 | 0.0185445 |
| 四分之一尺度 | 0.9398015 | 0.9470474 | 0.00009967 | 0.00008630 |

主head硬预测已能区分部分目标，但大量低于0.5的背景概率仍进入soft Dice分母。背景平均概率约0.13不等于13%体素是假阳性；soft Dice与hard Dice不是同一端点。最粗head已较好拟合同一训练批，主head仍不足；此尺度差异是局部诊断证据，不证明深监督梯度冲突、InstanceNorm导致失败或模型容量不够。

全部24个head/变体的闭式BCE梯度与autograd最大误差为0，Dice最大误差2.32830644e-10。输出logit上，BCE与Dice对hard前景均推高、对hard背景均压低；本诊断未发现这两个项的逐logit符号冲突。参数共享、路径Jacobian及多head之间的参数梯度仍未测量，因此不能升级为无优化冲突的证明。

下一项可执行能力诊断：保留这两份最后checkpoint，固定骨干与同一批特征，在新协议下分别只拟合主head偏置或主head17个参数，使用固定阈值0.5、固定步数和最后权重，检查输出层是否有足够分离能力；若训练crop改善还需完整FOV和充分训练检验。它是优化/表征能力对照，不是新MRI恢复方法，也不能替代19series充分适配或四验证能力门槛。

内部统计路径候选仍待查新和独立实验：以部署可见PCHIP的特征统计作为归一化参照，分离candidate内容与归一化反馈。现有弱checkpoint只允许开发诊断；没有合格任务网络时不做已见验证/八确认科学效果试验。

图的原版本保留。新增v2把absRVE与0–1端点分别作图，避免absRVE=5.617压缩Dice刻度；没有改数值/门槛。

来源：[完整结果](MC_RC_3D_CPU_FIXED_FIT_RESULT_2026-10-07.md)、[新图](figures/mc_rc_3d_cpu_fixed_fit_2026_10_07/fixed_fit_results_v2.png)、[四变体完整计数和梯度](experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json)、[候选创新与停止条件](INNOVATION_CANDIDATES_AFTER_3D_LOSS_READING_2026-10-07.md)。
