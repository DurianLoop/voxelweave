# TopCaw MR GAN Pipeline

This folder packages the next three project phases into one reproducible workflow:

1. Quantitative evaluation protocol for generated intermediate slices.
2. Formal GAN training on TopCaw MR-only training volumes.
3. Classical interpolation baselines: linear and cubic.

## One-command runs

From `D:\MRI` with the `MRI` conda environment activated:

```powershell
python -m topcow_gan.run_all --profile smoke
```

This verifies the whole workflow quickly using the already trained checkpoint when available.

For a quick case-level split check:

```powershell
python -m topcow_gan.run_all --profile case_smoke
```

For the full experiment:

```powershell
python -m topcow_gan.run_all --profile full
```

For the preferred full experiment with case-level train/validation split:

```powershell
python -m topcow_gan.run_all --profile case_full
```

For the structure-aware GAN variant added after the baseline run:

```powershell
python -m topcow_gan.run_all --profile case_struct_smoke
python -m topcow_gan.run_all --profile case_struct_full
```

The full profile:

- stages all TopCaw MR training files as hard links
- trains the GAN for 50 epochs
- creates sparse validation inputs from TopCaw MR validation volumes
- runs GAN reconstruction
- runs linear and cubic interpolation baselines
- evaluates generated intermediate slices
- writes CSV/JSON summaries under `topcow_gan\runs\full`

The case-level profiles:

- split TopCaw MR training volumes by case before slice extraction
- train on `runs/<profile>/train_mr_links`
- validate on held-out cases in `runs/<profile>/val_mr_links`
- use validation loss from held-out cases for `pix2pix_epoch_best.pth`
- use `ReduceLROnPlateau` and early stopping to handle later-epoch degradation
- run an additional labeled holdout evaluation on the validation cases when labels exist

## Main outputs

- `runs/<profile>/checkpoints`
- `runs/<profile>/gan_outputs`
- `runs/<profile>/baseline_outputs`
- `runs/<profile>/eval_inputs`
- `runs/<profile>/labeled_eval`
- `runs/<profile>/metrics`

## Metrics

The metrics summary includes:

- intensity metrics: PSNR, SSIM, MAE, MSE, NCC, Pearson
- foreground-aware metrics: mask-PSNR, mask-SSIM
- proxy structure metrics: auto-Dice, auto-HD95

TopCaw official MR validation cases in `imagesVal` do not include matching labels in
`cow_seg_labelsTr`, so Dice/HD95 here are computed on automatically thresholded
foreground masks from the generated and ground-truth MR slices. They are useful for
structural sanity checks, but they are not official vessel-segmentation Dice/HD95.

For case-level profiles, the pipeline also writes:

- `labeled_holdout_per_case_metrics.csv`
- `labeled_holdout_summary_metrics.csv`

These files evaluate reconstruction quality inside the real vessel labels of held-out
training cases, including vessel-PSNR, vessel-SSIM, vessel-MAE, vessel-MSE, and
vessel-boundary-MAE. This is a stronger structural evaluation than auto-thresholded
foreground masks, although true Dice/HD95 still require a segmentation prediction.

## Extra analysis

After a run, generate visual QC and GAN-vs-baseline deltas with:

```powershell
python -m topcow_gan.visual_qc --profile case_full
python -m topcow_gan.result_analysis --profile case_full
```
