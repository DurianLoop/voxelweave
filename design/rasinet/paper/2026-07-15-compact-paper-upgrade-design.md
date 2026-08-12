# Compact Conference Paper Upgrade Design

## Objective

Rewrite the current manuscript as a compact, evidence-driven conference paper about ground-truth-free reliability assessment for MRI through-plane interpolation. The paper must not claim a new reconstruction model or state-of-the-art reconstruction quality. Its central question is whether disagreement among heterogeneous reconstructors can identify unreliable pixels and cases when the target slice is unavailable at deployment.

## Scientific Positioning

The paper will use the working title **When MRI Slice Interpolators Disagree: Ground-Truth-Free Reliability Assessment Across Models and Datasets**.

The contribution is a model-agnostic quality-control protocol. Given a target reconstructor and a committee of alternative reconstruction outputs, the protocol derives a target-specific disagreement map, aggregates it into a case score, and uses that score to prioritize manual review. Ground truth is used only for retrospective evaluation.

The main paper will make three claims:

1. Target-to-committee disagreement is positively associated with reconstruction error across models and datasets.
2. Sorting cases by disagreement improves retained reconstruction quality relative to random review, with performance bounded by an oracle ranking.
3. The signal is not explained by one weak interpolation reference or one committee member, as shown by proxy, committee-composition, and leave-one-model-out analyses.

## Corrected Method Definition

For target prediction `p_m` and committee predictions `C_m`, the primary uncertainty map is the pixel-wise median absolute disagreement

`U_m = median_{b in C_m} |p_m - p_b|`.

The target prediction is excluded from its committee. Linear and cubic interpolation are permitted committee members but their influence is tested explicitly. The previous shared standard-deviation map is retained under the separate name `committee_dispersion`; it is not described as target-specific.

The case score is the foreground mean of `U_m`. Evaluation uses the nonzero foreground mask as primary and reports all-pixel results only as a sensitivity analysis.

## New Experiments

The existing three datasets remain the evidence base: IXI T2 (115 cases), fastMRI-brain T2 (24 cases), and NingXia T2 cross-validation (22 cases). Existing I3Net, HAT, SwinIR, and ACSI outputs are reused where available.

The upgrade adds:

- target-to-committee disagreement for every available target model;
- committee dispersion as a method-independent comparator;
- committee composition ablation: neural peers only, analytical references only, and all available members;
- leave-one-member-out sensitivity for the all-member committee;
- risk-coverage curves with random and oracle references;
- normalized AURC and excess AURC so values can be compared across datasets;
- retained MAE and relative risk reduction at 25%, 50%, and 75% coverage;
- paired case-bootstrap confidence intervals for the main proxy against residual and dispersion comparators.

TTA variance remains an auxiliary experiment on SwinIR. Failure AUROC/AUPRC remains secondary because fastMRI and NingXia contain only three failure cases under the main threshold.

## Paper Structure

The manuscript targets approximately eight pages of main content in a compact two-column conference layout, followed by references and supplementary material.

1. Abstract: problem, method, three-dataset protocol, operational risk-coverage result, boundary.
2. Introduction: deterministic interpolation gap, deployment question, precise contributions.
3. Related Work: slice interpolation, reconstruction uncertainty, selective prediction and quality control.
4. Method: deployment setting, target-to-committee disagreement, alternative proxies, evaluation protocol.
5. Experiments: datasets, reconstructors, masks, committee construction, statistical analysis.
6. Results: main reliability result, selective review benefit, robustness and ablations, qualitative failure modes.
7. Discussion and Limitations: correlated committee failures, committee availability, small external cohorts, no clinical reader study.
8. Conclusion.

The main paper will contain no more than two tables and three figures. Complete confidence intervals, reconstruction context, TTA, failure-definition sensitivity, calibration bins, and per-case rankings move to the supplement.

## Evidence and Claim Controls

- No claim may use smoke or mini results.
- No statement may call the proxy calibrated probability or Bayesian uncertainty.
- `1.000` AUROC on fastMRI must be accompanied by the 24-case and three-failure sample size.
- Linear and cubic interpolation are committee/reference components, not primary competing reconstruction methods.
- Every reported number must originate from a generated CSV.
- The manuscript must distinguish retrospective evaluation with ground truth from deployment-time scoring without ground truth.

## Verification

The implementation is complete only when unit tests cover the corrected disagreement and risk metrics, all three full profiles produce the new CSVs, paper tables and figures regenerate from those CSVs, LaTeX compiles without undefined references, numeric consistency checks pass, and rendered PDF pages have no clipping or unreadable text.

