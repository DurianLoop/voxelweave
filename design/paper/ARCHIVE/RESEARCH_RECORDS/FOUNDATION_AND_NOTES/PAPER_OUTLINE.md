# Paper Outline

## Working title

When Consistency Reveals Error—and When It Cannot: Physical Sampling-Context Tests for Deterministic MRI Interpolation

## Central message

For two reconstructions of the same physical plane, their distance is a ground-truth-free lower-bound witness on at least one reconstruction error. Physical sampling-factor changes make this witness empirically useful in two T2-brain cohorts, but shared stable errors remain invisible. The paper is about the mechanism and its boundary, not universal uncertainty calibration.

## Abstract structure

- Problem: deterministic interpolation has no deployment-time target and agreement is often overinterpreted.
- Principle: triangle inequality gives a one-sided error witness under target-preserving interventions.
- Method: frozen world-coordinate cross-factor consistency, with no learned uncertainty head.
- Evidence: 8-case derivation, 16-case held-out fastMRI confirmation, 22-case NingXia OOF replication, three architectures, 2,424 confirmation/replication planes.
- Main localization results: fastMRI pixel 0.693, slice 0.799, case-pair 0.915, top-decile enrichment 2.49x; NingXia 0.489, 0.727, 0.883, 2.06x, with case-clustered intervals.
- Boundary: blur and natural first-generated-plane failures prove that consistency cannot certify correctness; intensity scale materially affects raw scores.

## 1. Introduction

- Distinguish error witnessing from calibrated uncertainty and from accuracy certification.
- Motivate physical sampling context as a target-preserving intervention.
- State contributions: formal one-sided principle, multi-granularity replication, controlled and natural failure regimes, and corrected case-level evaluation.

## 2. Related work

- Probabilistic MRI reconstruction and learned error prediction.
- Ensemble/TTA/perturbation consistency.
- No-reference IQA and selective prediction.
- Exact distinction: same reconstructor, same world plane, physically meaningful acquisition-context change, plus explicit impossibility of the reverse inference.

## 3. Method and guarantee

- Define matched physical plane, factor contexts, pixel/plane/examination aggregation, and `PC-v1-FROZEN`.
- Prove `d(f_a,f_b) <= d(f_a,y)+d(f_b,y)` and hence `max(e_a,e_b) >= d(f_a,f_b)/2`.
- State assumptions and non-guarantees, including intensity representation.

## 4. Experimental governance

- Two cohorts, three architectures, factors 2/4/6.
- Derivation/confirmation split and NingXia OOF replication.
- Examination-clustered bootstrap/permutation; complete risk-coverage curves.
- Geometry and provenance audits.

## 5. Results

- Multi-granularity localization confirmation and replication.
- Examination-level ranking, with the fastMRI/NingXia distinction.
- Profile and factor-pair heterogeneity.
- Comparison with committee and limited TTA.

## 6. Falsification and boundaries

- Common-mode blur: error rises as both disagreement scores fall.
- Fourteen natural NingXia consistent-but-wrong planes, concentrated at x4-x6 first generated planes.
- Raw intensity scale confounding and exploratory shared-range normalization.
- Why low consistency is not a safety certificate.

## 7. Discussion and limitations

- Interpretation as an error witness, not calibrated uncertainty.
- T2 brain only; no untouched site/anatomy, reader study, downstream endpoint, or decisive multi-architecture TTA comparison.
- Stored multi-factor outputs or extra inference are required.

## 8. Conclusion

State the one-sided scientific principle and its observed scope; do not claim universal deployment superiority or clinical benefit.

