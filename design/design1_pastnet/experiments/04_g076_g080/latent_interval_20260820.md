# PAST-Net G076-G080 Latent Interval 设计与运行指令

更新时间：2026-08-20

## 1. 本轮目标

目标仍然是推动 fastMRI x4 PSNR 向 `26 dB` 靠近，但不预设这五次实验必然一次跨越约 `1.665 dB` 的差距。所有实验必须能解释成可迁移到 IXI / NingXia 的结构或训练机制，不使用测试集调参、不做手工输出融合，也不读取 I3Net 预测。

当前锚点：

| 模型 | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| I3Net | 24.0102 | .792094 | 41.0101 | 7755.65 | .930840 |
| G071，当前 PSNR 最优 | **24.3351** | .804652 | 38.5066 | **7370.85** | .935584 |
| G073，当前结构最优 | 24.3285 | **.805583** | 38.4356 | 7384.60 | .935484 |

G071 证明优化策略只能提供约 `+0.044 dB`；G073 证明 multi-scale context 能持续改善结构指标；G075 证明输出图像后的低分辨率 3D 小残差不足以建模 z 轴关系。因此本轮统一从 G073 best checkpoint 出发，把三 offset 交互前移到 decoder 之前。

## 2. 共享主干与无损初始化

三个缺失位置 `S1/S2/S3` 各自使用同一个 G073 encoder：

```text
13-channel rich multi-anchor condition for each offset
  -> shared anchor/aux encoders
  -> five-way pixel gate
  -> 64-channel, 10-block MA3 trunk
  -> two multi-scale context adapters
  -> latent feature F1/F2/F3
```

新 latent mixer 处理 `(B,C,3,H/s,W/s)`，将校正后的 feature 送入共享 decoder 和 detail refiner。所有 mixer 的输出 projection 为零初始化，所以加载 G073 时：

```text
new_model(S1,S2,S3) == G073(S1,S2,S3)
```

实测五个版本 warm-start 最大输出误差均为 `0.0`。这保证 full 结果相对 G073 的变化来自新模块训练，而不是初始化预测漂移。

## 3. 共同训练策略

| 项目 | 设置 |
|---|---|
| 初始化 | `full_pastnet_g073_multiscale_opt200` best checkpoint |
| Optimizer | AdamW，betas `(0.9,0.99)` |
| 基础 LR | backbone `5e-6`，head `1e-5`，latent adapter `4e-5` |
| Scheduler | linear warmup + cosine decay，最低比例 `.03` |
| 训练阶段 | warmup 期间只训练 latent adapter，随后全网联合微调 |
| EMA | `.999`，用于验证和保存 best checkpoint |
| Batch | batch 1，gradient accumulation 16，有效 batch 16 |
| 早停 | 每个 profile 使用独立 patience，未改善时提前结束 |
| 基础 loss | Charbonnier + MSE + gradient + Laplacian edge + symmetry + weak z-curvature |

不再把训练轮数强制统一为 200。架构复杂度和收敛速度不同，使用最大预算加早停更合理。

## 4. 五个版本总览

| ID | Full profile | Latent interaction | 新 loss | 最大 epoch | Patience | Params(M) |
|---|---|---|---|---:|---:|---:|
| G076 | `full_pastnet_g076_latent_conv120` | H/4 depthwise 3D conv | 无 | 120 | 35 | .7934 |
| G077 | `full_pastnet_g077_latent_attention150` | H/4 offset self-attention | 无 | 150 | 45 | .8089 |
| G078 | `full_pastnet_g078_latent_multiscale160` | H/2 + H/4 3D conv | 无 | 160 | 50 | .8039 |
| G079 | `full_pastnet_g079_tail_aware160` | G078 双尺度 | top-10% tail MSE | 160 | 50 | .8039 |
| G080 | `full_pastnet_g080_hybrid_tail180` | H/2 conv + H/4 attention | tail MSE + pyramid | 180 | 60 | .8194 |

FLOPs 估算约为 `140.3-140.7 G/slice`；attention 的内部矩阵乘法未完全计入 hook 估算，因此最终论文效率表需另做实测时间和显存 profiling。

## 5. G076：单尺度 Latent 3D Conv

G076 是本轮最干净的结构基线。在 `H/4 × W/4` latent 上使用：

```text
[F1,F2,F3]
  -> learned offset embedding
  -> depthwise Conv3d 3x3x3
  -> pointwise Conv3d
  -> zero-initialized feature residual + confidence gate
  -> shared decoder
```

它与 G075 的区别不是简单换卷积：G075 修正已经生成的图像，G076 让三个 offset 在 decoder 前交换特征，因此 decoder 可以把 z 轴信息转化成像素级结构。

最大 120 轮、patience 35。若 35 轮没有新 best 会自动停止。

## 6. G077：Offset Self-Attention

G077 将每个低分辨率空间位置上的 `F1/F2/F3` 视为长度 3 的 token sequence，使用 4-head self-attention：

```text
tokens at each (x,y): [F1(x,y), F2(x,y), F3(x,y)]
  -> LayerNorm + learned offset embedding
  -> multi-head self-attention along z-offset
  -> depthwise spatial refinement
  -> zero-initialized latent residual
```

