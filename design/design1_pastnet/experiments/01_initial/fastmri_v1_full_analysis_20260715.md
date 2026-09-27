# PAST-Net fastMRI full result analysis

Date: 2026-07-15

## Run

- Package: `D:\MRI\design\fastmri_brain_pastnet_2p5d`
- Profile: `full`
- Dataset: fastMRI-brain-T2 expanded
- Scale: x4
- Test cases: 24
- Best val loss: 0.0280005265
- Epochs: 30, no early stop

## Main Result

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| Linear | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| Cubic | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |
| PAST-Net v1 | 22.9327 | 0.7682 | 45.9173 | 10275.2267 | 0.9108 |
| PAST-Net v1 extend60 | 23.2583 | 0.7760 | 43.9351 | 9501.8090 | 0.9178 |
| I3Net | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 |

## Interpretation

PAST-Net v1 is clearly effective on fastMRI: it beats linear by +3.8194 dB PSNR and improves all main metrics. It also beats SMamba full on most case-level comparisons and is stronger than HAT full.

Warm-start continuation to 60 epochs improves PAST-Net from 22.9327 to 23.2583 PSNR. The extension also improves SSIM, MAE, MSE, and NCC, so the extra training is useful rather than just metric noise.

Against HAT extend60, PAST-Net extend60 is stronger on mean PSNR by +0.1689 dB and wins PSNR on 20/24 cases. Against SMamba full and HAT full, it wins PSNR on 24/24 cases.

It does not yet beat I3Net. Against I3Net, PAST-Net extend60 still loses on all 24 cases for PSNR, SSIM, MAE, and NCC. The mean PSNR gap is reduced from -1.0775 dB to -0.7519 dB. This is a systematic gap, not a few outlier cases.

The most likely limitation is that PAST-Net v1 uses only the two adjacent sparse anchors for each target slice. I3Net uses a broader sparse-slice window and can exploit more through-plane context. The current result supports the phase-aware residual design, but suggests that I3Net's multi-slice context advantage must be absorbed in v2.

## Immediate Next Step

The training curve was still improving near the end of the 30-epoch budget, so the lowest-risk next run is warm-start continuation:

```powershell
$env:PYTHONPATH="D:\MRI\design;D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_extend60
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_extend60
```

`full_extend60` improved the model but did not close most of the I3Net gap. The next architecture step should be PAST-Net v2 with multi-anchor context, e.g. `prev_anchor, left_anchor, right_anchor, next_anchor` plus phase-aware gated residual decoding.

A final low-cost continuation profile is available:

```powershell
$env:PYTHONPATH="D:\MRI\design;D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_extend90
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_extend90
```

However, the priority should shift to v2 multi-anchor context, because the remaining I3Net gap is likely architectural.
