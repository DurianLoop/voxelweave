# T2 x4 训练日志收敛性审计

日期：2026-06-29

本文只审计当前论文主线：T2 模态、x4 through-plane interpolation、三数据集横向主表相关实验。`pre/` 旧预实验、transfer package 备份、smoke/mini 只作为历史记录，不作为主表收敛证据。

## 结论先行

不建议因为“30 epoch 看起来比官方 I3Net 的 1500 epoch 少”就把所有实验推倒重跑。当前日志显示，大部分 full/full_test115/NingXia 8-fold 实验的验证损失已经接近 best 或进入平台期；真正需要谨慎的是少数几项：IXI-I3Net 训练日志出现 NaN、fastMRI-HAT 最佳点在最后一轮、fastMRI-SwinIR 缺 training_history、NingXia-GAN 波动明显、IXI-GAN 仍未完成/缺日志。

所以更稳的策略不是全量重跑所有 baseline，而是：

1. 对“不确定”项做定向补训或补日志。
2. 对未来新模型和最强对照做延长训练 sanity check。
3. 论文里明确写统一协议、best validation checkpoint、验证集早停/平台判据，并避免声称“复现官方绝对数值”。

## 分类规则

这里的“肯定拟合”不是指全局最优，而是指“日志证据较强，足以说明当前训练预算下已经接近验证集平台”。具体按以下规则判断：

| 分类 | 判据 |
|---|---|
| 日志证据较强 | 无 NaN；验证损失有明显下降；最后一轮相对 best 通常在 1% 左右，或触发 early stopping；末段波动较小。 |
| 大概率拟合 | 无 NaN；验证损失已经明显下降并接近 best，但末段仍有一些波动，或 best 出现在较晚 epoch。 |
| 不确定 | 缺 `training_history.csv`；出现 NaN；best 仍在最后且末段还在下降；最后一轮明显偏离 best；GAN 类训练震荡较大；或实验尚未完成。 |

日志指标解释：

| 指标 | 含义 |
|---|---|
| `best eK` | 验证损失最低的 epoch。 |
| `last/best` | 最后一轮验证损失比 best 高多少。越接近 0 越说明末段贴近最优 checkpoint。 |
| `last5 span` | 最后 5 个有效验证点的相对波动范围。越小说明越平台。 |
| `NaN val/train` | 验证或训练损失出现非有限值，必须谨慎。 |

## IXI-T2 审计

| 方法 | 分类 | 日志证据 | 备注 |
|---|---|---|---|
| ArSSR | 日志证据较强 | 30 epoch；best e24 = 0.0102945；last/best +0.31%；last5 span 0.23%。 | 验证损失已平台。 |
| CycleINR | 日志证据较强，但学习增益极小 | 30 epoch；best e29 = 0.0117778；last/best +0.00%；last5 span 0.00%；首轮到 best 只改善 0.01%。 | 不是没收敛，而是模型几乎没有有效学习，结果接近插值/恒定解。 |
| SwinIR 2.5D | 大概率拟合 | 28 epoch；best e19 = 0.075460；last/best +2.56%；触发 early stopping。 | last5 span 21.58%，说明末段有尖峰波动；使用 best checkpoint 是合理的，但不宜说非常充分饱和。 |
| I3Net | 不确定 | 14 epoch；best e5 = 0.00701433；之后 8 个 epoch 的 train/val 出现 NaN；early stopping。 | 这是最需要补的项。当前主表结果来自 best-val checkpoint，但训练过程有数值不稳定，论文里不能把它说成正常充分收敛。 |
| HAT 2.5D | 大概率拟合 | 19 epoch；best e10 = 0.0746768；last/best +2.23%；触发 early stopping。 | last5 span 32.15%，末段有波动；结果可用，但最好作为 sanity check 候选。 |
| SMamba-UNet 2.5D | 日志证据较强 | 30 epoch；best e22 = 0.0695119；last/best +0.36%；last5 span 0.95%。 | 末段已经很贴近 best。 |
| Pix2Pix-GAN 2.5D | 不确定 | `ixi_gan_2p5d/runs/full_test115_b64/training_history.csv` 当前不存在。 | IXI-GAN 仍未形成可审计的 full_test115 训练证据。 |

## fastMRI-brain-T2 expanded 审计

