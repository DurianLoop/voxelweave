# Design 4：SCPI-Net，连续尺度相位感知 T2 层间插值

更新时间：2026-07-06

本文档对应“连续 z 轴 / Scale-Continuous Slice Interpolation”方向。该方向不再为 x2、x4、x6 分别设计模型，而是训练一个可以处理任意中间位置和任意 through-plane scale 的统一模型。

暂定模型名：

```text
SCPI-Net
Scale-Continuous Phase-aware Interpolation Network
```

中文名称：

```text
连续尺度相位感知层间插值网络
```

## 1. 核心动机

当前实验主线是 x4，但后续希望补 x2 和 x6，做成类似 I3Net 的超大表。

如果每个 scale 都单独训练模型，会有几个问题：

1. 训练成本高；
2. 模型数量多；
3. 论文叙事像工程堆表；
4. 无法处理未见过的 spacing；
5. 真实 MRI through-plane spacing 并不总是固定 x2/x4/x6。

SCPI-Net 的目标是：

```text
一个模型支持任意 p 和任意 scale
```

即：

```text
f(L, R, p, scale) -> target slice at relative position p
```

其中：

```text
p in (0, 1)
scale in {2, 4, 6} or continuous
```

## 2. 论文核心观点

可以这样定义问题：

> MRI through-plane interpolation is inherently continuous along the slice direction. Fixed-scale models trained separately for x2/x4/x6 ignore the continuous nature of anatomical transitions and are inefficient to extend across acquisition spacings.

中文：

> MRI 层间结构变化本质上是连续的。固定倍率模型只能处理预设 spacing，不能自然泛化到不同层厚或不同缺失间隔。

SCPI-Net 的贡献：

1. 统一 x2/x4/x6 的 scale-continuous 框架；
2. 显式使用 phase p；
3. 用 coarse interpolation 提供稳定低频先验；
4. 用条件残差网络学习连续 z 轴结构变化；
5. 评价 seen-scale 和 unseen-phase 泛化能力。

## 3. 任务定义

给定两个 anchor slice：

```text
L = S0
R = Ss
```

其中 s 是 scale / stride。

目标是预测：

```text
Sk, k = 1 ... s-1
```

定义：

```text
p = k / s
```

于是：

```text
Y_hat = f(L, R, p, s)
```

具体：

| Scale | Targets | Phase |
|---|---|---|
| x2 | S1 | 0.5 |
| x4 | S1, S2, S3 | 0.25, 0.5, 0.75 |
| x6 | S1...S5 | 1/6, 2/6, 3/6, 4/6, 5/6 |

## 4. 输入设计

基础输入：

```text
Input = [L, R, C, P, S, D, A]
```

其中：

| Symbol | Meaning |
|---|---|
| L | left anchor |
| R | right anchor |
| C | linear coarse interpolation |
| P | phase map |
| S | scale map |
| D | R - L |
| A | abs(R - L) |

coarse interpolation：

```text
C = (1 - p) * L + p * R
```

phase map：

```text
P[i, j] = p
```

scale map：

```text
S[i, j] = normalized scale
```

建议 scale normalization：

```text
s_norm = log(s) / log(6)
```

这样 x2/x4/x6 都在合理范围。

## 5. 模型结构

推荐结构：

```text
[L, R, C, P, S, D, A]
          |
          v
Scale-phase encoder
          |
          v
Conditional residual backbone
          |
          v
Continuous residual head
          |
          v
Y_hat = C + R(p, s)
```

### 5.1 Scale-phase encoder

把 p 和 s 同时编码：

```text
z = MLP([p, s_norm, sin(pi*p), cos(pi*p)])
```

输出：

```text
gamma_l, beta_l for each layer
```

用于 FiLM 调制：

```text
F_l = gamma_l(z) * F_l + beta_l(z)
```

这样模型不只是把 p/s 当输入图，而是在每层动态调整特征变换。

### 5.2 Conditional residual backbone

推荐 backbone：

- depthwise separable conv；
- residual blocks；
- light window attention optional；
- local-global context block optional。

第一版建议轻量：

```text
channels = 48
blocks = 10
kernel = 5
FiLM every 2 blocks
```

### 5.3 Continuous residual head

输出：

```text
R_raw = Head(F, z)
Y_hat = C + alpha(s) * tanh(R_raw)
```

alpha 可以和 scale 相关：

```text
alpha(s) = alpha0 * g(s)
```

原因：

- x2 间隔小，残差应小；
- x6 间隔大，残差可能更大；
- scale-aware residual amplitude 更合理。

## 6. 训练策略

### 6.1 Multi-scale mixed training

每个 batch 混合不同 scale：

```text
scale sampled from {2, 4, 6}
```

对每个 scale，随机采样 target offset：

