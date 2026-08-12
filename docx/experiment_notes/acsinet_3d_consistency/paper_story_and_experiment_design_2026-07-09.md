# ACSI-Net Paper Story and Experiment Design

## Core Story

ACSI-Net should not be framed as a generic slice-wise super-resolution network.
The paper story is: through-plane MRI interpolation should recover an anatomically coherent 3D volume, not merely maximize isolated 2D slice fidelity.

The strongest claim supported by the current IXI-T2 x4 full_test115 result is:

> ACSI-Net improves z-axis structural coherence while remaining competitive with strong 2.5D baselines, and it substantially outperforms interpolation baselines on both slice fidelity and 3D consistency.

The claim should not be:

> ACSI-Net is the overall SOTA on every reconstruction metric.

I3Net is still stronger on IXI full_test115 PSNR/SSIM, so the paper should use I3Net as the reconstruction upper baseline and ACSI-Net as the anatomy-consistency method.

## Hypotheses

1. Slice-level PSNR/SSIM are insufficient to describe through-plane interpolation quality.
2. Group prediction of all intermediate slices improves volume-level continuity versus independent slice prediction.
3. z-gradient, z-Laplacian, and edge-z losses reduce anatomical discontinuities.
4. The benefit is visible in sagittal/coronal reformats and z-profile plots.
5. ACSI-Net can be slightly below I3Net in PSNR while still contributing a distinct clinically meaningful axis: anatomical coherence.

## Main IXI-T2 x4 Experiment

Dataset:

- IXI-T2
- x4 through-plane interpolation
- full_test115 split
- 115 test volumes

Primary reconstruction metrics:

- PSNR
- SSIM
- MAE
- MSE
- NCC

Primary 3D consistency metrics:

- ZGE: z-gradient error
- ZLE: z-Laplacian error
- EdgeZ: edge continuity error along z
- NCC-z-MAE: mismatch of adjacent-slice NCC profiles

Required table groups:

1. Linear and cubic interpolation baselines.
2. Published or strong neural baselines: I3Net, HAT, SMamba-UNet, SwinIR, ACVTT, ARSSR, CycleINR.
3. ACSI-Net.

## Figure Plan

Figure 1: Motivation

- Show axial slices alone look acceptable.
- Show sagittal/coronal view reveals z-axis discontinuity.
- Use linear or cubic as the failure example.

Figure 2: Method

- Sparse anchors S0 and S4.
- Linear coarse group C1/C2/C3.
- Phase maps P1/P2/P3.
- Group decoder producing S1/S2/S3.
- Shallow 3D z-context refinement.
- Anatomy consistency losses.

Figure 3: IXI full_test115 quantitative result

- Reconstruction table.
- 3D consistency table.
- Per-case win rate bar chart for ACSI-Net vs linear/cubic.

Figure 4: Sagittal/coronal QC

- Choose best, median, and worst cases by ACSI-Net z-consistency gain.
- Columns: GT, Linear, I3Net, ACSI-Net, error map.
- Add z-profile line plot through a high-gradient anatomical boundary.

Figure 5: Ablation

- Full ACSI-Net.
- w/o z-gradient loss.
- w/o z-Laplacian loss.
- w/o edge-z loss.
- w/o z-refine.
- optional: single-slice output instead of group output.

## Experiment Order

1. Finish IXI full_test115 story package.
2. Compute 3D consistency for available full_test115 neural baselines without retraining.
3. Generate visual QC cases.
4. Only then train ablations.
5. Extend the same evaluation to fastMRI and NingXia if existing predictions are available.

## Acceptance Criteria

The ACSI-Net story is strong enough for a paper section if:

- ACSI-Net beats linear/cubic on all reconstruction metrics over full_test115.
- ACSI-Net beats linear/cubic on at least 3/4 3D consistency metrics.
- ACSI-Net remains competitive with HAT/SMamba/SwinIR.
- I3Net remains acknowledged as a stronger reconstruction baseline.
- Visual QC demonstrates fewer z-axis discontinuities in sagittal/coronal views.

## Current Status

IXI full_test115 already satisfies the first two criteria. The next missing piece is visual QC and cross-neural-baseline 3D consistency.
