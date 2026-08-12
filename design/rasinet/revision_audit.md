# ICASSP 2027 Revision Audit

Audit date: 2026-07-22

## 1. Existing manuscript and build state

- Main source: `design/rasinet/paper/main.tex`.
- Bibliography: `design/rasinet/paper/references.bib`.
- Existing PDF: `design/rasinet/paper/main.pdf`.
- Existing supplement: `design/rasinet/paper/supplement.tex` and `supplement.pdf`.
- Existing build log reports 6 pages for `main.pdf` and 2 pages for the supplement.
- The manuscript uses `article` plus custom `geometry`, not the official ICASSP style. It therefore cannot establish format compliance.
- The official ICASSP 2027 publication-options page specifies four technical pages plus an optional fifth page containing only references, and eight technical pages plus one references page for the OJSP route: `https://2027.ieeeicassp.org/publishing-and-paper-presentation-options/`.
- The 2027 template download was unavailable during the audit. The new drafts provisionally use the official ICASSP 2026 `spconf.sty` and `IEEEbib.bst` from `https://cmsworkshops.com/ICASSP2026/papers/paper_kit.php`; the 2027 kit must be substituted and rechecked when released.
- The log has no LaTeX errors, undefined references, missing citations, or overfull boxes, but it has multiple underfull boxes.
- Existing sections: Introduction, Related Work, Method, Experiments, Results, Discussion, and Conclusion.
- Existing main visuals: framework, main result table, risk--coverage figure, committee-composition table, and qualitative examples.

## 2. Experiment and asset locations

- Core score: `design/rasinet/committee_reliability.py`.
- Profile runner: `design/rasinet/committee_experiments.py`.
- Bootstrap/statistics: `design/rasinet/committee_statistics.py`.
- Paper assets: `design/rasinet/committee_paper_assets.py`.
- Consistency checks: `design/rasinet/check_paper_consistency.py`.
- Main run outputs: `design/rasinet/runs/committee_reliability/*/metrics/`.
- Statistical reports: `design/rasinet/reports/committee_reliability/`.
- Generated paper tables and figures: `design/rasinet/paper/tables/` and `design/rasinet/paper/figures/`.
- Existing tests: `tests/test_rasinet_committee_reliability.py`.

## 3. Datasets, cases, models, and sampling

| Dataset profile | Examinations | Neural targets | Analytical outputs | Sampling |
|---|---:|---|---|---|
| IXI T2 (`full_test115`) | 115 | I3Net, HAT, SwinIR, ACSI | linear, cubic | through-plane x4 |
| fastMRI-brain T2 (`fastmri_full`) | 24 | I3Net, HAT, SwinIR | linear, cubic | through-plane x4 |
| NingXia T2 (`ningxia_cv`) | 22 | I3Net, HAT, SwinIR | linear, cubic | through-plane x4, eight-fold held-out out-of-fold predictions |

There are 161 examinations and ten fixed target--dataset evaluations. Generated slices are indices satisfying `index % 4 != 0`; observed slices are excluded from evaluation.

## 4. Existing results and traceability

- Main table source: `design/rasinet/paper/tables/table_committee_main.csv`.
- Bootstrap source: `design/rasinet/reports/committee_reliability/main_bootstrap_ci.csv`.
- Coverage operating points: `design/rasinet/reports/committee_reliability/coverage_operating_points.csv`.
- Paired proxy comparisons: `design/rasinet/reports/committee_reliability/paired_proxy_bootstrap.csv`.
- Committee composition and score-level leave-one-out: `design/rasinet/reports/committee_reliability/committee_composition.csv`.
- Profile data rows are complete: 2760 IXI, 432 fastMRI-brain, and 396 NingXia rows, excluding CSV headers.
- Existing fixed-profile ranges are foreground pixel correlation 0.277--0.519, examination Spearman 0.890--0.966, nAURC 0.024--0.092, and RRR50 19.3--52.1%.

## 5. Existing methods and statistics

Implemented:

- median target-to-committee absolute difference with target-name exclusion in the profile runner;
- all-member, neural-only, and analytical-only committees;
- shared standard deviation over all outputs;
- residual to linear and residual to cubic;
- examination-level Spearman, risk--coverage, raw/oracle/random AURC, nAURC, and RRR25/50/75;
- per-examination foreground and all-pixel Pearson correlation;
- 2,000-replicate case bootstrap and paired nAURC/proxy differences;
- auxiliary SwinIR TTA results from an older, partially different evaluation pipeline.

Not implemented in the unified committee pipeline:

- mean, maximum, trimmed mean, distance-to-committee-mean, and distance-to-committee-median scores;
- pairwise committee scores, combined analytical residuals, gradient/Laplacian/patch-SSIM scores;
- normalization variants, mask variants, exact voxel-map leave-one-out, committee subset/size, or diversity analysis;
- Fisher-z pixel-correlation aggregation, Kendall tau, bootstrap samples on disk, or Holm correction;
- controlled target-specific versus shared-error stress tests;
- measured inference time, peak GPU memory, parameter counts, or scoring memory/time.

