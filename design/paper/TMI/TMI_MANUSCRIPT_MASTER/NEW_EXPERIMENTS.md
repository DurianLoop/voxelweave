# TMI Plan6 New Experiments

Registration and execution date: 2026-08-13. Default coverage is fastMRI + IXI + NingXia. The only two-dataset exception is IXI + fastMRI for the x4→x2 consequence endpoint.

## E01 — Multi-endpoint robustness

- Coverage: all three cohorts, HAT/SwinIR, three physical planes per examination, seven endpoints.
- Result: 42/42 disjoint-minus-shared Spearman differences positive.
- Stable region: MAE, RMSE, MSE, low-frequency MAE.
- Boundary: absolute SSIM-error ranking weak/negative on fastMRI and NingXia; some small-cohort gradient/high-frequency intervals cross zero.
- Files: `experiments/p6_e01_metric_robustness*`; figure `figures/p6_e01_metric_robustness.pdf`.

## E02 — Consensus distributions and stable-wrong prevalence

- Coverage: all three cohorts, both architectures, disjoint and maximal-shared contexts.
- Result: partial Spearman between shared fraction and normalized disagreement, controlling total error and examination, −0.746 to −0.975 in all 12 strata.
- Strict stable-wrong: zero under disjoint contexts; 0–0.32% fastMRI/IXI and 2.42–3.23% NingXia under maximal sharing.
- Boundary: extreme event is rare and NingXia intervals are wide under eight patient clusters.
- Files: `experiments/p6_e02_*`; figure `figures/p6_e02_consensus_distributions.pdf`.

## E03 — Geometry and intensity operating range

- Coverage: 322 x4 HAT/SwinIR outputs across all cohorts.
- Geometry: identical shapes/orientations/affines; 100% same-plane matches for tolerances 1e−6–0.1 mm.
- Intensity: one common per-case robust transform preserves a positive overlap contrast in all six strata; case ranks change, especially IXI/NingXia.
- Rejection: independent output normalization is not a valid absolute-discrepancy operation.
- Files: `experiments/p6_e03_*`; figure `figures/p6_e03_intensity_audit.pdf`.

## E11 — Analytical x2/x4/x6 factor response

- Coverage: all cohorts; two-anchor linear and nearest-anchor replication.
- Result: paired error and shared fraction rise monotonically; observable fraction and reliability fall monotonically.
- Shared fraction x2→x6: 0.843→0.953 fastMRI; 0.750→0.923 IXI; 0.860→0.953 NingXia.
- Reliability rho x2→x6: 0.955→0.798; 0.961→0.947; 0.937→0.818.
- Boundary: analytical estimator evidence; not a surrogate for unrun neural x6.
- Files: `experiments/p6_e11_*`; figure `figures/p6_e11_factor_robustness.pdf`.

## E12 — Three-cohort selective risk

- Common endpoint: stored mean HAT/SwinIR x4 examination MAE.
- Comparators: measurement-disjoint, maximal-shared, HAT–SwinIR committee, adjacent-anchor MAE.
- nAURC (fastMRI/IXI/NingXia): disjoint 0.0119/0.0013/0.0107; shared 0.0684/0.0139/0.0306; committee 0.0193/0.0140/0.0504; adjacent 0.0212/0.0143/0.0070.
- Conclusion: disjoint is the best tested output-based construction in all cohorts, not the universal best score.
- Files: `experiments/p6_e12_*`; figure `figures/p6_e12_risk_coverage.pdf`.

## Cross-paper consequence evidence used as a boundary

- Frozen IXI x2 inference: 115/115 outputs complete; checkpoint hash recorded in `../../../IXI_X2_FROZEN_EVALUATION.md`.
- Permitted pair: IXI + fastMRI.
- Anchor-CV vs realized benefit rho: 0.948 IXI, 0.871 fastMRI; positive gains above random at 10/20/30/50% budgets.
- Boundary: IXI compares mean HAT/SwinIR x4 error with I3Net x2 error; it is not a same-model causal effect.

## Reproducibility rule

Every experiment retains per-observation CSV, summary CSV/JSON, source script, and generated figure. Historical frozen outputs were not overwritten. No missing structural endpoint was replaced by a proxy, and no uncovered neural volume was padded.
