# 已迁移：此处不再维护

当前清单已经改成中文，并迁移到 `D:\MRI\rasinet` 专门目录：

`D:\MRI\rasinet\reports\posthoc_uncertainty\checklist.md`

后续 RASI post-hoc uncertainty 的代码、报告、图表和 QC 文档都应优先放在 `D:\MRI\rasinet`。

---

# RASI-Net Post-hoc Uncertainty Checklist

Purpose: keep Design 3 on the low-compute reliability-analysis track. This checklist is for post-hoc uncertainty using existing predictions, not for training a new RASI-Net model.

## 0. Direction Lock

- [x] Re-check `docx/design/design3_rasinet_reliability.md`.
- [x] Re-check `docx/design/design_overview_table.md`.
- [x] Re-check `docx/design/design3_rasinet_next_guide.md`.
- [x] Confirm current track is post-hoc uncertainty analysis, not full RASI-Net training.
- [x] Stop treating linear/cubic as main comparison methods. They are only coarse/reference signals for proxy construction.

## 1. Code And Run Artifacts

- [x] Add post-hoc analysis entrypoint: `rasinet/posthoc_uncertainty.py`.
- [x] Use existing full_test115 predictions from I3Net/HAT/SwinIR/ACSI.
- [x] Add progress logging so full runs do not look frozen.
- [x] Run post-hoc smoke profile.
  - Output: `rasinet/runs/posthoc_uncertainty/smoke/metrics/`
- [x] Run post-hoc mini profile.
  - Output: `rasinet/runs/posthoc_uncertainty/mini/metrics/`
- [x] Run post-hoc full_test115 profile.
  - Output: `rasinet/runs/posthoc_uncertainty/full_test115/metrics/`
- [x] Confirm full_test115 output files exist:
  - `paper_table_posthoc.md`
  - `summary_posthoc_reliability.csv`
  - `per_case_posthoc_reliability.csv`
  - `risk_coverage_posthoc.csv`
  - `calibration_bins_posthoc.csv`
  - `failure_detection_posthoc.csv`

## 2. Current Full-Test115 Snapshot

- [x] Full profile completed on 115 IXI cases.
- [x] Methods included: `i3net`, `hat`, `swinir`, `acsinet`.
- [x] Proxies included:
  - `baseline_disagreement`
  - `residual_linear`
  - `residual_cubic`
- [x] First result readout from `paper_table_posthoc.md`:
  - `swinir__baseline_disagreement`: pixel corr `0.6153`, slice corr `0.4572`, failure AUROC `0.9871`.
  - `hat__baseline_disagreement`: pixel corr `0.6090`, slice corr `0.4578`, failure AUROC `0.9871`.
  - `acsinet__baseline_disagreement`: pixel corr `0.5667`, slice corr `0.4178`, failure AUROC `0.9871`.
  - `i3net__baseline_disagreement`: pixel corr `0.5018`, slice corr `0.3567`, failure AUROC `0.9822`.

## 3. Quality-Control Checks To Do Next

- [ ] Verify that all 115 cases are aligned across GT, linear, cubic, I3Net, HAT, SwinIR, and ACSI outputs.
- [ ] Add a manifest CSV listing per-case input paths used by post-hoc analysis.
- [ ] Check whether the proxy is evaluated only on generated slices, matching the x4 interpolation task.
- [ ] Check whether background voxels dominate pixel-level correlation.
- [ ] Add brain-mask or nonzero-region evaluation variant if background dominance is visible.
- [ ] Compare pixel-level and slice-level conclusions; flag cases where they disagree.
- [ ] Inspect top failure cases from `failure_detection_posthoc.csv` and per-case MAE ranking.

## 4. Tables To Build

- [ ] Create a clean reliability summary table for notes:
  - Source: `rasinet/runs/posthoc_uncertainty/full_test115/metrics/summary_posthoc_reliability.csv`
  - Target: `docx/experiment_notes/rasinet_posthoc_uncertainty/full_test115_summary.md`
- [ ] Create a proxy comparison table:
  - baseline disagreement vs residual linear vs residual cubic.
- [ ] Create a method comparison table:
  - I3Net vs HAT vs SwinIR vs ACSI under the same proxy.
- [ ] Create a failure-detection table:
  - AUROC, AUPRC, top-k recall.
- [ ] Keep `docx/experiment/experiment_master_table.md` untouched until results are paper-ready.

## 5. Figures To Build

- [ ] Plot risk-coverage curves for the four methods using `baseline_disagreement`.
- [ ] Plot correlation bar chart for all method/proxy combinations.
- [ ] Plot failure-ranking curve or top-k recall curve.
- [ ] Export figures under `docx/experiment_notes/rasinet_posthoc_uncertainty/figures/`.

## 6. Visual Case Review

- [ ] Pick top 5 high-risk/high-error cases.
- [ ] Pick top 5 low-risk/low-error cases.
- [ ] Pick 3 mismatch cases:
  - high uncertainty but low error.
  - low uncertainty but high error.
- [ ] Save image panels with prediction, absolute error, and uncertainty proxy.
- [ ] Write a short visual QC note explaining whether the uncertainty highlights anatomy boundaries or failure regions.

## 7. Interpretation

- [ ] Decide whether `baseline_disagreement` is the main proxy.
- [ ] Decide whether residual proxies are too weak or still useful as ablations.
- [ ] Write the main claim conservatively:
  - Existing interpolation methods can be equipped with post-hoc reliability signals.
  - Baseline disagreement correlates with reconstruction error and detects failure cases.
  - This is a reliability layer, not a new SOTA reconstruction model.
- [ ] Identify limitations:
  - proxy is not calibrated probabilistic uncertainty.
  - method disagreement may fail when all models make similar errors.
  - full validation on fastMRI/NingXia is still needed before broad claims.

## 8. Optional Follow-up Experiments

- [ ] Add TTA variance proxy for one strong model if runtime is acceptable.
- [ ] Run the same post-hoc analysis on fastMRI-brain T2 outputs.
- [ ] Run the same post-hoc analysis on NingXia CV outputs.
- [ ] Compare post-hoc uncertainty against learned RASI-Net uncertainty only as an auxiliary ablation, not as the main route.

## 9. Commands

Smoke:

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_uncertainty --profile smoke --progress-every 1
```

Mini:

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_uncertainty --profile mini --progress-every 1
```

Full:

```powershell
cd D:\MRI
$env:PYTHONPATH=(Resolve-Path .\pre).Path
D:\conda\envs\MRI\python.exe -u -B -m rasinet.posthoc_uncertainty --profile full_test115 --progress-every 1
```
