# CVPR final-candidate claim traceability

Status: Plan7 final scientific candidate, 2026-08-14. Paths beginning `../../../PLAN7_ACCEPTANCE_OPTIMIZATION/` refer to the Plan7 workspace.

| Manuscript claim | Experiment | Unit and coverage | Evidence artifact | Allowed wording / boundary |
|---|---|---|---|---|
| Integer overlap count is not a monotone influence law. | Plan6 analytical ladders | compact three-cohort and wider IXI/NingXia grids | `../outputs/*overlap_ladder*` | Count is insufficient; do not claim overlap is irrelevant. |
| Neural shared influence explains error geometry more strongly than count on broad grids. | P6-E04 | fastMRI 24, IXI 115, NingXia 8 patients/22 series; HAT/SwinIR; three planes | `../outputs/plan6_neural_shared_influence_confirm3*` | All 18 primary advantages positive with clustered CIs above zero under the frozen perturbation. |
| Continuous influence remains informative when count equals one. | P6-E04B | four overlap-one contexts, all cohorts/models | `../outputs/plan6_fixed_overlap_ladder.*` | Supported on fastMRI/IXI; NingXia mixed/null. No universal claim. |
| Influence→alignment→cancellation/observable fraction is supported locally. | P6-E05 | plane–context observations clustered by examination/patient | `../outputs/plan6_mechanism_chain*` | Conditional association, not causal mediation. Context-ranking arrow is heterogeneous. |
| Neural influence is stable to perturbation parameters at a declared plane, but not plane-invariant. | P7-CV-E02 | 42 perturbation-condition strata; 18 plane-pair strata | `../../../PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_cvpr_neural_influence_stability*`, `p7_cvpr_neural_influence_plane_rank_stability.csv` | All parameter strata pass, minimum .942; plane pairs span .779–.954 and two of three gates fail. |
| Minimum-influence context selection provides a new capability. | P7-CV-E01 | fastMRI split; IXI/NingXia transfer | `../../../PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_cvpr_influence_context_selection*` | FALSIFIED; IXI below random/PC, NingXia heterogeneous. |
| Multi-anchor jackknife adds beyond adjacent MAE. | P7-CV-E03 | development freeze, confirmation and transfer | `../../../PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_cvpr_multi_anchor_jackknife*` | FALSIFIED; no retuning. |
| Influence residualization improves ranking. | P7-CV-E04 | zero-fit correction, confirmation/transfers | `../../../PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_cvpr_influence_residualization*` | FALSIFIED; changes negligible/inconsistent. |
| Anchor-CV is cheap and strongly ranks difficulty, but is not unique. | P6-E06/E10 | three cohorts, measured representative cost | `../outputs/plan6_anchor_cv_explanation*`, `plan6_efficiency.*` | Cost advantage only; adjacent MAE/RMSE statistically competitive. |
| No universal reliability-score winner exists. | P6-E07A | every retained prefix, both models, all cohorts | `../outputs/plan6_frozen_risk_coverage*` | Output PC wins fastMRI/IXI nAURC; adjacent wins NingXia. |
| Frozen scores retrospectively rank x4→x2 benefit. | P6-E07B | fastMRI 24 + IXI 115 | `../outputs/plan6_ixi_x2_consequence*` | Retrospective value-of-densification only, not prospective acquisition optimization. |

## Prohibited claims

No superior uncertainty estimator, calibrated posterior uncertainty, causal mediation, universal count law, prospective acquisition policy, clinical safety, local error-map localization, or “first” wording. NingXia always uses eight independent patient clusters. The reviewer memory target is: **measurement count is not estimator influence, and explaining disagreement blindness does not automatically solve reliability ranking.**

## Submission mapping

- Main: `main.tex` / `main.pdf` (eight content pages plus references).
- Detail: `supplement.tex` / `supplement.pdf`.
- Internal risk and responses: `REVIEWER_RISK_AUDIT.md`, `REBUTTAL_BANK.md`.
