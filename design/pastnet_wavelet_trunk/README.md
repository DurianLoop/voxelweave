# PAST-Net：共享卷积核的小波多尺度主干

**2026-09-24：full 已完成，分支停止。** 25.585002 dB，相对修复 control +0.017549 dB；23/23 患者提升，全部其它守卫通过，但未达到 +0.10 dB。按计算前协议不运行 J1、额外 seeds 或外部测试。下文的 full 命令与准备说明只作历史记录。详见 [最终复核](results/full_review.md)；下一项为 [双锚点对应实验](../pastnet_bilateral_transport/README.md)。

独立候选包，2026-09-23。上一轮正确的数据修复已保留，但仅带来 +0.005442 dB，未晋级。本轮以修复版 **25.567453 dB** 为共同数据 control，只改变主干空间算子。

**实现、容量检查、J3/J1 trainer smoke、恢复加载、指标复算和 full 入口 preflight 均已通过。** J3 训练峰值 20.70 GiB allocated /21.39 GiB reserved；完整 forward 延迟相对 control 为 1.113 倍。现在只运行 [wavelet3 seed3407 full](docs/运行指令.md)，尚无 full 结果。

## 核心假设

十个 MA3 block 原有全分辨率 3×3 depthwise 卷积，已有全局归一化/通道统计和后端多尺度模块。本轮检验：**逐层加入带空间位置的多尺度关系，能否补足仅在后端融合尺度的不足？** 不增加观测切片或 target 信息，而是改变现有观测如何传播。

每个原卷积 `K` 改为 `K(x)+g*(W_J(K,x)-K(x))`。`W_J` 对特征进行正交 Haar 分解，各尺度四个子带复用原来的卷积核，递归处理 LL 后逆变换；细节子带保留。`g=0.5*tanh(a)`，每通道零初始化，共增加 640 参数。初始预测与原 G086 完全一致，原 326 个 tensor 保留；训练可以逐步学习尺度混合。

当前候选为 J=3（最粗 1/8）。只有通过正式 validation 门槛后，才运行参数数目一致的 J=1 full 消融。四锚点、wide MA3、linear coarse + bounded residual、多尺度 latent、dual-domain residual、原目标函数与 AdamW/warmup cosine/EMA 均保留。它不是输出端 refiner，也不是方向增强。

思想参考 [Finder 等，ECCV 2024，Wavelet Convolutions for Large Receptive Fields](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07137.pdf)。这是共享预训练核与零初始化有界混合的本地实现，不是官方 WTConv 复现，不主张小波卷积理论原创。临界采样小波有相位/边界风险；重建检查不能替代质量验证。

## 实验边界

训练使用已修复 manifest：1356 train 区间；只用 23 患者、69 区间 validation 选型。从原 G086 初始化，最多 80 轮，min30/patience15。与修复 control 的筛选要求至少 +0.10 dB（即 25.667453 dB），并同时通过配对 CI、患者胜率、困难组、质量、tail10 和效率守卫。未通过即停，不靠续训或修改门槛救实验。

单 seed 筛选和 J1 消融均通过后才补齐三 seeds。锁定最终方案后再做 IXI/NingXia；fastMRI test-24 仍只算 development test。当前无 SOTA 结论。

- [计算前协议](PROTOCOL_ZH.md)
- [运行与恢复指令](docs/运行指令.md)
- [full 前检查](results/pre_full_review.md)
- 上轮 [数据修复完整复核](../pastnet_series_integrity/results/full_review.md)
