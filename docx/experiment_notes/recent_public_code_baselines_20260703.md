# Recent Public-Code Baselines: ACVTT and Res-SRDiff

Date: 2026-07-03

## Scope

Current main task remains T2-only, x4 through-plane interpolation. The two newly added public-code baselines are:

- ACVTT (2025/2026 public code): official repository `https://github.com/khuhm/ACVTT`
- Res-SRDiff (2025): official repository `https://github.com/mosaf/Res-SRDiff`

Both official source trees were cloned under:

- `D:\MRI\external\ACVTT`
- `D:\MRI\external\Res-SRDiff`

The project-side wrappers are:

- `D:\MRI\ixi_acvtt_2p5d`
- `D:\MRI\ixi_ressrdiff_2p5d`

## Adaptation Rule

These are not entered into the master table until at least IXI-T2 `full_test115` is completed and judged stable. The current smoke results are only pipeline sanity checks.

ACVTT is the closer task match because its official code targets slice interpolation and includes IXI preprocessing/generalization support. In this project it is adapted as:

- Input: left sparse slice, right sparse slice, linear coarse slice, relative-position map.
- ACVTT core input: two coarse channels.
- ACVTT reference input: left/right sparse slices.
- Output: refined target slice.
- No intermediate ground-truth slice is used as input.

Res-SRDiff is a diffusion MRI SR/refinement baseline rather than a native slice-interpolation method. In this project it is adapted as:

- Input condition: linear coarse slice only.
- Target: true intermediate slice.
- Core: official `UNetModelSwin` plus official residual-shifting Gaussian diffusion process.
- Output: diffusion-refined slice.
- No intermediate ground-truth slice is used as input.

## Smoke Verification

Both IXI smoke pipelines completed end-to-end: train, validation, inference, linear/cubic baselines, project metrics, and paper-table export.

ACVTT smoke:

- Command: `D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.run_all --profile smoke`
- Training history: `ixi_acvtt_2p5d\runs\smoke\training_history.json`
- best_val_loss: 0.1101598653
- epochs_completed: 1
- early_stopped: false
- Smoke metric sanity: ACVTT PSNR 27.3072, SSIM 0.8671, MAE 27.2641, MSE 3356.0824, NCC 0.9557.
- In this very small smoke run, linear remains slightly higher on PSNR/SSIM, so this is not evidence of final model quality.

Res-SRDiff smoke:

- Command: `D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.run_all --profile smoke`
- Training history: `ixi_ressrdiff_2p5d\runs\smoke\training_history.json`
- best_val_loss: 0.0314554557
- epochs_completed: 1
- early_stopped: false
- Smoke metric sanity: Res-SRDiff PSNR 23.5757, SSIM 0.6192, MAE 52.8890, MSE 7432.6400, NCC 0.9240.
- This weak smoke result is expected for a diffusion refinement model after only one epoch and should not be used in the master table.

## IXI Full Result

ACVTT `full_test115_b64` completed on IXI-T2 test n=115.

- Command: `D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.run_all --profile full_test115_b64`
- Paper table command: `D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.paper_table --profile full_test115_b64`
- Training history: `ixi_acvtt_2p5d\runs\full_test115_b64\training_history.json`
- epochs_completed: 30
- early_stopped: false
- best_val_loss: 0.0868123959
- best epoch by validation: epoch 28
- final epoch validation loss: 0.0868627733
- per-epoch wall time: about 714-753 seconds after caching

ACVTT IXI-T2 test n=115 metrics:

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| ACVTT (2025) | 27.3431 | 0.8822 | 25.5217 | 5206.8325 | 0.9557 |
| Linear | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 |
| Cubic | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 |

Interpretation:

- ACVTT is clearly above Linear/Cubic and slightly above ArSSR/CycleINR/ResUNet on several IXI metrics.
- ACVTT remains clearly below SwinIR 2.5D, HAT 2.5D, SMamba-UNet 2.5D, SAINT, and I3Net on IXI-T2.
- Current role: useful recent public-code slice-interpolation baseline, not a first-tier strong baseline.
- Convergence judgment: ACVTT is sufficiently fitted for a baseline row. The best validation loss is reached at epoch 28, and the final validation loss differs from the best value by only about 0.06% relative, so the run is in a plateau rather than an obviously under-trained descent phase.
- Fairness judgment: it is fair to compare in this paper's master table because it uses the same IXI-T2 train/val/test split, x4 sparse input construction, test n=115, and PSNR / SSIM / MAE / MSE / NCC evaluation. The method should be described as official ACVTT adapted to this T2/x4 through-plane protocol, not as the original ACVTT paper's exact task setting.
- The master table was updated with the IXI-T2 column only. fastMRI and NingXia remain pending.

