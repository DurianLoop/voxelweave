# CVPR Plan6 claim traceability

Status: final internal scientific audit, 2026-08-13. Paths are relative to this `PAPER/` directory.

| Manuscript claim | Experiment / decision | Independent unit and coverage | Evidence artifact | Allowed wording / boundary |
|---|---|---|---|---|
| Clean measurement sharing hides reconstruction error | C5-E003/E005/E010 | fastMRI 24 examinations; IXI 115 examinations; NingXia 8 patients / 22 series | `../outputs/clean_max_overlap*_summary.json`; `../outputs/stable_wrong_prevalence.json` | Three-cohort controlled association; do not call low disagreement correctness. |
| Overlap count is associated but not a sufficient dose | C5-E012/E013 | compact ladder: all three cohorts; wide ladder: IXI + NingXia | `../outputs/*four_anchor_overlap_ladder_summary.json` | State the repeated 0→1 nonmonotonicity; no monotone count law. |
| Finite-difference neural shared influence explains paired-error geometry better than count | P6-E04 | 24/115/22 cases or series, clustered 24/115/8; HAT + SwinIR; 72/345/66 planes per model | `../outputs/plan6_neural_shared_influence_confirm3*`; `figures/plan6_neural_influence_forest.pdf` | All 18 primary advantages positive with clustered CIs above zero; raw disagreement is supporting and fastMRI intervals cross zero. |
| Influence contains information beyond count in a clean fixed-count design | P6-E04B | same cohorts/models; four contexts with overlap count exactly one | `../outputs/plan6_fixed_overlap_ladder.*` | Confirmed on fastMRI and IXI; NingXia null/mixed. Never claim universal three-cohort confirmation. |
| Local influence→alignment→disagreement cancellation chain is supported | P6-E05 | all three cohorts and both models; clustered by examination/patient | `../outputs/plan6_mechanism_chain*` | All 18 local-arrow CIs exclude zero. Describe conditional association, not causal mediation. |
| The context-level ranking consequence is partial | P6-E05 | eight non-self contexts per cohort/model | `../outputs/plan6_mechanism_chain_context_ranking.csv` | Expected point direction in all strata; supported in IXI both models and NingXia HAT only. |
| Frozen Anchor-CV ranks x4 case error but is not uniquely informative | P6-E06 | fastMRI 24; IXI 115; NingXia 8 patients / 22 series | `../outputs/plan6_anchor_cv_explanation*`; `figures/plan6_anchor_cv_audit.pdf` | Report ρ=.943/.955/.958 and exact reproduction; adjacent MAE/RMSE indistinguishable; reject unavailable-information claim. |
| Raw scale and simple adjacent change explain much of Anchor-CV | P6-E06 | same three cohorts | `../outputs/plan6_anchor_cv_baseline_deltas.csv`; `../outputs/plan6_anchor_cv_explanation_summary.csv` | Partial ρ=.333/−.059/−.100; scale normalization harms. No universal curvature explanation. |
| Examination difficulty dominates architecture choice | P6-E08 | HAT + SwinIR x4, all cohorts | `../outputs/plan6_intrinsic_difficulty_variance.csv` | Case SS fraction 99.1/99.99/99.78%; limited to evaluated architectures/factor. |
| Anchor-CV predicts held-out examination difficulty; feature stacking fails | P6-E08 | leave-one-examination/patient-cluster-out | `../outputs/plan6_intrinsic_difficulty_loco.csv` | Anchor-only ρ=.939/.954/.953; do not promote fusion. |
| Frozen x4 risk ranking has no universal winner | P6-E07A | all cohorts, both models, every retained-case prefix | `../outputs/plan6_frozen_risk_coverage*`; `figures/plan6_frozen_risk_coverage.pdf` | Output PC best nAURC fastMRI/IXI; adjacent best NingXia. Anchor-CV is useful, not SOTA. |
| Frozen score predicts retrospective x4→x2 benefit | P6-E07B | permitted two-dataset pair: fastMRI 24 + IXI 115 | `../outputs/plan6_ixi_x2_consequence*`; `../../../IXI_X2_FROZEN_EVALUATION.md`; `figures/plan6_ixi_x2_budget.pdf` | All 10/20/30/50% gains positive. IXI endpoint is cross-estimator and retrospective, not a causal acquisition effect. |
| Anchor-CV and output PC have complementary rare failures but no justified fusion | P6-E09 | 48/230/44 architecture-cases | `../outputs/plan6_failure_taxonomy*`; `figures/plan6_failure_exemplars.pdf` | Keep granularity boundary: examination triage, not plane localization. |
| Anchor-CV has a verified computational advantage | P6-E10 | representative deterministic case per cohort; RTX 5090 D v2; CPU repeats | `../outputs/plan6_efficiency.*` | 0 neural calls, .42–3.97 ms, zero output storage; this is cost superiority, not accuracy superiority. |

## Prohibited or rejected claims

- No causal mediation, prospective acquisition optimization, clinical safety, calibrated posterior uncertainty, universal overlap-count law, local error-map localization, or universal score superiority.
- NingXia uses eight patient clusters, never 22 independent patients.
- IXI x4→x2 is a frozen cross-estimator consequence test; do not describe it as a same-model treatment effect.
- Prior art prevents “first consensus blindness” and “first leave-one-slice-out” claims. The novelty is the physical overlap intervention, nonlinear neural shared-influence measurement, controlled fixed-count test, and scoped frozen capability audit.

## PDF mapping

- Main paper: `main.pdf`, eight content pages plus references.
- Complete detail: `supplement.pdf`, five pages, with full architecture strata, CIs, negative results, and reproducibility map.
- Experiment narrative: `NEW_EXPERIMENTS.md`.
- Page justification: `PAGE_GROWTH_LEDGER.md`.
