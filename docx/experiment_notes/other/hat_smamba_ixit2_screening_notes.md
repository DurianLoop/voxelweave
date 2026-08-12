# HAT and SMamba/Mamba IXI-T2 x4 Screening Notes

Date: 2026-06-17

Scope: T2 modality, x4 through-plane interpolation, IXI-T2 smoke/mini screening only.

## Source Positioning

HAT:

- Public source: `https://github.com/XPixelGroup/HAT`
- Paper family: HAT / Hybrid Attention Transformer for Image Restoration.
- Local package: `ixi_hat_2p5d`
- Local reproduction status: HAT-style 2.5D residual reproduction adapted to this project's IXI-T2 x4 slice interpolation protocol.
- Not an official HAT reported protocol, because the official repository is an image SR / restoration codebase built around BasicSR and natural-image LR/HR training configs.

SMamba / Mamba:

- SMamba-UNet paper: `https://arxiv.org/abs/2407.05993`
- MambaIR public source: `https://github.com/csguoh/MambaIR`
- Local package: `ixi_smamba_unet_2p5d`
- Local reproduction status: SMamba-UNet / MambaIR-style 2.5D residual reproduction with a dependency-light directional selective scan surrogate.
- Not an official SMamba-UNet exact reproduction. A direct public SMamba-UNet GitHub repository was not found during this screening pass. The implemented baseline is therefore a clearly labeled 2024+ Mamba-style medical SR architecture control, not a claim of exact paper reproduction.

## Commands

HAT smoke:

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_hat_2p5d.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m ixi_hat_2p5d.paper_table --profile smoke
```

HAT mini:

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_hat_2p5d.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_hat_2p5d.paper_table --profile mini
```

SMamba-UNet/MambaIR-style smoke:

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_smamba_unet_2p5d.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m ixi_smamba_unet_2p5d.paper_table --profile smoke
```

SMamba-UNet/MambaIR-style mini:

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_smamba_unet_2p5d.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_smamba_unet_2p5d.paper_table --profile mini
```

Note: HAT mini and SMamba mini completed and wrote checkpoints/metrics, but the shell tool returned timeout code because tqdm output was very long. The result files were verified after completion.

## IXI-T2 Smoke Results

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 1 | 27.4291 | 0.8772 | 26.3205 | 3283.3493 | 0.9566 |
| Cubic | 1 | 27.1568 | 0.8682 | 27.6104 | 3523.0295 | 0.9507 |
| SwinIR-style 2.5D | 1 | 27.4712 | 0.8762 | 26.3609 | 3258.6717 | 0.9570 |
| HAT-style 2.5D | 1 | 27.3934 | 0.8747 | 26.8006 | 3303.3029 | 0.9566 |
| SMamba-UNet/MambaIR-style | 1 | 27.4394 | 0.8706 | 26.3852 | 3274.6368 | 0.9567 |

Smoke interpretation:

- HAT was close enough to SwinIR-style 2.5D to justify mini.
- SMamba-UNet/MambaIR-style was close in PSNR/MSE/NCC but weaker in SSIM; mini was still run because the goal is also to add a 2024+ architecture control.

## IXI-T2 Mini Results

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 5 | 25.0849 | 0.8268 | 47.0867 | 12633.8805 | 0.9121 |
| Cubic | 5 | 24.6061 | 0.8131 | 51.1790 | 14744.4780 | 0.8988 |
| SwinIR-style 2.5D | 5 | 26.1677 | 0.8547 | 41.4350 | 10526.4317 | 0.9303 |
| HAT-style 2.5D | 5 | 26.3827 | 0.8610 | 40.4737 | 10126.3046 | 0.9326 |
| SMamba-UNet/MambaIR-style | 5 | 26.1450 | 0.8551 | 41.7967 | 10641.3355 | 0.9292 |

Mini interpretation:

1. HAT-style 2.5D passes the expansion gate. It beats SwinIR-style 2.5D on PSNR, SSIM, MAE, MSE, and NCC on IXI-T2 mini.
2. SMamba-UNet/MambaIR-style is useful as a 2024+ architecture control, but does not currently pass the "stronger than SwinIR" gate. It is slightly below SwinIR-style 2.5D on PSNR, MAE, MSE, and NCC, and approximately tied/slightly higher on SSIM.
3. HAT should be expanded first. SMamba should stay as an IXI screening result unless the paper specifically needs a 2024+ Mamba-style architecture row; if expanded, it should be framed as exploratory and not expected to beat the first-tier baselines.

## Artifacts

HAT:

- `ixi_hat_2p5d/model.py`
- `ixi_hat_2p5d/runs/smoke/`
- `ixi_hat_2p5d/runs/mini/`
- `ixi_hat_2p5d/runs/mini/metrics/paper_table.md`

SMamba/Mamba:

- `ixi_smamba_unet_2p5d/model.py`
- `ixi_smamba_unet_2p5d/runs/smoke/`
- `ixi_smamba_unet_2p5d/runs/mini/`
- `ixi_smamba_unet_2p5d/runs/mini/metrics/paper_table.md`

## Next Step

Recommended next execution order:

1. Expand HAT-style 2.5D to IXI-T2 full test n=115 or current full n=25, depending on whether the next table refresh is switching all IXI rows to n=115.
2. If HAT full remains competitive, then run fastMRI-brain-T2 expanded.
3. Run NingXia only after HAT has shown value on IXI full and fastMRI.
4. Keep SMamba/Mamba as a documented 2024+ architecture control. Do not prioritize three-dataset expansion before HAT.
