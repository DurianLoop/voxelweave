# Consensus Error Research

## Central question

If 81–87% of three-context squared error is shared, can that component be explained, predicted, exposed, or reduced without observing the missing target?

## Working decomposition

For context reconstructions `f_i` and target `y`, squared error obeys

`mean_i ||f_i-y||² = ||mean_i f_i-y||² + mean_i ||f_i-mean_i f||²`.

- `consensus component`: error of the context mean; invisible to ordinary context spread.
- `context-sensitive component`: observable spread around the context mean.
- `architecture-specific component`: residual change under model identity; empirically much smaller than case/factor effects.

This identity quantifies observability but does not label consensus error irreducible. It may contain acquisition ambiguity, shared inductive bias, preprocessing scale, and common regression bias.

## Competing mechanisms

1. **Sampling-curvature mechanism:** target trajectories bend between acquired anchors; larger physical spacing amplifies approximation error for every architecture.
2. **Shared-information mechanism:** contexts that reuse anchors inherit correlated errors, suppressing disagreement even when target curvature is high.
3. **Intensity-scale mechanism:** much of apparent shared difficulty is same-unit scaling of MAE/MSE.
4. **Conditional-central-tendency mechanism:** deterministic L1/L2-trained models converge toward similar central predictions under ambiguous inputs.
5. **Architecture-prior mechanism:** shared training data/objectives impose common smoothing unrelated to fundamental sampling difficulty.

## Falsifiable predictions

- At fixed factor/model/case, contexts with zero anchor overlap should expose more target-correlated separation than contexts sharing an anchor.
- A curvature–spacing term should explain cross-factor error better than factor alone and predict steeper degradation in high-curvature cases.
- If overlap rather than raw diversity matters, artificial perturbations with large output diversity but target/context corruption will not improve reliability.
- If shared error is mainly conditional ambiguity, changing architecture will not materially reduce high-curvature error, whereas reducing spacing will.
- A mechanism-derived input estimate of shared risk should improve detection of PC stable-wrong cases without degrading ordinary context-sensitive detection.

## Innovation target

Develop a target-preserving, anchor-disjoint intervention or a curvature/spacing-based intrinsic-difficulty estimator that observes consensus failures missed by PC, then validate its predicted advantage over flip-TTA, ordinary overlapping PC, dynamic range, and naive fusion.

