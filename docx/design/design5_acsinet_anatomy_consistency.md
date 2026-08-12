# Design 5：ACSI-Net，解剖一致性 T2 层间插值

更新时间：2026-07-06

本文档对应“解剖一致性 / Anatomy-Consistent Interpolation”方向。该方向强调 MRI 层间插值的最终目标不是生成单张 2D 图像，而是恢复一个在 z 轴上解剖连续、结构可信的 3D volume。

暂定模型名：

```text
ACSI-Net
Anatomy-Consistent Slice Interpolation Network
```

中文名称：

```text
解剖一致性层间插值网络
```

## 1. 核心动机

当前主表指标是 slice-level 或 volume-averaged 的 PSNR / SSIM / MAE / MSE / NCC。它们能衡量像素误差，但不一定能衡量 3D anatomy 是否连续。

可能出现的问题：

1. 单张 slice PSNR 高，但 3D 结构有轻微断裂；
2. z 轴边界跳变；
3. 脑室或皮层结构不连续；
4. 小结构在相邻切片中忽隐忽现；
5. 插值后 volume 对下游任务不友好。

ACSI-Net 的核心观点：

> MRI through-plane interpolation should optimize anatomical coherence across the reconstructed 3D volume, not only per-slice fidelity.

## 2. 研究问题升级

普通定义：

```text
给定 L/R，预测中间 slice Y
```

ACSI-Net 的定义：

```text
给定稀疏 volume，恢复解剖连续的 dense volume
```

这意味着模型需要考虑：

- 单 slice fidelity；
- 相邻预测 slice 之间的连续性；
- anchor slice 与预测 slice 的一致性；
- z-direction gradient；
- 3D edge / surface continuity；
- downstream anatomical stability。

## 3. 输入输出设计

对于 x4，输入：

```text
S0, S4
```

输出不是单独预测 S1/S2/S3，而是一次性预测一个中间 slice group：

```text
Y_hat_group = [S1_hat, S2_hat, S3_hat]
```

这样模型可以直接建模：

```text
S0 -> S1 -> S2 -> S3 -> S4
```

的 z 轴连续变化。

基础输入：

```text
[S0, S4, C1, C2, C3, P1, P2, P3, D, A]
```

其中：

- C1/C2/C3 是 linear coarse；
- P1/P2/P3 是 phase map；
- D = S4 - S0；
- A = abs(S4 - S0)。

第一版为了简单，也可以逐 slice 预测，但训练时加入 group consistency。

## 4. 模型结构

推荐结构：

```text
Sparse anchor encoder
        |
        v
Phase-conditioned group decoder
        |
        v
3-slice prediction group
        |
        v
Anatomy consistency regularization
```

### 4.1 Anchor encoder

编码两端 anchor：

```text
F0 = E(S0)
F4 = E(S4)
```

融合：

```text
F = Fuse(F0, F4, D, A)
```

### 4.2 Group decoder

一次输出多个 phase：

```text
Y1_hat, Y2_hat, Y3_hat = Decoder(F, p=[0.25, 0.5, 0.75])
```

输出形式仍然建议 residual：

```text
Yk_hat = Ck + Rk
```

### 4.3 Shared decoder with phase tokens

更优雅的做法：

```text
for p in [0.25, 0.5, 0.75]:
    token_p = MLP(p)
    Y_p = Decoder(F, token_p)
```

三个 phase 共享 decoder，但使用不同 phase token。

### 4.4 z-context module

在输出 group 后加一个轻量 z-context refinement：

```text
Stack = [S0, Y1, Y2, Y3, S4]
Stack_refined = 3D depthwise conv over z
```

注意不要用重 3D CNN。只需要非常浅的 3D refinement：

```text
Conv3D kernel=(3,3,3), groups/channel-wise optional
```

目的是修正 z 轴不连续，而不是重新生成图像。

## 5. 解剖一致性损失

### 5.1 Slice reconstruction loss

```text
L_rec = sum_k L1(Yk_hat, Yk)
```

### 5.2 z-gradient consistency

真实 dense stack：

```text
T = [S0, S1, S2, S3, S4]
```

预测 stack：

```text
P = [S0, Y1_hat, Y2_hat, Y3_hat, S4]
```

z-gradient：

```text
grad_z(T)_i = T_{i+1} - T_i
grad_z(P)_i = P_{i+1} - P_i
```

损失：

```text
L_zgrad = L1(grad_z(P), grad_z(T))
```

### 5.3 z-Laplacian smoothness

二阶差分：

```text
lap_z(S_i) = S_{i-1} - 2*S_i + S_{i+1}
```

损失：

```text
L_zlap = L1(lap_z(P), lap_z(T))
```

这能约束 z 轴结构变化的曲率，避免忽然跳变。

### 5.4 Edge continuity loss

