# PAST-Net G086：IXI 固定候选泛化验证

## 1. 为什么下一步不是 G091-G095

G086 在 fastMRI 上达到当前最好 PSNR `24.4470 dB`，但只比 G084 高 `0.0046 dB`；继续低学习率训练已经没有研究价值。G087-G090 的独立 sparse-window 主干最高只有 `24.1089 dB`，比 G084 低 `0.3334 dB`，也不应靠增加轮数或宽度挽救。

当前可重复的正证据只有三项：成熟多锚点主干、多尺度 latent interaction 与 tail-aware objective、FFT dual-domain residual。下一步冻结这套机制，检查它是否能离开 fastMRI 后仍然成立。

## 2. IXI G086 模型

IXI G086 使用与 fastMRI G086 相同的结构定义：

1. 每个 x4 interval 读取 `prev/left/right/next` 四个稀疏锚点。
2. 对 `1/4、2/4、3/4` 三个 phase 构造13通道条件并联合前向。
3. 主干由 IXI G07 wide MA3 checkpoint 初始化，240个张量全部映射。
4. 在 `1/2` 和 `1/4` 分辨率加入三 offset latent Conv3D interaction。
5. 输出端加入 spatial expert 与 FFT low/mid/high expert，并由学习门控融合。
6. 新增 latent mixer 和 dual-domain head 均为零残差初始化；初始化输出与 IXI G07 的最大绝对差为 `0.0`。

训练目标固定为 Charbonnier + MSE + gradient + Laplacian + residual regularization + reversal symmetry + z-curvature + top-10% tail MSE + base trust region。前8轮只训练新增 adapter，之后联合微调；AdamW betas `(0.9,0.99)`，backbone LR `3e-6`，adapter LR `2.4e-5`，8轮 warmup 后 cosine decay，EMA `.999`。

## 3. 协议与防止后验调参

- 数据划分、归一化和 test-115 与既有 IXI G07、I3Net 完全相同。
- 只运行一个固定 full profile，不根据 IXI test 病例挑选 checkpoint、loss 权重或模型变体。
- epoch-0 会先评估并保存原始 G07 等价状态；后续 checkpoint 只按 validation objective 选择。
- 上限160轮，patience 40；允许验证集早停，不要求凑满160轮。
- 真实 batch 1、梯度累积16；主预测和 reversal 分支使用 activation checkpointing。完整256×256对称 loss 反向峰值由 `22.81 GiB` 降至实测 `11.99 GiB`，避免此前 IXI batch 过大造成显存溢出。

## 4. 预注册判定

既有 IXI test-115：G07 PSNR `29.9892`、SSIM `.9155`、MAE `19.7240`、MSE `3291.94`；I3Net PSNR `31.3058`、SSIM `.9285`、MAE `17.5276`、MSE `2565.32`。

1. 若 G086 相对 G07 的 PSNR 至少提高 `0.05 dB`，且 SSIM、MAE、MSE 不退步，则 fastMRI 机制通过跨数据集验证，下一步迁移 NingXia。
2. 若增益在 `0-0.05 dB`，记为弱泛化证据，不再对 IXI 调参，仍可直接进 NingXia 作最终判定。
3. 若 PSNR 或两个以上结构/误差指标退步，停止 G086 路线，回到训练协议和任务定义层面重新设计。
4. 只有实际超过 I3Net，才报告为在当前统一 IXI 协议上超过该对照；不能预先承诺 SOTA。

## 5. 已完成验证

- Python 编译：通过。
- G07 warm-start：240/240 tensor 映射，初始化 `max_abs_diff=0.0`。
- 一轮训练、AMP累积、EMA、checkpoint保存/重载、整卷推理：通过。
- Paper table 与复杂度统计：通过。
- Smoke `skipped_nonfinite=0`。
- Full-shape 单 batch 完整反向：loss finite，峰值显存 `11.99 GiB`。

## 6. Full 运行指令

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'

& $py -B -m ixi_pastnet_2p5d.run_all --profile full_g086_dual_interval160_test115
& $py -B -m ixi_pastnet_2p5d.paper_table --profile full_g086_dual_interval160_test115
```

本阶段只执行这一组。运行完成后先做 G086 对 G07、I3Net 的115病例配对 bootstrap，再决定是否迁移 NingXia，不启动新的 IXI 变体搜索。
