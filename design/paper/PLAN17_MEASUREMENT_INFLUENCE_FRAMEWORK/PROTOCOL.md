# Plan 17 limited experiment protocol

Written after the provenance audit and before these new experiment outcomes. This is a local execution record, not external preregistration. Historical cohorts are analysis-reused. Seed 20260911. No reconstruction training, no GPU occupation, no result-directed continuation.

## E01 — local covariance proposition verification

Fixed finite-dimensional linear estimators, unchanged marginal input covariance and biases; vary only cross-context covariance. Positive, orthogonal, and opposing sensitivities and shared correlations −0.5/0/0.5/1 are all retained. Analytic covariance trace predicts the change in expected error inner product and disagreement energy. Numerical calculation and Monte Carlo check the signs/factors, including negative sensitivity counterexamples. This is a mathematical implementation check, not non-MRI generalization evidence.

## E02 — one acquired-only dependency guard, four neural architectures

Read existing phase-0 ×4 predictions for HAT/SwinIR and I3Net/CycleINR on all 24 fastMRI and 115 IXI examinations. These two pairs are fixed by architecture lineage before the new scoring results, not by new performance. Model weights differ by dataset as in the historical experiment. No new checkpoint selection.

Use five target planes missing from phase 0. fastMRI targets 3/5/7/9/11; IXI uses the same five physical targets already recorded by Plan 11. At each target, the score support is the union of the nearest two acquired phase-0 foregrounds, each abs(x)>1% max(abs(x)). A single scale per case is acquired phase-0 nonzero finite intensity Q99−Q1, floored at 1e−6. Never use the target to form scores, masks, ranges, or context choices. Evaluation errors use that same acquired mask. Calculate both prediction MAEs, their minimum (both must be inaccurate), pair average, difference MAE and population two-member ensemble variance. Case features are plane medians. Anchor-CV, adjacent-anchor MAE/RMSE, acquired range and header z-spacing are baseline inputs; spacing is an available header number, not verified clinical physical spacing.

Development: sort the 24 fastMRI case IDs by SHA256('P17-dev:'+case); first 12 are development, remaining 12 internal evaluation. IXI is a distinct-cohort transfer audit. All were historically observed, so neither is advertised as a pristine holdout. Fix and save membership before reading the new scores.

One candidate only: S_guard=max(F_dev(D_norm), F_dev(AnchorCV_norm)), because both predictors reuse the same phase-0 evidence. F_dev is the right-continuous empirical CDF estimated only from development cases, separately by pair. This is a dependency-triggered acquired-data floor, not a learned influence estimator. No λ scan or candidate-family expansion. The rule, thresholds and CDF samples are frozen once development features are calculated. No tuning to validation/IXI results.

Primary detection label: both-error=min(MAE_A,MAE_B)/acquired_range at or above development Q75 AND D_norm at or below development Q25, separately by pair. Report AUROC and AUPRC; no positives or no negatives yields NA, never a zero-valued successful test. Comparators: D_norm, AnchorCV_norm, adjacent_MAE_norm, adjacent_RMSE_norm, acquired_range, spacing. Secondary paired-error ranking and top-20% enrichment are descriptive. 5,000 paired examination bootstraps; simultaneous intervals for guard-minus-baseline AUPRC over the two pairs × six baselines within each evaluation cohort, with invalid replicates counted. If endpoints degenerate or superiority is not simultaneous and cross-cohort, no method-success claim and stop. AUC on scarce positives is explicitly unstable. No patient pooling across cohorts.

## E03 — real qualitative phenomenon and limited practical proxy check

Select the main example from the existing full fastMRI SwinIR clean table: median case mean observable gain, tie by case ID; within case, target with gain closest to that case mean, tie by physical z. Supplemental example: one seeded random distinct case, target z=7. Save the full selection ranking before new inference. Display GT, A, B, |A−B|, |A−GT|, |B−GT| for shared and disjoint conditions at the same target. One intensity scale and one difference/error scale per complete example; no separately autoscaled favorable maps, no manual ROI. CPU float32 reproduction of frozen SwinIR weights, save all arrays and compare metrics against historical GPU outputs; dtype differences must be reported.

For an actual cross-model proxy intervention, additionally use fixed Linear/Cubic interpolation on all fastMRI/IXI cases, both phase0/phase2 grids with complete four-point cubic support. Targets are all eligible odd planes (fastMRI 7 and 9), with residue-1/3 equal weighting within case. Compare L0/C0 versus L0/C2 and C0/L2; estimate prediction disagreement MAE and population two-member variance (=|A−B|²/4). This is one two-member analytic ensemble, not independent evidence from two equivalent variance formulas and not a Bayesian ensemble benchmark. Evaluate pair errors and fixed reference-model error as distinct endpoints. Acquisition masks/ranges as E02. Reuse all existing five-architecture TTA results as the other practical construction rather than rerun their full networks. Bootstrap 5,000 examinations; simultaneous two-direction intervals for local gain and proxy ranking differences per cohort.

## E04 — theory and input-access checks

Verify covariance sign/factor, embedded all-anchor response cosine, target mutation invariance of acquired-only scores/masks, patient membership, unique paired keys and interval family size. No tests that merely assert a desired result. Non-MRI natural-image experiment skipped because no qualified matched resource is established; do not substitute a toy for empirical domain transfer.

## Stop

Q1–Q3 use audited historical replication plus these checks. Q4 remains unproven unless the limited new audit succeeds AND an untouched patient-independent dataset is established. Failure/NA ends score search. All new attempts go into experiment_registry.csv. Revise only the CVPR main/supplement; TMI remains preserved for this scoped iteration.
