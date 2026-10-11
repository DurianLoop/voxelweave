# Clean Overlap-Ladder Feasibility Audit

## Geometric result

For the frozen HAT/SwinIR x4 protocol, each missing target is reconstructed from the two bracketing acquired slices. If contexts must simultaneously preserve:

- the same physical target;
- two measurements;
- the same factor;
- the same left/right distance pair;
- the same preprocessing;

then a one-dimensional uniform grid admits only the identical bracketing pair. Its overlap is maximal (2/2). Translating the uniform grid changes the bracketing distances; mixing one translated and one original anchor gives a 1/2-overlap context but necessarily introduces distance/asymmetry changes. A strict five-level ladder with all listed quantities fixed is therefore geometrically infeasible for two-anchor interpolators.

This is not a reason to fabricate intermediate levels. Plan-5 comparisons are separated into:

1. **Clean maximal overlap:** identical x4 anchors with in-plane flip equivariance; z ordering and distances are unchanged.
2. **Clean zero overlap:** phase-0 versus phase-2 x4 grids; measurement count is fixed, but individual target-to-anchor distances swap for target phases 1 and 3.
3. **Natural partial overlap:** x4–x6 same-target contexts with 0/1 shared anchors; measurement distance and factor differ and are modeled as covariates, not treated as a clean causal level.
4. **Asymmetric/leave-one-anchor contexts:** useful mechanism probes, not points on an otherwise controlled dose-response curve.

## Registered decision

The primary causal contrast will be zero versus clean maximal overlap, stratified by target phase and architecture, with identical phase-0-defined masks. Natural partial-overlap observations are secondary. A monotone five-level dose-response claim is prohibited unless a future architecture with larger fixed context supports such a design.

