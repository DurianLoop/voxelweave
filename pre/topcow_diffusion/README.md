# TopCaw MR Diffusion Pipeline

This folder is the diffusion counterpart to `topcow_gan`.

It keeps the same experiment discipline:

- case-level train / validation split
- best checkpoint selected on held-out cases
- early stopping and LR scheduling
- visual QC
- per-case analysis
- structural training loss
- labeled holdout evaluation inside real vessel labels

## One-command runs

```powershell
python -m topcow_diffusion.run_all --profile quick_smoke
python -m topcow_diffusion.run_all --profile smoke
python -m topcow_diffusion.run_all --profile full
```

`full` is configured for the 24 GB GPU setup:

- batch size: 16
- max epochs: 30
- sampling steps: 20
- early stopping patience: 5
- AMP mixed precision enabled automatically on CUDA

If CUDA runs out of memory, lower `batch_size` in `settings.py` to 8 and rerun.

## Structural objective

The current diffusion baseline predicts noise while also regularizing reconstructed
`x0` with:

- foreground-weighted L1
- SSIM loss
- gradient loss

## Main outputs

- `runs/<profile>/checkpoints`
- `runs/<profile>/diffusion_outputs`
- `runs/<profile>/baseline_outputs`
- `runs/<profile>/labeled_eval`
- `runs/<profile>/metrics`

After a run:

```powershell
python -m topcow_diffusion.visual_qc --profile full
python -m topcow_diffusion.result_analysis --profile full
python -m topcow_diffusion.summary_plots --profile full
```
