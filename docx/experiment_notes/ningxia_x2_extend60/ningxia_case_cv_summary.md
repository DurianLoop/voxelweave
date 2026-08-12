# NingXia-T2 x2 60-epoch case-level CV

| Method | Folds | PSNR mean | SSIM mean | MAE mean | MSE mean | NCC mean |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 8 | 24.9741 | 0.7264 | 78.5349 | 27551.4768 | 0.9112 |
| Cubic | 8 | 24.1081 | 0.6767 | 89.5215 | 33708.1987 | 0.8952 |
| CycleINR | 8 | 25.1538 | 0.7427 | 76.6723 | 26571.4690 | 0.9146 |
| Res-SRDiff | 8 | 22.6714 | 0.5619 | 140.4503 | 56206.7760 | 0.8894 |
| SMamba-UNet 2.5D | 8 | 25.9101 | 0.7813 | 68.4655 | 22757.3826 | 0.9281 |
| SwinIR 2.5D | 8 | 26.0556 | 0.7821 | 67.3308 | 21930.8546 | 0.9310 |
| HAT 2.5D | 8 | 26.1387 | 0.7853 | 66.2919 | 21520.2802 | 0.9321 |
| SAINT | 8 | 25.6706 | 0.7677 | 72.4046 | 23699.0011 | 0.9245 |

Note: this table averages case-level CV fold means; the main table only uses PSNR / SSIM / MAE / MSE / NCC.
