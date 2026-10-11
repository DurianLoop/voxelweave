# TMI Claim Traceability

| Claim | Evidence | Dataset coverage | Status / allowed wording |
|---|---|---|---|
| Shared error suppresses observable disagreement | P6-E02 partial correlations −0.746 to −0.975 | fastMRI + IXI + NingXia | Supported conditionally; association, not causal mediation |
| Disjoint measurement support improves intensity-error ranking | P6-E01 MAE/RMSE/MSE/low-frequency; P6-E12 risk curves | all three | Supported for tested deterministic interpolators |
| Effect is not MAE-only | 42/42 endpoint differences positive | all three | Direction supported; do not claim universal absolute endpoint utility |
| Pixelwise disagreement ranks SSIM error | P6-E01 SSIM rows | all three | **Rejected universally**; useful only on IXI in this evidence |
| Physical matching is exact | P6-E03, 322 output volumes | all three | Supported for stored outputs and tested tolerances |
| Result survives normalization | P6-E03 common transform | all three | Direction survives one common transform; triage ranks are scale dependent |
| Independent output normalization is valid | P6-E03 independent strategy | all three | **Rejected** |
| Increasing factor strengthens consensus blindness | P6-E11 monotone x2/x4/x6 trends | all three | Supported for analytical estimators only |
| Measurement-disjoint is the best reliability score | P6-E12 | all three | **Rejected universally**; best tested output score, adjacent wins NingXia |
| Stable-wrong failures are common | P6-E02 prevalence | all three | **Rejected**; coherent but rare, wide NingXia intervals |
| Disagreement certifies correctness when low | Algebra + stable-wrong examples | all three | **Rejected categorically** |
| Architecture diversity removes shared difficulty | P6-E08 case variance | all three | **Rejected**; case error ranks 0.989/1.000/0.997 |
| Retrospective score predicts x4→x2 benefit | P6-E07 frozen budgets | IXI + fastMRI | Supported as cross-estimator case-level prediction only |
| Prospective acquisition benefit / clinical safety | none | none | **Not supported** |
| Consensus blindness or leave-one-out is itself novel | Hu 2021; Horváth 2017 | literature | **Not novel** |
| Novel contribution | paired physical measurement-overlap intervention + three-cohort characterization | all three | Defensible scoped novelty |

## Manuscript anchors

- Central formulation: `Theory: Consensus Error and Disagreement Blindness`; `Measurement-Overlap Hypothesis`.
- Main controlled evidence: `Controlled Measurement-Overlap Intervention`; `Three-Cohort Multi-Endpoint Robustness`.
- Mechanism characterization: `Consensus Energy and Disagreement Suppression`; `Analytical Factor Response`.
- Validation controls: `Physical Geometry and Intensity Operating Range`.
- Deployment consequence: `Complete Examination-Level Risk–Coverage`; `Retrospective Densification Consequence`.
- Negative evidence: `Failure Boundary and Negative Results`; `Threats to Validity and Falsification Logic`.
- Novelty boundary: `What Is and Is Not Novel`.

## Prohibited wording

- “Calibrated uncertainty,” “guarantees correctness,” “clinically safe,” “prospectively improves acquisition,” “universally superior,” “first leave-one-slice-out method,” or “first demonstration that uncertainty misses systematic error.”
- NingXia must be described as eight independent patient groups / 22 series, never as 22 independent patients.
- IXI x2 consequence must state the cross-estimator HAT/SwinIR x4 versus I3Net x2 endpoint.
