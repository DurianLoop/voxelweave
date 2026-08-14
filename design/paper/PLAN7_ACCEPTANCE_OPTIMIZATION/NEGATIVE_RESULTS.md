# Plan7 negative-results register

Inherited falsifications remain active constraints:

1. Integer overlap count is not strictly monotone.
2. Fixed-count neural influence is null/mixed in NingXia.
3. The context-ranking arrow is weaker than local cancellation arrows.
4. ANCHOR_CV_V1 is not uniquely informative beyond adjacent MAE/RMSE.
5. Raw-scale normalization can substantially harm or reverse ranking.
6. Naive acquired-feature fusion harms IXI calibration.
7. Examination scores do not localize the worst physical plane.
8. No reliability score is universally best across cohorts/budgets.
9. Retrospective densification is not prospective acquisition optimization.

New Plan7 falsifications will be appended with experiment ID, frozen rejection rule, evidence path, and manuscript consequence.

## P7-CV-E01 — Influence-aware context selection failed the method gate

- Frozen rule: choose the minimum neural-influence context among four candidates with overlap count exactly one; no target error enters selection.
- Positive local result: fastMRI confirmation Spearman was 0.986/0.965 for HAT/SwinIR.
- Transfer failure: IXI minimum-influence correlations 0.973/0.977 were below random-context expectation 0.983/0.983 and output PC 0.994/0.994. NingXia showed no stable advantage over random expectation or adjacent MAE.
- Boundary: Plan6 neural influence is identically zero for zero-overlap pairs, so it cannot rank the minimum-overlap family without a new definition.
- Decision: P7-CV-H01 is falsified as a general capability. Shared influence remains an explanatory variable, not a promoted context-selection method.
- Evidence: `outputs/p7_cvpr_influence_context_selection*`.

## P7-CV-E03 — Multi-anchor jackknife dispersion failed locked evaluation

- Development-only selection chose residual IQR for its conditional association beyond adjacent MAE/scale/spacing.
- On fastMRI confirmation, its error-ranking Spearman fell to 0.399 versus 0.944 for adjacent MAE; the paired delta interval excluded zero against the new score.
- IXI/NingXia correlations were 0.732/0.310 versus adjacent MAE 0.956/0.973. Conditional associations were negative or uncertain.
- Decision: P7-CV-H02 is falsified. Do not promote upper-tail/dispersion variants or tune a weighted fusion on these cohorts.
- Evidence: `outputs/p7_cvpr_multi_anchor_jackknife*`.

## P7-CV-E04 — Covariance-derived influence residualization failed the method gate

- `INFLUENCE_RESIDUAL_V1` used the zero-fit correction `median_context[d / sqrt(1 - clip(I,0,0.95))]`, frozen from the paired-error covariance model before inspecting outcomes.
- On fastMRI confirmation, HAT tied raw disagreement and SwinIR decreased by 0.014 Spearman; output PC remained as good or better.
- IXI gains over raw disagreement were only 0.0011/0.0006 and their clustered intervals crossed zero. NingXia HAT decreased by 0.0011 and intervals were wide.
- Decision: do not promote or retune the correction. Continuous shared influence remains explanatory evidence, not a universally superior reliability correction.
- Evidence: `outputs/p7_cvpr_influence_residualization*`.

## P7-TMI-E02 — Prespecified spectral-family explanation was not coherent

- The proposed ordering—stronger consensus blindness for intensity/low-frequency endpoints than structural/high-frequency endpoints—changed sign across cohorts.
- IXI showed the opposite contrast for both models (about -0.068 and -0.074, intervals below zero), while NingXia point estimates were positive (about +0.063/+0.064) and fastMRI was uncertain.
- Decision: endpoint heterogeneity remains real, but do not claim metric independence or a universal spectral law.
- Evidence: `outputs/p7_tmi_metric_endpoint_effects.csv`, `outputs/p7_tmi_metric_family_contrast.csv`.

## P7-CV-E02 — Influence is perturbation-stable but not plane-invariant

- The full central-plane grid covers 0.5/1/2% amplitude, positive/negative sign, Rademacher/Gaussian fields and 1/2/4/8 directions for HAT/SwinIR on fastMRI, IXI and NingXia.
- All 42 nonbaseline condition–stratum ranks pass the frozen gate; minimum stability is .942. This rejects the simple “one perturbation seed/scale artifact” criticism.
- Across three physical planes, pairwise rank stability is .779–.954. Only central–late passes in all six strata; early–central reaches .85 in 4/6 and early–late in 3/6. The broader plane-invariance hypothesis is falsified.
- Decision: retain finite differences as a local mechanism probe at a declared plane; prohibit global/plane-invariant attribution wording. NingXia fixed-count mixed/null evidence remains unchanged.
- Evidence: `outputs/p7_cvpr_neural_influence_stability.json`, `p7_cvpr_neural_influence_stability_summary.csv`, and `p7_cvpr_neural_influence_plane_rank_stability.csv`.
