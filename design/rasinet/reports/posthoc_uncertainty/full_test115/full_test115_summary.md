# full_test115 RASI post-hoc reliability 中文总结

说明：本页只汇总 post-hoc uncertainty 结果，不包含任何新 RASI-Net 训练结论。

## 1. 主结论

- `baseline_disagreement` 是当前最稳的 proxy：在 SwinIR、HAT、ACSI、I3Net 上全像素 corr 约 `0.50-0.62`，非零脑区 corr 仍为正。
- 背景区域会抬高 pixel-level corr，因此论文表述中应优先报告 masked/nonzero 版本。
- residual-to-linear / residual-to-cubic 可以作为 sanity 或 ablation，不应作为主故事。

## 2. 全部 method/proxy 可靠性表

| 方法 | Proxy | Cases | MAE | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Failure AUPRC | Top-k recall |
|---|---|---|---|---|---|---|---|---|---|---|
| ACSI | Baseline disagreement | 115 | 20.8475 | 0.5667 | 0.4178 | 4.2948 | 1.4552 | 0.9871 | 0.8849 | 0.8333 |
| ACSI | Residual to cubic | 115 | 20.8475 | 0.4271 | 0.1999 | 5.3230 | 2.8784 | 0.9862 | 0.8682 | 0.8333 |
| ACSI | Residual to linear | 115 | 20.8475 | 0.4101 | 0.1692 | 5.2693 | 2.8683 | 0.9838 | 0.8522 | 0.7500 |
| HAT | Baseline disagreement | 115 | 22.2500 | 0.6090 | 0.4578 | 4.4683 | 1.5250 | 0.9871 | 0.8849 | 0.8333 |
| HAT | Residual to cubic | 115 | 22.2500 | 0.4269 | 0.1576 | 5.7275 | 3.1794 | 0.9879 | 0.8882 | 0.8333 |
| HAT | Residual to linear | 115 | 22.2500 | 0.4096 | 0.1288 | 5.6766 | 3.2166 | 0.9862 | 0.8641 | 0.8333 |
| I3Net | Baseline disagreement | 115 | 17.5276 | 0.5018 | 0.3567 | 3.9249 | 1.4225 | 0.9822 | 0.8473 | 0.7500 |
| I3Net | Residual to cubic | 115 | 17.5276 | 0.4406 | 0.3317 | 4.5618 | 2.5275 | 0.9814 | 0.8443 | 0.7500 |
| I3Net | Residual to linear | 115 | 17.5276 | 0.4363 | 0.3466 | 4.4718 | 2.4456 | 0.9773 | 0.8036 | 0.7500 |
| SwinIR | Baseline disagreement | 115 | 22.4556 | 0.6153 | 0.4572 | 4.4922 | 1.5253 | 0.9871 | 0.8849 | 0.8333 |
| SwinIR | Residual to cubic | 115 | 22.4556 | 0.4217 | 0.1431 | 5.8561 | 3.3856 | 0.9862 | 0.8682 | 0.8333 |
| SwinIR | Residual to linear | 115 | 22.4556 | 0.4031 | 0.1120 | 5.8223 | 3.5002 | 0.9846 | 0.8558 | 0.8333 |

## 3. Proxy 对比表

| 方法 | 排名 | Proxy | Cases | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---|---|---|---|---|---|---|---|
| ACSI | 1 | Baseline disagreement | 115 | 0.5667 | 0.4178 | 4.2948 | 1.4552 | 0.9871 | 0.8333 |
| ACSI | 2 | Residual to cubic | 115 | 0.4271 | 0.1999 | 5.3230 | 2.8784 | 0.9862 | 0.8333 |
| ACSI | 3 | Residual to linear | 115 | 0.4101 | 0.1692 | 5.2693 | 2.8683 | 0.9838 | 0.7500 |
| HAT | 1 | Baseline disagreement | 115 | 0.6090 | 0.4578 | 4.4683 | 1.5250 | 0.9871 | 0.8333 |
| HAT | 2 | Residual to cubic | 115 | 0.4269 | 0.1576 | 5.7275 | 3.1794 | 0.9879 | 0.8333 |
| HAT | 3 | Residual to linear | 115 | 0.4096 | 0.1288 | 5.6766 | 3.2166 | 0.9862 | 0.8333 |
| I3Net | 1 | Baseline disagreement | 115 | 0.5018 | 0.3567 | 3.9249 | 1.4225 | 0.9822 | 0.7500 |
| I3Net | 2 | Residual to cubic | 115 | 0.4406 | 0.3317 | 4.5618 | 2.5275 | 0.9814 | 0.7500 |
| I3Net | 3 | Residual to linear | 115 | 0.4363 | 0.3466 | 4.4718 | 2.4456 | 0.9773 | 0.7500 |
| SwinIR | 1 | Baseline disagreement | 115 | 0.6153 | 0.4572 | 4.4922 | 1.5253 | 0.9871 | 0.8333 |
| SwinIR | 2 | Residual to cubic | 115 | 0.4217 | 0.1431 | 5.8561 | 3.3856 | 0.9862 | 0.8333 |
| SwinIR | 3 | Residual to linear | 115 | 0.4031 | 0.1120 | 5.8223 | 3.5002 | 0.9846 | 0.8333 |

