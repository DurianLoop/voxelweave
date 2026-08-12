# T2 x4 主表补全总结

日期：2026-07-03

## 完成状态

当前主表 `docx/experiment/experiment_master_table.md` 已更新为最新横向结果。IXI-T2 已统一补齐到 test n=115，不再混用早期 test n=25。

已完成并写入主表的补充项：

| 项目 | 状态 | 采用结果 |
|---|---|---|
| IXI-T2 Linear / Cubic | 已补齐 | `ixi_i3net/runs/full_test115/metrics/summary_metrics.csv` 中的 n=115 baseline |
| IXI-T2 ArSSR | 已补齐 | `ixi_arssr/runs/full_test115/metrics/summary_metrics.csv`，eval-only 复用 full best checkpoint |
| IXI-T2 CycleINR | 已补齐 | `ixi_cycleinr/runs/full_test115/metrics/summary_metrics.csv`，eval-only 复用 full best checkpoint |
| IXI-T2 ResUNet residual | 已补齐 | `pre/ixi_diffusion/runs/resunet_full_t2_test115/metrics/summary_metrics.csv`，eval-only 复用 full best checkpoint |
| IXI-T2 SwinIR 2.5D | 已补齐 | `ixi_swinir_2p5d/runs/full_test115/metrics/summary_metrics.csv`，eval-only 复用 full best checkpoint |
| IXI-T2 SAINT | 已补齐 | `pre/ixi_diffusion/runs/saint_full_t2_test115/metrics/summary_metrics.csv`，eval-only 复用 full best checkpoint |
| IXI-T2 I3Net | 已补齐 | `ixi_i3net/runs/full_test115_stable/metrics/summary_metrics.csv`，稳定版重训 |
| fastMRI HAT | 已更新 | `fastmri_brain_hat_2p5d/runs/full_extend60/metrics/summary_metrics.csv` |
| fastMRI SwinIR | 已更新 | `fastmri_brain_swinir_2p5d/runs/full_audit/metrics/summary_metrics.csv` |

## IXI-T2 test n=115 排名

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| I3Net (2024) | 31.3058 | 0.9285 | 17.5276 | 2565.3177 | 0.9788 |
| SMamba-UNet 2.5D (2024+) | 29.3536 | 0.9077 | 21.1352 | 3691.2381 | 0.9699 |
| HAT 2.5D (2023) | 28.7249 | 0.9016 | 22.2500 | 4088.7422 | 0.9663 |
| SAINT (2020) | 28.6677 | 0.8970 | 22.8365 | 4128.0151 | 0.9660 |
| SwinIR 2.5D (2021) | 28.6485 | 0.8997 | 22.4556 | 4137.5109 | 0.9658 |
| ResUNet residual (Internal) | 27.4611 | 0.8812 | 25.2395 | 4985.4989 | 0.9552 |
| ArSSR (2021) | 27.2467 | 0.8773 | 25.5509 | 5267.3658 | 0.9533 |
| Pix2Pix-GAN 2.5D (2017) | 27.1070 | 0.8506 | 27.0202 | 5372.2668 | 0.9538 |
| CycleINR (2024) | 26.1728 | 0.8527 | 29.2765 | 6553.8469 | 0.9390 |
| Linear (Classical) | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 |
| Cubic (Classical) | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 |

IXI-T2 上，I3Net 稳定版在五个指标上全部最强。第二梯队是 SMamba-UNet 2.5D，其后 HAT / SAINT / SwinIR 非常接近。CycleINR 基本贴近 Linear，说明这条 INR 线在当前 protocol 下没有形成明显增益。

## I3Net 稳定版收敛情况

`ixi_i3net/runs/full_test115_stable/training_history.csv` 显示：

| 项目 | 数值 |
|---|---:|
| epochs_completed | 51 |
| early_stopped | true |
| best_epoch | 38 |
| best_val_loss | 0.0065419 |
| last_val_loss | 0.0065643 |
| last_vs_best | +0.34% |

这说明此前 IXI-I3Net 的 NaN 风险已经通过稳定版训练基本消除，可以作为主表 I3Net 结果使用。

## fastMRI 更新点

HAT 使用 `full_extend60` 后明显提升：

| Method / Profile | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| HAT old full | 22.7858 | 0.7536 | 49.6702 | 10454.4878 | 0.9079 |
| HAT full_extend60 | 23.0894 | 0.7688 | 47.2467 | 9773.1765 | 0.9138 |

SwinIR 使用 `full_audit` 后 PSNR 基本持平，SSIM / MAE / NCC 略好，并补上训练日志证据：

| Method / Profile | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| SwinIR old full | 22.3615 | 0.7455 | 52.0221 | 11591.7882 | 0.8974 |
| SwinIR full_audit | 22.3578 | 0.7494 | 50.8733 | 11636.3791 | 0.8977 |

fastMRI 当前仍由 I3Net 在五个主指标上领先。

## 当前论文口径建议

1. 主表可以写成统一 T2/x4 through-plane interpolation protocol，下游比较全部使用同一 test split / CV split / metrics。
2. IXI-T2 现在已经可以统一称为 test n=115，不需要再解释表内混合 n=25。
3. I3Net 是最强 published medical slice synthesis baseline，IXI 与 fastMRI 都领先，NingXia 不领先。
4. NingXia 上应强调外部临床分布差异：SwinIR / HAT / SMamba / SAINT 更接近，I3Net 没有在该数据集保持第一。
5. GAN 线只作为 inherited weak baseline，不建议作为强 baseline 展开过多讨论。
6. ArSSR / CycleINR 已完成横向补齐，但当前结果说明 INR 线在此 deterministic T2/x4 through-plane setting 中不是主攻方向。

