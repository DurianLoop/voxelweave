# I3Net T2 x4 Three-Dataset Run Notes

Date: 2026-06-17

Scope: T2 modality, x4 through-plane interpolation. I3Net uses the published inter-/intra-slice synthesis setting: 4 sparse through-plane slices -> 13 high-resolution slices.

## Code Paths

| Component | Path |
|---|---|
| IXI-T2 runner | `ixi_i3net/` |
| fastMRI / NingXia reusable runner | `fastmri_brain_i3net/` |
| NingXia CV driver | `processing/run_ningxia_case_cv.py` |
| NingXia CV summary | `processing/summarize_case_cv.py` |

## IXI-T2 Full Test n=115

The n=115 evaluation reuses the best checkpoint from the earlier IXI full run.

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m ixi_i3net.run_all --profile full_test115 --eval-only-checkpoint ixi_i3net\runs\full\checkpoints\i3net_epoch_best.pth
D:\conda\envs\MRI\python.exe -B -m ixi_i3net.paper_table --profile full_test115
```

Output:

```text
ixi_i3net/runs/full_test115/
```

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 115 | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 |
| Cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 |
| I3Net | 115 | 30.7526 | 0.9231 | 18.5089 | 2858.7057 | 0.9771 |

I3Net wins against Linear and Cubic on all 115 cases for PSNR / SSIM / MAE / MSE / NCC.

## fastMRI-Brain-T2 Expanded Full

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_i3net.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_i3net.paper_table --profile full
```

Output:

```text
fastmri_brain_i3net/runs/full/
```

Training was stable: 30 epochs, `skipped_nonfinite=0`, best validation loss `0.0155516`.

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 24 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| Cubic | 24 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |
| I3Net | 24 | 24.0102 | 0.7921 | 41.0101 | 7755.6546 | 0.9308 |

Per-case result against Linear: 24/24 wins on PSNR / SSIM / MAE / MSE / NCC. This makes I3Net the current strongest fastMRI-brain-T2 expanded baseline, ahead of the previous SAINT-style row.

## NingXia-T2 Case-Level CV Full

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B processing\run_ningxia_case_cv.py --models i3net --profile full
D:\conda\envs\MRI\python.exe -B processing\summarize_case_cv.py --profile full --include-arssr --include-cycleinr --include-swinir --include-i3net --title "NingXia-T2 Case-Level CV Full"
```

Output:

```text
ningxia_t2_i3net_cv/runs/fold_00/full/
...
ningxia_t2_i3net_cv/runs/fold_07/full/
docx/experiment_notes/ningxia_case_cv_summary.csv
docx/experiment_notes/ningxia_case_cv_summary.md
```

The redirected full CV command returned a non-zero shell exit code, but all 8 fold `summary_metrics.csv` files and best checkpoints were produced. The log tail shows fold_00 through fold_07 completed; the non-zero status is treated as a logging/redirection artifact unless reproduced without redirection.

| Method | Folds | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| Linear | 8 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| Cubic | 8 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |
| ArSSR-style | 8 | 23.1634 | 0.7091 | 96.4890 | 38343.9409 | 0.8708 |
| CycleINR-style | 8 | 22.9009 | 0.6935 | 101.0990 | 40735.3568 | 0.8625 |
| ResUNet residual | 8 | 23.3816 | 0.7209 | 97.0409 | 36316.2290 | 0.8785 |
| I3Net | 8 | 23.4911 | 0.7208 | 93.5655 | 35725.4805 | 0.8825 |
| SwinIR-style 2.5D | 8 | 23.9513 | 0.7525 | 85.9679 | 32030.5455 | 0.8930 |
| SAINT-style | 8 | 23.8350 | 0.7422 | 89.4140 | 32992.9496 | 0.8905 |

Against Linear over 22 NingXia test series: PSNR 20/22 wins, SSIM 20/22, MAE 20/22, MSE 20/22, NCC 21/22. I3Net is clearly useful on NingXia but not the first-tier winner there.

## Interpretation

1. I3Net is now a strong published medical slice synthesis baseline in the main table.
2. IXI and fastMRI support the claim that a task-matched medical slice-interpolation architecture can outperform generic interpolation and prior local baselines.
3. NingXia is more mixed: SwinIR-style 2.5D remains the strongest average baseline, with SAINT-style second and I3Net middle-to-high. This is useful because it prevents overclaiming a universal I3Net win.
4. For the paper claim, the clean framing is not "one model always wins", but "our evaluation includes task-matched medical synthesis, transformer/SwinIR-style, spatially aware adjacent-slice, INR, CNN residual, and interpolation baselines across public and external clinical-like T2 data."

## Next Steps

1. Keep I3Net in the main table as the primary published medical slice synthesis baseline.
2. Use IXI-T2 test n=115 for new IXI screening and future full comparison, but only migrate the master IXI column after the next batch of methods is rerun under the same n=115 protocol.
3. Start HAT 2.5D on IXI-T2 smoke/mini next; only expand if it can approach or beat SwinIR-style 2.5D.
4. After HAT, screen a 2024+ Mamba medical SR baseline on IXI-T2 smoke/mini.
5. Add efficiency / visual QC for I3Net versus SwinIR / SAINT before writing the final related-work experiment paragraph.
