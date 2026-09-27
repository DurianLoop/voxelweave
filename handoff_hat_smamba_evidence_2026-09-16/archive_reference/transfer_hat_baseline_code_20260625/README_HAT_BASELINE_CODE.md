# HAT-style 2.5D baseline code package

Date: 2026-06-25

This package contains only the training/evaluation code for the local HAT-style 2.5D baseline used in the T2 x4 through-plane interpolation experiments. It intentionally excludes datasets, generated runs, checkpoints, NIfTI outputs, and cache files.

## Contents

```text
code/ixi_hat_2p5d/
  IXI-T2 HAT-style 2.5D model, training, evaluation, and paper-table scripts.

code/fastmri_brain_hat_2p5d/
  fastMRI-brain-T2 compatible HAT-style 2.5D model, dataset loader, training,
  evaluation, and paper-table scripts. The same package is also reused by the
  NingXia case-level CV driver through environment variable data roots.

code/ixi_diffusion/
  Shared IXI data/staging/common utilities required by the IXI runner.

code/topcow_diffusion/
  Shared baseline interpolation and metric utilities.

code/processing/run_ningxia_case_cv.py
code/processing/summarize_case_cv.py
  Case-level CV runner and summarizer. The runner supports HAT through
  `--models hat`.

requirements.txt
environment.yml
  Original local environment references.

docx/experiment_notes/hat_smamba_ixit2_screening_notes.md
  Lightweight run note for HAT/SMamba screening context.
```

## What is not included

```text
dataset/
runs/
checkpoints
*.nii.gz
__pycache__/
```

The recipient needs the same project data layout or must edit paths in the settings files.

## Expected project placement

The code was written to run from the project root:

```text
D:\MRI
```

If unpacking into another checkout, copy the folders under `code/` into that checkout root, or add `code/` to `PYTHONPATH`.

## Main commands

Run from the project root:

```powershell
Set-Location D:\MRI
```

IXI-T2 full test n=115:

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_hat_2p5d.run_all --profile full_test115
D:\conda\envs\MRI\python.exe -B -m ixi_hat_2p5d.paper_table --profile full_test115
```

fastMRI-brain-T2 expanded full:

```powershell
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_hat_2p5d.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m fastmri_brain_hat_2p5d.paper_table --profile full
```

NingXia-T2 case-level CV full:

```powershell
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile full --models hat
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --profile full --include-hat
```

## Current full profile notes

The full HAT profile currently uses:

```text
epochs = 30
batch_size = 8
grad_accum_steps = 3
effective_batch_size = 24
num_workers = 0
embed_dim = 48
depths = (2, 2, 2)
num_heads = (3, 3, 3)
```

`num_workers=0` is intentional for this Windows setup.

