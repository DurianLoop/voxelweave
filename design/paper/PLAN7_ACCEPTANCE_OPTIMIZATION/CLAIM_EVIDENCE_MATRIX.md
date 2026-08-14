# Plan7 claim–evidence matrix

Last updated: 2026-08-14. “Supported” means the cited artifact directly tests the stated scope; it does not imply clinical validity or universality.

## TMI

| Claim | Direct evidence | Scope / independent unit | Status and allowed wording |
|---|---|---|---|
| Reusing the same physical slice measurements can align errors and make deterministic interpolators agree while wrong. | Plan6 controlled max-shared/disjoint analyses; `TMI/.../figures/fig1_concept.pdf`; Plan7 novelty audit | fastMRI 24 exams, IXI 115 exams, NingXia 8 patients/22 series | SUPPORTED as an MRI interpolation mechanism; algebra itself is not claimed novel. |
| The phenomenon survives multiple error endpoints, but strength depends on endpoint and cohort. | `outputs/p7_tmi_metric_endpoint_effects.csv`; inherited P6-E01 | Seven endpoints, HAT/SwinIR, three cohorts | SUPPORTED; prohibit “metric independent.” |
| Blindness is universally stronger for intensity/low-frequency errors. | `outputs/p7_tmi_metric_family_contrast.csv` | Clustered within-case contrasts | FALSIFIED; sign reverses across cohorts. |
| Shared-context agreement can retain high-error examinations that disjoint ranking would reject. | `outputs/p7_tmi_operational_false_retention*` | Fixed coverage, clustered bootstrap | PARTIAL: clearest on IXI at 70%; sparse elsewhere. Frame as technical QA, not patient safety. |
| Disjoint scoring has a conditional operating regime rather than universal practicality. | `outputs/p7_tmi_reliability_compute_tradeoff.csv`; `p7_tmi_operating_regimes.json` | Full-cohort reliability plus representative measured cost | SUPPORTED: use when complementary reconstructions already exist; adjacent acquired-only score is default when zero calls are required. |
| Closest prior art does not already report this exact controlled chain. | `NOVELTY_COLLISION_AUDIT.md`; `VENUE_CALIBRATION.md` | Ten closest works plus venue sets | SUPPORTED as a scoped distinction, never a “first” claim. |

## CVPR

| Claim | Direct evidence | Scope / independent unit | Status and allowed wording |
|---|---|---|---|
| Integer overlap count is not a sufficient description of measurement dependence. | Plan6 exact overlap ladder and fixed-count analysis | Three cohorts, two architectures | SUPPORTED; count is neither a monotone law nor estimator influence. |
| Neural finite-difference shared influence explains broad-grid error geometry more strongly than count. | Plan6 P6-E04 three-plane outputs and clustered intervals | fastMRI 24, IXI 115, NingXia 8 patient clusters; HAT/SwinIR | SUPPORTED for the frozen perturbation; Plan7 confirms parameter robustness but identifies plane dependence. |
| With overlap fixed to one, influence remains informative universally. | Plan6 fixed-count outputs | Four contexts per dataset/model | PARTIAL: fastMRI/IXI support; NingXia mixed/null. |
| Influence→alignment→cancellation/observable fraction is locally supported. | Plan6 mechanism-chain outputs | Plane–context observations clustered by exam/patient | SUPPORTED as conditional association; not causal mediation. Final context-ranking arrow is heterogeneous. |
| Minimum-influence context selection improves reliability. | `outputs/p7_cvpr_influence_context_selection*` | Development freeze, confirmation and transfer | FALSIFIED: IXI below random expectation/output PC; NingXia heterogeneous. |
| Multi-anchor jackknife contains incremental information beyond adjacent MAE. | `outputs/p7_cvpr_multi_anchor_jackknife*` | Development-selected statistic; locked confirmation/transfer | FALSIFIED. |
| Covariance-derived residualization improves disagreement ranking. | `outputs/p7_cvpr_influence_residualization*` | Zero fitted parameters; locked cohorts/models | FALSIFIED; negligible/inconsistent changes. |
| The paper provides a universally superior reliability estimator. | All Plan6/Plan7 score audits | All evaluated cohorts/models | REJECTED CLAIM. Current contribution is mechanism/findings, not method superiority. |
| Neural influence is stable to amplitude, sign/field, direction count and plane. | P7-CV-E02 | 42 perturbation strata plus 18 plane-pair strata | PARTIAL: all perturbation conditions pass; two of three plane-pair gates fail. |

## Cross-paper constraints

- `SUBMISSION_OVERLAP_AUDIT.md` is authoritative for paragraph/figure/table/experiment separation.
- The TMI paper owns comprehensive MRI imaging-science characterization and operational QA consequences.
- The CVPR paper owns nonlinear response influence, fixed-count tests, the arrow-wise mechanism chain and failed mechanism-derived capability gates.
- Low textual overlap does not remove moderate-to-high scientific overlap; sequence/merge remains a human decision.