它回答固定局部 3D kernel 是否限制了非线性 slice correspondence。由于只有三个 token，attention 计算量受控，但比 G076 更灵活。

## 7. G078：双尺度 Latent 3D Conv

G078 并行使用 `H/2` 和 `H/4` 两个 latent 尺度：

```text
fine branch H/2: local boundary and small anatomy change
coarse branch H/4: larger field-of-view and global z trajectory
  -> upsample both latent residuals
  -> average and inject before decoder
```

这是对 G073 multi-scale 结论的自然延伸：G073 只扩大单 offset 的面内上下文，G078 在两个尺度上同时建模 offset 间关系。

## 8. G079：Tail-Aware PSNR Objective

G073/G074 改善了 SSIM 和 MAE，却没有同步获得最优 PSNR/MSE，说明大误差尾部仍是瓶颈。G079 保持 G078 架构，只改变 loss：

```text
tail_mse = mean(top 10% pixel-wise squared errors per generated slice)
loss += 0.20 * tail_mse
```

它不按病例名采样、不查看测试集，也不会固定关注特定图像区域。top-k 每个训练切片动态计算，目标是减少少量高误差像素对 MSE/PSNR 的破坏。

同时把普通 MSE 权重从 `.25` 提高到 `.35`。G079 必须与相同结构的 G078 比较，才能判断 tail objective 是否有效。

## 9. G080：Hybrid Latent + Tail + Pyramid

G080 是本轮组合候选：

```text
H/2 branch: 3D convolution for local continuity
H/4 branch: offset attention for non-local correspondence
loss: standard reconstruction
    + top-10% tail MSE
    + H/2,H/4 average-pooling pyramid L1
```

pyramid loss 权重为 `.10`，用于约束低频脑结构与强度趋势；tail MSE 负责高误差局部。二者分别对应 G073 暴露的“结构指标改善”和“PSNR 尾部没有同步改善”。

G080 风险最高，因此给 180 轮上限和 patience 60，但仍会在停止改善时提前结束。

## 10. Smoke 验证

五个 smoke 均实际完成一轮训练、验证、EMA checkpoint 保存/重载、整卷推理、指标计算和 paper table，`skipped_nonfinite=0`，无 OOM。

| Smoke profile | Val loss | 单病例 PSNR | Params(M) | 状态 |
|---|---:|---:|---:|---|
| `smoke_pastnet_g076_latent_conv` | .019850 | 23.5631 | .7934 | passed |
| `smoke_pastnet_g077_latent_attention` | .019850 | 23.5648 | .8089 | passed |
| `smoke_pastnet_g078_latent_multiscale` | .019850 | 23.5635 | .8039 | passed |
| `smoke_pastnet_g079_tail_aware` | .023870 | 23.5872 | .8039 | passed |
| `smoke_pastnet_g080_hybrid_tail` | .025424 | 23.5871 | .8194 | passed |

G079/G080 的 loss 包含额外正项，绝对 val loss 不能与 G076-G078 横比。单病例 PSNR 也只用于检查链路，不能作为 full 排名预测。

## 11. Full 结果筛选规则

1. G076/G077/G078 分别回答 conv、attention、multi-scale latent 哪个结构有效，主比较对象是 G073。
2. G079 只和 G078 比；若 MSE/PSNR改善但 SSIM明显下降，说明 tail 权重过强，不能直接作为最终版。
3. G080 必须同时超过 G078/G079 才能证明 hybrid 组合有意义。
4. 相对 G071 PSNR 至少 `+0.08 dB`，并保持 SSIM/MAE不退化，才进入 IXI 移植候选。
5. 若仍只有 `0.02-0.05 dB` 级收益，应承认当前 G073 表征接近局部上限，下一阶段转向完整 sparse-window synthesis，而不是继续叠 adapter。
6. `26 dB` 是研究目标，不把未达到该目标的模型通过 test-time blend 或测试集权重搜索包装成达到目标。

## 12. 运行准备

先在 PowerShell 执行一次：

```powershell
Set-Location D:\MRI
$py = 'D:\conda\envs\MRI\python.exe'
$env:PYTHONPATH = 'D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI'
```

## 13. 分开的 Full 运行指令

### G076

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g076_latent_conv120
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g076_latent_conv120
```

### G077

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g077_latent_attention150
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g077_latent_attention150
```

### G078

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g078_latent_multiscale160
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g078_latent_multiscale160
```

### G079

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g079_tail_aware160
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g079_tail_aware160
```

### G080

```powershell
& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_pastnet_g080_hybrid_tail180
& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_pastnet_g080_hybrid_tail180
```

结果分别位于：

```text
D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_pastnet_g076_latent_conv120
D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_pastnet_g077_latent_attention150
D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_pastnet_g078_latent_multiscale160
D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_pastnet_g079_tail_aware160
D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_pastnet_g080_hybrid_tail180
```

## 14. Full 正式结果（2026-08-29）

五组均完成预设轮数、full 测试集 24 个病例评估和 paper table 生成。训练过程中均为 `skipped_nonfinite=0`，没有 OOM、AMP 异常或坏 checkpoint。

