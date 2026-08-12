# Design 3：RASI-Net，可信不确定性感知 T2 层间插值

更新时间：2026-07-06

本文档对应“可信插值 / Reliability-Aware Slice Interpolation”方向。该方向不把唯一目标放在 PSNR 第一，而是把问题提升为医学图像层间插值中的可信重建：模型不仅要给出预测切片，还要告诉使用者哪里可靠、哪里可能错。

暂定模型名：

```text
RASI-Net
Reliability-Aware Slice Interpolation Network
```

中文名称：

```text
可信不确定性感知层间插值网络
```

## 1. 核心动机

当前主表方法主要输出一张 deterministic prediction：

```text
L, R, p -> Y_hat
```

但医学场景里，单张预测图不够。一个模型即使平均 PSNR 很高，也可能在脑室边界、小结构、病灶样异常、外部临床数据上产生局部错误。如果模型无法指出这些错误区域，临床可信度会弱。

RASI-Net 的核心目标是：

```text
prediction + confidence + uncertainty
```

即同时输出：

| 输出 | 含义 |
|---|---|
| Y_hat | 预测目标切片 |
| C_map | confidence map，模型认为可靠的位置 |
| U_map | uncertainty map，模型认为不确定的位置 |
| R_map | residual map，相对 coarse interpolation 的修正 |

论文核心观点：

> MRI through-plane interpolation should be accurate and reliability-aware. A clinically useful interpolation model should estimate where it may be wrong, not only produce a visually plausible slice.

## 2. 与 SOTA 导向模型的区别

RASI-Net 不一定第一目标就是三数据集 PSNR 最高，而是追求：

1. 指标接近第一梯队；
2. 错误区域可被 uncertainty map 捕捉；
3. 外部 NingXia 数据上更稳；
4. 能发现失败 case；
5. 能提供风险提示；
6. 能支撑医学可信 AI 论文叙事。

这类贡献即使 PSNR 只接近 SOTA，也可能比单纯刷表更容易被顶刊认可。

## 3. 当前任务设置

| 项目 | 设置 |
|---|---|
| Modality | T2 |
| Task | through-plane interpolation |
| Main scale | x4 |
| Extension | x2 / x6 |
| Datasets | IXI-T2, fastMRI-brain-T2 expanded, NingXia-T2 |
| Metrics | PSNR, SSIM, MAE, MSE, NCC |
| Extra metrics | calibration, error-uncertainty correlation, risk-coverage |

x4 下：

```text
输入: S0, S4, phase p
输出: S1/S2/S3 prediction + uncertainty
```

## 4. 输入设计

基础输入沿用当前任务先验：

```text
Input = [L, R, C, P, D, A]
```

其中：

| Symbol | Meaning |
|---|---|
| L | left anchor slice |
| R | right anchor slice |
| C | linear coarse interpolation |
| P | phase map |
| D | R - L |
| A | abs(R - L) |

可选增强：

```text
G = gradient magnitude of C
```

因为 uncertainty 往往在边界和结构变化处更高，引入 coarse gradient 有助于模型学习风险区域。

第一版建议：

```text
6-channel input
```

第二版再尝试：

```text
7-channel input = [L, R, C, P, D, A, grad(C)]
```

## 5. 模型输出

RASI-Net 输出三类图：

```text
R_raw = residual prediction
W = confidence map
S = log variance / uncertainty logits
```

最终预测：

```text
R = alpha * tanh(R_raw)
Y_hat = C + W * R
U = softplus(S)
```

其中：

- W in [0, 1]；
- U > 0；
- alpha 控制最大残差幅度；
- C 是 coarse interpolation。

## 6. 模型结构

推荐结构：

```text
[L, R, C, P, D, A]
        |
        v
Shared encoder
        |
        v
Phase-aware fusion
        |
        v
Reliability feature block
        |
        v
Three heads:
  residual head
  confidence head
  uncertainty head
        |
        v
Y_hat, W, U
```

### 6.1 Shared encoder

第一版不需要太重：

```text
Conv 3x3 -> GELU -> Conv 3x3
```

推荐 channels：

```text
48 or 64
```

### 6.2 Phase-aware fusion

和 PAST-Net 类似，但可以简化：

```text
F = Encoder([L, R, C, P, D, A])
F = PhaseFiLM(F, p)
```

PhaseFiLM：

```text
gamma, beta = MLP(p)
F = gamma * F + beta
```

### 6.3 Reliability feature block

推荐使用轻量 residual blocks：

```text
DepthwiseConv 5x5
PointwiseConv 1x1
Channel attention
Residual add
```

不建议第一版使用重 Transformer，因为 uncertainty 分支本身已经增加训练复杂度。

### 6.4 三头输出

```text
ResidualHead:
  Conv 3x3 -> GELU -> Conv 3x3 -> R_raw

ConfidenceHead:
  Conv 3x3 -> GELU -> Conv 1x1 -> sigmoid -> W

UncertaintyHead:
  Conv 3x3 -> GELU -> Conv 1x1 -> softplus/logvar -> U
```

## 7. 损失函数

RASI-Net 的核心是 uncertainty-aware loss。

### 7.1 Heteroscedastic regression loss

设：

```text
e = |Y - Y_hat|
s = log variance
```

损失：

```text
L_unc = exp(-s) * |Y - Y_hat| + lambda_s * s
```

含义：

