# NingXia-T2 x6 60-epoch case-level CV

| Method | Folds | PSNR mean | SSIM mean | MAE mean | MSE mean | NCC mean |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 8 | 21.7375 | 0.6509 | 118.6269 | 53812.4881 | 0.8146 |
| Cubic | 8 | 21.6523 | 0.6483 | 119.6982 | 54616.6079 | 0.8118 |
| ArSSR | 8 | 22.4720 | 0.7020 | 106.4477 | 46384.2568 | 0.8423 |
| CycleINR | 8 | 22.1578 | 0.6886 | 111.6263 | 49569.1804 | 0.8335 |
| ResUNet residual | 8 | 22.9161 | 0.7281 | 100.4640 | 41591.4635 | 0.8610 |
| Res-SRDiff | 8 | 20.8328 | 0.6008 | 139.9794 | 62636.9837 | 0.7782 |
| SwinIR 2.5D | 8 | 23.0201 | 0.7392 | 97.7710 | 40687.7343 | 0.8637 |

Note: this table averages case-level CV fold means; the main table only uses PSNR / SSIM / MAE / MSE / NCC.
