# Publication Readiness Report

## Exact central claim

In deterministic MRI slice interpolation, disagreement is not intrinsically reliable: its ability to reveal error depends on whether the compared reconstructions reuse measurements that induce the same failure. Holding target plane, case, model, and evaluation mask fixed, predictions from measurement-disjoint phase grids expose error substantially better than a maximal-shared-anchor control. This motivates a general reliability-design principle: **maximize independence of error-generating information, not raw prediction diversity**.

## Contributions

1. **Consensus-error diagnosis.** An exact decomposition establishes that 81–87% of squared reconstruction error is shared across contexts, explaining why ordinary agreement can miss dominant failures.
2. **Controlled mechanism experiment.** A same-target phase-grid intervention varies acquired-anchor overlap from zero through natural one-anchor comparisons to maximal shared context.
3. **New reliability principle and protocol.** Measurement-disjoint phase-grid consistency is introduced as a stress test for consensus blindness.
4. **Cross-method evidence.** The predicted effect survives two MRI cohorts, two frozen neural architectures, linear/cubic interpolation, paired endpoints, and case-cluster inference.
5. **Calibrated negative findings.** Curvature is mechanistically relevant but not a universal proxy; deployable IGC does not universally beat PC; acquisition-budget circularity is explicitly rejected.

## Novelty versus closest work

Classical interpolation theory links derivatives and spacing to approximation error; slice-synthesis work focuses on reconstruction quality; video interpolation studies temporal ambiguity; MRI consistency methods enforce acquired-data constraints; posterior methods sample acquisition-compatible solutions. The reviewed work did not combine a fixed missing target, controlled measurement-overlap manipulation, and disagreement-observability evaluation across neural and analytical reconstructors. See `PLAN4_LITERATURE_AND_NOVELTY.md` for the bounded audit and primary links.

## Strongest evidence

- Zero vs maximal overlap, same target/case/model/plane and identical mask:
  - fastMRI: rho 0.960 vs 0.605; Δ=0.355; case-cluster 95% CI [0.225, 0.557].
  - NingXia OOF: rho 0.891 vs 0.699; Δ=0.193; 95% CI [0.111, 0.306].
- Per-architecture Δrho remains positive with clustered intervals above zero:
  - fastMRI HAT 0.340 [0.205, 0.559], SwinIR 0.375 [0.233, 0.586].
  - NingXia HAT 0.128 [0.048, 0.258], SwinIR 0.258 [0.149, 0.401].
- Raw-magnitude control: on fastMRI, disjoint disagreement is smaller than maximal-shared disagreement but more informative.
- Analytical generalization: linear/cubic case rho 0.958–0.977 across both cohorts.
- Predictive consequence: the x4 disjoint signal predicts realized x4→x2 benefit, rho 0.811 [0.592, 0.904] and 0.626 [0.341, 0.804]. This is evidence of predictive validity, not a cost-free acquisition policy.

## Mechanism

If two deterministic estimates reuse measurements that underdetermine the target in the same way, their errors have a large common direction. Subtracting the estimates cancels that direction and leaves only context-sensitive residual error. A target-preserving phase shift replaces the supporting anchors, reducing shared error direction while retaining the same physical prediction target. The intervention therefore makes previously hidden consensus bias observable.

This mechanism is supported causally at the intervention level; it does not prove that all shared error is irreducible conditional ambiguity. Shared training objectives, smoothing bias, and anatomy-dependent information loss can all contribute.

## Method and ablations

- **Method:** phase-grid consensus-blindness stress test, using disagreement between target-preserving, measurement-disjoint reconstructions.
- **Overlap ablation:** zero, natural zero/one in x4–x6, and maximal overlap.
- **Architecture ablation:** HAT and SwinIR separately.
- **Estimator ablation:** linear and cubic analytical interpolation.
- **Perturbation-size ablation:** raw disagreement magnitude does not account for ranking improvement.
- **Mask ablation/fix:** all decisive comparisons use the phase-0-only mask and achieve exact endpoint equality.
- **Deployment ablation:** interleaved x2 IGC is strong but not superior to ordinary PC, delimiting the claim.
- **Input baseline:** adjacent-anchor RMSE is weaker for densification-benefit prediction on fastMRI and not significantly weaker on NingXia.

## Reviewer red-team

1. **“Is this obvious from interpolation theory?”** Theory predicts spacing/curvature difficulty, not that reliability accuracy changes under controlled reuse of error-generating measurements. The overlap experiment is the new empirical mechanism.
2. **“Is it merely more diversity?”** No. The strongest fastMRI intervention has smaller raw disagreement yet higher error correlation.
3. **“Is this architecture-specific?”** No. It replicates across two neural models and two analytical interpolators.
4. **“Is this pseudoreplication?”** Plane effects use case-cluster bootstrap; case-level correlations are also reported.
5. **“Does it require the missing target?”** The score does not. Dense targets synthesize the retrospective alternative acquisition and provide evaluation labels; this limitation is explicit.
6. **“Is the new score universally better?”** No such claim is made. A deployable IGC variant fails to beat strong ordinary PC consistently.
7. **“Could reversal be an unfair negative control?”** It is a maximal same-measurement stress control and may include ordering effects. The key paired effect is robust, but a prospective randomized overlap ladder remains desirable.
8. **“Why does this matter outside MRI?”** Any deterministic inverse problem that compares estimates sharing measurements can hide common error directions. External imaging validation is needed before asserting cross-domain generality.

## Limitations and remaining risks

- Retrospective synthetic phase grids rather than prospective acquisitions.
- Two brain MRI cohorts; no CT, video, or k-space reconstruction validation.
- Two neural architectures in the controlled overlap comparison, although analytical methods expand estimator diversity.
- Maximal-overlap reversal changes ordering while preserving measurements; a cleaner control would use independently trained/equivariant estimators with identical anchors.
- No reconstruction-quality improvement is claimed; the contribution is reliability evaluation and intervention design.
- Literature search is bounded and cannot establish absolute absence of prior art.

None of these is fatal to the scoped central claim, but all should be prominent in a submission.

## Recommended CVPR-style paper structure

1. Introduction: agreement blindness and shared error.
2. Related work: deterministic reconstruction uncertainty, medical slice synthesis, interpolation ambiguity, consistency, sampling theory.
3. Error decomposition: consensus versus context-sensitive components.
4. Measurement-overlap hypothesis and phase-grid protocol.
5. Controlled experiments: zero/one/maximal overlap, paired inference, architecture and analytical ablations.
6. Predictive consequence and deployment boundary.
7. Curvature/spacing supporting analysis.
8. Limitations, ethics, and prospective validation.

## Readiness verdict

The controlled measurement-overlap principle reaches the Plan 4 heuristic threshold (Novelty, Importance, Mechanistic depth, Experimental rigor, Reviewer resilience = 4/5 each) with no fatal collision found in the bounded audit. Further work would primarily broaden external validity and improve the maximal-overlap control rather than determine whether the core effect is real.
