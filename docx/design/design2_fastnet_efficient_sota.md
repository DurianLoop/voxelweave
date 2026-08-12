# Design 2：FAST-Net，高效率 T2 through-plane interpolation 模型

更新时间：2026-07-06

本文档是第二个自研模型方向，定位和 `self_model_sota_design.md` 中的 PAST-Net 不同。

PAST-Net 更偏向冲击三数据集 SOTA，结构可以稍复杂；本方案更偏向效率优先，目标是在显存、训练时间、推理速度明显更友好的前提下，效果尽可能接近当前第一梯队，最好在 NingXia 或 fastMRI 上局部超过现有强 baseline。

暂定模型名：

```text
FAST-Net
Fast Adaptive Slice Transfer Network
```

中文名称：

```text
快速自适应切片迁移网络
```

核心定位：

```text
轻量、快、稳、易扩展、接近 SOTA
```

## 1. 设计目标

当前主线任务：

| 项目 | 设置 |
|---|---|
| Modality | T2 |
| Task | through-plane interpolation |
| Main scale | x4 |
| Extension | x2 / x6 |
| Datasets | IXI-T2, fastMRI-brain-T2 expanded, NingXia-T2 |
| Metrics | PSNR, SSIM, MAE, MSE, NCC |

FAST-Net 的目标不是第一版就绝对超过 I3Net，而是成为一个高效率强基线 / 自研轻量模型：

1. 训练速度明显快于 HAT、SMamba、diffusion 类方法；
2. 显存占用明显低于 HAT / SMamba；
3. 推理速度适合大规模 case-level CV；
4. 指标尽量接近 I3Net / HAT / SwinIR / SAINT；
5. 在 NingXia 这种外部临床数据上保持稳定；
6. 后续可以作为主模型的 lightweight branch 或 ablation 对照。

## 2. 当前强 baseline 目标

### 2.1 IXI-T2 x4

当前最强为 I3Net：

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| I3Net | 31.3058 | 0.9285 | 17.5276 | 2565.3177 | 0.9788 |

FAST-Net 的现实目标：

| Level | 目标 |
|---|---|
| 合格 | 超过 ResUNet residual |
| 强基线 | 接近 HAT / SMamba |
| 理想 | 接近 I3Net 95% 以上的提升幅度 |
| 惊喜 | IXI 上超过 HAT / SMamba，并缩小与 I3Net 的差距 |

### 2.2 fastMRI-brain-T2 expanded x4

当前最强为 I3Net：

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| I3Net | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 |

FAST-Net 的现实目标：

| Level | 目标 |
|---|---|
| 合格 | 超过 ResUNet residual |
| 强基线 | 接近 SAINT / HAT |
| 理想 | 接近 I3Net |
| 惊喜 | 在 MAE / MSE 或 NCC 上局部超过 I3Net |

### 2.3 NingXia-T2 x4

当前第一梯队是 SwinIR / HAT / SAINT / SMamba。

FAST-Net 的现实目标：

| Level | 目标 |
|---|---|
| 合格 | 超过 Linear / ResUNet / GAN |
| 强基线 | 接近 SwinIR / HAT / SMamba |
| 理想 | 在部分 fold 或部分指标超过 HAT / SwinIR |
| 惊喜 | 平均指标进入 NingXia 第一梯队第一名 |

NingXia 是 FAST-Net 最值得冲的地方，因为轻量模型如果正则性好、残差控制稳，可能比重模型更不容易过拟合。

## 3. 设计原则

FAST-Net 的原则是：

```text
少用重 attention
少堆大 backbone
多利用任务先验
多利用 coarse interpolation
多做 residual correction
多做显式相位调制
```

### 3.1 不从零生成

输出形式固定为：

```text
Y_hat = C + W * R
```

其中：

- C 是 Linear coarse interpolation；
- R 是预测残差；
- W 是空间置信权重；
- Y_hat 是最终预测。

这样模型只学习 Linear 做不好的部分，训练更快，泛化更稳。

### 3.2 不使用重 Transformer 作为主干

HAT / SwinIR 已经验证了 window attention 的强度，但这类结构训练慢、显存高。

FAST-Net 第一版不使用完整 Transformer backbone，只保留轻量局部结构建模：

- depthwise separable convolution；
- large-kernel depthwise convolution；
- ECA / SE channel attention；
- phase-conditioned FiLM；
- residual gate。