## 6. Input integrity audit

- Target exclusion: profile construction excludes the target model by name. The low-level function only rejects the same NumPy object and therefore needs explicit model-identity validation in the new pipeline.
- Case identity: case lists come from the I3Net reference directory. Missing peer files fail during load, but extra files, duplicate identities, and complete set equality are not checked.
- Shape: IXI and fastMRI QC report all required files present and shape-aligned. NingXia lacks equivalent current-path alignment and generated-slice summaries.
- Affine/orientation: headers are loaded but discarded; no affine, orientation, voxel-size, or qform/sform check exists.
- Intensity: model inference generally performs per-volume min--max normalization followed by inverse scaling to the source range. No cross-model percentile/location-scale audit is performed. NingXia intensity sanity files show non-identical model distributions.
- Clipping: HAT/SwinIR residual outputs and ACSI outputs are clipped in normalized space; I3Net follows its own restored-output path. This must be documented and sensitivity-tested.
- Generated slices: IXI and fastMRI QC match the x4 pattern. Current committee code evaluates generated indices only.
- Foreground mask: the current committee result uses a 1% target-prediction-derived mask and does not use ground truth. An older `posthoc_qc.py` sensitivity analysis used a ground-truth-derived nonzero mask; those old values are offline-only and must not be presented as the deployment mask.

## 7. Reproducibility and leakage audit

- The all-member median score with a 1% target-derived mask is treated as the pre-specified default.
- fastMRI-brain and NingXia results have already been observed and cannot be used to select a new score, threshold, normalization, or committee.
- No explicit IXI development split or nested selection registry exists.
- There is no `results_registry.csv`, experiment configuration directory, environment lock file, or single evaluation entry point.
- `D:\MRI` is not a Git repository, so a code commit cannot currently be recorded; registry entries must use `unversioned-workspace` unless a repository is initialized later.
- NingXia QC and run manifests contain stale pre-move paths. HAT/SwinIR manifests also contain an incorrect fastMRI dataset label and null train/validation/test counts.

## 8. Manuscript risks

1. The abstract incorrectly calls the score a median absolute deviation.
2. The current title and contributions over-emphasize an estimator rather than a reliability-ranking protocol.
3. `external cross-validation cohort` is ambiguous for NingXia; evidence supports an internal eight-fold out-of-fold cohort.
4. Version-history wording such as `corrected target-specific score` appears in the paper.
5. The shared-error limitation is stated but lacks the requested derivation and controlled experiment.
6. Median is not compared with equally simple target-specific alternatives.
7. Pixel correlations are averaged directly rather than with Fisher z; median/IQR are absent.
8. The current leave-one-out analysis is score-level and not equivalent to recomputing voxel maps.
9. Cost claims are unsupported by timing and memory measurements.
10. The bibliography is too narrow for no-reference IQA, reconstruction error prediction, correlated ensembles, and selective prediction.
11. The framework figure omits sparse input, target exclusion, committee heterogeneity, and foreground aggregation.
12. The regular manuscript exceeds ICASSP 2027's four technical pages and uses a noncompliant template.

## 9. Experiments that cannot currently be claimed

- New MRI contrast, organ, acquisition site, or interpolation factor: no verified additional prediction set is connected to the committee pipeline.
- Full cross-model TTA/MC-dropout/deep ensemble: only SwinIR TTA is available and comes from a separate pipeline.
- Online deployment latency and GPU memory: historical logs do not contain complete comparable measurements.
- Clinical validity, diagnostic harm, reader performance, or downstream-task benefit: no corresponding study exists.

These items must remain limitations or explicit TODOs unless real inputs and runs are added.

## 10. Audit decision

The existing data support a strong examination-ranking result, but they do not establish a new calibrated uncertainty estimator. The defensible paper is a target-specific, ground-truth-free reliability-ranking and selective-review protocol with explicit composition, normalization, mask, cost, and shared-error boundaries. The original manuscript and original outputs must be preserved; all ICASSP revisions will be written to separate files.

## 11. Post-audit implementation state

The audit findings were acted on in separate files under `design/rasinet`; the original manuscript and result directories remain unchanged. A YAML-controlled evaluator now performs explicit identity/geometry checks, target-excluded score variants, deployment masks, normalization sensitivity, exact voxel-level committee subsets, Fisher-z aggregation, paired bootstrap, risk--coverage output, checkpoints, and result registration. Two-case IXI smoke results reproduce the prior primary method exactly. The registered run completed with 161 examinations, 33,672 case-specification rows, 504 summary groups, and 2,000 bootstrap replicates. The fixed-count validator and 19 unit tests pass; both manuscript versions consume the same automatically generated assets.
