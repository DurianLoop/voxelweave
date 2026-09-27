# PAST-Net G071-G075 重构方案与 fastMRI 运行指令

更新时间：2026-08-20

## 1. 为什么重新设计

fastMRI G07（wide MA3）的正式结果为 PSNR `24.2910 dB`、SSIM `0.8031`，比本地 I3Net 高 `0.2808 dB`；但同一结构迁移到 IXI test-115 后为 `29.9892 dB`，低于 I3Net 的 `31.3058 dB`。其中 HH 差 `0.614 dB`，Guys 差 `1.812 dB`，IOP 差 `1.034 dB`。这说明 G07 有潜力，但现有单切片结构和训练策略不足以支撑跨站点泛化。

旧训练器还有一个明确问题：所有参数统一使用 AdamW 和同一学习率，调度器只用 `ReduceLROnPlateau`。G07 与 IXI G07 的验证损失持续产生很小的改进，使 Plateau 很少触发，学习率长期不变。因此本轮同时重构结构和优化，不再只改 adapter。

五个 full 实验均从同一个 fastMRI G07 best checkpoint 无损初始化，并统一训练 200 个新增 epoch。除 G075 的联合区间输入外，数据、损失和有效 batch 均保持一致。

## 2. 新训练底座

### 2.1 参数分组

训练器把参数分为三组：

| 组 | 主要模块 | 目的 |
|---|---|---|
| backbone | anchor encoder、aux encoder、10 个 LocalStructureBlock | 小步微调已有表征，减少灾难性遗忘 |
| head | gate、decoder、detail refiner | 以 backbone 的 2 倍学习率适应输出分布 |
| adapter | reliability、multi-scale context、3D interval refiner | 新模块使用 6-10 倍学习率，尽快离开零初始化 |

bias、norm 和一维参数不做 weight decay；卷积和线性权重使用 decoupled weight decay。

### 2.2 Warmup-cosine

新实验不依赖验证集触发降学习率，而是使用确定性的 linear warmup + cosine decay。最后一轮达到 `base_lr × min_lr_ratio`。这既避免高学习率破坏 G07，也保证训练后半程真正进入低学习率精修。

### 2.3 Adapter-first

带新模块的 G072-G075 在 warmup 阶段只更新 adapter，backbone/head 学习率为 0。warmup 结束后再联合训练。这样可以先让零初始化模块学习合理残差，再允许整个网络协同调整。

### 2.4 EMA

验证、best checkpoint 和最终 checkpoint 使用 EMA 权重。G071-G073 为 `0.999`，更长、更复杂的 G074-G075 为 `0.9995`。EMA 只平滑真实训练轨迹，不读取测试集，也不做测试时调参。

## 3. 五个版本总览

| ID | Full profile | 结构 | Optimizer | LR（backbone/head/adapter） | Warmup | EMA | Epoch |
|---|---|---|---|---|---:|---:|---:|
| G071 | `full_pastnet_g071_cosine_ema200` | 原 G07 wide MA3 | AdamW, β=(0.9,0.99) | 1.5e-5 / 3e-5 / - | 5 | .999 | 200 |
| G072 | `full_pastnet_g072_reliability_opt200` | G07 + anchor reliability | AdamW, β=(0.9,0.99) | 1e-5 / 2e-5 / 8e-5 | 5 adapter-only | .999 | 200 |
| G073 | `full_pastnet_g073_multiscale_opt200` | G07 + 2 个 multi-scale adapter | AdamW, β=(0.9,0.99) | 1e-5 / 2e-5 / 6e-5 | 5 adapter-only | .999 | 200 |
| G074 | `full_pastnet_g074_afms_radam200` | reliability + multi-scale | RAdam, β=(0.9,0.99) | 1e-5 / 2e-5 / 6e-5 | 8 adapter-only | .9995 | 200 |
| G075 | `full_pastnet_g075_interval3d_opt200` | reliability + context + 3D interval refiner | AdamW, β=(0.9,0.99) | 8e-6 / 1.6e-5 / 8e-5 | 10 adapter-only | .9995 | 200 |

