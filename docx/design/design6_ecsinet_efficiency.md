# Design 6：ECSI-Net，高效临床 T2 层间插值

更新时间：2026-07-06

本文档对应“高效临床插值 / Efficiency-First Clinical Interpolation”方向。该方向不只追求最高 PSNR，而是追求质量、速度、显存、训练成本之间的最优 Pareto trade-off。

暂定模型名：

```text
ECSI-Net
Efficient Clinical Slice Interpolation Network
```

中文名称：

```text
高效临床层间插值网络
```

## 1. 核心动机

当前强 baseline 中，HAT、SMamba、diffusion/refinement 类方法通常训练慢、显存高、扩展三数据集成本大。I3Net 任务匹配强，但如果后续要扩 x2/x4/x6、多数据集、多消融、多 fold，计算成本仍然很重要。

ECSI-Net 的目标是：

```text
用明显更低的计算成本达到接近 SOTA 的效果。
```

这条线的论文价值在于：

> 临床 MRI 层间插值需要可以大规模、快速、稳定部署的模型，而不只是离线刷表的重模型。

## 2. 目标定义

ECSI-Net 的成功不是单看 PSNR 第一，而是看 Pareto frontier。

目标：

| 维度 | 目标 |
|---|---|
| Quality | 接近 I3Net/HAT/SwinIR/SAINT 第一梯队 |
| Params | 明显低于重 Transformer |
| VRAM | 23.5GB 显存下可大 batch 训练 |
| Training | 每 epoch 时间显著低于 HAT/SMamba |
| Inference | 可快速处理 whole volume |
| Robustness | NingXia CV 稳定 |
| Extension | x2/x4/x6 容易扩展 |

## 3. 核心设计原则

### 3.1 任务先验优先于大模型

不用重 backbone 硬学一切，而是显式提供：

- linear coarse；
- phase；
- left/right anchor；
- slice difference；
- residual output。

### 3.2 只在必要位置计算

MRI 切片中大量区域是背景或低变化区域。ECSI-Net 应减少无意义计算。

可以设计：

```text
change-aware residual computation
```

即变化大的区域强修正，变化小的区域少修正。

### 3.3 轻量模块替代重 attention

使用：

- depthwise conv；
- grouped conv；
- pointwise conv；
- ECA；
- large-kernel depthwise；
- dynamic residual gate。

避免第一版使用：

- full attention；
- large HAT blocks；
- diffusion sampling；
- heavy 3D CNN。

## 4. 输入输出

输入：

```text
[L, R, C, P, D, A]
```

输出：

```text
Y_hat = C + M * R
```

其中：

- C 是 coarse；
- R 是 residual；
- M 是 change-aware mask / confidence gate。

ECSI-Net 的关键是 M：

```text
M = g(A, grad(C), learned feature)
```

M 越小，越接近 Linear；M 越大，模型修正越强。

## 5. 模型结构

```text
Input
  |
  v
Ultra-light stem
  |
  v
Change-aware mask branch
  |
  v
Efficient residual branch
  |
  v
Shared refinement blocks
  |
  v
Residual output
  |
  v
C + M * R
```

### 5.1 Ultra-light stem

```text
Conv 3x3, 6 -> C
GELU
DepthwiseConv 3x3
PointwiseConv 1x1
```

推荐：

```text
C = 32 or 48
```

### 5.2 Change-aware mask branch

输入：

```text
A = |R - L|
grad(C)
feature F
```

输出：

```text
M in [0, 1]
```

可初始化为偏保守：

```text
M bias < 0
```

这样训练初期输出接近 Linear，稳定。

### 5.3 Efficient residual branch

残差分支使用 E-Blocks：

```text
E-Block:
  1x1 expansion
  depthwise 5x5
  GELU
  ECA
  1x1 projection
  residual add
```

推荐：

```text
channels = 48
blocks = 8
```

### 5.4 Optional early-exit head

为了效率，可以设计 early-exit：

```text
Head-1 after 4 blocks
Head-2 after 8 blocks
```

对于简单 slice，Head-1 已足够；对于困难 slice，使用 Head-2。

训练时两个 head 都监督：

```text
L = L_head1 + L_head2
```

推理时可以根据 mask/uncertainty 决定是否 early exit。

第一版可以先不做 early-exit，第二版加入。

## 6. 损失函数

基础：

```text
L = L1 + 0.05 * L_grad + 0.001 * L_res
```

### 6.1 Mask sparsity regularization

希望模型不要全图大修：

```text
L_mask = mean(M)
```

