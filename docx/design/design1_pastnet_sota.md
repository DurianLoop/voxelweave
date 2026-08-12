# Design 1：PAST-Net，面向三数据集 SOTA 的 T2 through-plane interpolation 方案

更新时间：2026-07-06

当前目标不是继续堆已有 baseline，而是设计一个真正贴合本任务定义的新模型：在 IXI-T2、fastMRI-brain-T2 expanded、NingXia-T2 8-fold case-level CV 三个数据集上都尽量达到或超过当前统一协议下的最强结果。

本文档用于后续“搓模型”的方向约束、结构设计、训练策略、消融实验和论文叙事。这里的 SOTA 指的是本项目统一任务定义、统一数据划分、统一指标计算方式下的 project-level SOTA，不直接等同于其他论文官方表格里的跨协议 SOTA。

## 1. 当前任务定义

主线实验设置：

| 项目 | 当前口径 |
|---|---|
| Modality | T2 |
| Task | through-plane slice interpolation / synthesis |
| Main scale | x4 |
| Later extension | x2 / x6 |
| Main datasets | IXI-T2, fastMRI-brain-T2 expanded, NingXia-T2 |
| NingXia split | 8-fold case-level CV |
| Main metrics | PSNR, SSIM, MAE, MSE, NCC |
| Main table | `docx/experiment/experiment_master_table.md` |

x4 情况下，两个已知 anchor slice 之间有 3 张缺失切片。给定：

```text
S0, S4
```

需要预测：

```text
S1, S2, S3
```

目标切片的 phase / offset 为：

```text
p = k / 4, k in {1, 2, 3}
```

即：

| Target | Phase |
|---|---:|
| S1 | 0.25 |
| S2 | 0.50 |
| S3 | 0.75 |

模型应该显式知道目标切片在两个 anchor slice 之间的位置，而不是把任务简单当成普通 2D image restoration 或 generic SR。

## 2. 当前三数据集 SOTA 目标

### 2.1 IXI-T2 x4

当前统一协议下，IXI 最强方法是 I3Net。

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| I3Net | 31.3058 | 0.9285 | 17.5276 | 2565.3177 | 0.9788 |

新模型需要挑战的目标：

| Metric | Target |
|---|---:|
| PSNR | > 31.3058 |
| SSIM | > 0.9285 |
| MAE | < 17.5276 |
| MSE | < 2565.3177 |
| NCC | > 0.9788 |

IXI 是 I3Net 优势最明显的数据集之一。新模型如果在 IXI 上远低于 I3Net，说明结构还没有真正抓住 slice interpolation 的任务本质。

### 2.2 fastMRI-brain-T2 expanded x4

当前统一协议下，fastMRI 最强方法也是 I3Net。

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| I3Net | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 |

新模型需要挑战的目标：

| Metric | Target |
|---|---:|
| PSNR | > 24.0102 |
| SSIM | > 0.7921 |
| MAE | < 41.0101 |
| MSE | < 7755.6546 |
| NCC | > 0.9308 |

fastMRI 的难点在于图像质量、FOV、slice 数量、采集差异和解剖变化更复杂。这里如果能超过 I3Net，说明模型不仅会拟合 IXI，还具备更好的跨来源泛化能力。

### 2.3 NingXia-T2 x4

NingXia 当前第一梯队是 SwinIR 2.5D、HAT 2.5D、SAINT、SMamba-UNet 2.5D。I3Net 在 NingXia 上不占优。

当前各指标需要挑战的强目标：

| Metric | Current best source | Target |
|---|---|---:|
| PSNR | SwinIR / HAT tier | > 23.9513 |
| SSIM | SwinIR / HAT tier | > 0.7525 |
| MAE | SwinIR / HAT tier | < 85.9679 |
| MSE | SwinIR / HAT tier | < 32030.5455 |
| NCC | HAT tier | > 0.8933 |

