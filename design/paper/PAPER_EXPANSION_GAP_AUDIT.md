# Plan6 Paper Expansion Gap Audit

Audit date: 2026-08-13. Scope: MRI inter-slice / through-plane interpolation only.

## Dataset coverage rule

All newly computed experiments default to fastMRI brain T2, IXI brain T2, and NingXia knee T2. A two-dataset experiment is permitted only when the endpoint or frozen asset is unavailable in one cohort, and then the pair must be IXI + fastMRI. A one-dataset result is a pilot or explicit feasibility audit, never confirmatory evidence. NingXia always has eight independent patient clusters despite 22 series.

## Current page and evidence inventory

### TMI current six-page manuscript

| Page | Current scientific content | Existing figures/tables | Main evidence gap |
|---:|---|---|---|
| 1 | abstract, motivation, consensus-blindness concept | Fig. 1 | theory is compact; no distributional decomposition |
| 2 | related work, exact error decomposition, overlap definition | Fig. 2 | only extreme cases and zero/max design; no full factor response |
| 3 | cohorts, models, scores, clustered statistics, start of results | Table I | metric, geometry, normalization and granularity protocols are compressed |
| 4 | primary overlap result, estimator generality, densification, failures | Figs. 3--5, Table II | many results appear as single correlations/bars; no full risk curves or forest plots |
| 5 | discussion, limitations, ethics, conclusion | none | reviewer answers are mostly verbal rather than dedicated experiments |
| 6 | references | none | appropriate |

TMI has five figures and two tables. Its current claims are traceable, but the manuscript is a compressed summary rather than a complete research master.

### CVPR current six-page manuscript

| Page | Current scientific content | Existing figures/tables | Main evidence gap |
|---:|---|---|---|
| 1 | abstract, motivation, contributions | none | neural shared-influence evidence absent |
| 2 | concept figure, related work, theory, cohort start | Fig. 1 | mechanism is exact only for linear estimators |
| 3 | methods, compact ladder, clean result | Fig. 2 | causal arrows are not jointly quantified |
| 4 | analytical shared influence, Anchor-CV comparisons | Figs. 3--4, Tables 1--3 | Anchor-CV explanation and strong input ablations incomplete |
| 5 | budget curve, discussion, conclusion, references begin | Fig. 5 | failure cases and efficiency lack measurements; only five true main-content pages |
| 6 | references | none | appropriate |

CVPR has five figures and three tables. Its strongest reviewer vulnerability is the gap between exact analytical coefficients and HAT/SwinIR.

## Ranked TMI gaps

### P0 — acceptance threats

1. **Metric dependence:** the primary claim is dominated by MAE/Spearman. Required test: MAE, RMSE/MSE, PSNR-equivalent error, SSIM, gradient, low/high-frequency endpoints on all three cohorts where paired predictions exist.
2. **Factor completeness:** x2/x4/x6 assets exist for fastMRI and NingXia but IXI is presently x4-only in the frozen manifest. Required action: three-cohort x4 characterization plus fastMRI+IXI whenever only two are possible; factor claims cannot be generalized to IXI until valid outputs exist.
3. **Statistical hierarchy and influence:** central effects need clustered CIs, paired tests and leave-one-cluster-out influence, not only pooled plane statistics.
4. **Geometry/intensity confounds:** tolerance and normalization claims are currently caveats. Required perturbation audit with explicit operating range.
5. **Risk coverage:** full curves and fixed coverage points are required; one nAURC or one 25% budget is insufficient.

### P1 — material strengthening

6. Complete consensus-error distributions by dataset/model/factor/examination and relate shared fraction to reliability failure.
7. Architecture/estimator panels beyond final rho, including error alignment and failure heterogeneity.
8. Pixel/plane/examination/patient granularity audit with stable-wrong examples.
9. Full retrospective 10/20/30/50% budget curves with absolute and oracle-normalized gains.
10. Error taxonomy with image/error/disagreement panels.
11. Measured runtime, memory, reconstruction-call and storage comparison.

### P2 — completeness

12. Expanded correlated-error theory tied to testable predictions.
13. Forest plots and curve-crossing interpretation.
14. Detailed protocol and reproducibility tables.

### P3 — cosmetic

No generic introduction expansion, background padding, oversized figures, whitespace manipulation or trivial sweeps are authorized.

## Ranked CVPR gaps

### P0 — acceptance threats

1. **Neural shared influence:** analytical coefficient evidence does not establish the mechanism for HAT/SwinIR. Required three-cohort finite-difference/local-sensitivity experiment with frozen perturbations.
2. **Mechanism chain:** quantify shared influence → error alignment → disagreement suppression → ranking loss with cluster inference and architecture/dataset heterogeneity.
3. **Cleaner neural context intervention:** compare multiple target-preserving two-anchor contexts; do not try to restore the falsified integer-count law.
4. **Anchor-CV independence:** freeze V1 immediately. No truly untouched examination subset is currently proven; search for one, otherwise label all existing-cohort confirmation as external-method/factor validation rather than independent data confirmation.
5. **Trivial baselines:** adjacent MAE/RMSE/SSIM, gradient difference, frequency difference, curvature and spacing must be compared under the same clustered endpoints.

### P1 — material strengthening

6. Explain Anchor-CV via partial correlations and variance decomposition against intensity scale, spacing, curvature and direct anchor difference.
7. Architecture-independent examination difficulty model.
8. Formal false-positive/false-negative and PC-versus-Anchor-CV failure analysis.
9. Actual efficiency/latency/memory measurements.
10. IXI x2 consequence test if a valid frozen model/output can be completed; otherwise document the exact asset/compute blocker.
11. Updated novelty audit targeted at leave-one-acquired-slice validation and dependent-ensemble error.

### P2 — completeness

12. Full eight-page figure/table plan with no redundant panels.
13. Separate supplementary manuscript with configuration, cluster interval and negative-result detail.

## Claims currently supported by only one experiment family

- TMI retrospective densification is supported by stored x4→x2 simulation but lacks complete budget curves in the manuscript.
- TMI geometry robustness is supported by an audit record but not tolerance perturbations.
- CVPR neural common-mode behavior has clean zero/max evidence but no neural influence dose.
- CVPR Anchor-CV's mechanism explanation is currently inferential; direct input-baseline and partial-correlation tests are missing.
- CVPR computational deployability is stated from required inputs, not measured latency/memory.

## Correlation-heavy conclusions needing predictive or controlled tests

- Shared fraction predicting reliability failure: require locked cross-case prediction/partial association.
- Anchor-CV predicting intrinsic difficulty: require normalized endpoints and competing-variable controls.
- Shared influence explaining error alignment: require neural local-sensitivity intervention, not only analytical configuration means.
- Resource allocation: require all fixed budgets and clustered absolute gain, while preserving the retrospective label.

## Mature-paper figure requirements

TMI: decomposition distributions; factor/model forest plot; metric robustness matrix; geometry/intensity sensitivity; multi-granularity stable-wrong panel; full risk curves; budget-benefit curves; failure taxonomy; efficiency table.

CVPR: mechanism overview; analytical and neural influence ladders; full mechanism-chain panel; Anchor-CV schematic; three-cohort reliability/ablation table; budget curves; failure cases; efficiency table.

## Immediate execution decision

P0/P1 experiments precede manuscript expansion. TMI master/submission directories and CVPR page-growth ledgers will be populated only after new results exist. Current LaTeX prose is not a page-count template.
