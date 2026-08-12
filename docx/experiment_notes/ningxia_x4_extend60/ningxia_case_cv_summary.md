# NingXia-T2 x4 60-epoch case-level CV

| Method | Folds | PSNR mean | SSIM mean | MAE mean | MSE mean | NCC mean |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 8 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| Cubic | 8 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |
| ArSSR | 8 | 23.4566 | 0.7241 | 91.8598 | 36115.4376 | 0.8793 |
| ResUNet residual | 8 | 23.7562 | 0.7379 | 90.5450 | 33771.8800 | 0.8876 |
| SMamba-UNet 2.5D | 8 | 24.0160 | 0.7542 | 84.8084 | 31545.2244 | 0.8947 |
| SwinIR 2.5D | 8 | 24.0370 | 0.7573 | 83.8378 | 31317.4826 | 0.8946 |
| SAINT | 8 | 23.8388 | 0.7473 | 88.1769 | 33105.9966 | 0.8909 |

Note: this table averages case-level CV fold means; the main table only uses PSNR / SSIM / MAE / MSE / NCC.
