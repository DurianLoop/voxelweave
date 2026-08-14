# TMI Error and Reliability Taxonomy

Status: Plan6 evidence-backed taxonomy, 2026-08-13.  
Scope: MRI inter-slice interpolation only. Categories below are supported by stored experiments; they are not diagnostic labels or prospective clinical event rates.

## Statistical units

- fastMRI: 24 independent examinations.
- IXI: 115 independent examinations.
- NingXia: 22 series nested in eight independent patients; all confidence intervals and prevalence statements use patient clustering.
- Pixel and plane examples are localization evidence only. They do not create extra independent patients.

## 1. Stable consensus error

Definition: two deterministic reconstructions have aligned target errors, so their average error is large while their difference is small.

Observable signature:

- high error cosine and shared-error fraction;
- low observable fraction and normalized disagreement;
- weak protection from agreement alone.

Evidence:

- Across three cohorts, two architectures and both disjoint/max-shared conditions, shared fraction was negatively associated with normalized disagreement after controlling total error and examination (`rho=-0.746` to `-0.975`; P6-E02).
- Under a strict pooled plane rule (top-quartile MAE and bottom-quartile disagreement), stable-wrong prevalence was rare: `0–0.32%` for fastMRI/IXI and `2.42–3.23%` for NingXia max-shared conditions. The mechanism is strong; the strict event is not common enough to call a frequent clinical failure.

Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e02_*`.

## 2. Measurement-sharing blindness

Definition: reliability estimates share acquired physical anchors or neural response directions, inducing correlated reconstruction errors that cancel in the difference.

Observable signature:

- max-shared contexts have higher error alignment and shared fraction;
- their disagreement–error ranking is worse than measurement-disjoint contexts;
- ordinary prediction diversity can remain nonzero but uninformative.

Evidence:

- With one independent HAT/SwinIR x4 error endpoint, measurement-disjoint nAURC was `0.0119/0.0013/0.0107` versus max-shared `0.0684/0.0139/0.0306` on fastMRI/IXI/NingXia (P6-E12).
- A common per-case normalization preserved the positive disjoint-minus-shared ranking difference in all six dataset–architecture strata (P6-E03).

Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e03_*`, `p6_e12_*`.

## 3. Factor-amplified consensus blindness

Definition: larger through-plane gaps increase reconstruction error while two estimators become proportionally more aligned, making absolute disagreement deceptively stable or smaller.

Observable signature:

- error increases from x2 to x6;
- shared fraction increases and observable fraction decreases;
- disagreement–error ranking weakens.

Evidence from a definition-matched analytical estimator pair:

| Cohort | Shared fraction x2→x4→x6 | Reliability rho x2→x4→x6 |
|---|---:|---:|
| fastMRI | 0.843→0.940→0.953 | 0.955→0.833→0.798 |
| IXI | 0.750→0.886→0.923 | 0.961→0.947→0.947 |
| NingXia | 0.860→0.933→0.953 | 0.937→0.830→0.818 |

Boundary: this is analytical-estimator factor evidence. It does not substitute for missing IXI neural x2/x6 outputs.

Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e11_*`.

## 4. Structural-metric mismatch

Definition: pixelwise disagreement ranks intensity, gradient or frequency error but need not rank structural similarity error.

Observable signature:

- strong MAE/RMSE/MSE ranking;
- weak or reversed SSIM-error association in some cohorts;
- endpoint-dependent conclusions.

Evidence:

- All 42 disjoint-minus-shared point differences across seven endpoints were positive.
- SSIM error had weak or negative absolute association in fastMRI/NingXia, with intervals crossing zero; some smaller gradient/high-frequency strata were also uncertain.

Interpretation: measurement disjointness is broadly useful but not metric-free. A low pixel discrepancy cannot certify structural fidelity.

Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e01_*`.

## 5. Intensity-scale confounding

Definition: examination-level error and disagreement ranks are partly driven by raw dynamic range; normalization changes the estimand.

Observable signature:

- raw common-scale ranks differ materially from pooled common-scale ranks;
- independently normalizing each prediction changes relative calibration further.

Evidence:

- Raw HAT–SwinIR disagreement versus error rho was `0.923/0.957/0.874` on fastMRI/IXI/NingXia.
- A shared case scale reduced these to `0.784/0.256/0.239` and strongly changed IXI/NingXia ranks.
- The overlap mechanism direction remained intact after a single shared transform, separating the mechanistic contrast from absolute triage calibration.

Valid operating rule: compare outputs on their raw common physical scale or after exactly the same case transform. Separate per-output normalization is a sensitivity analysis, not a calibrated reliability score.

Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e03_*`.

## 6. Boundary and local-context failure

Definition: limited support near the volume boundary or concentrated local anatomy produces high plane error not represented by a global examination score.

Evidence:

- Existing Plan3 boundary-position and context-geometry panels show position-dependent error/inconsistency and NingXia stable-wrong examples.
- Plan6 failure exemplars show that examination-level Anchor-CV and PC cannot localize the worst physical plane.

Interpretation: examination triage and plane localization are separate tasks. Global scores should not be advertised as voxel- or lesion-level uncertainty.

Trace: `plan3_outputs/boundary_position_per_plane.csv`, `plan3_outputs/context_geometry_per_plane.csv`, `CVPR/CVPR_UPGRADE/outputs/plan6_failure_taxonomy_*`.

## 7. Benign diversity

Definition: two predictions differ substantially even though both have moderate error, so high disagreement over-ranks the case.

Observable signature:

- high disagreement / low error quadrant;
- low error cosine or opposing residual directions;
- diversity without corresponding risk.

Evidence:

- Theory gives `||e_a-e_b||² = ||e_a||² + ||e_b||² - 2<e_a,e_b>`; large diversity may arise from the inner-product term without large individual error energy.
- Multi-endpoint and risk-coverage curves contain high-disagreement cases that do not remain high-risk under the independent endpoint.

Interpretation: diversity is not reliability by itself; both shared-error cancellation and harmless diversity prevent a one-to-one mapping.

## 8. Cohort-specific input-baseline dominance

Definition: an acquired-input difficulty statistic can outperform output disagreement because it exposes global through-plane change without dependence on a particular prediction pair.

Evidence:

- In NingXia, adjacent-anchor MAE nAURC (`0.0070`) was lower than measurement-disjoint (`0.0107`), committee (`0.0504`) and max-shared (`0.0306`).
- Anchor-CV was statistically indistinguishable from adjacent MAE/RMSE and did not retain unique information after scale/direct-difference control.

Interpretation: TMI should claim the reliability consequence of measurement dependence, not universal superiority over all acquired-input baselines.

## 9. Practical taxonomy for qualitative panels

Every final qualitative panel should use the following four mutually interpretable cells under one fixed dataset/model normalization:

1. high disagreement / high error — correctly flagged difficult case;
2. high disagreement / low error — benign diversity or over-ranking;
3. low disagreement / high error — stable consensus error / blindness;
4. low disagreement / low error — correct stable agreement.

Panels must report dataset, case, patient cluster, model(s), factor, physical plane, score percentile and error percentile. Selection is performed from frozen tabular results before visual inspection. No panel may be used to estimate prevalence.

## 10. Claim boundary

The evidence supports: measurement dependence controls how much reconstruction error is observable through disagreement, and disjoint construction often improves retrospective ranking.

The evidence does not support:

- low disagreement as a correctness certificate;
- universal superiority over input-derived difficulty scores;
- pixelwise/lesion-level clinical uncertainty;
- a prospective acquisition policy;
- 22 NingXia series as 22 independent patients;
- metric-independent reliability across all structural endpoints.