### 3.3 显式利用 phase

x4 的三个目标 slice 不是同一个问题：

| Target | Phase |
|---|---:|
| S1 | 0.25 |
| S2 | 0.50 |
| S3 | 0.75 |

模型必须知道 phase，否则会把靠近左 anchor、正中间、靠近右 anchor 的情况混在一起。

### 3.4 控制残差幅度

FAST-Net 的输出应该偏保守：

```text
R_bounded = alpha * tanh(R_raw)
Y_hat = C + W * R_bounded
```

这样可以避免外部数据上乱改结构，也能提升 MAE / MSE 稳定性。

## 4. 输入设计

基础输入使用 6 通道：

```text
Input = [L, R, C, P, D, A]
```

含义：

| Symbol | Meaning |
|---|---|
| L | left anchor slice |
| R | right anchor slice |
| C | linear coarse slice |
| P | phase map |
| D | R - L |
| A | abs(R - L) |

其中：

```text
C = (1 - p) * L + p * R
D = R - L
A = |R - L|
```

P 是和图像同大小的常数 map：

```text
P[i, j] = p
```

为什么这 6 个通道足够：

- L/R 给出两侧结构；
- C 给出稳定 coarse target；
- P 给出目标切片位置；
- D 给出方向性变化；
- A 给出局部变化幅度。

FAST-Net 不优先加入复杂额外输入，是为了保证效率和实现稳定。

## 5. 模型总结构

FAST-Net 总体结构：

```text
[L, R, C, P, D, A]
          |
          v
Lightweight stem
          |
          v
Phase-adaptive residual blocks
          |
          v
Efficient multi-scale context
          |
          v
Residual and confidence heads
          |
          v
Y_hat = C + W * alpha * tanh(R)
```

模型由四部分组成：

1. Lightweight stem；
2. Phase-Adaptive Residual Block；
3. Efficient Multi-scale Context Module；
4. Confidence-Gated Residual Head。

## 6. Lightweight stem

输入 6 通道，先用很浅的 stem 提取基础特征：

```text
Conv 3x3, in=6, out=C
GELU
Conv 3x3, out=C
```

推荐：

| Version | Channels |
|---|---:|
| FAST-Tiny | 32 |
| FAST-Base | 48 |
| FAST-Large | 64 |

第一版推荐：

```text
FAST-Base, channels = 48
```

如果优先追速度：

```text
FAST-Tiny, channels = 32
```

## 7. Phase-Adaptive Residual Block

核心模块：

```text
PARB = Phase-Adaptive Residual Block
```

结构：

```text
x
|
1x1 conv expansion
|
depthwise 5x5 conv
|
GELU
|
ECA / SE channel attention
|
phase FiLM modulation
|
1x1 conv projection
|
residual add
```

### 7.1 为什么用 depthwise conv

普通卷积计算量：

```text
K * K * Cin * Cout * H * W
```

Depthwise separable conv 计算量：

```text
K * K * Cin * H * W + Cin * Cout * H * W
```

在 256x256 MRI slice 上，depthwise separable conv 可以显著降低计算量。

### 7.2 为什么用 5x5 / 7x7

普通 3x3 卷积感受野太小，而 attention 太重。使用 depthwise 5x5 或 7x7 可以用很低成本扩大局部感受野。

推荐：

```text
FAST-Tiny: depthwise 5x5
FAST-Base: depthwise 5x5
FAST-Large: depthwise 7x7
```

### 7.3 Phase FiLM

phase 不只作为输入通道，还用于调制中间特征。

定义：

```text
gamma, beta = MLP(p)
F_out = gamma * F + beta
```

其中 p 是标量 phase。

这样模型可以根据 p=0.25 / 0.50 / 0.75 自动切换融合策略。

### 7.4 ECA / SE attention

使用轻量 channel attention：

```text
ECA preferred
```

原因：

- 参数少；
- 速度快；
- 对医学图像局部纹理有帮助；
- 比 window attention 更省显存。

## 8. Efficient Multi-scale Context Module

为了补偿轻量卷积感受野不足，加入一个低成本多尺度上下文模块。

推荐结构：

```text
F1 = DWConv 3x3(F)
F2 = DWConv 5x5(F)
F3 = DWConv 7x7(F)
F4 = DWConv 3x3 dilation=2(F)

F_context = 1x1 Conv(concat(F1, F2, F3, F4))
```