| 方法 | 分类 | 日志证据 | 备注 |
|---|---|---|---|
| ArSSR | 日志证据较强 | 30 epoch；best e29 = 0.0288746；last/best +0.00%；last5 span 0.25%。 | best 在最后，但末段波动很小，继续训练大概率只带来小幅变化。 |
| CycleINR | 日志证据较强 | 30 epoch；best e29 = 0.0288613；last/best +0.00%；last5 span 0.45%。 | 同上，末段已很平。 |
| ResUNet residual | 不确定/需谨慎 | 17 epoch；best e8 = 0.254596；last/best +8.27%；last5 span 6.40%；early stopping。 | 模型学到了东西，但最后偏离 best 明显。若测试确实用 best checkpoint，结果可以保留；若不是，需核查。 |
| Pix2Pix-GAN 2.5D | 大概率拟合 | 30 epoch；best e26 = 0.0372214；last/best +2.28%；last5 span 3.25%。 | GAN 有正常震荡，但没有失控。 |
| SwinIR 2.5D | 不确定/缺日志 | `fastmri_brain_swinir_2p5d/runs/full` 有结果和 manifest，但没有 `training_history.csv`。 | 主表指标可存在，但“收敛性”不能用日志证明，建议补日志或查是否被移动到备份。 |
| SAINT | 日志证据较强 | 30 epoch；best e22 = 0.264787；last/best +0.03%；last5 span 0.59%。 | 非常典型的平台。 |
| I3Net | 日志证据较强 | 30 epoch；best e25 = 0.0155516；last/best +0.26%；last5 span 0.74%。 | fastMRI-I3Net 训练稳定，和 IXI-I3Net 的 NaN 情况不同。 |
| HAT 2.5D | 不确定/建议延长 | 30 epoch；best e29 = 0.184046；last/best +0.00%；last5 span 3.52%。 | best 在最后一轮，说明仍可能受益于继续训练。建议优先补 60 epoch 或 resume +30。 |
| SMamba-UNet 2.5D | 大概率拟合 | 30 epoch；best e28 = 0.183777；last/best +2.94%；last5 span 6.05%。 | 末段接近平台但波动偏大，可作为次优先 sanity check。 |

## NingXia-T2 8-fold CV 审计

| 方法 | 分类 | 8 折证据 | 备注 |
|---|---|---|---|
| ArSSR | 日志证据较强 | 8/8 folds；mean last/best +0.19%；mean last5 span 1.19%；mean improve 4.38%；4/8 folds best 在最后。 | best-at-last 较多，但末段波动极小。 |
| CycleINR | 日志证据较强，但学习增益极小 | 8/8 folds；mean last/best +0.00%；mean last5 span 0.00%；mean improve 0.01%。 | 和 IXI 类似，稳定但几乎没学到新增量。 |
| ResUNet residual | 日志证据较强 | 8/8 folds；mean last/best +1.05%；mean last5 span 1.94%；mean improve 31.43%。 | 整体平台，个别 fold best 在最后但幅度很小。 |
| Pix2Pix-GAN 2.5D | 不确定/波动明显 | 8/8 folds；mean last/best +12.16%；mean last5 span 22.38%；mean improve 27.03%。 | 多个 fold 的最后状态明显偏离 best，GAN 结果可作为历史/弱 baseline，但不宜作为“充分训练”的强证据。 |
| SwinIR 2.5D | 日志证据较强 | 8/8 folds；mean last/best +0.31%；mean last5 span 0.85%；mean improve 20.53%。 | 当前 NingXia 最稳强 baseline 之一。 |
| SAINT | 大概率拟合 | 8/8 folds；mean last/best +0.76%；mean last5 span 2.32%；mean improve 59.31%。 | 学习充分，末段略有 fold 波动。 |
| I3Net | 大概率拟合 | 8/8 folds；mean last/best +4.27%；mean last5 span 2.08%；mean improve 26.74%。 | 没有 NaN，但最后距离 best 稍大；如果后续重点用 I3Net 做强 medical baseline，可考虑补一次更稳训练。 |
| HAT 2.5D | 日志证据较强 | 8/8 folds；mean last/best +0.39%；mean last5 span 1.11%；mean improve 21.04%。 | 8 折整体稳定。 |
| SMamba-UNet 2.5D | 日志证据较强 | 8/8 folds；mean last/best +0.37%；mean last5 span 1.81%；mean improve 21.36%。 | 8 折整体稳定。 |

## 为什么不能只用 epoch 数比较

I3Net 官方论文写了 1500 epochs、batch size 6，但它的官方代码训练集 `__len__` 是 volume 数量；每个 epoch 对每个 volume 随机抽一个 `hr_slice_patch` 切片块，并且 `one_batch_n_sample` 再在该 volume 内抽样。也就是说，官方的一个 epoch 更像“每个 volume 随机看若干个局部块”，不是穷举所有 possible slice windows。

我们当前很多 2.5D baseline 的数据管线更接近“把体数据切成大量训练样本/窗口后训练”，一个 epoch 内看到的样本覆盖范围可能远大于官方 I3Net 的一个随机 epoch。因此：

1. 数据集更大不必然意味着 epoch 数必须更多。
2. 更合理的比较单位是 optimizer updates、每个 case/每个 slice window 的覆盖次数、验证损失是否平台。
3. 论文里不应写“我们比官方少跑但等价”，而应写“所有方法在统一协议下训练，使用验证集 best checkpoint；收敛性由验证损失曲线和早停判据确认”。

## 为什么我们的 I3Net 指标不能直接对齐官方表

官方 I3Net 和我们当前协议有几个关键差异：