NingXia 是外部临床泛化验证，也是最容易暴露模型是否过拟合 public dataset 的数据集。新模型不能只在 IXI / fastMRI 上强，还必须在 NingXia 上超过 SwinIR / HAT / SAINT / SMamba 这一组第一梯队。

## 3. 已有 baseline 暴露的问题

### 3.1 Linear 很强，说明 coarse interpolation prior 必须保留

Linear 虽然简单，但在三数据集上不是完全崩溃的弱基线。这说明相邻切片之间的大部分低频变化可以被粗插值解释。

因此新模型不应该从零生成目标切片，而应该采用：

```text
prediction = coarse interpolation + learned residual
```

模型重点学习 Linear 无法处理的部分：

- 组织边界位移
- 局部结构非线性变化
- 小结构恢复
- 模糊边缘锐化
- slice 间形态变化
- 不同数据域下的残差幅度控制

### 3.2 Cubic 往往不如 Linear，说明盲目高阶平滑会伤结构

Cubic 在多个数据集上反而低于 Linear，说明高阶插值可能带来过度平滑、结构错位和伪影。

这给新模型一个明确约束：

```text
不要把目标做成“更平滑”，而是要做成“结构更对”。
```

所以模型设计必须保护边界和结构，而不是只优化全局平滑。

### 3.3 ResUNet residual 稳定但上限不足

ResUNet residual 明显强于 Linear，但整体弱于 I3Net、SwinIR、HAT、SAINT、SMamba。

说明：

- residual learning 是对的；
- 纯 CNN 局部建模是稳定的；
- 但 CNN alone 对长距离结构对应、phase 感知、全局 anatomy consistency 不够。

新模型可以继承 residual 思路，但不能只做普通 U-Net。

### 3.4 SwinIR / HAT 在 NingXia 强，说明局部结构恢复能力非常重要

SwinIR / HAT 在 NingXia 上表现很强，说明外部临床数据集更依赖稳定的局部结构恢复能力。

这类模型擅长：

- 局部纹理恢复；
- 边缘保持；
- 噪声鲁棒；
- window-level structure modeling；
- domain shift 下相对稳健。

但它们原本不是为 through-plane interpolation 设计的，通常没有显式使用目标 slice 的 phase 信息，也没有专门建模左右 anchor slice 的结构迁移。

### 3.5 I3Net 在 IXI / fastMRI 强，说明任务定义匹配非常关键

I3Net 是目前最贴近 medical slice interpolation / through-plane synthesis 的 published baseline，因此在 IXI 和 fastMRI 上明显强。

这说明新模型必须吸收 I3Net 的任务匹配优势：

- 不能只当作 generic SR；
- 必须输入相邻 slice；
- 必须知道目标 slice 位于两个 anchor slice 之间；
- 必须允许不同 offset 使用不同融合策略；
- 最好能显式约束左右方向的一致性。

### 3.6 INR 类方法目前不是主攻方向

ArSSR 和 CycleINR 已经补齐 published INR baseline，但当前不是第一梯队。

暴露的问题：

- 可能退化到 Linear 附近；
- 对局部结构恢复能力不足；
- 依赖坐标表达，但没有充分利用 slice-to-slice structure transfer；
- 对当前三数据集主表新增量有限。

除非引入强 image encoder、phase-aware fusion 和 residual constraint，否则不建议继续把纯 INR 作为主线。

### 3.7 Diffusion 可以做 refinement，但不适合作为第一版主干

Res-SRDiff 在 IXI / fastMRI 上有一定潜力，但 NingXia 上不稳，说明直接 diffusion refinement 存在风险。

问题包括：

- 推理成本高；
- 训练成本高；
- deterministic interpolation 任务不一定需要随机生成；
- 外部临床小样本 CV 上可能产生不稳定残差；
- 可能改善视觉观感，但牺牲 PSNR / MAE / MSE。

当前建议：

