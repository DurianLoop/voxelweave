# fastMRI-brain-T2 SMamba-UNet/MambaIR-style 2.5D Paper Table

| dataset | scale | profile | method | cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G) | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fastMRI-brain-T2 expanded | x4 | full | linear | 24 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 | 0.0000 | 0.0000 | ours rerun |
| fastMRI-brain-T2 expanded | x4 | full | cubic | 24 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 | 0.0000 | 0.0000 | ours rerun |
| fastMRI-brain-T2 expanded | x4 | full | smamba_unet | 24 | 22.7322 | 0.7618 | 49.4487 | 10826.4468 | 0.9051 | 0.6042 | 31.8034 | ours SMamba-UNet/MambaIR-style 2.5D reproduction |

Note: this is an ours SMamba-UNet/MambaIR-style 2.5D reproduction using the project fastMRI-brain-T2 expanded x4/split/metrics protocol, not an official SMamba-UNet or MambaIR reported protocol.