统一 weight decay 为 `3e-5`，比旧值 `1e-4` 更适合从已收敛 checkpoint 微调。G071-G074 的有效 batch 为 16；G075 为 batch 1、累积 16，避免 24GB 显存溢出。

## 4. G071：优化控制组

G071 不改模型结构，只替换训练策略。它用于分离“优化器/调度器收益”和“新结构收益”。

```text
13-channel rich multi-anchor input
  -> shared five-anchor encoder + auxiliary encoder
  -> pixel-wise five-way gate
  -> 64-channel, 10-block wide MA3 trunk
  -> decoder + temporal detail refiner
  -> residual over linear coarse
```

与旧续训不同，G071 的 head 学习率是 backbone 的 2 倍，前 5 轮 warmup，随后余弦衰减到 `7.5e-7`，并用 EMA 保存。若它已经显著超过 G07，说明过去确实存在优化不足；后续结构版必须与 G071 比，而不只与 G07 比。

## 5. G072：优化后的锚点可靠性

G072 保留 G07 原有五路 pixel gate，再增加共享 reliability scorer。每个锚点的 feature 与辅助 feature 共同产生局部可靠性和全局可靠性修正，修正值加到原 gate logits 后再 softmax。

```text
anchor feature + auxiliary feature
  -> shared reliability scorer
  -> local score + spatially pooled global score
  -> zero-initialized correction to five-way gate logits
```

新增模块约 `2.3K` 参数。前 5 轮仅用 `8e-5` 训练 reliability adapter，之后 backbone/head 才加入。它重点验证跨站点时某些外锚点失真是否需要动态降权。

## 6. G073：优化后的多尺度上下文

G073 在 MA3 trunk 与 decoder 之间串联两个 residual context adapter。每个 adapter 包含 dilation 1/2/3 的 depthwise 3×3 并行分支、1×1 融合和 channel attention。

```text
wide MA3 trunk
  -> [DWConv d1 | DWConv d2 | DWConv d3]
  -> pointwise fusion + channel attention
  -> zero-initialized residual projection
```

新增约 `39.3K` 参数，扩大面内感受野而不继续盲目增加普通 block。adapter 先以 `6e-5` 独立 warmup，再与 G07 主干联合精修。

## 7. G074：组合结构与 RAdam 对照

G074 组合 G072 和 G073，结构上回答 anchor routing 与面内上下文是否互补，优化上改用 RAdam。RAdam 的自适应方差整流对小学习率 warm-start 和新旧参数混合训练更稳定，也能检验 G072/G073 的结果是否依赖 AdamW 的特定轨迹。

G074 不是为了只做优化器刷分：它必须结合 G072、G073 判断。若单模块有效但组合无增益，后续只保留有效分支；若组合稳定超过两者，说明两类瓶颈确实正交。

## 8. G075：低分辨率 3D 区间细化

G075 是面向 IXI 泛化的高风险版本。旧 MA3J 只是把三张预测拼成 2D 通道后卷积，没有显式 z 轴特征。新 MA3IR 对每个 x4 区间的三个缺失位置联合预测：

```text
three offset conditions: (B, 3, 13, H, W)
  -> shared G07 single-slice branch
  -> base predictions for offsets 1/2/3
  -> per-offset low-resolution encoder (H/4, W/4)
  -> depthwise 3D conv across offset × height × width
  -> pointwise 3D mixing
  -> confidence-gated correction for each offset
  -> upsample and add to G07 base predictions
```

3D refiner末层零初始化，warm-start 时输出与 G07 完全一致。联合残差幅度限制为 `0.12`，并加入较弱的 z-curvature loss `0.02`，避免为了平滑而抹掉真实解剖变化。前 10 轮只训练 reliability/context/3D refiner，随后全网联合训练。

G075 的目标不是人为贴合 IXI 测试集，而是学习对不同扫描站点都合理的局部 z 轴结构。fastMRI 若没有稳定收益，不直接把它包装成 IXI 最优结构。

## 9. Smoke 验证结果

