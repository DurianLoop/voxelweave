# NingXia-T2 GAN Smoke CV

| Method | Folds | PSNR mean | SSIM mean | MAE mean | MSE mean | NCC mean |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 1 | 23.0590 | 0.6681 | 92.4671 | 28483.7821 | 0.8721 |
| Cubic | 1 | 21.8955 | 0.6138 | 107.2163 | 37366.5693 | 0.8409 |
| ResUNet residual | 1 | 23.6557 | 0.7039 | 86.8604 | 24881.6793 | 0.8874 |
| Pix2Pix/GAN-style 2.5D | 1 | 20.9636 | 0.6637 | 127.8096 | 46056.8271 | 0.8380 |
| SAINT-style | 1 | 22.3373 | 0.6921 | 111.5875 | 33341.9659 | 0.8677 |

Note: this table averages case-level CV fold means; the main table only uses PSNR / SSIM / MAE / MSE / NCC.
