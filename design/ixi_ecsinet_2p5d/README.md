# ECSI-Net IXI-T2 x4 Baseline

This package implements ECSI-Net, an efficient clinical slice interpolation model for the repository's T2 through-plane interpolation mainline.

Run a quick IXI smoke test:

```powershell
python -m ixi_ecsinet_2p5d.run_all --profile smoke
```

Generate paper-table artifacts after a completed run:

```powershell
python -m ixi_ecsinet_2p5d.paper_table --profile smoke
```

The first implementation follows `docx/design/design6_ecsinet_efficiency.md`: linear coarse interpolation remains the base prediction, while a change-aware mask controls how much lightweight residual correction is applied.

Run the gated acceptance workflow by double-clicking `run_acceptance.cmd`, or from PowerShell:

```powershell
cmd /c D:\MRI\design\ixi_ecsinet_2p5d\run_acceptance.cmd
```

The workflow runs static checks, GPU preflight, profiling, smoke, and mini in order. It stops at the first failed gate and records resumable state under `reports/efficiency/one_click_state.json`. Full and cross-dataset runs remain blocked until the Pareto baseline gate is satisfied.
