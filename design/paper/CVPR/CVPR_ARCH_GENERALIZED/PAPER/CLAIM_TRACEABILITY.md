# Claim Traceability — CVPR Recovered

| Final claim | Main-paper location | Evidence source | Boundary carried with claim |
|---|---|---|---|
| Measurement-disjoint same-target contexts rank error better than dependence-preserving controls across evaluated cohorts | Abstract; Sec. 5.1; Fig. 2 | `CVPR/CVPR_UPGRADE/outputs/clean_max_overlap_summary.json`, `clean_max_overlap_ixi_summary.json` | Controlled interpolation setting only; NingXia has eight patient clusters |
| Clean sharing leaves only .25–2.61% of paired error energy observable | Sec. 5.1; Fig. 2 | Same clean-control outputs; error decomposition identity | Paired-error decomposition, not calibrated uncertainty |
| Integer overlap is not a sufficient monotone dose | Sec. 5.2 | `compact_four_anchor_overlap_ladder_*`, `plan6_fixed_overlap_ladder.*` | Analytical design; broad trend remains strong despite 0→1 reversal |
| Analytical coefficient influence explains error geometry better than count | Sec. 5.2 | `shared_influence_summary.json`, `shared_influence_per_case_config.csv` | Linear estimator result, not proof of neural behavior |
| Local neural shared influence improves on count in all broad-grid cohort–architecture strata | Abstract; Sec. 5.2; Fig. 3 | `plan6_neural_shared_influence_confirm3_summary.csv` and per-cohort JSON/CSV | Grid varies span/asymmetry; controls applied; direct disagreement is supporting only on fastMRI |
| Beyond-count influence is supported on fastMRI/IXI but not NingXia | Abstract; Sec. 5.2; Supplement Table 4 | `plan6_neural_shared_influence_confirm3_*_per_case_config.csv`; fixed-count analysis | NingXia estimates are null/mixed with all intervals crossing zero |
| Local influence→alignment→cancellation/observability chain is supported | Sec. 5.3 | `plan6_mechanism_chain_summary.csv` | Conditional associations, not causal mediation; context-ranking arrow supported in only 3/6 strata |
| Influence is local rather than plane-invariant | Sec. 5.3 | `PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_cvpr_neural_influence_stability*`, `p7_cvpr_neural_influence_plane_rank_stability.csv` | 42 perturbation strata pass, 2/3 plane gates fail |
| Anchor-CV provides a simple acquired-only examination difficulty signal | Abstract; Sec. 5.4; Fig. 4 | `plan6_anchor_cv_explanation.json`, `plan6_efficiency.*` | Not novel as a holdout operation; not uniquely informative; does not localize worst plane |
| Anchor-CV tracks retrospective densification benefit on fastMRI/IXI | Sec. 5.4; Fig. 4 | `plan6_ixi_x2_consequence_correlations.csv`, `plan6_ixi_x2_consequence_budgets.csv` | Retrospective and cross-estimator on IXI; no prospective scanner utility claim |
| No evaluated score universally dominates | Sec. 5.4; Discussion; supplement | Anchor-CV, frozen risk–coverage, and consequence tables | Output PC/adjacent MAE are stronger in several strata/budgets |

## Forbidden inference map

- “Plane-invariant global model influence” is contradicted by the plane audit.
- “Universal cohort-level beyond-count law” is contradicted by NingXia fixed-count results.
- “Anchor-CV is superior/unique” is contradicted by adjacent MAE/RMSE and output PC.
- “Local uncertainty localization” is contradicted by the failure taxonomy/localization audit.
- “Calibrated uncertainty” is not evaluated.
- “Prospective acquisition benefit” is not evaluated.

No sentence in the final main paper or supplement should imply any of the above.
