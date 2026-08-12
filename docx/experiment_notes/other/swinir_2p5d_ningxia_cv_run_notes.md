# SwinIR-style 2.5D NingXia-T2 8-fold CV run notes

Date: 2026-06-15

Dataset: NingXia-T2, 8 patient-level folds, 22 T2 NIfTI series.
Task: T2 x4 through-plane interpolation.
Protocol: project split/metrics, same main-table metrics as Linear / Cubic / ArSSR / ResUNet / SAINT.

## Commands

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m processing.ningxia_case_cv
D:\conda\envs\MRI\python.exe -u -B -m processing.run_ningxia_case_cv --profile smoke --models swinir --fold-limit 1 --force
D:\conda\envs\MRI\python.exe -u -B -m processing.run_ningxia_case_cv --profile full --models swinir
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --title "NingXia-T2 Case-Level CV Full" --include-arssr --include-swinir
```

Full run log:

```text
logs/ningxia_swinir_full_20260615_161634.out.log
logs/ningxia_swinir_full_20260615_161634.err.log
```

## Results

| Dataset | Scale | Profile | Method | Folds | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| NingXia-T2 case-level CV | x4 | full | Linear | 8 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| NingXia-T2 case-level CV | x4 | full | Cubic | 8 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |
| NingXia-T2 case-level CV | x4 | full | ArSSR-style | 8 | 23.1634 | 0.7091 | 96.4890 | 38343.9409 | 0.8708 |
| NingXia-T2 case-level CV | x4 | full | ResUNet residual | 8 | 23.3816 | 0.7209 | 97.0409 | 36316.2290 | 0.8785 |
| NingXia-T2 case-level CV | x4 | full | SwinIR-style 2.5D | 8 | 23.9513 | 0.7525 | 85.9679 | 32030.5455 | 0.8930 |
| NingXia-T2 case-level CV | x4 | full | SAINT-style | 8 | 23.8350 | 0.7422 | 89.4140 | 32992.9496 | 0.8905 |

## Paired fold comparison

| Compared method | PSNR wins | SSIM wins | MAE wins | MSE wins | NCC wins | Mean delta summary |
|---|---:|---:|---:|---:|---:|---|
| Linear | 7/8 | 8/8 | 7/8 | 6/8 | 5/8 | PSNR +0.7891, SSIM +0.0650, MAE -24.5915, MSE -22540.4634, NCC +0.0158 |
| Cubic | 7/8 | 8/8 | 8/8 | 7/8 | 8/8 | PSNR +1.8417, SSIM +0.1250, MAE -42.0169, MSE -35715.2871, NCC +0.0427 |
| ArSSR-style | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | PSNR +0.7879, SSIM +0.0434, MAE -10.5211, MSE -6313.3955, NCC +0.0221 |
| ResUNet residual | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | PSNR +0.5697, SSIM +0.0316, MAE -11.0730, MSE -4285.6835, NCC +0.0145 |
| SAINT-style | 5/8 | 8/8 | 7/8 | 5/8 | 6/8 | PSNR +0.1163, SSIM +0.0103, MAE -3.4461, MSE -962.4041, NCC +0.0024 |

## Decision

SwinIR-style 2.5D is now complete across IXI-T2, fastMRI-brain-T2 expanded, and NingXia-T2 8-fold CV. It is a first-tier baseline. On NingXia it is the best current method by mean PSNR / SSIM / MAE / MSE / NCC, but the margin over SAINT-style is small and fold-level wins are mixed for PSNR / MSE / NCC.

The table-level conclusion should be: SAINT-style remains the strongest fastMRI baseline and is still very strong on IXI, while SwinIR-style 2.5D is the strongest NingXia CV baseline and the best SSIM/MAE method on IXI. They form the current first tier before I3Net arrives.
