# Plan 11 frozen protocol: claim-strengthening experiments

Frozen: 2026-08-27, before Plan 11 outcome inspection.

This package does not edit either manuscript. It implements three experiments requested after Plan 10 and keeps all eligible outcomes regardless of sign.

## P11-E01 — Same-model x4 to x2 benefit prediction

Question: can a score rank retrospective densification benefit when the reconstruction model is held fixed?

- Data: recovered common-support per-case fidelity on fastMRI and patient-folded NingXia.
- Eligible models: every model with finite common-support MAE at both x2 and x4; no result-based model removal.
- Benefit: `MAE_x4 - MAE_x2` for the same dataset, case, fold, model and evaluation support.
- Frozen scores:
  1. Anchor-CV;
  2. adjacent-anchor MAE;
  3. median x4 target-model disagreement against the registry's frozen candidate-bank members, using `intensity_mean__target_0.01`.
- Primary reporting unit: dataset-model. fastMRI resamples examinations; NingXia resamples patient folds with subordinate series retained.
- Endpoints: Spearman, Kendall, selected benefit at 10/20/30/50% budgets, gain above random, and oracle-normalized gain.
- Primary interpretation: evidence is supportive only if a score has positive direction in a majority of eligible models in both datasets. No score is called universally superior unless its paired advantage is positive across the declared datasets and models.
- Boundary: all acquisition and targets are retrospective. The experiment is not a randomized sampling treatment effect.

## P11-E02 — IXI five-architecture clean shared/disjoint replication

Question: does the local observable-error gain replicate on an independent 115-examination brain cohort across five architectures spanning four architecture lineages?

- Dataset: IXI held-out T2 split, seed 3407, 115 examinations.
- Frozen models/checkpoints: HAT, SwinIR, I3Net, SAINT-style and CycleINR-style; all are pre-existing before this protocol.
- Reference grid: phase 0, physical slices `0,4,8,...`.
- Disjoint grid: phase 2, physical slices `2,6,10,...`.
- Clean shared control: horizontal flip of phase-0 inputs, with predictions mapped back.
- Targets: five per examination, selected without image values and balanced across odd residue classes `z mod 4 = 1` and `3`, from targets bracketed by both grids.
- Mask: `abs(target) > 0.01 * max(abs(target))`.
- Primary endpoint: per-examination median `observable_error_fraction(disjoint) - observable_error_fraction(shared)`.
- Secondary endpoints: error cosine/shared-fraction changes, disagreement-error ranking difference and leave-one-family-out equal-family summary.
- Inference: examination bootstrap. A five-model universal claim requires every model interval to exclude zero in the positive direction; otherwise model-specific outcomes are retained.
- Wrapper gate: one full-volume phase-0 reproduction per model must match its frozen stored output within declared floating-point tolerance. A failed wrapper is a technical failure, not an unfavorable scientific result.
- SAINT correction: phase-2 inference uses the same global physical `z_abs` coordinate as the target rather than resetting the coordinate at phase 2.

## P11-E03 — Reflection-matched geometry identity swap

Question: after matching local sampling geometry up to left-right reflection, does changing physical anchor identity still change observable error?

- Reuses P11-E02 predictions; it does not introduce a second outcome-selected inference run.
- For odd targets, the nearest phase-0 and phase-2 anchors have the same unordered distance multiset `{1,3}` and opposite left/right assignment.
- Both predictions use the same target, model, anchor count, stride and local span; their physical anchor identities are disjoint.
- Primary unit: within-examination average of the `z mod 4 = 1` and `z mod 4 = 3` median effects, requiring both mirror classes.
- Symmetry check: report the paired difference between the two residue-class effects. The identity conclusion is weakened if the effect is confined to one residue class.
- Wording boundary: this is reflection-equivalent geometry, not exact signed-geometry identity. Any orientation sensitivity is reported.

## Common rules

- Seed: 20260827.
- Full inference: 5,000 clustered bootstrap samples. Smoke tests may use fewer and must carry a `PILOT` suffix/status.
- Raw per-plane/per-case outputs, invalid rows and wrapper checks are retained.
- No manuscript integration occurs until all three experiments finish and their adverse as well as favorable outcomes are reviewed.