权重：

```text
lambda_mask = 0.0005 to 0.002
```

注意权重不能过大，否则模型退化到 Linear。

### 6.2 Change-aware mask guidance

用 A 和 grad(C) 给 mask 弱监督：

```text
M_prior = normalize(A + grad(C))
L_mask_prior = L1(M, M_prior)
```

权重很小：

```text
lambda_prior = 0.01
```

### 6.3 总损失

```text
L_total =
    L1(Y_hat, Y)
  + 0.05 * L_grad
  + 0.001 * L_res
  + 0.001 * L_mask
  + 0.01 * L_mask_prior
```

## 7. 效率评价

ECSI-Net 必须建立完整 efficiency table。

记录：

| 指标 | 含义 |
|---|---|
| Params | 参数量 |
| MACs/FLOPs | 计算量 |
| Peak VRAM | 峰值显存 |
| Batch max | 最大 batch |
| sec/epoch | 每 epoch 时间 |
| it/s | 训练吞吐 |
| ms/slice | 单 slice 推理 |
| sec/case | 单 case 推理 |
| energy proxy | 可选，用 GPU time 近似 |

主表之外额外做：

```text
Quality-Efficiency Pareto plot
```

x 轴：

```text
inference time / params / VRAM
```

y 轴：

```text
PSNR / SSIM / NCC
```

目标是让 ECSI-Net 位于 Pareto frontier 上。

## 8. 训练策略

### Stage 0：速度 profile

先不跑 full，先测：

- batch 8/16/32/64；
- AMP on/off；
- channels 32/48；
- blocks 6/8/10；
- it/s；
- VRAM。

找到最优配置再正式跑。

### Stage 1：IXI mini

目标：

- 验证质量不差；
- 速度明显快；
- mask 不退化。

### Stage 2：IXI full_test115

记录：

- 主表指标；
- 训练时间；
- 推理时间；
- 显存；
- params。

### Stage 3：fastMRI full

看复杂数据下是否保持高吞吐和稳定质量。

### Stage 4：NingXia CV

看小样本临床数据上是否因为轻量和 mask 更稳。

## 9. 消融实验

| Variant | 目的 |
|---|---|
| Full ECSI-Net | 主模型 |
| w/o mask branch | 证明 change-aware mask 有效 |
| w/o mask sparsity | 证明 mask 正则有效 |
| w/o mask prior | 证明先验引导有效 |
| channels 32/48/64 | 速度-质量权衡 |
| blocks 4/8/12 | 深度权衡 |
| kernel 3/5/7 | 感受野权衡 |
| early-exit on/off | 推理效率权衡 |

## 10. 论文卖点

ECSI-Net 的论文可以不主打绝对第一，而主打：

1. 接近 SOTA 的质量；
2. 显著更低显存；
3. 显著更快训练；
4. 显著更快推理；
5. 更适合临床批量重建；
6. 在三数据集和 NingXia CV 上稳定；
7. 位于 quality-efficiency Pareto frontier。

可以写：

> We demonstrate that task-aware efficient residual interpolation can achieve a better quality-efficiency trade-off than heavy generic restoration backbones for clinical MRI through-plane interpolation.

## 11. 风险与应对

### 11.1 模型过轻，指标不够

应对：

- channels 32 -> 48；
- blocks 6 -> 10；
- 加 large-kernel branch；
- 加 phase FiLM；
- 用 FAST-Net/PAST-Net 模块增强。

### 11.2 mask 过稀疏，退化到 Linear

应对：

- 降低 `lambda_mask`；
- 增大 residual alpha；
- 去掉 mask bias；
- 检查 M 可视化。

### 11.3 mask 全 1，失去效率意义

应对：

- 增大 `lambda_mask`；
- 加 mask prior；
- 限制 residual branch；
- 使用 early-exit。

### 11.4 速度优势不明显

应对：

- 减少 blocks；
- depthwise 替代普通 conv；
- 删除 dilation；
- 用 channels=32；
- batch 放大；
- 用 AMP；
- 避免 symmetry 双 forward。

## 12. 最终定位

ECSI-Net 的目标是成为高效临床层间插值模型。

如果它做到：

```text
指标接近第一梯队
+ 训练/推理显著更快
+ 显存显著更低
+ NingXia 稳定
```

那么即使它不是每个指标第一，也具有很强论文价值。它可以作为独立论文方向，也可以作为最终大论文中的 efficient variant，与 PAST-Net / RASI-Net / SCPI-Net 形成互补。
