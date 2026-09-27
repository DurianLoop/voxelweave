# PAST-Net G07 在 IXI-T2 test-115 的结果与下一步路线

更新时间：2026-08-11

## 实验结论

`full_g07_ma3_wide200_test115` 已完整训练 200 轮，并在 IXI-T2 x4 的全部 115 个测试病例上完成评估。结果为：

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G/slice) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Linear | 115 | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 | 0 | 0 |
| Cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 | 0 | 0 |
| I3Net `full_test115_stable` | 115 | **31.3058** | **0.9285** | **17.5276** | **2565.3177** | **0.9788** | 23.2052 | 100.7761 |
| PAST-Net G07 wide MA3 | 115 | 29.9892 | 0.9155 | 19.7240 | 3291.9361 | 0.9733 | **0.7436** | 114.0851 |

结论：G07 没有在 IXI 上超过 I3Net，因此当前不能声称达到 SOTA。它仍是当前本地同协议结果中的第二名，并且以约 I3Net `1/31` 的参数量达到接近 30 dB，但由于全部特征都在 256x256 分辨率处理，单切片 FLOPs 并不低于 I3Net。

## 相对 I3Net

| Metric | G07 - I3Net | 近似配对 95% CI | G07 wins |
|---|---:|---:|---:|
| PSNR | -1.3165 dB | `[-1.4360, -1.1970]` | 5/115 |
| SSIM | -0.0130 | `[-0.0142, -0.0117]` | 5/115 |
| MAE | +2.1964 | `[+1.8980, +2.4947]` | 5/115 |
| MSE | +726.62 | `[+562.91, +890.32]` | 5/115 |
| NCC | -0.00555 | `[-0.00623, -0.00487]` | 6/115 |

PSNR 的病例差异范围为 `-2.8852` 到 `+0.3610 dB`。置信区间和胜负数都说明差距是结构性的，不是由少量异常病例拉低平均值。

## 本地 test-115 排名

下表只比较本地已有、IXI-T2 x4、test n=115 的同协议结果：

| Rank | Method | PSNR | SSIM | G07 相对差值 |
|---:|---|---:|---:|---:|
| 1 | I3Net stable | 31.3058 | 0.9285 | -1.3165 |
| 2 | **PAST-Net G07** | **29.9892** | **0.9155** | 0 |
| 3 | ACSI-Net | 29.3904 | 0.9078 | +0.5989 |
| 4 | SMamba-UNet | 29.3536 | 0.9077 | +0.6356 |
| 5 | HAT | 28.7249 | 0.9016 | +1.2644 |
| 6 | SAINT | 28.6677 | 0.8970 | +1.3216 |
| 7 | SwinIR | 28.6485 | 0.8997 | +1.3407 |

这说明 G07 从 fastMRI 迁移到 IXI 后仍然是有效架构，而不是只对一个数据集有效；但 I3Net 的 interval-level 建模在 IXI 上仍有明显优势。

## 站点分层

| Site | Cases | G07 PSNR | I3Net PSNR | ΔPSNR | G07 wins |
|---|---:|---:|---:|---:|---:|
| HH | 32 | 29.8472 | 30.4613 | -0.6141 | 5/32 |
| Guys | 59 | 30.4727 | 32.2852 | -1.8125 | 0/59 |
| IOP | 24 | 28.9901 | 30.0239 | -1.0338 | 0/24 |

G07 与 I3Net 的最大差距集中在 Guys，而不是所有站点等比例下降。Guys 本身是三组中 I3Net PSNR 最高的站点，这表明 I3Net 更能利用该站点平滑、规则的 z 向变化；G07 的单目标切片残差预测没有完全利用 interval 内多个缺失切片的联合规律。

## 训练过程

| 项目 | 值 |
|---|---:|
| Planned/completed epochs | 200/200 |
| Best epoch | 191 |
| Best validation loss | 0.0115178 |
| Last validation loss | 0.0115701 |
| Last learning rate | 1.5e-4 |
| AMP overflow optimizer-step skips | 63 / about 150,000 updates (0.042%) |
| Total training time | 124.30 h |
| Samples per epoch | 12,000 from 153,195 |
| Total sampled examples | 2,400,000 |
| Equivalent full-pool passes | about 15.7 |

验证损失从 epoch 0 的 `0.01524` 持续下降到 epoch 191 的 `0.01152`，没有明显过拟合。训练中动态 AMP scaler 共跳过 63 次梯度溢出的 optimizer update，约占 15 万次更新的 `0.042%`；每次最多一轮一次，训练和验证 loss 均保持有限，说明 scaler 的恢复逻辑正常，不影响总体结论。学习率始终未衰减，继续低学习率训练可能仍有小幅收益，但不可能合理解释或填补 `1.32 dB` 的结构差距。

## 从 fastMRI 与 IXI 联合得到的判断

1. G07 在 fastMRI 相对 I3Net为 `+0.2808 dB`，在 IXI 为 `-1.3165 dB`。宽 MA3 对困难、噪声更强的 fastMRI 有优势，但在规则、平滑的 IXI 上，独立单切片预测弱于 interval-level 联合建模。
2. 不能因为 IXI 结果退步就回到已经失败的 MA4W。G09/G10 已证明原 MA4W window 实现不稳定。正确方向是在强 G07 单切片 backbone 后增加轻量、残差式的 interval refinement。
3. 下一版应共享同一架构与超参数在 fastMRI/IXI 上验证，不能针对 Guys 站点单独调 loss 或后处理，否则会损伤外部泛化可信度。
4. G071-G075 的 fastMRI 消融仍应先完成。若 reliability/context 在 fastMRI 上成立，再把胜出的组件迁移到 IXI，避免直接用 IXI test-115 反复选型。

## 下一步结构路线

建议在 G071-G075 完成后只推进一条 `G076` 路线：

```text
G07/G075 single-slice predictions for offsets 1/2/3
    -> shared low-resolution interval feature stack
    -> lightweight z-axis mixer across three offsets
    -> zero-initialized residual correction
    -> three refined missing slices
```

关键约束：

- 保留 G07 的四锚点、coarse skip、confidence-gated residual 和宽 MA3 trunk。
- 三个 offset 仍先由共享单切片模型生成，避免重新走 MA4W 的整窗生成路线。
- 只在 1/4 或 1/8 分辨率做 z-axis mixing，控制 FLOPs 和显存。
- refinement 输出零初始化残差，warm-start 时严格等价于已训练 G07/G075。
- 不使用 I3Net 输出、测试病例级 blend、站点特定权重或测试集 checkpoint 选择。
- 先在 fastMRI validation 验证，再锁定后一次性评估 IXI test-115。

阶段目标不是立即承诺超过 31.31 dB，而是先把 IXI 差距从 `1.32 dB` 压缩到 `0.5 dB` 以内，同时保持 fastMRI 不退步。若轻量 interval refinement 在两个数据集上都成立，再继续扩大 z-axis receptive field。