五个 profile 均已完成一轮训练、EMA 验证、checkpoint 保存/重载、整卷推理、指标计算和 paper table 生成，均为 `skipped_nonfinite=0`。

| Smoke profile | Val loss | PSNR（单病例，仅链路检查） | Params(M) | FLOPs(G/slice) | 状态 |
|---|---:|---:|---:|---:|---|
| `smoke_pastnet_g071_opt` | .019605 | 23.5171 | .7436 | 114.0851 | passed |
| `smoke_pastnet_g072_reliability_opt` | .019816 | 23.4863 | .7459 | 115.4378 | passed |
| `smoke_pastnet_g073_multiscale_opt` | .019819 | 23.4831 | .7829 | 118.8330 | passed |
| `smoke_pastnet_g074_afms_radam` | .019819 | 23.4850 | .7852 | 120.1857 | passed |
| `smoke_pastnet_g075_interval3d_opt` | .020531 | 23.4853 | .7799 | 117.9976 | passed |

G072-G074 初始预测与 G07 最大绝对误差约 `2.38e-7`（数值舍入），G075 为 `0.0`。smoke 的一病例 PSNR 不用于排序，因为 adapter-first 阶段主干被刻意冻结。

## 10. FastMRI full-200 正式结果

五个实验均完成 200 个新增 epoch 和全部 24 个测试病例评估。主指标如下：

| 方法 | PSNR | SSIM | MAE | MSE | NCC | 相对 G07 PSNR | 相对 I3Net PSNR |
|---|---:|---:|---:|---:|---:|---:|---:|
| I3Net | 24.0102 | .792094 | 41.0101 | 7755.65 | .930840 | -0.2808 | 0.0000 |
| G07 wide MA3 | 24.2910 | .803080 | 38.8905 | 7448.96 | .934988 | 0.0000 | +0.2808 |
| G071 cosine + EMA | **24.3351** | .804652 | 38.5066 | **7370.85** | .935584 | **+0.0441** | **+0.3249** |
| G072 reliability | 24.3330 | .804674 | 38.5111 | 7375.39 | .935552 | +0.0420 | +0.3227 |
| G073 multi-scale | 24.3285 | **.805583** | 38.4356 | 7384.60 | .935484 | +0.0375 | +0.3183 |
| G074 AFMS + RAdam | 24.3298 | .805581 | **38.4294** | 7382.01 | .935510 | +0.0389 | +0.3196 |
| G075 3D interval | 24.3338 | .804664 | 38.4998 | 7373.87 | **.935605** | +0.0428 | +0.3235 |

### 10.1 逐病例证据

- G071 相对 G07：PSNR 提升 `+0.0441 dB`，22/24 病例获胜，配对 bootstrap 95% CI 为 `[+0.0280, +0.0604] dB`；SSIM、MAE 均为 24/24 获胜。
- G073 相对 G07：SSIM 提升 `+0.002503`、MAE 降低 `0.4548`，均为 24/24 获胜；但 PSNR 只提升 `+0.0375 dB`，且 MSE 不如 G071。
- G075 相对 G071：PSNR 平均低 `0.0013 dB`，仅 11/24 获胜；SSIM 也是 11/24。差异可视为打平，没有证据表明 3D 输出细化优于纯优化控制组。
- 五个新版相对 I3Net 都是 PSNR 21/24、SSIM 24/24、MAE 23/24、MSE 20/24、NCC 21/24 获胜。当前 fastMRI 上超过 I3Net 已较稳定，但最大优势仍只有约 `0.325 dB`，距离 26 dB 目标很远。

### 10.2 收敛与数值稳定性

| 方法 | Best epoch | Best val loss | 全程 nonfinite/overflow 计数 | 轨迹判断 |
|---|---:|---:|---:|---|
| G071 | 2 | .02333139 | 17 | 纯优化收益在极早期完成，后续 198 轮无新 best |
| G072 | 7 | .02333115 | 17 | reliability 只在 warmup/解冻阶段产生微小变化 |
| G073 | 197 | **.02329317** | 17 | 多尺度分支持续改善到训练末期 |
| G074 | 185 | .02329519 | 17 | 与 G073 轨迹接近，RAdam 没有形成额外优势 |
| G075 | 15 | .02415897 | 0 | interval loss 口径不同，不能横比绝对 val；第 15 轮后无新 best |