| 项目 | 官方 I3Net | 当前主线 |
|---|---|---|
| IXI 子集 | 185 个 Hammersmith Hospital volumes，150 train / 35 test。 | 当前 IXI split 是 train 404 / val 58 / test 115，且混合 HH、Guys、IOP；早期表还有 test n=25。 |
| 数据归一化 | 官方代码按 `[0,4095] -> [0,1]`，center crop 256x256。 | 当前主线按本地统一 NIfTI/强度协议，评估输出为统一主表五指标。 |
| 评估切片 | 官方 test 先从 HR 直接 `gt[..., ::upscale]` 得到 LR，再预测整段，最后裁掉两端若干 slice，并在 axial/coronal/sagittal 三方向算 SSIM。 | 当前主线主要评价 x4 缺失目标切片，指标为 PSNR/SSIM/MAE/MSE/NCC，与 Linear/Cubic 及其他 baseline 保持一致。 |
| 训练 epoch | 官方 1500 epoch，但每 epoch 是 volume-level 随机 patch 抽样。 | 当前多数脚本 30 epoch，但每 epoch 的样本定义不同，不能直接按数字比较。 |

因此，官方表里 T2 x4 PSNR 44 左右，而我们主表 IXI-I3Net 约 31，并不自动说明复现失败。它更多反映数据切分、强度尺度、评估对象、SSIM/PSNR 计算口径不同。论文里可以自成体系，但必须把自己定位为“统一 T2/x4 through-plane benchmark protocol”，而不是“严格复现官方 IXI 数值”。

## 能不能支撑论文 claim

可以，但 claim 要精确。当前体系能支撑的说法是：

1. 在统一 T2/x4 through-plane interpolation 协议下，我们比较了 classical interpolation、CNN residual、INR、Transformer、medical slice synthesis、Mamba/GAN 等多类 baseline。
2. 三个数据集分别覆盖公开健康脑 MRI、公开 fastMRI brain T2、以及本地临床 NingXia case-level CV，能支持跨数据源泛化讨论。
3. 主表指标必须全部来自同一评估脚本、同一 sparse sampling 规则、同一 test split/CV split。
4. 对于 published baseline，应写“adapted/re-implemented under our protocol”，不要写成“完全复现原论文官方指标”。

不建议支撑的说法：

1. “所有 baseline 都达到官方最优训练预算。”
2. “30 epoch 与官方 1500 epoch 等价。”
3. “我们的 I3Net 复现应当和官方 IXI 表格数值直接一致。”
4. “GAN 结果已经充分优化。”目前 GAN 日志不支持这个强说法。

顶刊层面的关键不只是 baseline 个数，而是问题定义、方法创新、数据协议严谨性、消融和统计可靠性。当前三数据集和主表框架是可以写成自洽体系的，但为了减少审稿风险，建议补一个“训练预算敏感性/收敛性验证”小节。

## 下一步建议

优先级 1：不用全量重跑，先补最容易被质疑的项。

| 优先级 | 动作 | 原因 |
|---|---|---|
| P0 | IXI-I3Net 重新训练稳定版，避免 NaN；可用更低 lr、关闭 AMP 或加梯度裁剪。 | I3Net 是最贴近任务的 published medical baseline，IXI 日志目前最不干净。 |
| P0 | fastMRI-HAT resume +30 或直接 60 epoch sanity check。 | best 在最后一轮，说明可能还没完全平台。 |
| P1 | 查找/补回 fastMRI-SwinIR full 的 `training_history.csv`。 | 主表有指标但缺收敛证据。 |
| P1 | 若 GAN 要进入论文主表，NingXia-GAN 需标注 best checkpoint，并考虑重训稳定版。 | 当前 8 折 mean last/best +12.16%，波动明显。 |
| P2 | 对最终新模型 + I3Net/HAT/SwinIR/SAINT 做 extended-budget 小实验。 | 用来证明 rank 稳定，避免“baseline 训练不足”质疑。 |

建议的论文补充实验不是把全部 baseline 都重跑到 100/150/300 epoch，而是选择 2-4 个关键模型做训练预算敏感性：

| 预算 | 目标 |
|---|---|
| 30 epoch | 当前主表统一预算。 |
| 60 epoch | 检查强 baseline 是否还有明显提升。 |
| 100 epoch 或 early-stop patience 更长 | 只给最终方法和最强对照，用于 rebuttal 级别的稳健性证据。 |

如果 60/100 epoch 相对 30 epoch 的 test PSNR 改善小于约 0.1-0.2 dB，且方法排序不变，就可以在论文里写：延长训练预算带来的收益有限，当前统一预算足以比较方法间趋势。

## 可以直接写进论文的方法学表述

推荐写法：

> All learning-based baselines were trained under the same T2 x4 through-plane interpolation protocol. We selected the checkpoint with the best validation loss and evaluated it on the held-out test cases or case-level cross-validation folds. Because different original papers define epochs and sampling units differently, we do not compare absolute epoch counts with the original implementations; instead, we report convergence diagnostics and use a unified validation-based checkpointing rule for all adapted baselines.

中文意思是：我们不是拿“30 epoch”去碰瓷官方“1500 epoch”，而是把所有方法放到同一个任务、同一个 split、同一个评估脚本、同一个 best-val 规则下比较。这是可以自圆其说的。