```text
第一版主模型走 deterministic residual interpolation。
Diffusion 后续作为 optional residual correction / refinement，不作为主干。
```

## 4. 新模型的核心判断

要在三个数据集都达到 SOTA，新模型不能只继承某一个 baseline，而要组合现有强基线的关键优势。

推荐核心组合：

```text
I3Net 的任务匹配
+ SAINT 的 slice/context 建模
+ SwinIR/HAT 的局部结构恢复
+ SMamba/Mamba 的长程建模思路
+ Linear coarse prior 的稳定性
+ residual/confidence gate 的外部域鲁棒性
```

模型目标不是“参数最大”，而是“最贴合 through-plane interpolation”。

## 5. 推荐模型：PAST-Net

暂定名称：

```text
PAST-Net
Phase-Aware Structure-Transfer Network
```

中文名称：

```text
相位感知结构迁移网络
```

核心观点：

> Through-plane interpolation 的关键不是普通 2D SR，而是在两个已知 slice 之间，根据目标 slice 的 phase 位置进行结构迁移和残差校正。

对应创新点：

1. Phase-aware bidirectional structure transfer；
2. Coarse interpolation guided residual prediction；
3. Spatial confidence gated residual correction；
4. Symmetry-consistent slice interpolation；
5. Cross-dataset robust deterministic reconstruction。

## 6. 输入设计

### 6.1 基础输入

对于任意目标切片，输入：

```text
L = left anchor slice
R = right anchor slice
C = linear interpolation coarse slice
P = phase map
D = R - L
A = |R - L|
```

基础输入通道：

```text
[L, R, C, P, R-L, |R-L|]
```

第一版建议使用 6 通道输入。

### 6.2 为什么要输入 coarse C

coarse slice C 是 Linear interpolation 的结果。

作用：

- 给模型一个稳定初值；
- 降低生成难度；
- 避免模型在外部数据上乱改；
- 让网络只学习必要残差；
- 对 MAE / MSE / PSNR 更友好。

### 6.3 为什么要输入 phase P

x4 下三个目标 slice 的位置不同：

```text
p = 0.25, 0.50, 0.75
```

模型必须知道目标 slice 更靠近 L 还是 R。

如果没有 phase map，模型只能从图像内容中隐式猜测 offset，容易造成：

- offset 1 / 3 混淆；
- 左右不对称；
- 中间切片过平滑；
- 不同倍率 x2 / x4 / x6 难以统一扩展。

### 6.4 可选增强输入

第二版可以加入：

```text
grad_x(C), grad_y(C), grad_mag(C)
```

用于显式提供边缘信息。

但第一版不要一次性堆太多输入，优先验证 6 通道核心设计。

## 7. 模型结构设计

### 7.1 总体框架

```text
L, R, C, P, D, A
        |
        v
Shared shallow encoder
        |
        v
Phase-aware bidirectional fusion
        |
        v
Local structure restoration blocks
        |
        v
Long-range context mixer
        |
        v
Confidence-gated residual decoder
        |
        v
Y_hat = C + W * tanh(Residual)
```

### 7.2 Shared shallow encoder

对 L、R、C 使用共享或半共享 shallow encoder：

```text
F_L = E(L)
F_R = E(R)
F_C = E(C)
```

共享 encoder 的好处：

- 左右 slice 使用相同特征空间；
- 减少参数；
- 更容易做 symmetry consistency；
- 小数据集 NingXia 上更稳。

如果后续发现左右 anchor 的角色差异很大，可以消融 separate encoder。

### 7.3 Phase-aware bidirectional fusion

设计 phase-conditioned spatial gate：

```text
G_L, G_R, G_C = Gate(F_L, F_R, F_C, P, D, A)

F = G_L * F_L + G_R * F_R + G_C * F_C
```

其中：

```text
G_L + G_R + G_C = 1
```

理想行为：

