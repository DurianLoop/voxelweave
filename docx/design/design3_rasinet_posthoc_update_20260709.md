# Design 3 RASI post-hoc update, 2026-07-09

## Current status

Design 3 should continue as a post-hoc reliability analysis track for now.

This update supersedes the accidental short detour toward full RASI-Net training. The trainable RASI-Net package and smoke/mini outputs can be kept as engineering exploration, but they should not be used as the main Design 3 evidence or placed in the main experiment table.

## Completed IXI full_test115 result

Input predictions:

| Method | Cases | Source |
|---|---:|---|
| I3Net | 115 | `ixi_i3net/runs/full_test115_stable` |
| HAT | 115 | `ixi_hat_2p5d/runs/full_test115` |
| SwinIR | 115 | `ixi_swinir_2p5d/runs/full_test115` |
| ACSI-Net | 115 | `acsinet/runs/full_test115` |

Output directory:

```text
rasinet/runs/posthoc_uncertainty/full_test115/metrics
```

Experiment note:

```text
docx/experiment_notes/rasinet_posthoc_uncertainty/full_test115_posthoc_report.md
```

## Main finding

`baseline_disagreement` is the strongest post-hoc uncertainty proxy across all four strong methods.

| Method | Best proxy | Pixel corr | Slice corr | Failure AUROC | Top-k recall |
|---|---|---:|---:|---:|---:|
| ACSI-Net | baseline_disagreement | 0.5667 | 0.4178 | 0.9871 | 0.8333 |
| HAT | baseline_disagreement | 0.6090 | 0.4578 | 0.9871 | 0.8333 |
| I3Net | baseline_disagreement | 0.5018 | 0.3567 | 0.9822 | 0.7500 |
| SwinIR | baseline_disagreement | 0.6153 | 0.4572 | 0.9871 | 0.8333 |

Residual-to-linear and residual-to-cubic are useful sanity proxies, but they should not be framed as main comparison targets.

## Correct paper framing

Do not claim:

```text
RASI-Net beats SOTA reconstruction models.
```

Claim instead:

```text
Existing slice interpolation methods report average reconstruction quality, while RASI-style post-hoc reliability analysis estimates case-level and region-level failure risk from existing predictions.
```

## Next actions

1. Use IXI full_test115 failure ranking to select 4-8 visual QC cases.
2. Build a figure with prediction, absolute error, uncertainty proxy, and overlay for the selected cases.
3. Repeat the same post-hoc reliability analysis on fastMRI if matching prediction caches are complete.
4. Repeat on NingXia CV outputs if the paper needs clinical/domain-shift evidence.
5. Only revisit trainable RASI-Net after post-hoc evidence is stable across datasets.

## Commands

Rebuild the IXI full_test115 post-hoc report:

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_uncertainty --source-set ixi --profile full_test115 --progress-every 1
D:\conda\envs\MRI\python.exe -B -m rasinet.posthoc_report --profile full_test115
```

Run the next low-cost fastMRI check:

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_uncertainty --source-set fastmri --profile fastmri_full --methods i3net,hat,swinir --progress-every 1
D:\conda\envs\MRI\python.exe -B -m rasinet.posthoc_report --profile fastmri_full
```

NingXia should be handled after this with a CV-aware source set, because its outputs are split by fold rather than a single `full_test115`-style run directory.

## Do not do now

- Do not run full RASI-Net training as the next default action.
- Do not compare only against linear/cubic as if they were the main baselines.
- Do not put the previous trainable RASI smoke/mini results into the full-result master table.
- Do not make a reliability claim without correlation, risk-coverage, and failure detection evidence.
