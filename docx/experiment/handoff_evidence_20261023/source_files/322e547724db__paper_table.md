# IXI-T2 ACSI-Net Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | ZGE | ZLE | EdgeZ | NCC-z-MAE | Params(M) | FLOPs(G) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IXI-T2 | x4 | mini | linear | 5 | 25.0849 | 0.8268 | 47.0867 | 12633.8805 | 0.9121 | 0.0180 | 0.0260 | 0.0129 | 0.0641 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | mini | cubic | 5 | 24.6061 | 0.8131 | 51.1790 | 14744.4780 | 0.8988 | 0.0189 | 0.0262 | 0.0135 | 0.0606 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | mini | acsinet | 5 | 25.7478 | 0.8438 | 43.0894 | 11134.6133 | 0.9229 | 0.0172 | 0.0255 | 0.0128 | 0.0555 | 0.2129 | 9.1244 | ours ACSI-Net anatomy-consistent group model |

Note: ACSI-Net v1 predicts the whole intermediate slice group and reports 3D consistency metrics. Smoke and mini runs are screening evidence only.
