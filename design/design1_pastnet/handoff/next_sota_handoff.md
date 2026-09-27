# PAST-Net v2：下一阶段 SOTA 冲刺简报

## 1. 问题重新定义

Design1 v1 已经回答了“在同一 residual-refiner 范式内还能不能靠加宽、加深、loss、3D head、INR、Flow、FFT 或续训到 26 dB”：现有证据回答是不能。

G086 距 26 dB 还有 `1.553 dB`。按 PSNR 与 MSE 的关系，这要求均方误差再下降约 `30%`。下一代研究问题应改成：

> 稀疏锚点中还存在什么未被当前模型提取的可辨识信息，以及哪些误差本来就无法由当前输入确定？

只有先区分“模型没有学到”和“输入根本不包含”，架构设计才不会继续盲试。

## 2. 先做五个不调 test 的上限诊断

### D1：phase 分解

分别统计 q=`.25/.50/.75` 的 PSNR、频带误差、边缘误差和病例方差。若 q=.5 明显更差，说明非线性形变/遮挡主导；若两端更差，检查边界与 outer-anchor 使用。

### D2：频率误差分解

把 G086 residual error 分为 low/mid/high bands，并按病例关联到 MSE tail。若主要剩余误差仍在低频，继续做纹理模块无效；若高频占主导，才值得加强结构匹配。

### D3：对齐 oracle

用非学习配准或有监督 flow，把左右真实锚点对齐到 target，再做简单融合。它不是提交模型，而是估计“完美对应”最多能贡献多少。如果 oracle 也远低于 26，Flow 路线不应成为主赌注。

### D4：信息 oracle

受控加入更近的真实邻层、更多外侧锚点或完整低分辨体数据，测量每类新增信息的上限。该实验回答 26 dB 是否受当前四锚点条件的不可约歧义限制。

### D5：域差异审计

比较 fastMRI、IXI、NingXia 的真实 z-spacing、in-plane spacing、方向矩阵、FOV、slice 数、强度分布、噪声和相邻层变化率。IXI 的 `-1.3165 dB` 反转必须先被解释，否则任何“跨域 SOTA”设计都缺乏基础。

这些诊断只用 train/validation 或固定模型误差分析，不依据 test 结果调一个特定病例。

## 3. 推荐的 PAST-Net v2 架构假设

工作名：**Physically Conditioned Correspondence and Frequency Residual Network**。

```text
Input
  four or longer sparse anchor sequence
  physical z coordinates / spacing / orientation / validity
  query coordinate in millimeters

Shared multi-resolution anchor encoder
  preserve G086 warm-start-compatible 2D features

Query-conditioned correspondence module
  coarse-to-fine feature matching for every anchor -> query
  bounded deformable sampling with cycle/visibility confidence
  no image-space post-hoc flow

Physical z sequence mixer
  distance-aware state-space or local attention over anchor features
  token positions use millimeters, not only .25/.50/.75 IDs

Frequency-factorized decoder
  low-frequency intensity trajectory branch
  mid/high-frequency structure residual branch
  learned uncertainty gate and exact coarse skip

Joint interval output
  q=.25/.50/.75 together
  anchor-clamped consistency at observed positions
```

### 为什么这不是又一次组件堆叠

- 它保留 Design1 已证实的 coarse residual、多锚点、wide trunk、多尺度 context 和 dual-domain 分解。
- 新增信息是物理 spacing/orientation，而不是只增加参数。
- 对齐发生在多尺度特征提取过程中，而不是 G081 那样修正已完成的 prediction。
- z mixer 处理可变距离和更长 anchor sequence，不是 G077 的三个固定 token attention。
- 低频与高频目标被显式分工，承接 G084 的全指标证据。

## 4. 训练目标应如何改

保留 Charbonnier/MSE/gradient 的稳定骨架，但替换 hard top-10% tail：

```text
L = L_charb
  + lambda_mse * L_mse
  + lambda_grad * L_gradient
  + lambda_freq * (L_low + L_mid + L_high)
  + lambda_risk * soft_CVaR(error, annealed_quantile)
  + lambda_corr * correspondence_consistency
  + lambda_anchor * observed_anchor_clamp
```