- p 接近 0 时，G_L 更大；
- p 接近 1 时，G_R 更大；
- 结构变化明显区域，G_C 和 residual correction 更重要；
- 背景区域，gate 应该抑制过度修改。

这个模块是区分普通 SR 模型和 through-plane interpolation 模型的关键。

### 7.4 Local structure restoration blocks

吸收 SwinIR / HAT 的优势，但不要直接堆完整 HAT。

推荐第一版模块：

```text
LocalBlock:
  LayerNorm / GroupNorm
  depthwise 3x3 conv
  pointwise 1x1 conv
  lightweight channel attention
  optional window attention
  residual connection
```

建议配置：

| 参数 | 建议 |
|---|---:|
| base channels | 48 或 64 |
| num blocks | 6 到 10 |
| window size | 8 |
| attention | 中高层少量使用 |
| activation | GELU |

目标：

- 保留 HAT/SwinIR 的局部结构恢复能力；
- 控制显存；
- 控制训练时间；
- 保持模型可解释。

### 7.5 Long-range context mixer

医学图像不仅有局部纹理，也有大范围解剖一致性。

可选 mixer：

| Mixer | 优点 | 风险 |
|---|---|---|
| Large-kernel depthwise conv | 稳、快、省显存 | 创新性一般 |
| Axial attention | 长程建模强 | 实现略复杂 |
| Mamba block | 2024+ 新架构叙事强 | 稳定性需要验证 |
| Full window attention | 恢复能力强 | 可能重 |

第一版建议：

```text
large-kernel depthwise conv + channel attention
```

第二版再做：

```text
Mamba / selective scan mixer
```

这样可以先保证模型有效，再补“新架构”版本。

### 7.6 Confidence-gated residual decoder

模型不直接输出最终图，而是输出：

```text
Residual = R_hat
Confidence = W, W in [0, 1]

Y_hat = C + W * alpha * tanh(R_hat)
```

其中：

- C 是 Linear coarse；
- R_hat 是预测残差；
- W 是空间 confidence map；
- alpha 控制最大残差幅度。

这个设计的意义：

- 背景少改；
- 稳定区域少改；
- 结构变化区域多改；
- 外部临床数据上更保守；
- 减少 hallucination；
- 有利于 PSNR / MAE / MSE。

### 7.7 左右对称设计

slice interpolation 天然满足：

```text
f(L, R, p) ≈ f(R, L, 1-p)
```

因此训练时可以加入 symmetry consistency：

```text
Y_forward = f(L, R, p)
Y_reverse = f(R, L, 1-p)

L_sym = |Y_forward - Y_reverse|
```

该约束特别适合 NingXia：

- 数据少；
- case-level CV；
- 容易过拟合方向偏置；
- symmetry 可以作为弱正则。

## 8. 损失函数设计

第一版推荐：

```text
L_total =
    L_charbonnier
  + lambda_grad * L_gradient
  + lambda_res  * L_residual
  + lambda_sym  * L_symmetry
```

### 8.1 Charbonnier loss

主损失：

```text
L_charbonnier = sqrt((Y_hat - Y)^2 + eps^2)
```

优点：

- 比 L2 抗异常值；
- 比 L1 更平滑；
- 适合医学图像重建。

### 8.2 Gradient loss

用于保护结构边界：

```text
L_gradient =
  |grad_x(Y_hat) - grad_x(Y)|
+ |grad_y(Y_hat) - grad_y(Y)|
```

建议：

```text
lambda_grad = 0.05
```

### 8.3 Residual regularization

避免模型大面积乱改 coarse：

```text
L_residual = |Y_hat - C|
```

建议：

```text
lambda_res = 0.001
```

### 8.4 Symmetry consistency loss

约束左右翻转一致：

```text
L_symmetry = |f(L, R, p) - f(R, L, 1-p)|
```

建议：

```text
lambda_sym = 0.01
```

### 8.5 暂不建议加入 GAN loss

