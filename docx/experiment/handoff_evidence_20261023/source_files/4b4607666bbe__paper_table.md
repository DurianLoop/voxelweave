# IXI-T2 ACSI-Net Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | ZGE | ZLE | EdgeZ | NCC-z-MAE | Params(M) | FLOPs(G) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IXI-T2 | x4 | smoke | linear | 1 | 27.4291 | 0.8772 | 26.3205 | 3283.3493 | 0.9566 | 0.0101 | 0.0132 | 0.0076 | 0.0236 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | smoke | cubic | 1 | 27.1568 | 0.8682 | 27.6104 | 3523.0295 | 0.9507 | 0.0104 | 0.0129 | 0.0078 | 0.0234 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | smoke | acsinet | 1 | 26.0174 | 0.7942 | 33.5206 | 4430.8866 | 0.9495 | 0.0149 | 0.0233 | 0.0098 | 0.0161 | 0.0633 | 2.7273 | ours ACSI-Net anatomy-consistent group model |

Note: ACSI-Net v1 predicts the whole intermediate slice group and reports 3D consistency metrics. Smoke and mini runs are screening evidence only.
