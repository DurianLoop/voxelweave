# Hypothesis Portfolio — Plan 4 Final State

| ID | Hypothesis | Decisive evidence | Falsification result | Status |
|---|---|---|---|---|
| P4-H01 | Shared error-generating measurements suppress disagreement observability | Zero vs maximal shared anchors on identical targets: Δrho 0.355 and 0.193; both clustered CIs >0; four neural cohort×model replications; analytical replication | Not falsified. Raw magnitude alternative rejected on fastMRI. Ordinary zero-overlap PC can already be equally good, so scope is conditional rather than universal | **SUPPORTED / CENTRAL** |
| P4-H02 | A universal curvature–spacing law predicts neural interpolation error | Held-out fastMRI fitted model improves over spacing-only; no-fit NingXia rho 0.606 | Universal form falsified: calibration fails cross-domain; theory term loses to anchor change on fastMRI | **PARTIAL / SUPPORTING** |
| P4-H03 | Acquired-anchor intrinsic difficulty is a portable standalone estimator | Adjacent-anchor and curvature features predict error in all cohorts | Rankings and normalization are domain dependent; no single proxy dominates | **PARTIAL** |
| P4-H04 | Shared deterministic failure is compatible with conditional-central-tendency bias | 81–87% shared MSE, cross-model error rho >0.96, ambiguity literature | Existing data do not identify a conditional distribution or directly prove mean regression | **PLAUSIBLE, NOT CLAIMED AS CAUSAL** |
| P4-H05 | A two-component estimator must beat strong PC baselines | IGC is deployable and highly predictive | It does not beat ordinary x2–x4 PC; arbitrary fusion already failed | **FALSIFIED AS CURRENT METHOD** |
| P4-H06 | Disjoint disagreement can guide prospective densification at no extra acquisition cost | It predicts x4→x2 benefit strongly | Two x4 phases already equal the x2 acquisition budget; prospective claim is circular | **WITHDRAWN** |

## Surviving scientific contribution

**Failure:** deterministic reconstructors share 81–87% of their squared error, so agreement can remain high when all are wrong.

**Mechanism:** when reliability contexts reuse measurements that induce the same reconstruction bias, the corresponding error directions remain correlated and disagreement loses observability.

**Intervention:** preserve the physical target while changing the supporting acquired slices; compare phase-shifted, measurement-disjoint grids against a maximal-shared-anchor control.

**Prediction:** disjoint contexts should reveal target error more faithfully even when they do not create a larger raw perturbation.

**Result:** the prediction survives exact paired tests, case-cluster bootstrap, two cohorts, two neural architectures, and two analytical interpolators.

**Methodological consequence:** reliability interventions should be designed and reported by error-direction independence / measurement overlap, not raw output diversity alone. The phase-grid protocol is a controlled stress test for consensus blindness, not a universal deployment replacement.

