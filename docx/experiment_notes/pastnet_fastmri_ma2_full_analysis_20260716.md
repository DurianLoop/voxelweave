# PAST-Net MA2 fastMRI full result analysis

Date: 2026-07-16

## Run

- Package: `D:\MRI\design\fastmri_brain_pastnet_2p5d`
- Profile: `full_ma2_90`
- Dataset: fastMRI-brain-T2 expanded
- Scale: x4
- Test cases: 24
- Checkpoint: `runs\full_ma2_90\checkpoints\pastnet_epoch_best.pth`
- Checkpoint metadata: MA2, 13 input channels, best epoch 80, best val loss 0.0255770803

The first run left only the checkpoint and eval input folders. Metrics were missing, so evaluation was completed with:

```powershell
$env:PYTHONPATH="D:\MRI\design;D:\MRI\pre;D:\MRI\baseline;D:\MRI"
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_ma2_90 --eval-only-checkpoint D:\MRI\design\fastmri_brain_pastnet_2p5d\runs\full_ma2_90\checkpoints\pastnet_epoch_best.pth
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_ma2_90
```

## Main Result

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| Linear | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| Cubic | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |
| PAST-Net v1 | 22.9327 | 0.7682 | 45.9173 | 10275.2267 | 0.9108 |
| PAST-Net v1 extend60 | 23.2583 | 0.7760 | 43.9351 | 9501.8090 | 0.9178 |
| PAST-Net MA2 full90 | 23.6079 | 0.7839 | 42.3850 | 8659.8746 | 0.9240 |
| I3Net | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 |

## Case-Level Comparison

MA2 is a real improvement over the previous PAST-Net line:

- vs PAST-Net v1: +0.6752 dB PSNR, +0.0157 SSIM, -3.5322 MAE
- vs PAST-Net v1 extend60: +0.3495 dB PSNR, +0.0079 SSIM, -1.5501 MAE
- MA2 beats v1 extend60 on PSNR for 23/24 test cases

MA2 still does not beat I3Net:

- Mean PSNR gap to I3Net: -0.4024 dB
- Mean SSIM gap to I3Net: -0.0082
- Mean MAE gap to I3Net: +1.3749
- PSNR wins vs I3Net: 0/24
- SSIM wins vs I3Net: 2/24
- MAE wins vs I3Net: 3/24

The hardest remaining cases by PSNR gap are:

| Case | MA2 - I3Net PSNR | MA2 - I3Net SSIM | MA2 - I3Net MAE |
|---|---:|---:|---:|
| `110083806921_ax_t2_acr.nii.gz` | -0.9762 | -0.0072 | +4.7904 |
| `109954766829_ax_t2.nii.gz` | -0.7593 | -0.0174 | +2.5665 |
| `102670846301_ax_t2.nii.gz` | -0.7044 | -0.0115 | +3.2157 |
| `105715969021_ax_t2.nii.gz` | -0.6647 | -0.0157 | +2.0491 |
| `107274371713_ax_t2.nii.gz` | -0.6037 | -0.0146 | +2.6529 |

The closest cases are already near I3Net:

| Case | MA2 - I3Net PSNR | MA2 - I3Net SSIM | MA2 - I3Net MAE |
|---|---:|---:|---:|
| `111719079643_ax_t2.nii.gz` | -0.0185 | -0.0086 | -0.3330 |
| `106167771242_ax_t2.nii.gz` | -0.0512 | -0.0004 | -0.9818 |
| `103098218097_ax_t2.nii.gz` | -0.0575 | +0.0044 | -1.1870 |
| `105359088378_ax_t2.nii.gz` | -0.1217 | -0.0049 | +1.4263 |
| `106681228532_ax_t2.nii.gz` | -0.1977 | +0.0069 | +0.1212 |

## Gate Check

Validation-set average gate and confidence from the best checkpoint:

| Component | Mean |
|---|---:|
| prev anchor | 0.0057 |
| left anchor | 0.2920 |
| right anchor | 0.4335 |
| next anchor | 0.0454 |
| coarse | 0.2234 |
| residual confidence | 0.2193 |

MA2 learns useful multi-anchor context, but after full training the residual branch is conservative and the outer anchors are not heavily used. This is consistent with the metric pattern: it improves nearly all PAST-Net cases but does not yet match I3Net's stronger sequence context.

## Interpretation

MA2 has potential. The mini result was not a false positive: the full result improved v1 extend60 by a meaningful margin and reduced the I3Net PSNR gap from -0.7519 dB to -0.4024 dB.

However, the remaining gap is still systematic. Since MA2 loses PSNR to I3Net on all 24 cases, a pure training-length extension is unlikely to be enough by itself. The model needs a stronger local sequence correction path or teacher-guided objective, not only more epochs.

## Recommended Next Step

Build PAST-Net MA3 as a small, controlled extension rather than a full rewrite:

1. Keep the MA2 data interface and 13-channel input so the split/eval path stays stable.
2. Add a temporal residual refinement head that predicts local high-frequency correction from `[prev, left, right, next, coarse]` features after the current MA2 fusion.
3. Add a Laplacian/edge consistency loss with a low weight, targeting the cases where MA2 has lower PSNR and higher MAE than I3Net.
4. Add profiles `mini_ma3` and `full_ma3_90`.
5. Validate first on `mini_ma3`; only launch full if mini beats MA2 on PSNR and MAE case-wise.

Expected bar before spending another long run:

- `mini_ma3` should beat `mini_ma2` on at least 3/4 PSNR cases and improve mean MAE.
- Gate/confidence should not collapse below MA2.
- Full run should target at least +0.40 dB over MA2 to have a credible chance of beating I3Net.

Artifacts written:

- `runs\full_ma2_90\metrics\summary_metrics.csv`
- `runs\full_ma2_90\metrics\per_case_metrics.csv`
- `runs\full_ma2_90\metrics\paper_table.md`
- `runs\full_ma2_90\metrics\pastnet_ma2_comparison_summary.csv`
- `runs\full_ma2_90\metrics\pastnet_ma2_vs_i3net_per_case_delta.csv`
