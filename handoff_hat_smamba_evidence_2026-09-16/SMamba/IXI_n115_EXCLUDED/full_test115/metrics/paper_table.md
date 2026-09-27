# IXI-T2 SMamba-UNet-style 2.5D Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IXI-T2 | x4 | full_test115 | linear | 115 | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | full_test115 | cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 | 0.0000 | 0.0000 | ours rerun |
| IXI-T2 | x4 | full_test115 | smamba_unet | 115 | 29.3536 | 0.9077 | 21.1352 | 3691.2381 | 0.9699 | 0.6042 | 31.8034 | ours SMamba-UNet/MambaIR-style 2.5D reproduction |

Note: this is an ours SMamba-UNet/MambaIR-style 2.5D reproduction using the project IXI-T2/x4/split/metrics protocol, not an official SMamba-UNet reported protocol.
