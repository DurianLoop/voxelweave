# IXI-T2 HAT-style 2.5D Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IXI-T2 | x4 | full_test115 | linear | 115 | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | full_test115 | cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | full_test115 | hat | 115 | 28.7249 | 0.9016 | 22.2500 | 4088.7422 | 0.9663 | 0.2551 | 34.2570 | ours HAT-style 2.5D reproduction |

Note: this is an ours HAT-style 2.5D reproduction adapted from the public HAT architecture family using the project IXI-T2/x4/split/metrics protocol, not an official HAT reported protocol.