## Res-SRDiff Full Profile Update

Res-SRDiff keeps the official `mosaf/Res-SRDiff` diffusion core but is adapted as a coarse-to-target slice refinement baseline. To make the IXI full run feasible on the local 24 GB NVIDIA GPU, the project wrapper now uses:

- Cached pre-resized IXI slices in RAM, avoiding repeated per-sample CPU resize.
- AMP on CUDA.
- CUDA `cudnn.benchmark`.
- Same effective batch target as other full baselines: effective batch 24.

Available full profiles:

- `full_test115`: batch 24, grad_accum 1, effective batch 24. Use this first; it keeps the same effective batch while avoiding gradient-accumulation overhead.
- `full_test115_safe`: batch 8, grad_accum 3, effective batch 24. Use this if `full_test115` runs out of dedicated GPU memory.
- `full_test115_fast`: batch 32, grad_accum 1, effective batch 32. Treat this as a speed-oriented run only if `full_test115` leaves clear dedicated-memory headroom.

Res-SRDiff is now eligible for the master table on IXI-T2 because full_test115 metrics have been generated.

## Res-SRDiff IXI Full Result

Res-SRDiff `full_test115` completed on IXI-T2 test n=115.

- Command: `D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.run_all --profile full_test115`
- Paper table command: `D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.paper_table --profile full_test115`
- Training history: `ixi_ressrdiff_2p5d\runs\full_test115\training_history.json`
- epochs_completed: 30
- early_stopped: false
- best_val_loss: 0.0053174327
- best epoch by validation: epoch 28
- final epoch validation loss: 0.0053313696
- per-epoch wall time: about 989-1085 seconds
- complexity: 10.270247 M parameters, 251.039645696 G FLOPs

Res-SRDiff IXI-T2 test n=115 metrics:

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| Res-SRDiff (2025) | 28.0441 | 0.8821 | 24.1938 | 4664.4129 | 0.9611 |
| Linear | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 |
| Cubic | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 |

Interpretation:

- Res-SRDiff is above Linear/Cubic and also above ACVTT, ArSSR, CycleINR, and ResUNet residual on IXI-T2 PSNR / MAE / MSE / NCC.
- Its SSIM is almost tied with ACVTT, slightly below ACVTT by about 0.0001, so the gain is not uniform across all metrics.
- It remains below SwinIR 2.5D, SAINT, HAT 2.5D, SMamba-UNet 2.5D, and I3Net on IXI-T2.
- Convergence judgment: sufficiently fitted for a baseline row. Validation loss drops sharply in the first epochs, then enters a plateau after about epoch 20. The final validation loss differs from the best value by about 0.26% relative.
- Current role: useful diffusion refinement baseline adapted from official public code, not a first-tier method on IXI-T2.
- The master table was updated with the IXI-T2 column only. fastMRI and NingXia remain pending.

## Recommended Execution Order

Run IXI mini first:

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.paper_table --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.paper_table --profile mini
```

Only if IXI mini is at least close to SwinIR/HAT/SMamba, run full_test115:

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.run_all --profile full_test115
D:\conda\envs\MRI\python.exe -B -m ixi_acvtt_2p5d.paper_table --profile full_test115
D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.run_all --profile full_test115
D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.paper_table --profile full_test115
```