GAN 可能提升视觉锐度，但对 PSNR / SSIM / MAE / MSE 不一定友好，并且医学图像中 hallucination 容易被质疑。

当前目标是三数据集主表 SOTA，因此第一版不建议使用 GAN loss。

### 8.6 暂不建议加入 diffusion loss

Diffusion 可作为后续 refinement，但第一版主模型应保持 deterministic。

原因：

- 成本低；
- 可复现；
- 指标稳定；
- 易写消融；
- 更适合先冲主表。

## 9. 训练策略

### 9.1 Stage 0：小样本 overfit sanity check

目的：

- 验证模型能不能拟合；
- 验证 loss 是否正常下降；
- 验证 output/residual/confidence map 是否合理；
- 排除数据、尺度、归一化、输出范围 bug。

建议：

| 设置 | 建议 |
|---|---|
| Dataset | IXI |
| Cases | 1 到 2 个 train case |
| Iterations | 200 到 500 |
| Batch | 尽量大 |
| Save | prediction, target, coarse, residual, error map |

通过标准：

- train loss 快速下降；
- prediction 明显接近 target；
- residual 主要集中在结构变化区域；
- confidence map 不应全 0 或全 1；
- 不出现全黑、全白、强噪声、checkerboard。

### 9.2 Stage 1：IXI smoke / mini

目的：

- 快速判断模型方向是否有希望；
- 不浪费大量训练资源。

通过标准：

- 明显超过 Linear；
- 明显超过 ResUNet residual；
- 接近 SwinIR / HAT / SMamba；
- per-offset 没有明显崩溃。

如果 IXI mini 都接近不了强 baseline，先不要扩三数据集。

### 9.3 Stage 2：IXI full_test115

目的：

- 正式挑战 I3Net；
- 证明模型在标准 IXI 115 test case 上成立。

重点看：

- average metrics；
- per-offset metrics；
- per-case win rate；
- visual QC；
- loss 是否收敛。

### 9.4 Stage 3：fastMRI full

目的：

- 验证复杂 public dataset 上的泛化；
- 判断是否能超过 I3Net / SAINT / HAT。

重点看：

- 是否超过 I3Net；
- 若未超过，是否超过 HAT/SMamba/SAINT；
- 是否存在特定 volume 崩溃；
- 图像边缘和低质量 slice 是否稳定。

### 9.5 Stage 4：NingXia 8-fold case-level CV

目的：

- 验证外部临床泛化；
- 判断是否真正有论文说服力。

重点看：

- fold-level mean；
- fold-level std；
- per-case win rate；
- 是否在某个 fold 崩溃；
- 是否超过 SwinIR / HAT / SAINT / SMamba 第一梯队。

NingXia 不能只看平均值。如果平均值提升来自少数 fold，大多数 fold 不赢，论文说服力会弱。

## 10. 第一版推荐超参数

### 10.1 Model

```text
input_channels = 6
base_channels = 48
num_blocks = 8
window_size = 8
use_phase_gate = true
use_confidence_map = true
use_symmetry_loss = true
use_gradient_loss = true
output_type = coarse_plus_bounded_residual
```

如果显存充足：

```text
base_channels = 64
num_blocks = 10
```

如果训练太慢或显存紧张：

```text
base_channels = 40
num_blocks = 6
```

### 10.2 Loss

```text
loss = charbonnier
     + 0.05 * gradient_loss
     + 0.001 * residual_regularization
     + 0.01 * symmetry_consistency
```

### 10.3 Optimizer

```text
optimizer = AdamW
lr = 2e-4
weight_decay = 1e-4
scheduler = cosine
amp = true
```

### 10.4 Training

建议优先保证 batch 不爆显存，其次追速度。

如果显存利用太低，可以提高 batch。

如果 shared GPU memory 开始大量占用，说明已经越过安全范围，应降低 batch 或模型宽度。

## 11. 消融实验设计