### 14.1 绝对指标

| 方法 | Epoch / best | PSNR (dB) | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| I3Net | baseline | 24.0102 | .792094 | 41.0101 | 7755.65 | .930840 |
| G071 | reference | 24.3351 | .804652 | 38.5066 | 7370.85 | .935584 |
| G073 | reference | 24.3285 | .805583 | **38.4356** | 7384.60 | .935484 |
| G076 latent conv | 120 / 120 | 24.3333 | .805773 | 38.4039 | 7376.36 | .935552 |
| G077 latent attention | 150 / 150 | 24.3332 | .805797 | 38.3991 | 7377.04 | .935552 |
| G078 latent multiscale | 160 / 158 | 24.3382 | .805912 | **38.3802** | 7368.14 | .935624 |
| G079 tail-aware | 160 / 160 | **24.4032** | .805964 | 38.4845 | **7239.44** | **.936450** |
| G080 hybrid tail | 180 / 180 | 24.4020 | **.806007** | 38.4829 | 7243.95 | .936417 |

表中 MAE 粗体只在同类 G076-G080 中比较；旧参考 G073 的 MAE 仍优于 G079/G080。G079 是当前 fastMRI PAST-Net 的最高 PSNR、最低 MSE 和最高 NCC；G080 只以 `.000043` 的幅度取得最高 SSIM，PSNR/MSE 反而略差于 G079。

### 14.2 配对统计与因果归因

| 比较 | PSNR 平均差 | 获胜病例 | 关键结论 |
|---|---:|---:|---|
| G077 - G076 | -0.0001 dB | 约半数 | offset attention 没有超过更简单的 3D conv |
| G078 - G076 | +0.0049 dB | 20/24 | 双尺度 latent 有小而一致的结构收益，但不是数量级突破 |
| G079 - G078 | **+0.0650 dB** | **24/24** | 相同架构下 tail objective 有效，MSE 平均减少 128.69 |
| G080 - G079 | -0.0011 dB | 约半数 | hybrid attention + pyramid loss 没有新增价值 |
| G079 - G071 | **+0.0681 dB** | **23/24** | bootstrap 95% CI `[+0.0523,+0.0833]`，Wilcoxon `p=2.38e-7` |
| G079 - I3Net | **+0.3929 dB** | 21/24 | SSIM 同时提高 `.01387`，MAE 降低 `2.5257` |

G079 对 G078 的 24/24 PSNR 获胜说明增益不是由少数测试病例偶然拉高，也不是通过 case-specific 调参获得。它直接验证了此前“少量大误差像素限制 MSE/PSNR”的判断。

代价同样清楚：G079 相对 G078 的 MAE 平均增加 `0.1043`，仅 1/24 病例 MAE 更好；自动 Dice 平均下降 `.00244`，主要来自 `105335865656`（`-.0300`）、`107274371713`（`-.0162`）和 `102670846301`（`-.0124`）。因此 tail-aware loss 是有效方向，但当前固定权重不是最终平衡点。

### 14.3 收敛状态

| 方法 | 最后一轮 LR | 末 10 轮 val loss 变化 | 判断 |
|---|---:|---:|---|
| G076 | 1.2e-6 | -2.82e-7 | 最优在末轮，已进入平台区 |
| G077 | 1.2e-6 | -1.84e-7 | 最优在末轮，已进入平台区 |
| G078 | 1.2e-6 | -0.78e-7 | 第 158 轮最优，基本拟合完成 |
| G079 | 1.2e-6 | -3.62e-7 | 最优在末轮，仍缓慢改善但日程已耗尽 |
| G080 | 1.2e-6 | -4.51e-7 | 最优在末轮，额外 20 轮仍未超过 G079 |

继续用同一极低学习率机械追加 40 轮，预期只能获得很小变化。若续训 G079，应从 best checkpoint 做受控的低学习率重启，并单独命名实验，不能把续训结果与原始 160 轮混写。

### 14.4 本轮决策

1. **保留 G078 作为结构基线**：它是无 tail loss 条件下综合指标最好的 latent mixer，并且比 G076 的改善覆盖 20/24 病例。
2. **保留 G079 作为 PSNR 主线**：它把当前纪录从 G071 的 `24.3351` 提到 `24.4032 dB`，相对 I3Net 稳定领先 `0.3929 dB`。
3. **停止 G077**：attention 增加复杂度却与 G076 数值等价，三 offset 的短序列不需要该机制。
4. **停止 G080**：更复杂的 hybrid/pyramid 仅换来不可解释为实质进步的 SSIM 微差，没有超过 G079。
5. **未通过预设晋级门槛**：G079 相对 G071 为 `+0.0681 dB`，低于预设 `+0.08 dB`，且距 `26 dB` 仍有 `1.5968 dB`。不能把这轮描述成接近 26。
6. **下一步应解决目标权衡**：以 G079 为起点研究 tail 权重退火或 robust-tail objective，保留其 MSE 收益，同时恢复 G078/G073 的 MAE 与分割稳定性；若仍只有 `0.0x dB`，则停止 adapter 级优化，转向完整 sparse-window synthesis。