作用：

- 捕获不同尺度结构；
- 不用 attention；
- 计算量可控；
- 对脑室、皮层、边界等不同尺度结构更友好。

如果速度仍然慢，可以删掉 F4。

## 9. Confidence-Gated Residual Head

输出两个 head：

```text
R_raw = residual_head(F)
W = sigmoid(confidence_head(F))
```

最终输出：

```text
R = alpha * tanh(R_raw)
Y_hat = C + W * R
```

其中：

```text
alpha = 0.25 或可学习参数
```

如果输入图像强度是 0 到 1，alpha 可以设为：

```text
alpha = 0.25
```

如果输入是 0 到 255，则需要按当前归一化方式调整。

### 9.1 为什么要 W

W 是空间置信门控。

理想行为：

- 背景区域 W 小；
- 结构稳定区域 W 小；
- 边界变化区域 W 大；
- slice 间差异大的区域 W 大。

这能减少外部数据上的过度修正。

### 9.2 为什么要 tanh

tanh 限制残差幅度，避免预测值突然爆。

这对 NingXia 特别重要，因为 NingXia case 少，训练容易受单 fold 分布影响。

## 10. 推荐模型配置

### 10.1 FAST-Tiny

用于 smoke / mini / 快速筛选。

```text
channels = 32
num_blocks = 6
kernel = 5
context = 3 branches
params target = < 1M
expected VRAM = very low
```

目标：

- 快速判断方向；
- 一天内多次试错；
- 用作 ablation 轻量版本。

### 10.2 FAST-Base

推荐主版本。

```text
channels = 48
num_blocks = 10
kernel = 5
context = 4 branches
params target = 1M 到 3M
expected VRAM = low to moderate
```

目标：

- 效率和效果平衡；
- 三数据集主力版本；
- 论文中作为 efficient model。

### 10.3 FAST-Large

用于冲指标。

```text
channels = 64
num_blocks = 12
kernel = 7
context = 4 branches
params target = 3M 到 6M
expected VRAM = moderate
```

目标：

- 如果 FAST-Base 接近 SOTA，再用 FAST-Large 冲刺；
- 不建议一开始就用 Large。

## 11. 损失函数

FAST-Net 的损失需要比 PAST-Net 更简单，避免训练慢。

推荐：

```text
L = L1
  + 0.05 * L_gradient
  + 0.001 * L_residual
```

### 11.1 L1 loss

主损失：

```text
L1 = |Y_hat - Y|
```

选择 L1 而不是复杂 perceptual / GAN loss，是为了：

- 稳；
- 快；
- 主表指标友好；
- 医学图像更容易解释。

### 11.2 Gradient loss

用于边界保持：

```text
L_gradient =
  |grad_x(Y_hat) - grad_x(Y)|
+ |grad_y(Y_hat) - grad_y(Y)|
```

权重：

```text
0.05
```

### 11.3 Residual regularization

用于防止大面积乱改：

```text
L_residual = |Y_hat - C|
```

权重：

```text
0.001
```

### 11.4 可选 symmetry loss

如果速度允许，可以加入：

```text
L_sym = |f(L, R, p) - f(R, L, 1-p)|
```

但注意 symmetry 会多一次 forward，训练时间接近翻倍。

因此 FAST-Net 第一版不默认开启 symmetry loss，只在以下情况开启：

- NingXia 不稳定；
- offset 1 / offset 3 明显不对称；
- 模型过拟合某个方向。

## 12. 训练策略

### 12.1 第一阶段：FAST-Tiny 试错

先用 FAST-Tiny 跑：

```text
IXI smoke / mini
```

目标：

- 验证结构能训练；
- 看是否超过 ResUNet residual；
- 看是否接近 HAT / SMamba；
- 检查 residual 和 confidence map。

如果 FAST-Tiny 都明显有效，再上 FAST-Base。

### 12.2 第二阶段：FAST-Base full_test115

在 IXI 上跑 full_test115：

目标：

- 作为主表候选；
- 对比 I3Net / HAT / SMamba；
- 记录速度、显存、训练时间。

如果 IXI 明显低于 HAT/SMamba，则需要调整结构，不要急着扩三数据集。

### 12.3 第三阶段：fastMRI full

