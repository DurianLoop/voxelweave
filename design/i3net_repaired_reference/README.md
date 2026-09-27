# I3Net 修复数据版：完整调度的强基线检查

**2026-09-26 修复入口更新：请改用 [AMP恢复脚本](../i3net_amp_recovery/README.md)。** 已从用户终端读取并在副本复现epoch237第52次更新的非有限梯度裁剪错误；原GradScaler尚未跳过溢出，严格裁剪就提前退出。独立恢复入口保留原源码/manifest，并单独记录数值修复与实际跳过的更新。原来的`full.ps1 -Resume`会重复遇到该错误，不再作为当前续跑命令。

**2026-09-25 状态核验：full 在第236/300轮后中断，尚未完成。** 没有 `completion.json` 或最终 `efficiency.json`，检查时GPU空闲且无Python训练进程。最后checkpoint、优化器状态、history、源码/数据/配方哈希均核验通过；从第237轮恢复，还剩64轮，按最近30轮中位耗时约需3.74小时。当前best为epoch41的25.144267dB，仅为未完成运行的中间记录。中断原因无现有日志可确认，不能当作正常早停或最终结果。用户应执行下方原命令并加 **`-Resume`**，不要重新训练。核验见 `results/resume_audit_20260925.json`。

本轮用于补强比较依据，**不是新 PAST-Net 模型或 SOTA 结果**。小波主干只提升 +0.01755 dB，按协议停止；新双锚点对应机制的真实样本容量检查也失败，未进入 full。

**实现、完整模型检查、真实两轮smoke、实际断点续训等价性、指标复算和正式入口preflight均已通过。** 检查汇总见 `results/final_verification.json`。

旧官方 I3Net 本地参照只执行到100轮，学习率仍为2.4495e−4，未走到原cosine的低学习率阶段；并且使用修复前数据。本独立包保留官方完整64通道/16 I2Block/3 CrossViewBlock，使用修复数据，从随机初始化**完整执行固定300轮调度**。保持原Adam、中央三层L1、无EMA，不调参、不从旧checkpoint续训。

与修复PAST control比较时，训练数据、真实输入、validation和指标一致，但PAST继承G086、I3Net随机初始化，目标函数与累计预算也不同，仍只能称为描述性本地参照。完成300轮也不自动证明最优收敛；将检查最后30轮增长。

执行设置：microbatch8×累积2，有效batch16，重计算2/8组。约18.8GiB allocated（约20.2GB），保留24GB显卡余量。full结束自动生成效率指标；只用23患者validation保存best，不读test或外部数据。

```powershell
Set-Location D:\MRI
powershell -NoProfile -ExecutionPolicy Bypass -File .\design\i3net_repaired_reference\full.ps1 -Seed 3407
```

中断加 `-Resume`。完整300轮不早停；按旧同架构的实测每轮约216秒粗估约18小时，实际受IO和设备状态影响。尚未启动full。

- [计算前协议](PROTOCOL_ZH.md)
- [运行与恢复](docs/运行指令.md)
- [full前核验](results/pre_full_review.md)
- [小波主干停止证据](../pastnet_wavelet_trunk/results/full_review.md)
- [双锚点对应容量失败](../pastnet_bilateral_transport/README.md)

旧Python/vendor/reference、原始数据、checkpoint与论文test表均保留。这个full无论优劣都保留，不按得分删除强对照，也不把validation分数写入旧test表。正式新模型最终仍需要三seeds与锁定后的IXI/NingXia验证。
