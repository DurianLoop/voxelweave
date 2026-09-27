# QGCR：查询条件全图真实锚点对应

**2026-09-16：E1 full完成，分支停止。** 79轮早停，best epoch64，validation25.571022 dB；相对control+.009011，低于注册+.10门槛。其余统计、质量和效率guards通过，但不进入local、额外seeds或外部测试。[完整复核](results/global_full_review.md)

QGCR让coarse中的每个query位置按内容读取每张真实锚点的整幅1/8特征图，保留四个锚点的匹配差，再读入原MA3主干。它扩大可访问的空间对应范围，没有增加采集图像。原linear coarse、有界残差、四锚点、宽MA3、multi-scale latent、dual-domain及优化recipe保留。

已完成的E1命令（留档，不重复执行）：

```powershell
Set-Location D:\MRI
.\design\pastnet_v2_globalmatch\full.ps1 -Variant global -Seed 3407
```

microbatch2×累积8，checkpoint前5/10 blocks，80轮上限与原早停。full实际训练峰值20.6409 GiB allocated /20.7598 GiB reserved，循环14.2042小时；forward49.2723ms/缺失层。已按原协议停止，不自动启动local或额外seeds。后续独立目标函数研究位于[softtail](../pastnet_softtail/README.md)，不使用本分支权重。

能力检查：冻结G086，仅新增路径96步，在注册的4个训练区间上MSE由.00293196降到.00248277（下降15.32%），MAE由.0246709降到.0226973。权重未保存，full从原G086重新开始。该检查只证明可学习性，不能预测泛化收益。

模型1,048,019参数，新增55,840。global/local形状与初始化完全相同，唯一差别是local的候选位置3×3 mask。forward实测global49.319ms/缺失层、local48.956ms；global相对control时间1.0341倍、显存1.0140倍。部分Conv/Linear与SDPA QK/AV计算量均448.643 GFLOPs/三层区间，不是全部算子FLOPs。

E1需相对同预算control至少+.10 dB及统计、质量、效率guards；本seed即validation≥25.662011。只有通过才跑同容量local；global对local还需+.05 dB及同套guards。任一失败停止。通过后补齐三seed，锁定后才测IXI/NingXia。

- [独立预登记](PROTOCOL_ZH.md)
- [设计、旧证据和相关工作](docs/01_设计与证据.md)
- [分开的full指令](docs/02_运行指令.md)
- [full前复核](results/pre_full_review.md)
- [能力检查](results/capacity.json)
- [最终入口与完整性核验](results/final_verification.json)

旧代码与checkpoint保持不变，本包首次full后冻结Python、协议与full.ps1哈希。smoke结果不允许进入正式gate；入口拒绝外部test和未通过E1的local full。
