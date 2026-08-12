# SwinIR-style 2.5D fastMRI-brain-T2 expanded run notes

Date: 2026-06-15

Dataset: fastMRI-brain-T2 expanded, 160 NIfTI, train/val/test = 112/24/24.
Task: T2 x4 through-plane interpolation.
Protocol: project split/metrics, same main-table metrics as Linear / Cubic / ArSSR / ResUNet / SAINT.

## Commands

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_swinir_2p5d.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_swinir_2p5d.paper_table --profile smoke

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_swinir_2p5d.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_swinir_2p5d.paper_table --profile mini

D:\conda\envs\MRI\python.exe -B -m fastmri_brain_swinir_2p5d.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_swinir_2p5d.paper_table --profile full
```

Note: the first full training run was interrupted after writing `swinir_epoch_best.pth`. Rerunning the same full command used `skip_training_if_checkpoint_exists=True`, skipped retraining, and completed test inference/metrics from the saved best checkpoint.

## Results

| Dataset | Scale | Profile | Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| fastMRI-brain-T2 expanded | x4 | full | Linear | 24 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| fastMRI-brain-T2 expanded | x4 | full | Cubic | 24 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |
| fastMRI-brain-T2 expanded | x4 | full | SwinIR-style 2.5D | 24 | 22.3615 | 0.7455 | 52.0221 | 11591.7882 | 0.8974 |

## Paired comparison

Against Linear: SwinIR wins 24/24 cases on PSNR, SSIM, MAE, MSE, and NCC.

Against Cubic: SwinIR wins 24/24 cases on PSNR, SSIM, MAE, MSE, and NCC.

Against ResUNet residual: SwinIR is slightly stronger overall, with paired wins PSNR 17/24, SSIM 23/24, MAE 24/24, MSE 16/24, NCC 14/24.

Against SAINT-style: SwinIR loses on all 24/24 cases for the five main metrics. SAINT-style remains the strongest fastMRI T2/x4 baseline.

## Decision

SwinIR-style 2.5D is worth keeping as a strong general Transformer SR baseline and should be expanded to NingXia-T2 8-fold CV for three-dataset completeness. It should not replace SAINT-style as the primary baseline.
