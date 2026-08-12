# Strict HiFi-Diff-Style Reproduction on IXI

This folder is separate from `ixi_diffusion/`.

`ixi_diffusion/` contains the earlier low-fi residual / partial diffusion prototype.
This folder follows the HiFi-Diff paper more closely:

```text
condition:
  two adjacent slices
  relative offset

condition module:
  hierarchical feature extractor
  offset-conditioned channel modulation

generation:
  Gaussian noise -> target intermediate slice

loss:
  DDPM noise prediction loss
```

Run smoke:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_hifidiff_strict.run_all --profile smoke *> temp\strict_hifidiff_smoke.log
```

Run mini:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_hifidiff_strict.run_all --profile mini *> temp\strict_hifidiff_mini.log
```

Run full:

```powershell
D:\conda\envs\MRI\python.exe -m ixi_hifidiff_strict.run_all --profile full *> temp\strict_hifidiff_full.log
```
