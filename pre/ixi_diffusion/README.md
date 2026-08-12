# IXI Pure-Noise Diffusion Baseline

This folder runs a conditional diffusion baseline on IXI while keeping the vanilla design:

```text
condition: z and z+4 slices + position channels
sample:    start from pure Gaussian noise
output:    z+1, z+2, z+3 full intermediate slices
```

It is intentionally not residual/refinement diffusion. The goal is to test whether the larger IXI dataset can make the pure-noise design stable.

## Commands

Run from `D:\MRI` with the MRI environment:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile smoke
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile mini
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile full
```

Recommended first run:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile smoke *> temp\ixi_diffusion_smoke.log
```

Then inspect:

```text
ixi_diffusion/runs/smoke/metrics/summary_metrics.csv
ixi_diffusion/runs/smoke/metrics/intensity_sanity.csv
```

If `diffusion` median / p99 are far from `gt` and `linear`, the same intensity collapse seen on TopCaw is still happening.

## HiFi-Diff-Like Prototype

The residual / partial diffusion profiles are closer to medical inter-slice interpolation papers:

```text
condition: left slice, right slice, linear coarse slice, relative position
target:    residual between target slice and linear coarse slice
sample:    start near zero residual with partial diffusion
```

Commands:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile hifidiff_smoke
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile hifidiff_mini
```

Clean evaluation-only rerun after `hifidiff_mini`:

```powershell
New-Item -ItemType Directory -Force ixi_diffusion\runs\hifidiff_mini_eval\checkpoints | Out-Null
Copy-Item ixi_diffusion\runs\hifidiff_mini\checkpoints\hifidiff_epoch_best.pth ixi_diffusion\runs\hifidiff_mini_eval\checkpoints\hifidiff_epoch_best.pth -Force
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile hifidiff_mini_eval
```

## ResUNet Residual Baseline

This is the current strong deterministic baseline for the IXI interpolation table:

```text
condition: left slice, right slice, linear coarse slice, relative position
target:    residual between target slice and linear coarse slice
output:    coarse + predicted residual
```

PD has already been run as `resunet_full`. The same case-level split and evaluation code can be used for T1/T2:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile resunet_full
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile resunet_full_t1
D:\conda\envs\MRI\python.exe -m ixi_diffusion.run_all --profile resunet_full_t2
```

After a run finishes, generate the paper table, visual QC, and sanity report:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_diffusion.paper_table --profile resunet_full
D:\conda\envs\MRI\python.exe -m ixi_diffusion.visualize_results --profile resunet_full --case-limit 3
D:\conda\envs\MRI\python.exe -m ixi_diffusion.baseline_report --profile resunet_full
```

Main outputs:

```text
ixi_diffusion/runs/<profile>/metrics/summary_metrics.csv
ixi_diffusion/runs/<profile>/metrics/per_case_metrics.csv
ixi_diffusion/runs/<profile>/metrics/paper_table.csv
ixi_diffusion/runs/<profile>/metrics/baseline_report.md
ixi_diffusion/runs/<profile>/metrics/visual_qc
```
