# Frozen four-plane interpolation control for disjoint ensembling

**Status:** post-result sensitivity, fixed after seeing the nearest-two-plane linear control, before calculating either cubic result. The question is whether the learned HAT0/SwinIR2 ensemble improves over standard interpolation using the same available phase-0 plus phase-2 published planes. This does not make the original x4 phase-0-only task deployable.

Use the exact 727 targets, source images, source hashes, phase-0 support and disjoint ensemble MSE sealed in [the prior equal-information protocol](UNION_EVEN_LINEAR_CONTROL_PLAN_2026-10-01.md). Its result `experiments/union_even_linear_control/per_target.csv` has SHA-256 `7b0c2fd2df320b9d2bc85071d20cfe43fe1fb69b2ca79b239c0d2f2e59903611`. No patient or target is selected from results; every target must have real even planes at `z-3,z-1,z+1,z+3`, otherwise record a source-contract failure and stop rather than replace the target.

Apply two fixed interpolation operators independently to each pixel along the native slice index, using four real even planes at offsets `[-3,-1,+1,+3]` from the odd target:

1. Uniform Catmull-Rom midpoint: `(-x_(z-3)+9*x_(z-1)+9*x_(z+1)-x_(z+3))/16`.
2. Shape-preserving cubic Hermite (PCHIP) at index zero, fitted to the same four samples with SciPy's standard `PchipInterpolator(axis=0)`. No clipping, normalization or trained parameters.

Calculate each baseline's MSE on the same phase-0 mask and original published target; verify source hash, target identity, support count and prior nearest-two-plane linear MSE. Report each baseline separately, including every target and patient, without choosing the better method after observing results. For each baseline, use `gain=(MSE(baseline)-MSE(disjoint learned ensemble))/MSE(baseline)`; positive favors the learned ensemble. Average target MSE within residue and residue means within patient, then average patient relative gains. Use the same exploratory 5,000-draw patient bootstrap seeds and 35/27 ReMIND stratification as the linear control.

If either standard cubic comparator removes the cross-source advantage (majority of patients not improved in either source or an interval including zero), do not claim a robust actionable ensembling benefit from these tests. If both remain weaker, a prospective equal-input learned x2 model and new source would still be needed for a publishable method claim. The observational MIRA `Delta O` result remains distinct.