### 11.1 必做消融

| Variant | 目的 | 预期 |
|---|---|---|
| Full model | 主模型 | 最强 |
| w/o coarse C | 证明 coarse prior 必要 | PSNR/MAE 下降 |
| w/o phase P | 证明 phase-aware 必要 | offset 1/3 下降明显 |
| w/o spatial gate | 证明空间自适应融合必要 | NingXia 下降 |
| w/o confidence map | 证明残差幅度控制必要 | 外部数据不稳 |
| w/o symmetry loss | 证明左右一致性约束有效 | per-offset 不平衡 |
| w/o gradient loss | 证明结构边界约束有效 | SSIM/visual 边界变差 |
| Conv-only | 证明 context mixer 有贡献 | 复杂结构下降 |

### 11.2 可选消融

| Variant | 目的 |
|---|---|
| Mamba mixer vs large-kernel conv | 验证 2024+ sequence mixer 是否有增益 |
| Window attention vs channel attention | 验证局部结构建模方式 |
| Shared encoder vs separate encoder | 验证左右特征空间是否应共享 |
| bounded residual vs unconstrained residual | 验证 residual 稳定性 |
| phase scalar vs phase map | 验证空间 phase 条件注入方式 |
| linear coarse vs learned coarse | 验证 coarse 来源 |

## 12. 诊断指标

主表只保留 PSNR / SSIM / MAE / MSE / NCC，但开发阶段必须保存更多诊断信息。

### 12.1 Per-offset metrics

x4 下必须分别统计：

| Offset | Phase |
|---|---:|
| 1 | 0.25 |
| 2 | 0.50 |
| 3 | 0.75 |

需要关注：

- offset 1 和 offset 3 是否对称；
- offset 2 是否最强；
- 是否某个 offset 明显崩溃；
- phase map 是否真的带来提升。

### 12.2 Per-case wins

统计模型相对强 baseline 的 case-level win rate：

```text
win_rate = cases where new_model beats baseline / total cases
```

推荐比较对象：

- IXI：I3Net、HAT、SMamba；
- fastMRI：I3Net、SAINT、HAT；
- NingXia：SwinIR、HAT、SAINT、SMamba。

### 12.3 Per-fold NingXia

NingXia 必须看 8 fold：

```text
fold_00 ... fold_07
```

需要保存：

- 每 fold 五个指标；
- mean；
- std；
- best/worst fold；
- 相对 baseline 的每 fold win/loss。

### 12.4 Residual statistics

保存：

- residual mean；
- residual std；
- residual max；
- residual energy；
- confidence map mean；
- confidence map std。

理想现象：

- residual 不应全图大幅度改变；
- confidence map 应在结构变化区域更高；
- 背景区域 confidence 应较低；
- 外部数据上 residual 应更保守。

### 12.5 Visual QC

每个数据集至少保存固定 case 的：

- left anchor；
- right anchor；
- linear coarse；
- prediction；
- target；
- error map；
- residual map；
- confidence map；
- zoomed structure patch。

重点看：

- 脑室边界；
- 皮层边界；
- 小结构；
- 背景噪声；
- 是否 hallucination；
- 是否过平滑；
- 是否局部断裂。

## 13. 论文 claim 设计

### Claim 1：through-plane interpolation 不是普通 2D SR

普通 SR 只知道输入图像和高分辨率目标，但本任务有明确的 slice phase。

对应模块：

- phase map；
- phase-aware gate；
- per-offset analysis；
- x2/x4/x6 extension。

### Claim 2：coarse interpolation prior 是稳定重建的关键

Linear 很强，说明低频结构应作为先验保留。

对应模块：

- coarse input C；
- coarse + residual output；
- residual regularization；
- w/o coarse ablation。

### Claim 3：spatially adaptive structure transfer 提升跨数据集鲁棒性

不同空间位置的变化幅度不同，不能用全局固定权重融合 L/R。

对应模块：

