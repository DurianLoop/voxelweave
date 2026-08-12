# RASI post-hoc uncertainty 跨数据集总结

本总结汇总 IXI full_test115、fastMRI-brain T2 full、NingXia 8-fold CV 三个数据集上的 post-hoc reliability 结果。所有结果均来自已有预测，不包含新 RASI-Net 训练。

## 1. Baseline disagreement 主结果

| Dataset | Cases | Methods | All-pixel corr range | Nonzero corr range | Failure AUROC range | 结论 |
|---|---:|---|---:|---:|---:|---|
| IXI full_test115 | 115 | I3Net / HAT / SwinIR / ACSI | 0.5018-0.6153 | 0.3068-0.4711 | 0.9822-0.9871 | 最强、最稳定；可作为主证据 |
| fastMRI-brain T2 | 24 | I3Net / HAT / SwinIR | 0.4138-0.5122 | 0.2347-0.3500 | 1.0000-1.0000 | 跨 public 数据仍为正相关，但 case 数较小 |
| NingXia CV | 22 | I3Net / HAT / SwinIR | 0.4562-0.4856 | 0.2886-0.3137 | 0.9474-0.9474 | 外部/临床域仍保持正相关，failure detection 略低于 IXI/fastMRI |

## 2. 主要观察

- `baseline_disagreement` 在三个数据集上都保持正相关，是当前最适合主线叙述的 proxy。
- nonzero/masked corr 明显低于 all-pixel corr，说明背景区域确实会抬高 pixel-level 结果；论文主表应优先报告 nonzero/masked 版本。
- fastMRI 和 NingXia 的 case 数都较小，因此更适合作为跨数据集补充证据，而不是单独支撑强结论。
- residual proxy 在部分 slice-level 指标上偶尔较高，但整体稳定性不如 `baseline_disagreement`，建议只作为 ablation。

## 3. 建议论文表述

推荐写法：

> Across IXI, fastMRI-brain T2, and NingXia T2, baseline disagreement consistently provides a positive post-hoc reliability signal for existing interpolation models. The signal remains positive under nonzero-mask evaluation and helps identify high-error cases without retraining the reconstruction networks.

中文版本：

> 在 IXI、fastMRI-brain T2 和 NingXia T2 上，多模型预测分歧均能提供稳定为正的 post-hoc 可信性信号；即使采用更严格的非零脑区评价，该信号仍与真实误差保持正相关，并能在不重新训练重建模型的情况下帮助发现高误差 case。

## 4. 产物位置

- IXI: `rasinet/reports/posthoc_uncertainty/full_test115/`
- fastMRI: `rasinet/reports/posthoc_uncertainty/fastmri_full/`
- NingXia: `rasinet/reports/posthoc_uncertainty/ningxia_cv/`

## 5. 仍未做的可选项

- TTA variance proxy：需要额外模型推理，暂不纳入当前低算力证据链。
- learned RASI-Net uncertainty ablation：只能作为辅助对照，不应改变当前 post-hoc 主线。
