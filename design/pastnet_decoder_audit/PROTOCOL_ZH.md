# 冻结解码器诊断（2026-09-15，计算前登记）

LACV E1 在 validation 上仅提高 .014654 dB，未达预设 .10 dB，已经停止。此诊断不重启该分支，不进行任何训练或 validation 选型。

固定读取同预算 control seed3407 的 best checkpoint，使用原 fastMRI train 全部 series 的 z%4=0 完整区间，原观测归一化、256²、三个缺失 phase。按 slice→series→patient 等权汇总。全部患者已经参与过网络训练，结果是训练内机制诊断，不是独立泛化估计。

## 固定测量

1. 捕获实际 mixed decoder 的主 residual、detail residual 和 dual correction，记录 tanh 后绝对值≥.95 的像素比例及这些位置承载的现有平方误差比例；记录两级 confidence 均值。不得用未混合的第一次 decoder 调用代替实际输出路径。
2. 固定两个 confidence，当前幅度包络为 coarse±[confidence×(1+.35)+.18×joint_confidence]。将真实 target 投影到这个逐像素区间，得到在此放松函数族下无法消除的 MSE；另报告 confidence 允许到1时的 coarse±1.53 包络。它们忽略共享参数、跨像素耦合和可预测性，是 target-assisted 的幅度限制诊断，不是可实现模型、Bayes 上限或性能预测。
3. 使用正交的离散 FFT 径向分区：低频 r<.10，中频 .10≤r<.28，高频 r≥.28（cycles/pixel）。与原网络重叠的平滑频带不同，此处仅用于 Parseval 可加的诊断，不改模型。记录误差能量，以及原损失各加权项对输出的梯度范数、相对 MSE 梯度的 cosine、总梯度的频带能量。
4. 梯度变量仅为正向 prediction；反向顺序预测、base prediction 保持当前 checkpoint 值并 detach。这是输出空间的偏导，不是整个网络参数梯度，不能据此声称存在参数优化冲突。原 objective 与分项和的数值、输出梯度必须核对。不得把频带梯度范数比例与误差能量比例相除后当成学习速率。

## 解释与停止规则

没有候选模型、参数更新、test 或 full 晋级。本轮不做 loss 系数扫描、输出校正或以 target 选频率边界。若固定 confidence 包络的 oracle MSE 不足当前 MSE 的1%，且饱和区域承载误差不足10%，不以“有界幅度饱和”作为下一次 full 的理由。即使超过，也只允许后续独立受控探针，不直接放宽 bounded residual。

频率能量/输出梯度分析只能定位现象。任何频率分解新模型仍必须先通过独立注册的训练内可学习性及患者分组检查，再做相同预算、单变量 validation 对照；本报告不能直接批准 full。所有旧源码、协议和 checkpoint 保持不变；本脚本与协议及来源哈希记录在新结果目录。
