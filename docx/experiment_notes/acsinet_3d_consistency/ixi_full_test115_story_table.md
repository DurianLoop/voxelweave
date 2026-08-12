# ACSI-Net IXI full_test115 Story Table

## Reconstruction Positioning

| Method | Cases | PSNR | SSIM | MAE | NCC | Run |
| --- | --- | --- | --- | --- | --- | --- |
| I3Net | 115 | 31.3058 | 0.9285 | 17.5276 | 0.9788 | full_test115_stable |
| ACSI-Net | 115 | 29.3904 | 0.9078 | 20.8475 | 0.9701 | full_test115 |
| SMamba-UNet | 115 | 29.3536 | 0.9077 | 21.1352 | 0.9699 | full_test115 |
| HAT | 115 | 28.7249 | 0.9016 | 22.2500 | 0.9663 | full_test115 |
| SwinIR | 115 | 28.6485 | 0.8997 | 22.4556 | 0.9658 | full_test115 |
| ACVTT | 115 | 27.3431 | 0.8822 | 25.5217 | 0.9557 | full_test115_b64 |
| ARSSR | 115 | 27.2467 | 0.8773 | 25.5509 | 0.9533 | full_test115 |
| CycleINR | 115 | 26.1728 | 0.8527 | 29.2765 | 0.9390 | full_test115 |
| Linear | 115 | 26.1722 | 0.8529 | 29.2781 | 0.9390 | full_test115 |
| Cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 0.9303 | full_test115 |

## ACSI-Net Per-Case Wins

| Metric | Opponent | Wins | Rate |
| --- | --- | --- | --- |
| psnr | linear | 115/115 | 1.000 |
| psnr | cubic | 115/115 | 1.000 |
| ssim | linear | 115/115 | 1.000 |
| ssim | cubic | 115/115 | 1.000 |
| mae | linear | 115/115 | 1.000 |
| mae | cubic | 115/115 | 1.000 |
| mse | linear | 115/115 | 1.000 |
| mse | cubic | 115/115 | 1.000 |
| ncc | linear | 115/115 | 1.000 |
| ncc | cubic | 115/115 | 1.000 |
| zge | linear | 115/115 | 1.000 |
| zge | cubic | 115/115 | 1.000 |
| zle | linear | 114/115 | 0.991 |
| zle | cubic | 115/115 | 1.000 |
| edge_z_error | linear | 112/115 | 0.974 |
| edge_z_error | cubic | 115/115 | 1.000 |
| interslice_ncc_mae | linear | 115/115 | 1.000 |
| interslice_ncc_mae | cubic | 115/115 | 1.000 |

## 3D Consistency Across Available Neural Methods

- This 3D table was recomputed for available neural baselines with the same metrics.

| Method | Cases | ZGE | ZLE | EdgeZ | NCC-z-MAE |
| --- | --- | --- | --- | --- | --- |
| i3net | 115 | 0.0097 | 0.0155 | 0.0090 | 0.0197 |
| acsinet | 115 | 0.0113 | 0.0178 | 0.0099 | 0.0256 |
| smamba_unet | 115 | 0.0114 | 0.0180 | 0.0099 | 0.0256 |
| hat | 115 | 0.0119 | 0.0185 | 0.0102 | 0.0269 |
| swinir | 115 | 0.0120 | 0.0186 | 0.0102 | 0.0277 |
| linear | 115 | 0.0143 | 0.0207 | 0.0110 | 0.0413 |
| cubic | 115 | 0.0148 | 0.0208 | 0.0114 | 0.0403 |

## Interpretation

- ACSI-Net is not the reconstruction SOTA on IXI-T2 x4 because I3Net remains clearly stronger.
- ACSI-Net is nevertheless a credible method candidate: it beats linear and cubic on every full_test115 case for all main reconstruction metrics.
- Its central story should be anatomy-consistent volume recovery, supported by lower z-gradient, z-Laplacian, edge-z, and inter-slice NCC mismatch.
- The next evidence gap is visual: sagittal/coronal panels should show why lower z-axis errors matter anatomically.
