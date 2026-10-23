# IXI-T2 RASI-Net Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | ZGE | ZLE | EdgeZ | NCC-z-MAE | Params(M) | FLOPs(G) | Source | Err-U-Corr | Slice-Err-U-Corr | Risk-AURC | Mean-U |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IXI-T2 | x4 | smoke | linear | 1 | 27.4291 | 0.8772 | 26.3205 | 3283.3493 | 0.9566 | 0.0101 | 0.0132 | 0.0076 | 0.0236 | 0.0000 | 0.0000 | ours rerun | NA | NA | NA | NA |
| IXI-T2 | x4 | smoke | cubic | 1 | 27.1568 | 0.8682 | 27.6104 | 3523.0295 | 0.9507 | 0.0104 | 0.0129 | 0.0078 | 0.0234 | 0.0000 | 0.0000 | ours rerun | NA | NA | NA | NA |
| IXI-T2 | x4 | smoke | rasinet | 1 | 26.5423 | 0.8473 | 30.0443 | 3966.2439 | 0.9501 | 0.0117 | 0.0165 | 0.0096 | 0.0186 | 0.0413 | 1.6924 | ours RASI-Net reliability-aware group model | -0.1654 | 0.1292 | 34.5782 | 0.1133 |

Note: RASI-Net v1 predicts the whole intermediate slice group and reports uncertainty-aware reliability metrics. Smoke and mini runs are screening evidence only.

## Failure Detection

- AUROC: NA
- AUPRC: 1.0000
- Top-k failure recall: 1.0000
