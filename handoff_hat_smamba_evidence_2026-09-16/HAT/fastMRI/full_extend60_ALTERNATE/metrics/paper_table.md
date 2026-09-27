# fastMRI-brain-T2 HAT-style 2.5D Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fastMRI-brain-T2 expanded | x4 | full_extend60 | linear | 24 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 | 0.0000 | 0.0000 | ours rerun |
| fastMRI-brain-T2 expanded | x4 | full_extend60 | cubic | 24 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 | 0.0000 | 0.0000 | ours rerun |
| fastMRI-brain-T2 expanded | x4 | full_extend60 | hat | 24 | 23.0894 | 0.7688 | 47.2467 | 9773.1765 | 0.9138 | 0.2551 | 34.2570 | ours HAT-style 2.5D reproduction adapted from XPixelGroup/HAT |

Note: this is an ours HAT-style 2.5D reproduction adapted from XPixelGroup/HAT using the project fastMRI-brain-T2 expanded x4/split/metrics protocol, not an official HAT reported protocol.