fastMRI 样本数比 IXI 少，但图像差异更复杂。

FAST-Net 在 fastMRI 上重点看：

- 是否超过 ResUNet residual；
- 是否接近 SAINT/HAT；
- 是否在 NCC 上稳定；
- 是否比重模型训练快很多。

### 12.4 第四阶段：NingXia 8-fold CV

NingXia 是 FAST-Net 的重点验证场景。

原因：

- 轻量模型不容易过拟合；
- residual gate 有利于外部数据稳定；
- case-level CV 更能体现泛化。

重点看：

- mean；
- std；
- 每 fold 是否稳定；
- 是否某些 fold 明显优于 HAT/SwinIR。

## 13. 效率评估指标

FAST-Net 必须额外报告效率。

建议记录：

| 指标 | 说明 |
|---|---|
| Params | 参数量 |
| FLOPs / MACs | 计算量 |
| Peak VRAM | 峰值显存 |
| Train sec/epoch | 每 epoch 时间 |
| Inference ms/slice | 单 slice 推理时间 |
| Inference sec/case | 单 case 推理时间 |
| Batch capacity | 23.5GB 显存下最大 batch |

论文中可以增加一张 efficiency table：

| Method | Params | VRAM | Time | PSNR | SSIM |
|---|---:|---:|---:|---:|---:|
| SwinIR | high | high | slow | strong | strong |
| HAT | high | high | slow | strong | strong |
| SMamba | medium/high | medium/high | medium | strong | strong |
| I3Net | task-specific | medium | medium | very strong | very strong |
| FAST-Net | low | low | fast | close to SOTA | close to SOTA |

## 14. 消融实验

### 14.1 必做消融

| Variant | 目的 |
|---|---|
| FAST-Net full | 主模型 |
| w/o phase FiLM | 证明 phase 调制有效 |
| w/o confidence gate | 证明空间残差门控有效 |
| w/o multi-scale context | 证明多尺度上下文有效 |
| w/o residual regularization | 证明残差约束稳定 |
| 3x3 conv only | 证明 large-kernel depthwise 有效 |
| no D/A input | 证明 slice difference 输入有效 |

### 14.2 速度消融

| Version | 目的 |
|---|---|
| FAST-Tiny | 最轻量 |
| FAST-Base | 主版本 |
| FAST-Large | 冲指标 |

需要同时报告：

- 指标；
- 参数量；
- 显存；
- 训练时间；
- 推理时间。

## 15. 预期优缺点

### 15.1 优点

FAST-Net 的优势：

1. 训练快；
2. 显存低；
3. 容易扩三数据集；
4. 容易扩 x2/x4/x6；
5. residual 输出稳定；
6. 对 NingXia 可能更稳；
7. 可作为论文里的 efficient baseline / lightweight model；
8. 模块简单，消融清楚；
9. 不依赖复杂第三方库；
10. 失败时容易定位问题。

### 15.2 缺点

潜在不足：

1. IXI 上可能难以超过 I3Net；
2. 极细结构恢复可能弱于 HAT；
3. 没有重 attention，长程建模上限有限；
4. 如果 residual gate 过保守，可能接近 Linear；
5. 如果 confidence map 学不好，可能整体欠拟合。

## 16. 风险与应对

### 16.1 模型太保守

表现：

- PSNR 比 Linear 高不多；
- residual map 很弱；
- confidence map 接近 0。

应对：

- 降低 residual regularization；
- 增大 alpha；
- 去掉或放松 confidence gate；
- 增加 blocks；
- 增加 channels。

### 16.2 模型乱改

表现：

- MAE/MSE 不稳；
- NingXia 某些 fold 崩；
- residual 大面积高响应；
- 背景出现伪影。

应对：

- 增大 residual regularization；
- 降低 alpha；
- 加 symmetry loss；
- 加强 confidence gate；
- 减小 model size。

### 16.3 IXI 强但 NingXia 弱

表现：

- IXI 接近 HAT/SMamba；
- NingXia 不如 ResUNet 或波动大。

应对：

- 使用 FAST-Tiny/FAST-Base 而不是 Large；
- 增加 residual regularization；
- 使用 stronger data augmentation；
- 加 symmetry loss；
- 检查 normalization。

### 16.4 速度仍然不够快

应对：