17 次计数相对约 34,000 个优化窗口约为 `0.05%`，没有导致训练中断，但正式论文仍应如实记录 AMP overflow。G075 为 0。

### 10.3 结构判断

1. **优化策略有效，但上限很低。** G071 证明分组学习率、cosine 和 EMA 能稳定增加约 `0.044 dB`，但 200 轮中的有效收益几乎都发生在最初几轮。以后同类控制组不必再固定跑满 200 轮。
2. **Anchor reliability 暂不保留。** G072 比 G071 低 `0.0021 dB`，其新增 gate 没有独立贡献；G074 中加入 reliability 也没有超过 G073。
3. **Multi-scale context 是唯一仍有结构潜力的分支。** G073/G074 在所有病例上改善 SSIM 和 MAE，且验证集一直改善到训练末期。它改变的是结构/纹理误差，而非 PSNR 大误差尾部。
4. **RAdam 不优于 AdamW。** G074 与 G073 近乎打平，没必要为下一版保留额外优化器变量。
5. **当前 G075 失败的是“输出端小残差 3D 修正”这一实现。** 它与 G071 的 PSNR 基本相同、逐病例胜负接近随机，说明在最终预测后增加受限低分辨率修正不足以学习真正的 z 轴对应关系。

### 10.4 下一步决策

- fastMRI PSNR checkpoint 保留 G071；结构研究主干保留 G073。
- 不直接把 G072、G074、G075 移植到 IXI，也不根据 IXI test-115 继续试学习率。
- 下一代应在 G073 基础上把跨 offset 建模前移到 **latent feature**，让三个缺失位置的 trunk feature 在 decoder 前交互，而不是在输出图像上做小残差。
- 下一次应同时加入 hard-case / high-error region 训练目标，专门降低 MSE 尾部；当前多尺度分支改善了 MAE/SSIM，却没有同步改善 PSNR，说明平均像素质量已不是主要瓶颈。
- 新结构先在 fastMRI 做统一协议验证；只有相对 G071 在 PSNR 上形成至少 `+0.08 dB`、并保持 SSIM/MAE 优势，才值得移植到 IXI。

## 11. 原定正式结果判定

优先级按以下规则确定：

1. 先比较 G071 与原 G07，量化纯优化收益。
2. G072/G073 分别与 G071 比，只有超过 G071 才算结构有效。
3. G074 必须超过表现更好的 G072/G073，才保留组合和 RAdam。
4. G075 除平均 PSNR/SSIM 外，还要检查 per-case 胜率与最差病例，防止 z 平滑只改善容易病例。
5. fastMRI 选出结构后，固定结构、优化器、学习率策略和随机种子协议再移植 IXI；不根据 IXI test-115 反复调参。

## 12. 运行指令

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'
```

### G071

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g071_cosine_ema200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g071_cosine_ema200
```

### G072

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g072_reliability_opt200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g072_reliability_opt200
```

### G073

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g073_multiscale_opt200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g073_multiscale_opt200
```

### G074

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g074_afms_radam200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g074_afms_radam200
```

### G075

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g075_interval3d_opt200
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g075_interval3d_opt200
```

### 五个依次运行

```powershell
$profiles = @(
    'full_pastnet_g071_cosine_ema200',
    'full_pastnet_g072_reliability_opt200',
    'full_pastnet_g073_multiscale_opt200',
    'full_pastnet_g074_afms_radam200',
    'full_pastnet_g075_interval3d_opt200'
)

foreach ($profile in $profiles) {
    Write-Host "===== RUN $profile ====="
    & $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile $profile
    if ($LASTEXITCODE -ne 0) { throw "$profile failed during run_all" }
    & $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile $profile
    if ($LASTEXITCODE -ne 0) { throw "$profile failed during paper_table" }
}
```