If Res-SRDiff full_test115 reports CUDA out-of-memory:

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.run_all --profile full_test115_safe
D:\conda\envs\MRI\python.exe -B -m ixi_ressrdiff_2p5d.paper_table --profile full_test115_safe
```

ACVTT GPU-efficient full profiles:

- `full_test115`: batch 48, grad_accum 1, effective batch 48.
- `full_test115_b64`: batch 64, grad_accum 1, effective batch 64.

Use `full_test115` first. If dedicated GPU memory remains safely below roughly 18 GB and GPU utilization is still low, try `full_test115_b64`.

## Efficiency Notes

ACVTT smoke finished quickly and behaves like a deterministic CNN/attention baseline.

Res-SRDiff smoke is slower than deterministic methods because every inference slice needs diffusion sampling. The current profiles intentionally keep it light:

- smoke: batch 1, 2 sampling steps, 32 base channels.
- mini: batch 2, grad_accum 6, 4 sampling steps, 32 base channels.
- full_test115_safe: batch 8, grad_accum 3, 4 sampling steps, 32 base channels.
- full_test115: batch 24, grad_accum 1, 4 sampling steps, 32 base channels.
- full_test115_fast: batch 32, grad_accum 1, 4 sampling steps, 32 base channels.

If Res-SRDiff is still too slow, first check whether GPU utilization is low and dedicated memory has headroom. Increase only to `full_test115_fast` if memory is clearly safe, and label it as a speed-oriented configuration because the effective batch changes to 32. Reducing `steps` changes the diffusion sampling/training budget and should be treated as a separate light-budget ablation, not the main comparable full baseline.

## Master Table Policy

Do not add smoke rows to `docx\experiment\experiment_master_table.md`.

Add a method row only when:

1. IXI-T2 `full_test115` has completed.
2. Metrics are generated with the same PSNR / SSIM / MAE / MSE / NCC code as the existing baselines.
3. The run manifest clearly states no intermediate ground truth is used as model input.
4. The method name should be concise: `ACVTT (2025)` and `Res-SRDiff (2025)`.

Current table status:

- `ACVTT (2025)` has been added for IXI-T2, fastMRI-brain-T2 expanded, and NingXia-T2 8-fold CV.
- `Res-SRDiff (2025)` has been added for IXI-T2, fastMRI-brain-T2 expanded, and NingXia-T2 8-fold CV.

## Cross-Dataset Code Expansion

The fastMRI and NingXia entrypoints for both methods have been implemented.

New fastMRI packages:

- `fastmri_brain_acvtt_2p5d`
- `fastmri_brain_ressrdiff_2p5d`

NingXia case-level CV integration:

- `processing.run_ningxia_case_cv --models acvtt ressrdiff`
- `processing.summarize_case_cv --include-acvtt --include-ressrdiff`

Smoke verification completed on fastMRI-brain-T2 expanded:

- ACVTT smoke: train / val / inference / linear / cubic / metrics / paper table completed.
- Res-SRDiff smoke: train / val / inference / linear / cubic / metrics / paper table completed.
- These smoke rows are pipeline checks only and must not be added to the master table.

Full-run commands:

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_acvtt_2p5d.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_acvtt_2p5d.paper_table --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_ressrdiff_2p5d.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_ressrdiff_2p5d.paper_table --profile full
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile full --models acvtt ressrdiff
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --profile full --include-acvtt --include-ressrdiff
```

Fallback commands if the default full profiles run out of dedicated GPU memory:

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_acvtt_2p5d.run_all --profile full_safe
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_acvtt_2p5d.paper_table --profile full_safe
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_ressrdiff_2p5d.run_all --profile full_safe
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_ressrdiff_2p5d.paper_table --profile full_safe
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile full_safe --models acvtt ressrdiff --force
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --profile full_safe --include-acvtt --include-ressrdiff
```

## Cross-Dataset Full Results

The completed cross-dataset runs used the `full_tiny` memory-safe profile:

- fastMRI ACVTT: `fastmri_brain_acvtt_2p5d\runs\full_tiny`
- fastMRI Res-SRDiff: `fastmri_brain_ressrdiff_2p5d\runs\full_tiny`
- NingXia ACVTT: `ningxia_t2_acvtt_2p5d_cv\runs\fold_00` ... `fold_07`, profile `full_tiny`
- NingXia Res-SRDiff: `ningxia_t2_ressrdiff_2p5d_cv\runs\fold_00` ... `fold_07`, profile `full_tiny`

fastMRI-brain-T2 expanded test n=24:

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| ACVTT (2025) | 20.1941 | 0.6624 | 71.5480 | 18286.6190 | 0.8320 |
| Res-SRDiff (2025) | 21.6727 | 0.6909 | 56.3371 | 13095.4191 | 0.8814 |
| Linear | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| Cubic | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |

NingXia-T2 case-level CV, 8 folds:

| Method | Folds | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| ACVTT (2025) | 8 | 23.4735 | 0.7281 | 95.4376 | 35779.4840 | 0.8804 |
| Res-SRDiff (2025) | 8 | 21.1538 | 0.5538 | 153.0213 | 66533.1526 | 0.8207 |
| Linear | 8 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| Cubic | 8 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |

Interpretation:

- ACVTT is consistently above Linear/Cubic on fastMRI and NingXia, but remains below the current first-tier methods.
- Res-SRDiff is useful on fastMRI, but fails to generalize on NingXia case-level CV, where it is worse than Linear/Cubic.
- The master table was updated for ACVTT and Res-SRDiff across all three datasets.
