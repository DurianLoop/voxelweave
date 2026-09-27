# full 前复核（2026-09-23）

**可以运行 wavelet3 seed3407 full；尚未启动 full。** 源码、协议、修复数据与检查结果的当前哈希全部一致。机器可读汇总见 `final_verification.json`。

## 数学与训练实现

- FP32 Haar 偶数/奇数尺寸重建最大误差 3.58e−7，能量误差在此次计算精度内为 0；递归 identity 核重建误差 4.77e−7。
- 非 identity 核的 impulse 响应在原 3×3 外有 263 个非零像素。这只验证新算子的空间支持，不是全网络感受野上限。
- 原 326 个 tensor 正确加载；零 gain 时与原 control 预测逐位一致，原参数梯度最大差 0；新增 gain 有非零梯度。
- 非零 gain 下 checkpoint=0/5 的梯度最大差 0，模型不读取 target。检查见 `checks.json`。
- 固定四个 train 区间、原完整 loss、96 步容量测试：J3 的 MSE 从 0.001982956 降至 0.001270790，下降 35.914%；MAE 0.0228601→0.0189879；gain 实际更新。J1 同样通过。仅验证可训练性，不据此选择 J 或宣称泛化，未保存容量权重。见 `capacity.json`。

## 真实 trainer 与成本

J3/J1 均通过 256×256、microbatch=2、checkpoint=5/10 的单 epoch trainer smoke。J3 峰值 **20.7045 GiB allocated /21.3906 GiB reserved**；额外保存两批样本的容量检查峰值 20.7315/21.4160 GiB。FULL 使用有效 batch16，通过累积获得，不提高 microbatch。

复制 smoke 目录后移走该副本的 completion，真实恢复入口成功加载 model、EMA、optimizer、scaler、RNG，重新完成评估；best/last 哈希及完成记录不变。此检查没有新优化步骤，**不是断点后继续优化的逐步等价实验**。

重新加载 smoke best 独立复算全部 8 项指标，最大差 0；正式报告入口拒绝 smoke。PowerShell 的 `full.ps1 -Preflight` 已实际运行，读取完整 train1356/val69 数据合同，没有创建 full 输出目录。

同设备、相同 forward-only/AMP 输入、10 warmup/30 repetitions：

| 项目 | 修复 control | J3 smoke best |
|---|---:|---:|
| 参数 | 992,179 | 992,819 |
| 中位 ms/缺失切片 | 47.8415 | 53.2589 |
| forward 峰值 GiB | 0.858745 | 0.858749 |
| 部分 Conv/Linear GFLOPs/三切片区间 | 446.590 | 449.562 |

延迟比 1.11324，显存比 1.000006，通过 <=1.5 的成本门槛。小波子带 functional convolution 已计入部分 FLOPs；Haar/FFT/逐元素操作未计入，所以不能称总 FLOPs。实测延迟和显存包含整个 forward。正式 full 后会对最终 best 自动重新测量。

## 比较与决策

修复 control 的 best epoch52 已重新评估全部 69 validation 区间，8 项均值与归档结果最大差 0，详见 `../../pastnet_series_integrity/results/full_reverification.json`。

J3 full 要求相对修复 control 至少 +0.10 dB，即 **25.667453 dB**，且患者 CI 下界>0、>=60% 患者胜出、困难四分位不退、全部质量/tail10 守卫与效率守卫通过。通过后才做 J1 full，要求 J3 相对 J1 至少 +0.03 dB及相同守卫；失败不续训、不改门槛。最后仍须匹配三 seeds 与锁定后的外部验证。

本次无 development test 或外部选型，无正式新模型效果或 SOTA 结论。旧代码、checkpoint 和论文测试表保持原状。具体命令见 [运行说明](../docs/运行指令.md)。
