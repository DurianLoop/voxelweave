> **2026-09-21：本轮 full 已完成。** I3Net 25.172132 dB，PAST control 25.562011 dB。详见[正式复核](results/full_review.md)。下方为原运行说明，不需重复本seed。下一步 `design/pastnet_orientation` 先做训练集机制检查。

# 官方 I3Net：同输入、同 validation 的独立参照

2026-09-17：实现、源码核对、真实 trainer smoke、恢复一致性、指标复算及 full preflight 均已完成，尚未启动 full。

soft-tail full 为 25.564924 dB，相对 control 仅 +0.002913 dB，未达到预设 +0.10 dB，按协议停止。已有结构与目标函数改动都没有取得足够增益；同时新交接审计指出部分历史 HAT/SMamba 结果不能作为其 strict-val 协议下的可信参照。下一轮先补齐官方 I3Net 在当前任务上的真实差距，避免围绕不清楚的比较目标继续追加模块。

本包采用 [官方 I3Net](https://github.com/eeeric-code/I3Net) 的完整 64 通道、16 个 I2Block、3 个 CrossViewBlock。两份模型源码与官方上游核对一致（仅换行符不同），副本保持原样。模型接收四个真实稀疏锚点，生成 13 个位置，仅监督和评估中央三个缺失层。没有借用额外 dense 输入或监督。

这是本地任务适配：使用当前 observed-sparse normalization、clean validation 23 患者和相同指标。**它从随机初始化开始，和继承 G086 权重的 PAST control 不构成同初始化、同累计训练预算的架构消融，也不是官方 IXI 数值复现。** 本轮不会产生 SOTA 结论。

现在只运行：

```powershell
Set-Location D:\MRI
powershell -NoProfile -ExecutionPolicy Bypass -File .\design\i3net_strict_reference\full.ps1 -Seed 3407
```

此处 `ExecutionPolicy Bypass` 仅作用于本次脚本进程，不修改系统设置；当前终端直接执行 ps1 曾被执行策略拦截，上述入口已通过实际 preflight。

固定最大 300 轮，至少 100 轮后启用 40 轮 patience；Adam、原生中央三层 L1、15 轮 warmup 后 cosine、无 EMA。microbatch 8 × 累积 2，有效 batch 16，重计算前 2/8 组。真实 trainer 峰值 **18.755 GiB allocated（约 20.14 GB）/19.693 GiB reserved**，满足 24 GB 卡的余量要求。1/8 组重计算可达到 21.245 GiB，但仅带来约 4% 微步吞吐改善，本次选 2/8 组。

full 完成会自动测量推理效率，产物在 `runs/full_i3net_seed3407_vram20`。中断恢复在原命令末尾加 `-Resume`。请勿在训练期间修改本包 Python、vendor/reference、协议或 full.ps1；恢复会核对源码、数据、训练与执行配置。

- [预登记协议](PROTOCOL_ZH.md)
- [运行、恢复与完成后的复核](docs/运行指令.md)
- [full 前检查记录](results/pre_full_review.md)
- [soft-tail 停止报告](../pastnet_softtail/results/soft_tail_full_review.md)

smoke 仅验证实现，不用于选择模型或预估最终质量。只有本地 validation 参照完成后，才决定下一项主要变量；不在本轮补其它 seeds 或启动 IXI/NingXia。
