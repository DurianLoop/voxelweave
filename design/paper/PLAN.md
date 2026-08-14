# Research Plan after Plan 2

## Decision

Plan 2 closed a scoped branch; Plan 3 subsequently reopened the project and superseded that stopping interpretation. The current program decision is in `PROJECT_EXHAUSTION_AUDIT.md`.

## Completed evidence chain

1. Froze `PC-v1-FROZEN` before confirmatory work.
2. Recomputed inference with examination-clustered bootstrap and rank permutation.
3. Measured leave-one-case influence, profile heterogeneity, and complete risk-coverage behavior on NingXia and fastMRI.
4. Verified 1,518 geometry records, including orientation, spacing, FOV, affine, plane count, and world-plane distance.
5. Falsified general common-mode detection with controlled smoothing.
6. Audited intensity scale, normalized endpoints, pair structure, and a generic TTA comparator.
7. Derived localization on 8 fastMRI cases, confirmed it without protocol changes on the remaining 16, then replicated on 22 NingXia OOF cases.
8. Formalized the triangle-inequality guarantee and documented natural consistent-but-wrong boundary cases.
9. Updated literature, novelty, claim-evidence, red-team, and reproducibility records.

## Locked interpretation

- Large context separation implies that at least one reconstruction has nontrivial error under the chosen metric.
- Small separation supplies no upper bound on error.
- Empirical ranking requires context-induced error diversity and a declared intensity representation.
- Examination-level superiority over the committee is confirmed on fastMRI, but statistically uncertain on clustered NingXia.
- Superiority over generic TTA, clinical relevance, and external anatomy/site generalization are not established.

## Next work, blocked by unavailable inputs

1. Untouched site/anatomy with aligned multi-factor predictions.
2. Reader or downstream labels for clinical relevance.
3. Frozen external confirmation of shared-range-normalized `PC-v2`.
4. Multi-target, multi-architecture TTA outputs for a decisive generic-perturbation comparison.

No additional tuning on NingXia or fastMRI may upgrade these claims.