建议从均匀损失开始，在训练中后期平滑提高 soft-CVaR 权重；不能一开始就让少量异常像素控制梯度。所有 loss 权重只在 validation 上选择，并预先限制搜索空间。

## 5. 训练策略

### Stage A：表征预训练

在训练 split 上做 masked-slice reconstruction、anchor-order prediction 或跨间距 query reconstruction，让 encoder 先学习解剖连续性。若允许联合数据训练，应统一预处理并把 dataset ID 仅用于归一化统计，而不是让模型记住测试域。

### Stage B：G086 权重迁移

迁移共享 anchor encoder、wide trunk 和 decoder 可兼容部分；新 correspondence/physical modules 零残差或 identity 初始化。先冻结旧主干训练新模块，再低学习率联合解冻。

### Stage C：多尺度间距训练

在 x2/x4/x6 或可变物理间距上联合训练 query-conditioned 模型。目标是让“位置”成为连续条件，而不是为每个倍率重新学习捷径。

### Stage D：固定候选复评

先在 fastMRI validation 筛选，架构锁定后使用新的 holdout 或预注册的 final test。随后原样迁移 IXI 和 NingXia；禁止跨数据集逐个改 loss recipe。

## 6. 最小可证伪实验序列

| 顺序 | 实验 | 唯一新增变量 | 晋级门槛 |
|---|---|---|---|
| P0 | G086 3-seed 锚点/新 holdout | 复现稳定性 | 方差与配对区间可接受 |
| P1 | + physical coordinate conditioning | spacing/orientation/query-mm | validation `>=+.08 dB`，主指标不退 |
| P2 | + multi-scale feature correspondence | 对齐位置改变 | 相对 P1 `>=+.10 dB`，hard cases 同向 |
| P3 | + soft-CVaR frequency risk | tail 目标重构 | PSNR/MSE 提升且 MAE/Dice 不再恶化 |
| P4 | + longer sparse context | 新增真实信息 | 相对 P3 `>=+.15 dB`，成本可控 |
| P5 | 组合锁定、3 seeds | 无新变量 | paired CI 下界 > 0，跨域方向一致 |

门槛是建议的研究纪律，不是为了淘汰所有小收益；未过门槛的实验仍记录，但不继续围绕其微调。

## 7. 三种可能的 IXI G086 结果与动作

| IXI 结果 | 解释 | 下一步 |
|---|---|---|
| 相对 G07 `>=+.05 dB` 且四主指标同向 | G079/G084 机制可迁移，但未必接近 I3Net | 固定迁移 NingXia；同时做 v2 诊断 |
| `0~+.05 dB` | 弱泛化证据，后期模块主要是域内微调 | 可做一次 NingXia 固定验证，不再调 IXI |
| 退步或多个指标退步 | v1 后期机制域依赖 | 终止 v1；优先 physical/domain audit 与 v2 |

即使 IXI G086 比 G07 提高 `.1 dB`，距离 I3Net 仍约 1.2 dB，因此不能把它当最终架构，只能作为机制验证。

## 8. 不要再做的事情

1. 不继续 G086 续训或做 G091 learning-rate sweep。
2. 不复活 MA4W、G087-G090 并靠更宽、更久来救。
3. 不把 diffusion/GAN 当默认答案；既有跨域 baseline 已显示直接 refinement 不稳定。
4. 不用 test-24/test-115 选 loss、blend、seed 或 checkpoint。
5. 不一次组合 Flow、FFT、3D、attention 和新 loss；每个新增机制先单独过门槛。
6. 不承诺 26 dB。先用 oracle 判断目标是否与输入信息上限相容。

## 9. 论文层面的诚实表述

当前可以说：PAST-Net 在反复使用的 fastMRI development test 上相对 I3Net 有稳定优势，机制消融支持 multi-anchor wide trunk、tail-risk optimization 和 dual-domain residual decomposition。

当前不能说：PAST-Net 已经在三个数据集达到 SOTA，或 G086 已被独立 test 验证。IXI G07 的明显落后和 G086/NingXia 的缺失结果必须正面报告。

Design1 最有价值的产出并不只是 `24.4470`，而是一条已经被大量对照压缩过的因果链：有效信息在哪里、哪些模块只做局部修补、何时优化已进入尾差，以及下一次突破必须改变什么。
