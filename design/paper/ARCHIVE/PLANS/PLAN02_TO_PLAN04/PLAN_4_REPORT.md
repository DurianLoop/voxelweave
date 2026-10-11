# Plan 4 Research Report

## Discovery

Deterministic slice-interpolation error is dominated by a shared component (81–87% in the prior exact decomposition). Agreement therefore observes only a minority of error unless the reliability intervention changes the measurements that support the shared failure.

## Mechanism experiment

For every evaluated target plane, phase-0 (`z=0,4,8,…`) and phase-2 (`z=2,6,10,…`) x4 contexts preserve the same missing target and share no acquired anchors. A maximal-overlap control reverses the same x4 anchor sequence and maps predictions back to physical z. Both comparisons use an identical foreground mask determined only by the phase-0 prediction.

Zero versus maximal overlap, exact case/model/plane pairs:

| Cohort | Planes | Zero rho | Maximal rho | Delta rho | Case-cluster 95% CI |
|---|---:|---:|---:|---:|---:|
| fastMRI | 192 | 0.960 | 0.605 | 0.355 | [0.225, 0.557] |
| NingXia OOF | 248 | 0.891 | 0.699 | 0.193 | [0.111, 0.306] |

Each of HAT and SwinIR replicates separately. On fastMRI the zero-overlap disagreement has only 0.59–0.77× the raw magnitude of the maximal-overlap control, yet is substantially more error-correlated. Thus output diversity magnitude is not the explanation.

## Generalization

- Linear interpolation: case rho 0.977 (fastMRI), 0.958 (NingXia).
- Cubic interpolation: case rho 0.974 (fastMRI), 0.967 (NingXia).
- The mechanism is therefore not restricted to Transformer architecture or learned reconstruction.

## Supporting curvature result

An acquired-anchor curvature–spacing model improved held-out fastMRI prediction over spacing alone (rho 0.722 vs 0.595; R² 0.479 vs 0.329). A no-fit curvature–spacing rank reached rho 0.606 on NingXia, but absolute calibration failed and a simple anchor-change proxy beat it on fastMRI. The universal-law hypothesis is rejected; curvature/spacing remains a supporting mechanism, not the central claim.

## New capability and its boundary

The phase-grid protocol is a controlled stress test for consensus blindness. Its validated design rule is:

> Preserve the target while changing the measurements responsible for the error; optimize error-direction independence, not raw prediction diversity.

The disjoint x4 witness predicted realized x4→x2 benefit (case/model rho 0.811 fastMRI; 0.626 NingXia), but prospectively acquiring both phases already costs an x2 grid. That adaptive-acquisition interpretation is therefore withdrawn. A no-extra-acquisition interleaved x2 variant remained strongly predictive but did not beat ordinary x2–x4 PC. The contribution is a diagnostic principle/protocol, not a universal estimator replacement.

## Falsified hypotheses

- A universal transferable curvature law.
- A universally superior disjoint-context estimator.
- Cost-free prospective densification using two newly acquired phase grids.
- The explanation that gains arise merely from larger perturbations.
- The explanation that the effect is a Transformer-specific artifact.

## Current strongest claim

Measurement overlap is a causal experimental determinant of whether reconstruction disagreement exposes shared deterministic error. Controlled target-preserving, measurement-disjoint contexts reveal error substantially better than maximal-shared contexts in two cohorts and multiple neural/analytical interpolators.

## Remaining reviewer attacks

- Phase-shift acquisitions are synthesized from dense retrospective volumes, not prospectively acquired repeat scans.
- Only through-plane brain MRI has been tested.
- Reversal is a practical maximal-overlap control but may introduce an ordering-equivariance artifact; this makes it a deliberately difficult negative control, not a pure overlap-only randomized experiment.
- The zero/one/maximal series is not strictly monotone in every natural x4–x6 stratum; the robust claim is zero versus maximal under the controlled pair, not universal monotonicity.

