# TMI final-candidate claim traceability

Candidate: `TMI_MANUSCRIPT_SUBMISSION_FINAL/main.tex`, compiled 2026-08-13.

| Manuscript claim | Experiment/evidence | Independent unit | Exact artifact | Boundary |
|---|---|---|---|---|
| Disjoint contexts improve error ranking over maximal sharing | Original all-plane intervention + P6-E01 | 24 fastMRI exams; 8 NingXia patients; 115 IXI exams in balanced analysis | `../TMI_MANUSCRIPT_MASTER/experiments/p6_e01_metric_robustness_*`; inherited frozen all-plane outputs | Reversal also changes order; directional paired intervention, not pure causal coefficient. |
| All 42 endpoint point differences are positive | P6-E01 | Examination/patient cluster | `p6_e01_metric_robustness_summary.csv` | Correlated rows are not 42 independent replications; SSIM utility is weak. |
| Shared fraction suppresses normalized disagreement | P6-E02 | Examination/patient cluster with subordinate planes | `p6_e02_consensus_failure_associations.csv` | Target-dependent retrospective diagnostic; not deployable calibration or causal mediation. |
| Stable-wrong events are possible but rare | P6-E02 | Examination/patient cluster | `p6_e02_stable_wrong_prevalence.csv` | Strict pooled quartiles; not a clinical incidence estimate. |
| Factor increase raises shared fraction and lowers reliability | P6-E11 | Examination/patient cluster | `p6_e11_analytic_factor_summary.csv`, `p6_e11_analytic_factor_trends.csv` | Analytical two-anchor estimators; not neural x6 evidence. |
| Geometry matches and common scaling preserves paired direction | P6-E03 | 322 output volumes / cluster inference | `p6_e03_geometry_per_output.csv`, `p6_e03_intensity_summary.csv` | Per-case scaling changes cross-case ranks; absolute threshold is not transferable. |
| Disjoint has lower nAURC than shared/committee, adjacent wins NingXia | P6-E12 | 24/115/8 clusters | `p6_e12_risk_summary.csv`, `p6_e12_risk_full_curves.csv` | One frozen MAE endpoint and examination aggregation. |
| At 70% IXI coverage disjoint retains 0/29 high-error exams vs 2/1/3 | P7-TMI-E01 | 115 IXI exams; 24 fastMRI exams; 8 NingXia patients | `../../../PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_tmi_operational_false_retention*.csv` | Benefit concentrated at intermediate coverage; technical QA only. |
| No universal endpoint-frequency ordering | P7-TMI-E02 | 24/115/8 clusters | `p7_tmi_metric_endpoint_effects.csv`, `p7_tmi_metric_family_contrast.csv` | Prespecified low-frequency hypothesis falsified and retained. |
| Operating regime depends on available measurements and outputs | P6-E10 + P6-E12 + P7-TMI-E03 | Representative timing exam per cohort; full-cohort reliability | `p7_tmi_reliability_compute_tradeoff.csv`, `plan6_efficiency.csv` | Latency is hardware/example-specific; acquisition cost is not GPU latency. |

## Prohibited claims

- No new correlated-error identity.
- No uncertainty calibration, correctness certificate, diagnostic validation, patient-safety effect, universal best score, prospective acquisition optimizer, or universal frequency mechanism.
- No “first” wording.