## 4. Baseline disagreement 方法对比表

| 排名 | 方法 | Cases | Pixel corr | Slice corr | AURC | MAE@50% low-U | Failure AUROC | Top-k recall |
|---|---|---|---|---|---|---|---|---|
| 1 | SwinIR | 115 | 0.6153 | 0.4572 | 4.4922 | 1.5253 | 0.9871 | 0.8333 |
| 2 | HAT | 115 | 0.6090 | 0.4578 | 4.4683 | 1.5250 | 0.9871 | 0.8333 |
| 3 | ACSI | 115 | 0.5667 | 0.4178 | 4.2948 | 1.4552 | 0.9871 | 0.8333 |
| 4 | I3Net | 115 | 0.5018 | 0.3567 | 3.9249 | 1.4225 | 0.9822 | 0.7500 |

## 5. Failure detection 表

| 方法 | Proxy | Cases | Failure cases | AUROC | AUPRC | Top-k recall |
|---|---|---|---|---|---|---|
| HAT | Residual to cubic | 115 | 12 | 0.9879 | 0.8882 | 0.8333 |
| ACSI | Baseline disagreement | 115 | 12 | 0.9871 | 0.8849 | 0.8333 |
| HAT | Baseline disagreement | 115 | 12 | 0.9871 | 0.8849 | 0.8333 |
| SwinIR | Baseline disagreement | 115 | 12 | 0.9871 | 0.8849 | 0.8333 |
| ACSI | Residual to cubic | 115 | 12 | 0.9862 | 0.8682 | 0.8333 |
| SwinIR | Residual to cubic | 115 | 12 | 0.9862 | 0.8682 | 0.8333 |
| HAT | Residual to linear | 115 | 12 | 0.9862 | 0.8641 | 0.8333 |
| SwinIR | Residual to linear | 115 | 12 | 0.9846 | 0.8558 | 0.8333 |
| ACSI | Residual to linear | 115 | 12 | 0.9838 | 0.8522 | 0.7500 |
| I3Net | Baseline disagreement | 115 | 12 | 0.9822 | 0.8473 | 0.7500 |
| I3Net | Residual to cubic | 115 | 12 | 0.9814 | 0.8443 | 0.7500 |
| I3Net | Residual to linear | 115 | 12 | 0.9773 | 0.8036 | 0.7500 |

## 6. Masked / nonzero 主表

| 方法 | Proxy | All pixel corr | Nonzero corr | Background corr | Nonzero-All | Background fraction |
|---|---|---|---|---|---|---|
| ACSI | Baseline disagreement | 0.5667 | 0.4037 | 0.5231 | -0.1630 | 0.5894 |
| HAT | Baseline disagreement | 0.6090 | 0.4628 | 0.5488 | -0.1462 | 0.5894 |
| I3Net | Baseline disagreement | 0.5018 | 0.3068 | 0.4941 | -0.1950 | 0.5894 |
| SwinIR | Baseline disagreement | 0.6153 | 0.4711 | 0.5660 | -0.1442 | 0.5894 |
| ACSI | Residual to cubic | 0.4271 | 0.2438 | 0.4136 | -0.1834 | 0.5894 |
| ACSI | Residual to linear | 0.4101 | 0.2335 | 0.4342 | -0.1766 | 0.5894 |
| HAT | Residual to cubic | 0.4269 | 0.2464 | 0.4111 | -0.1805 | 0.5894 |
| HAT | Residual to linear | 0.4096 | 0.2386 | 0.4183 | -0.1711 | 0.5894 |
| I3Net | Residual to cubic | 0.4406 | 0.2548 | 0.4404 | -0.1858 | 0.5894 |
| I3Net | Residual to linear | 0.4363 | 0.2552 | 0.4706 | -0.1811 | 0.5894 |
| SwinIR | Residual to cubic | 0.4217 | 0.2408 | 0.4215 | -0.1809 | 0.5894 |
| SwinIR | Residual to linear | 0.4031 | 0.2336 | 0.4321 | -0.1695 | 0.5894 |

## 7. 建议写法

当前更稳的表述是：在不重新训练模型的情况下，多个强插值模型之间的 baseline disagreement 可以作为低成本 failure-aware reliability signal；它与真实误差保持正相关，并能较好识别高误差 case。由于全像素结果受背景影响，主文应优先报告 nonzero/masked 版本，all-pixel 结果作为补充。
