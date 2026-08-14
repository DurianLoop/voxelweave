# Local Physical Measurement Influence sampling addendum

Frozen: 2026-08-14, before any Plan-9 influence output for I3Net, SAINT, or CycleINR was generated.

This addendum resolves dataset and geometry details left open in `UNIFIED_INFLUENCE_PROTOCOL.md`. It does not change the perturbation, response statistic, endpoints, or stability gate.

## Samples and target planes

- **SAINT:** all 24 examinations in the frozen fastMRI T2 test split, factor x4, at three deterministic interior target planes. Planes are the rounded, unique interior tertiles of the valid interval `[3, depth-4]`. This retains the already frozen pair-input context grid.
- **I3Net and CycleINR:** the first 24 geometry-eligible cases in the frozen IXI T2 test-list order, factor x4, one target plane per examination. Eligibility requires depth at least 23. The target is the integer midpoint of the volume, clipped to `[10, depth-12]`; no case is selected or rejected using reconstruction results.

The 24-case IXI subset matches the fastMRI confirmation size and keeps the coordinate/3-D finite-response computation tractable. It is a preregistered subset analysis, not a claim about all 115 IXI test examinations. Reconstruction benchmarking continues to use the available full test outputs.

## Four-anchor context grid

For I3Net and CycleINR, every context contains four equally spaced x4 anchors relative to target zero:

- reference: `(-5,-1,+3,+7)`;
- overlap-three: `(-9,-5,-1,+3)`, `(-1,+3,+7,+11)`;
- overlap-zero: `(-10,-6,-2,+2)`, `(-7,-3,+1,+5)`, `(-6,-2,+2,+6)`, `(-3,+1,+5,+9)`, `(-2,+2,+6,+10)`.

All contexts bracket the same missing physical target; none contains the target. The design supports overlap counts zero and three (plus the reference self-comparison, which is excluded from association tests). Fixed-count inference is performed at overlap three. The narrower overlap support than the pair-input grid is reported as a limitation.

## Normalization and prediction support

The full examination defines one fixed min/max normalization. This prevents a perturbation from changing the normalization constants and matches the earlier HAT/SwinIR influence probe. Predictions and response vectors are evaluated at 256 x 256, the normal trained input support of all three wrappers. CycleINR is queried only at the target-plane coordinates needed for evaluation; its full 13-plane densified x4 input and coordinate normalization are unchanged.

## Stability computation

The primary response uses amplitude `+0.01`. The same cases, planes, contexts, anchors, and four fields are recomputed at `+0.005`, `+0.02`, and `-0.01`. Stability rank correlation is evaluated over non-self context pairs with at least one shared physical measurement; zero-overlap pairs are deterministically zero and therefore excluded from this gate.

