# 训练集解码器诊断：幅度饱和不是当前主要证据

后续进展：文中提出的[成熟latent分频读出对照](../pastnet_latent_readout/REPORT_ZH.md)现已完成并停止；下文保留本轮诊断产生时的解释边界。

2026-09-15 完成。冻结同预算control best，在112个train series、111名患者、340个真实稀疏区间（1,020个缺失层）测量；没有参数更新、validation选择或test使用。所有汇总先按slice、series、patient逐级等权。该训练集见过历史网络训练，不能用作独立泛化证据。

## 实测结果

| 诊断量 | 结果 |
|---|---:|
| 当前患者等权MSE | .002232158 |
| 主 residual tanh饱和像素（绝对值≥.95） | 0% |
| detail residual饱和像素 | 1.8665% |
| dual correction饱和像素 | 0% |
| 上述饱和位置承载的平方误差 | 1.4480% |
| 固定confidence幅度包络的oracle MSE / 当前MSE | .09646% |
| confidence允许到1时的幅度包络oracle MSE | 0 |

实际模型为 coarse + confidence×(residual+.35×detail) + .18×joint_confidence×dual。固定confidence后允许各有界项逐像素任意取值，其可达区间仍几乎覆盖target；结合实际饱和位置仅承载1.45%误差，本轮不支持以“tanh幅度限制是主要瓶颈”为由放宽bounded residual或启动full。

这些oracle允许target决定逐像素输出，忽略共享参数、图像耦合和输入可预测性。包络可覆盖target不意味着网络能从稀疏输入推断它，也不能排除小confidence带来的优化衰减。平均confidence为.17817，joint confidence为.55141；这里没有检验它们的参数空间学习动力学。

## 频带与原损失输出梯度

频率以cycles/pixel计，用不重叠FFT径向分区，能量遵循Parseval可加性。它不同于模型内部的平滑重叠频带，不能直接与旧审计的频带百分比对齐。

| 频带 | 当前误差能量 | 原总loss输出梯度能量 | 总输出梯度与MSE输出梯度cosine（逐患者均值） |
|---|---:|---:|---:|
| 低频 r<.10 | 51.13% | 32.77% | .82176 |
| 中频 .10≤r<.28 | 40.10% | 33.81% | .69744 |
| 高频 r≥.28 | 8.78% | 33.43% | .44581 |

低中频承载91.22%误差。总输出梯度在三个频带均与MSE方向正相关；没有出现某一频带总方向反转的均值证据。Charbonnier输出梯度RMS为4.357e-6，加权MSE为1.636e-7，tail为8.671e-7；这不能被解读为MSE权重应按倍数放大。损失对误差大小的响应本就不同，输出梯度也没有乘以网络Jacobian，梯度能量占比不是学习速度。

symmetry的反向预测与base_guard的参考输出在此诊断中固定，只求正向prediction的偏导。原损失数值及此偏导与直接调用原objective核验一致；结论不扩展到两次forward共同产生的参数梯度。

## 对下一步的约束

停止LACV，不把其checkpoint用作新分支起点。保留有界残差，不根据本报告直接改loss权重或追加FFT。

值得下一轮独立检验的具体假设是：**同一成熟MA3混合latent中，是否存在共享标量解码头没有读出的、可跨患者预测的低中频残差信号？** 应先冻结control，从相同latent比较共享读出与频带独立读出，保持输入、损失与训练预算不变，先做训练患者分组的低成本检查。若相同信息不能带来满足MAE不退的实质增益，就停止频率解码假设，不把本表91.22%的残差能量当成可学习收益。

这是后续待检验假设，本轮没有实现或训练这一新候选，当前没有full晋级。此前线性图像残差探针及MAE约束探针的失败继续有效；更换到latent读出必须独立登记，不能挑选本报告target辅助结果作为部署规则。

## 核验与产物

smoke通过；全量诊断约121秒，峰值显存.928 GiB。没有训练反传，无需占满20 GiB。核验包括实际mixed decoder调用、AMP输出重建容差、频带重建与Parseval、原loss分项和及输出梯度一致性、来源哈希。旧模型代码及checkpoint未修改。

- [原始汇总](results/v1/summary.json)
- [逐slice数据](results/v1/per_slice.csv)
- [逐patient数据](results/v1/per_patient.csv)
- [预登记协议](PROTOCOL_ZH.md)
- [诊断实现](run.py)

复现命令（助手已执行，用户无需运行）：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH='D:\MRI\design;D:\MRI'
& D:\conda\envs\MRI\python.exe -B -m pastnet_decoder_audit.run --smoke
& D:\conda\envs\MRI\python.exe -B -m pastnet_decoder_audit.run
```

结果已存在时入口拒绝覆盖。完整运行是只读诊断，不是full训练。