对每张 slice 计算 edge：

```text
E_i = grad_xy(S_i)
```

要求 edge 在 z 轴上连续：

```text
L_edge_z = L1(grad_z(edge(P)), grad_z(edge(T)))
```

重点保护：

- 脑室边界；
- 皮层边界；
- 高梯度组织边缘。

### 5.5 Anatomy mask weighted loss

如果没有 segmentation mask，可以用 coarse edge / brain mask 近似。

定义：

```text
W_anat = normalize(grad(C) + abs(R-L))
```

加权重建：

```text
L_anat = W_anat * |Y_hat - Y|
```

结构变化区域权重更高。

### 5.6 总损失

推荐：

```text
L_total =
    L_rec
  + 0.05 * L_grad_xy
  + 0.05 * L_zgrad
  + 0.02 * L_zlap
  + 0.05 * L_edge_z
  + 0.001 * L_res
```

## 6. 评价指标

除了主表指标，ACSI-Net 必须增加 3D consistency 指标。

### 6.1 z-gradient error

```text
ZGE = mean(|grad_z(P) - grad_z(T)|)
```

越低越好。

### 6.2 z-Laplacian error

```text
ZLE = mean(|lap_z(P) - lap_z(T)|)
```

越低说明 z 轴二阶变化更接近真实。

### 6.3 Inter-slice NCC consistency

比较真实和预测 stack 的相邻 NCC：

```text
NCC(S_i, S_{i+1})
```

看 z 轴相邻相关性是否匹配真实 volume。

### 6.4 3D volume visual QC

保存：

- axial view；
- sagittal reformat；
- coronal reformat；
- z-profile line plot；
- error volume projection。

特别重要的是 sagittal/coronal，因为 through-plane 问题在重建平面上更容易暴露。

### 6.5 Downstream stability

如果有可用分割工具，可以做：

```text
interpolated volume -> segmentation -> anatomical consistency
```

即使不做复杂 segmentation，也可以做 brain mask / edge continuity。

## 7. 训练路线

### Stage 0：逐 slice 模型 + consistency loss

先不改太多架构，只在现有 single-slice 框架中加入：

- z-gradient loss；
- z-laplacian loss；
- edge-z loss。

目的：快速验证 anatomy consistency 是否有效。

### Stage 1：group prediction

一次输出 x4 的 3 张中间 slice。

好处：

- 三张预测互相协调；
- z 轴 loss 更自然；
- 更接近 3D volume recovery。

### Stage 2：IXI full_test115

重点看：

- 主表指标是否不掉；
- z-consistency 是否提升；
- sagittal/coronal 视觉是否更连续。

### Stage 3：fastMRI full

fastMRI slice 数少，z 轴建模更难，适合验证 consistency 是否有帮助。

### Stage 4：NingXia CV

看外部临床数据上是否减少结构断裂和 fold 波动。

## 8. 消融实验

| Variant | 目的 |
|---|---|
| Full ACSI-Net | 主模型 |
| w/o z-gradient loss | 证明一阶 z 连续性有效 |
| w/o z-laplacian loss | 证明二阶平滑有效 |
| w/o edge-z loss | 证明边界连续性有效 |
| single-slice output | 证明 group prediction 有效 |
| w/o 3D refinement | 证明轻量 z-context 有效 |
| no anatomy weighting | 证明结构区域加权有效 |

## 9. 论文卖点

ACSI-Net 的强点是把任务从 2D 指标提升到 3D 解剖合理性。

可写 claim：

1. Slice-level metrics are insufficient for through-plane interpolation；
2. ACSI-Net restores anatomically coherent dense volumes；
3. z-gradient and edge-continuity losses improve 3D structural consistency；
4. group prediction reduces inter-slice discontinuity；
5. 三数据集上在保持主表指标的同时提升 3D consistency。

## 10. 风险与应对

### 10.1 z-smooth 过强导致过平滑

应对：

- 降低 z-laplacian 权重；
- 保留 edge-z loss；
- 增加 reconstruction loss 权重；
- 只在结构区域做 z consistency。

### 10.2 group prediction 显存变大

应对：

- shared decoder；
- channels 降低；
- 先用 x4；
- 不使用重 3D CNN；
- 只在 head 处做 3D refinement。

### 10.3 主表指标略降

应对：

- 把 ACSI-Net 定位为 anatomy-consistent model；
- 同时报告 3D 指标；
- 做 visual QC；
- 做下游稳定性。

## 11. 最终定位

ACSI-Net 不一定必须 PSNR 第一。它的论文价值在于：

```text
从单张切片重建，提升到 3D 解剖连续体重建。
```

如果它能在主表指标接近第一梯队的同时显著提升 z-axis consistency 和 sagittal/coronal visual quality，这是一条非常适合医学影像顶刊的路线。
