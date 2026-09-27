# 训练序列修复 full 复核（2026-09-23）

67 轮完成并早停，validation PSNR **25.567453 dB**；旧数据 control 为 25.562011 dB。23 患者配对增益 **+0.005442 dB**，患者 bootstrap 95% CI **[+0.002286,+0.008808]**，17/23 患者提升，困难四分位 +0.002187 dB。这是一个 seed 的患者不确定性，不是跨 seed 稳定性。

| 指标 | 修复版 | 相对旧 control 差值 |
|---|---:|---:|
| SSIM | 0.83519953 | +0.00011117 |
| MAE | 0.02461251 | −0.00001584 |
| MSE | 0.00309643 | −0.00000271 |
| NCC | 0.93962475 | +0.00007599 |
| Dice intensity proxy | 0.97720832 | +0.00001954 |
| HD95 intensity proxy | 5.34404763 | −0.05867479 |
| tail10 MSE | 0.02694596 | −0.00002153 |

全部质量方向、患者胜率、困难组、配对 CI 和效率守卫通过，**效应量不足预登记 +0.10 dB，promoted=false**。不降低门槛，不继续本分支学习率/轮数搜索，不进入三 seeds 或外部测试。Dice/HD95 是强度阈值代理指标，不能解释为解剖分割质量。

模型仍为 992,179 参数；同一设备/输入/AMP/10 warmup/30 repetitions 的 forward-only 中位延迟 47.8415 ms/缺失切片，峰值 0.858745 GiB。训练峰值 19.6314 GiB allocated /20.3223 GiB reserved，累计记录训练时间约 11.13 小时。部分 Conv/Linear FLOPs 为 446.590 G/三切片区间，非包含 FFT 等全部算子的总 FLOPs。

best SHA256：`9255425ab9d66dffbb70d416a3c499012dea00f3906e58fe8cfb063ba89b45ba`。代码、配置、manifest、完成标记与 checkpoint 已核验；重新加载 best 对全部 69 validation 区间独立复算的证据见 `full_reverification.json`。配对统计见 `gate_repair_seed3407.json`。

**数据修复保留。** UID、物理位置和逐像素匹配证明旧训练 volume 混合了两个不同 DICOM series，修复有效性不由分数决定。训练变为 113 series、111 患者、1356 区间；validation 23 患者/69 区间逐字段相同。本轮是数据修复实验，不能称为模型结构消融。G086 历史初始化仍包含旧数据影响。

后续 `pastnet_wavelet_trunk` 使用相同修复 manifest，以本 full 为 control，重新从同一 G086 初始化；不从本 best 续训。已用旧数据训练的 I3Net 参照不能直接充当同数据公平架构对照，后续正式对比需匹配数据与预算。未打开 development test、IXI 或 NingXia，未修改论文测试表。