- channels 48 改 32；
- blocks 10 改 6；
- 删除 dilation branch；
- kernel 7 改 5；
- ECA 替代 SE；
- 关闭 symmetry loss；
- 使用 AMP；
- 提高 batch，减少梯度累积。

## 17. 推荐实现文件结构

建议先实现 IXI：

```text
ixi_fastnet_2p5d/
  __init__.py
  settings.py
  data.py
  model.py
  train.py
  run_all.py
  paper_table.py
  visual_qc.py
```

后续扩展：

```text
fastmri_brain_fastnet_2p5d/
processing.run_ningxia_case_cv --models fastnet
```

必须复用当前统一口径：

- IXI full_test115；
- fastMRI full；
- NingXia 8-fold case-level CV；
- 当前 metrics；
- 当前 paper_table 格式；
- 当前主表列顺序。

## 18. 推荐实验顺序

### Step 1：实现 FAST-Tiny

目的：

- 快速验证结构；
- 检查输出；
- 看是否明显超过 Linear / ResUNet。

### Step 2：IXI mini

如果 FAST-Tiny 有希望，继续。

如果没有希望，先调：

- alpha；
- confidence gate；
- phase FiLM；
- residual loss。

### Step 3：FAST-Base IXI full_test115

作为正式候选。

### Step 4：fastMRI full

看泛化和速度。

### Step 5：NingXia CV

重点验证外部临床稳定性。

### Step 6：FAST-Large 冲刺

只有 FAST-Base 接近第一梯队时才跑 Large。

### Step 7：x2 / x6 扩展

如果 x4 成立，再扩展多倍率。

## 19. 和 PAST-Net 的关系

| 项目 | PAST-Net | FAST-Net |
|---|---|---|
| 目标 | 冲三数据集 SOTA | 效率优先，接近 SOTA |
| 结构复杂度 | 中高 | 低中 |
| 是否用复杂 fusion | 是 | 简化 |
| 是否默认 symmetry | 是 | 否，可选 |
| 是否可能加 Mamba | 是 | 后续可选 |
| 是否适合快速扩数据集 | 中 | 强 |
| 论文角色 | 主模型候选 | 轻量高效模型 / 主模型候选 |

如果 FAST-Net 效果已经很接近 SOTA，它反而可能比 PAST-Net 更适合作为论文主模型，因为效率优势更好讲。

如果 FAST-Net 效果略低，但速度明显更快，可以作为：

- efficient variant；
- ablation backbone；
- deployment-friendly model；
- 主模型中 residual branch 的 lightweight version。

## 20. 论文叙事

FAST-Net 可以支撑的论文叙事：

> Existing high-performing interpolation and restoration models often rely on heavy backbones or task-specific complex designs. We show that a lightweight phase-adaptive residual formulation, guided by coarse interpolation and spatial confidence gating, can achieve competitive through-plane interpolation performance with substantially lower computational cost.

中文表达：

> 现有强方法往往依赖较重的 Transformer、复杂任务网络或生成式 refinement。我们证明，在医学 T2 层间插值中，只要充分利用 coarse interpolation、phase 位置、slice difference 和空间残差门控，一个轻量网络也可以达到接近 SOTA 的性能，并显著降低训练和推理成本。

核心 claim：

1. Efficient phase adaptation is sufficient for strong through-plane interpolation；
2. Coarse-guided bounded residual learning improves stability；
3. Spatial confidence gating prevents over-correction under clinical domain shift；
4. Lightweight multi-scale depthwise context is a strong alternative to heavy attention。

## 21. 最终建议

FAST-Net 是一个值得优先实现的第二模型方向。

推荐第一版：

```text
FAST-Base
input_channels = 6
channels = 48
num_blocks = 10
depthwise_kernel = 5
context_branches = [3x3, 5x5, 7x7, dilated 3x3]
phase_film = true
confidence_gate = true
bounded_residual = true
loss = L1 + 0.05 gradient + 0.001 residual
```

如果它能在 IXI 接近 HAT/SMamba，在 fastMRI 接近 SAINT/HAT，在 NingXia 进入第一梯队，同时训练速度和显存明显优于重模型，那么它就非常有论文价值。

如果它进一步接近或超过 I3Net，那么可以考虑把 FAST-Net 作为主模型，把 PAST-Net 的复杂模块作为增强版或 ablation。