- spatial gate；
- confidence map；
- local structure restoration；
- NingXia CV。

### Claim 4：symmetry consistency 提升 interpolation 合理性

从 L 到 R 和从 R 到 L 应该一致。

对应模块：

- symmetry loss；
- offset 1/3 对称性；
- reverse input ablation。

### Claim 5：新模型在 task-specific 和 generic baseline 之间取得更优平衡

I3Net 在 IXI/fastMRI 强，但 NingXia 不占优；SwinIR/HAT 在 NingXia 强，但不是任务专用。

新模型目标：

```text
I3Net-level task matching
+ HAT/SwinIR-level local restoration
+ stronger cross-dataset robustness
```

## 14. 实现路线

### 14.1 推荐包名

先做 IXI：

```text
ixi_pastnet_2p5d
```

后续扩展：

```text
fastmri_brain_pastnet_2p5d
processing.run_ningxia_case_cv --models pastnet
```

### 14.2 文件结构

```text
ixi_pastnet_2p5d/
  __init__.py
  settings.py
  data.py
  model.py
  train.py
  run_all.py
  paper_table.py
  visual_qc.py
```

### 14.3 优先复用现有代码

必须复用当前统一实验口径：

- IXI full_test115 split；
- fastMRI expanded split；
- NingXia 8-fold case-level CV；
- 当前 metrics；
- 当前 paper_table 输出格式；
- 当前 checkpoint best 选择逻辑；
- 当前主表列顺序。

不要重新写一套评估逻辑，否则结果不能直接进入主表。

## 15. 推荐开发顺序

### Step 1：实现最小可跑 PAST-Net v1

只包含：

- 6-channel input；
- shared shallow encoder；
- phase-aware gate；
- local blocks；
- confidence residual decoder；
- Charbonnier + gradient + residual + symmetry loss。

### Step 2：IXI 1-2 case overfit

确认：

- loss 能下降；
- output 正常；
- residual 正常；
- confidence 正常；
- no NaN。

### Step 3：IXI smoke / mini

确认：

- 超过 Linear / ResUNet；
- 接近 HAT / SMamba；
- per-offset 正常。

### Step 4：IXI full_test115

判断能否挑战 I3Net。

### Step 5：fastMRI full

判断是否有跨 public dataset 泛化。

### Step 6：NingXia 8-fold CV

判断是否真正具备论文主模型价值。

### Step 7：消融实验

优先做：

1. w/o phase；
2. w/o coarse；
3. w/o gate；
4. w/o confidence；
5. w/o symmetry；
6. w/o gradient。

### Step 8：x2 / x6 扩展

如果 x4 成立，再扩展 x2 和 x6，形成类似 I3Net 的 multi-scale 大表。

## 16. 成功标准

### P0：方向成立

满足：

- IXI mini 明显超过 Linear；
- IXI mini 明显超过 ResUNet；
- 输出视觉正常；
- residual 主要集中在结构变化区域；
- offset 1/2/3 无明显崩溃。

### P1：有进入主表价值

满足：

- IXI full 接近 I3Net；
- fastMRI full 超过 HAT/SMamba/SAINT 中至少一部分；
- NingXia CV 进入第一梯队。

### P2：具备论文主模型价值

满足：

- IXI 超过或非常接近 I3Net；
- fastMRI 超过或非常接近 I3Net；
- NingXia 超过 SwinIR/HAT/SAINT/SMamba 第一梯队；
- 消融能证明核心模块有效；
- visual QC 有明显优势。

### P3：具备强论文 claim

满足：

- x2/x4/x6 均稳定；
- 三数据集都达到 project-level SOTA；
- NingXia 外部临床数据提升明确；
- 参数量和推理速度可接受；
- 有 per-case/per-offset/fold-level 支撑；
- failure case 可解释。

## 17. 不建议优先做的方向

### 17.1 从零 diffusion 主模型