```text
k sampled from 1 ... scale-1
p = k / scale
```

这样一个模型同时学习 x2/x4/x6。

### 6.2 Curriculum training

建议训练顺序：

1. 先训练 x2；
2. 加入 x4；
3. 加入 x6；
4. 最后 multi-scale joint finetune。

原因：

- x2 最容易；
- 先学稳定短距离插值；
- 再学更大 through-plane gap。

### 6.3 Scale-balanced sampling

不能让 x6 因为 target 多而占据过多 batch。

建议：

```text
P(scale=2) = 1/3
P(scale=4) = 1/3
P(scale=6) = 1/3
```

每个 scale 内再随机 offset。

### 6.4 Dataset strategy

第一步：

```text
IXI multi-scale smoke
```

第二步：

```text
IXI full multi-scale
```

第三步：

```text
fastMRI multi-scale
```

第四步：

```text
NingXia multi-scale CV
```

## 7. 损失函数

基础：

```text
L = L1 + 0.05 * L_grad + 0.001 * L_res
```

### 7.1 Phase consistency loss

对于同一组 L/R，可以预测多个 phase。

要求 z 轴变化平滑：

```text
Y_p1, Y_p2, Y_p3
```

加入：

```text
L_zsmooth = |Y_p2 - 0.5*(Y_p1 + Y_p3)|
```

尤其适合 x4 的 0.25/0.5/0.75。

### 7.2 Scale consistency loss

同一个物理位置可由不同 scale 组合得到。

例如：

```text
x4 p=0.5 等价于 x2 p=0.5
```

如果数据构造允许，可加入：

```text
L_scale = |f_x4(p=0.5) - f_x2(p=0.5)|
```

这可以证明模型真的学习连续尺度，而不是记住 scale 标签。

### 7.3 Symmetry loss

```text
f(L, R, p, s) ≈ f(R, L, 1-p, s)
```

对连续 phase 尤其重要。

## 8. 评价设计

### 8.1 Seen-scale evaluation

分别评估：

- x2；
- x4；
- x6。

和单独训练模型比较：

```text
SCPI-Net joint model vs scale-specific model
```

### 8.2 Cross-scale generalization

训练：

```text
x2 + x4
```

测试：

```text
x6
```

或者：

```text
train x2 + x6, test x4
```

这能形成很强论文亮点：

```text
unseen scale interpolation
```

### 8.3 Per-phase evaluation

统计每个 phase 的指标。

x6 中尤其重要：

```text
p = 1/6, 2/6, 3/6, 4/6, 5/6
```

看模型是否在靠近 anchor 和中间位置都稳定。

### 8.4 One model vs many models

效率表：

| Setting | Number of models | Total training time | Total storage | Mean metric |
|---|---:|---:|---:|---:|
| Separate x2/x4/x6 | 3 | high | high | strong |
| SCPI-Net | 1 | lower | lower | close/strong |

## 9. 消融实验

| Variant | 目的 |
|---|---|
| Full SCPI-Net | 主模型 |
| w/o scale input | 证明 scale 条件必要 |
| w/o phase FiLM | 证明 phase 条件调制必要 |
| phase map only | 比较 FiLM 和输入图方式 |
| w/o z-smooth loss | 证明连续性约束有效 |
| w/o scale consistency | 证明跨尺度一致性有效 |
| train single-scale | 证明 joint training 价值 |

## 10. 论文卖点

SCPI-Net 的论文亮点：

1. 从 fixed-scale interpolation 转向 scale-continuous interpolation；
2. 一个模型统一 x2/x4/x6；
3. 可处理 unseen scale / unseen phase；
4. 更符合真实 MRI slice spacing 连续变化；
5. 降低训练和维护成本；
6. 支撑超大多倍率表格。

## 11. 风险与应对

### 11.1 多尺度混训导致每个 scale 都不最优

应对：

- 使用 scale-balanced sampler；
- 加 scale-specific adapter；
- 最后对 x4 做轻量 finetune；
- 使用 LoRA-like scale adapter。

### 11.2 x6 太难拖累训练

应对：

- curriculum；
- 先 x2/x4；
- x6 后加入；
- x6 loss 权重先小后大。

### 11.3 phase 条件没有被利用

应对：

- 使用 FiLM；
- 加 per-phase diagnostic；
- 加 symmetry loss；
- 可视化不同 p 的 residual。

## 12. 最终定位

SCPI-Net 是非常适合作为顶会/顶刊主线的方向，因为它改变了问题定义：

```text
从固定倍率插值，变成连续尺度层间重建。
```

如果它能在 x2/x4/x6 上接近或超过单尺度强 baseline，并展示 unseen-scale 泛化能力，论文价值会明显高于单纯 x4 刷表。
