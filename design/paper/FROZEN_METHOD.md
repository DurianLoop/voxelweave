# PC-v1-FROZEN

Frozen on: 2026-08-12, before the `plan2` confirmation/falsification analyses.

This specification reproduces the already implemented physical-consistency method. It must not be modified after new results are inspected. Any later variant requires a new identifier and `EXPLORATORY` status.

## Inputs and identity

- Deterministic NIfTI predictions of the same target reconstructor and examination at interpolation factors x2, x4, and x6.
- Factor pairs: (x2,x4), (x2,x6), and (x4,x6).
- The same case identifier and target-model identity are required across factors.
- No ground truth participates in score computation.

## Geometry matching

- For slice index `z`, the plane origin is `affine[:3,3] + affine[:3,2] * z`.
- Generated indices at factor `r` are exactly those satisfying `z % r != 0`; acquired anchor indices are excluded.
- For every generated plane in the first factor, select the nearest generated plane in the second factor by Euclidean distance between world-coordinate origins.
- Accept a match only when the distance is at most 0.001 mm.
- In-plane array shapes must be identical. No interpolation, registration, or post-validation resampling is allowed.
- PC-v1 also requires finite arrays. The extended `plan2` geometry audit separately tests normals, spacing, dimensions, field of view, and affine conventions; it does not change matching.

## Intensity preprocessing and support

- Use stored prediction intensities as written after each reconstruction pipeline's inverse normalization.
- For a matched slice pair `a,b`, define the deployment support as `abs(a) > t OR abs(b) > t`, where `t = 0.01 * max(max(abs(a)), max(abs(b)), 1e-6)`.
- Do not normalize intensities across factors in PC-v1.

## Discrepancy and aggregation

1. For every matched generated plane, compute mean absolute intensity difference on the union support.
2. For each factor pair, take the median across matched plane discrepancies. This is `consistency` for that pair.
3. For an evaluation factor, retain the two pair scores involving that factor and take their median.
4. The result is one examination-level score for each dataset, factor, and target model.

## Ranking and evaluation

- Higher physical-consistency score means higher predicted reconstruction error and higher review priority.
- Evaluate each dataset-factor-target profile separately.
- Retrospective label: common-support examination MAE on generated slices.
- Primary metrics: normalized AURC and examination Spearman; Kendall and risk reductions at 25%, 50%, and 75% coverage are secondary.
- Aggregate across fixed profiles by an unweighted arithmetic mean of profile metrics.
- Case-level resampling must keep all factor/architecture measurements from one examination together.
- Comparator: frozen target-excluded median committee disagreement using its existing fixed committee and target-derived 1% deployment mask.

## Frozen scope

- Primary target architectures: I3Net, HAT, SwinIR.
- Factors: x2, x4, x6.
- NingXia: internal eight-fold OOF evaluation, never called external validation.
- fastMRI-brain: cross-dataset replication using the same frozen formula, but not an untouched prospective confirmation because fastMRI artifacts were inspected during earlier development.

## Prohibited rescue changes

No factor-pair selection, normalization change, mask change, discrepancy change, threshold tuning, architecture filtering, or coverage selection may be used to rescue PC-v1-FROZEN. Such analyses are confounder checks or new exploratory methods only.

