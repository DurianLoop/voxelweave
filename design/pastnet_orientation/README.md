> **2026-09-22：本分支已完成并按门槛停止。** +0.094388dB未达到+0.10，HD95 proxy退化，质量守卫失败；不要重复下方历史full指令。详见[复核报告](results/full_review.md)。下一步 `design/pastnet_frame_context`。

# PAST-Net 方向泛化：单变量 full

2026-09-21：训练集机制诊断、8动作契约、真实反传、trainer smoke、恢复和指标复核、效率、正式脚本 preflight 全部通过。尚未启动 full。

上一轮官方 I3Net 在同输入、同 clean validation 下得到25.172132 dB，PAST control为25.562011 dB，配对优势+0.389879 dB；但初始化、优化目标和累计预算不同，不构成SOTA结论。完整结果在 [I3Net复核报告](../i3net_strict_reference/results/full_review.md)。

本轮检查出了新问题：全部112个训练series/111患者、固定z=4区间中，7个非恒等D4方向反变换后的MSE，相对原方向按患者平均增加73.89%；预测方向差异平方为原误差的80.11%。八方向平均反而降低约1.063 dB。这是训练集方向敏感性的证据，不是增强会改善泛化的证明，也不是输入信息上限。

**此次只验证随机D4训练增强。** 每个microbatch均匀选择一个90度旋转/翻转动作，对输入、目标及物理方向元数据一起变换。不增加参数，原loss、G086初始化、AdamW/warmup cosine/EMA与原80轮方案保持一致；validation和推理使用原方向单次forward。这是标准增强，不声称原创架构或严格方向等变模型。成功才为后续等变参数共享结构提供证据。

用户现在只运行：

```powershell
Set-Location D:\MRI
powershell -NoProfile -ExecutionPolicy Bypass -File .\design\pastnet_orientation\full.ps1 -Seed 3407
```

最多80轮，原min30/patience15。microbatch2×累积8、checkpoint前5/10 blocks；全部8动作实测峰值19.658 GiB allocated /20.330 GiB reserved，trainer smoke约19.64/20.36 GiB。无需再运行smoke，不建议并行另一个同卡full。

中断后在同一命令末尾加 `-Resume`。源码、协议、full.ps1将在full后冻结；请保留旧权重和运行目录。`ExecutionPolicy Bypass`仅作用于此次PowerShell进程。

晋级目标不是超过较低的I3Net，而是相对原PAST control提升至少0.10 dB，即当前seed至少25.662011 dB，并通过患者配对CI、胜率、困难四分位、质量、tail10和效率守卫。失败即停止，不调整增强集合或概率来挽救。通过后才补配对三seeds，锁定后再评估IXI/NingXia。

- [计算前协议与理论来源](PROTOCOL_ZH.md)
- [运行与产物](docs/运行指令.md)
- [full前核验](results/pre_full_review.md)
- [完整训练集诊断](results/probe.json)
- [最终核验记录](results/final_verification.json)