不建议作为第一版主线。

原因：

- 训练慢；
- 推理慢；
- 指标不一定稳；
- NingXia 风险大；
- 容易产生 hallucination 质疑。

可以后续做：

```text
PAST-Net output + diffusion residual refinement
```

### 17.2 GAN 主模型

不建议作为主线。

原因：

- 医学图像 hallucination 风险高；
- PSNR/MAE/MSE 可能下降；
- 审稿人容易质疑生成细节真实性；
- 当前已有 Pix2Pix-GAN baseline 表现不是第一梯队。

### 17.3 纯 INR

当前 ArSSR / CycleINR 结果不支持继续主攻纯 INR。

除非做成：

```text
image encoder + phase-aware implicit residual field
```

否则不建议继续投入主资源。

### 17.4 单纯堆大 Transformer

HAT 已经是强 Transformer baseline。如果只是换一个更大 Transformer，论文创新会弱。

应该强调：

```text
task-specific phase-aware interpolation
```

而不是：

```text
larger generic restoration backbone
```

## 18. 可能的第二版增强

如果 PAST-Net v1 有希望，可以继续做 v2。

### 18.1 Multi-scale phase unification

统一 x2/x4/x6：

```text
p = k / scale
```

训练时混合 scale：

```text
scale in {2, 4, 6}
```

让一个模型支持多倍率插值。

### 18.2 Mamba context mixer

在 bottleneck 加入轻量 Mamba block：

```text
F = LocalBlocks(F)
F = MambaMixer(F)
F = Decoder(F)
```

论文叙事：

```text
long-range anatomical dependency modeling
```

### 18.3 Residual diffusion refinement

在 deterministic 模型之后做极轻量 refinement：

```text
Y0 = PAST-Net(L, R, p)
Y_refined = DiffusionRefiner(Y0, L, R, C, p)
```

注意这只能作为 optional enhancement，不建议成为主模型第一版。

### 18.4 Uncertainty-aware evaluation

confidence map 可作为 uncertainty proxy。

分析：

- confidence 高的区域是否对应真实 error 高的区域；
- 是否能解释模型失败；
- 是否能用于后续 refinement。

## 19. 论文方法图建议

方法图可以画成 5 个部分：

```text
Left / Right sparse slices
        |
Linear coarse interpolation + phase map
        |
Phase-aware bidirectional structure transfer
        |
Local-global structure restoration
        |
Confidence-gated residual correction
        |
Predicted target slice
```

旁边放两个小约束：

```text
Symmetry consistency:
f(L, R, p) ≈ f(R, L, 1-p)

Residual formulation:
Y_hat = C + W * tanh(R)
```

## 20. 最终推荐结论

如果目标是在 IXI、fastMRI 和 NingXia 三个数据集上都达到 SOTA，最值得优先实现的不是 diffusion、GAN、纯 INR 或更大的 generic Transformer，而是一个专门针对 through-plane interpolation 的 phase-aware residual structure transfer 模型。

推荐主线：

```text
PAST-Net =
  coarse interpolation prior
+ phase-aware bidirectional fusion
+ spatial structure transfer
+ local restoration blocks
+ long-range context mixer
+ confidence-gated bounded residual
+ symmetry consistency
```

这条线有几个优势：

1. 能解释为什么 Linear 是强 prior；
2. 能吸收 I3Net 的任务匹配优势；
3. 能吸收 SwinIR/HAT 在 NingXia 上的局部结构优势；
4. 能避免 diffusion/GAN 的不稳定和 hallucination 风险；
5. 能自然扩展到 x2/x4/x6；
6. 能设计出清晰、可发表的消融实验；
7. 能在论文中形成明确的新方法 claim。

第一版目标不是一开始就复杂，而是先用稳定 deterministic residual 模型打穿 IXI -> fastMRI -> NingXia，再逐步加入 Mamba、multi-scale、diffusion refinement 等增强模块。