- 如果模型认为某区域不确定，可以给更大的 variance；
- 但 log variance 本身有惩罚，不能无限变大；
- 真实误差大的区域应对应更高 uncertainty。

建议：

```text
lambda_s = 0.01 to 0.05
```

### 7.2 Reconstruction loss

保留普通重建损失：

```text
L_rec = L1(Y_hat, Y)
```

### 7.3 Gradient loss

保护结构边界：

```text
L_grad = L1(grad(Y_hat), grad(Y))
```

### 7.4 Residual regularization

避免乱改 coarse：

```text
L_res = L1(Y_hat, C)
```

### 7.5 Uncertainty calibration loss

让 uncertainty 与真实 error 对齐：

```text
E = normalize(|Y - Y_hat|)
U_norm = normalize(U)
L_cal = L1(U_norm, stopgrad(E))
```

注意 `stopgrad(E)`，避免模型通过改变 prediction 作弊。

### 7.6 总损失

第一版：

```text
L_total =
    L_rec
  + 0.5 * L_unc
  + 0.05 * L_grad
  + 0.001 * L_res
  + 0.05 * L_cal
```

如果训练不稳，先去掉 `L_cal`，只保留 `L_unc`。

## 8. 评价指标

除了主表指标，RASI-Net 必须增加可信性指标。

### 8.1 Error-uncertainty correlation

计算：

```text
corr(|Y - Y_hat|, U)
```

越高越好。

可分别统计：

- pixel-level；
- slice-level；
- case-level；
- edge-region；
- non-edge-region。

### 8.2 Risk-coverage curve

按 uncertainty 从低到高筛选像素或 slice：

```text
低 uncertainty 区域 -> 应该 error 更低
```

计算：

- coverage；
- retained MAE；
- retained PSNR；
- AURC。

如果模型能正确识别低风险区域，coverage 降低时 error 应快速下降。

### 8.3 Failure detection

以 case-level MAE 或 PSNR 定义失败 case：

```text
worst 10% cases = failure cases
```

用平均 uncertainty 预测 failure：

```text
score = mean(U)
```

评价：

- AUROC；
- AUPRC；
- top-k failure recall。

这对论文非常有价值。

### 8.4 Calibration plot

把 uncertainty 分桶：

```text
bin 1 ... bin N
```

看每个 bin 的平均 uncertainty 和真实平均 error 是否单调一致。

## 9. 可视化

每个数据集固定保存：

- left anchor；
- right anchor；
- coarse；
- prediction；
- target；
- absolute error；
- confidence map；
- uncertainty map；
- overlay(error, uncertainty)。

理想现象：

- uncertainty 在脑室边界、皮层边界、小结构处更高；
- 大 error 区域被 uncertainty 捕捉；
- 背景区域 uncertainty 较低；
- NingXia 的异常 case 有更高 case-level uncertainty。

## 10. 训练路线

### Stage 0：单 case overfit

目标：

- 确认 prediction 能拟合；
- uncertainty 不崩；
- W 不全 0；
- U 不全常数。

### Stage 1：IXI mini

看：

- PSNR 是否超过 ResUNet；
- uncertainty-error correlation 是否为正；
- risk-coverage 是否有效。

### Stage 2：IXI full_test115

正式统计：

- 主表指标；
- calibration；
- failure detection。

### Stage 3：fastMRI full

重点看：

- 外部 public 数据复杂性下 uncertainty 是否更有意义；
- 是否能识别低质量 volume。

### Stage 4：NingXia 8-fold CV

重点看：

- fold-level uncertainty；
- failure detection；
- clinical domain shift 下是否能提示风险。

## 11. 消融实验

| Variant | 目的 |
|---|---|
| Full RASI-Net | 主模型 |
| w/o uncertainty head | 证明可信性分支价值 |
| w/o confidence gate | 证明 W 对稳定重建有用 |
| w/o L_unc | 证明 heteroscedastic loss 有用 |
| w/o L_cal | 证明 calibration loss 有用 |
| w/o phase | 证明 phase 对 uncertainty 也有用 |
| residual direct output | 证明 coarse residual 稳定 |

## 12. 论文卖点

可以形成以下 claim：

1. 当前 MRI interpolation 方法只关注平均重建质量，缺少可靠性估计；
2. RASI-Net 同时输出 prediction 和 uncertainty；
3. uncertainty 能定位结构变化和潜在错误区域；
4. case-level uncertainty 能帮助发现失败 case；
5. 在三数据集上接近 SOTA，同时提供临床可信解释。

## 13. 风险与应对

### 13.1 uncertainty 变成常数

应对：

- 加 `L_cal`；
- 调低 `lambda_s`；
- 可视化 U；
- 检查 softplus/logvar 范围。

### 13.2 uncertainty 虚高

应对：

- 增大 log variance penalty；
- 对 U 加均值约束；
- 限制 U 最大值。

### 13.3 指标下降

应对：

- 先训练 reconstruction，再加入 uncertainty；
- 两阶段训练；
- 降低 uncertainty loss 权重。

## 14. 最终定位

RASI-Net 的价值不只是刷主表，而是把论文从“我提出一个更强网络”提升到：

```text
医学层间插值需要可信、可校准、可提示风险的重建框架。
```

如果 RASI-Net 主表指标接近 I3Net/HAT/SwinIR，同时 uncertainty 能可靠定位错误区域，这条线具有很强顶刊潜力。
