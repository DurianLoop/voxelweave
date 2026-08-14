# Protocol Amendment 001 — Shared-Control Equivariance

Date: 2026-08-14  
Timing: after a one-case wrapper smoke test, before any full-cohort Plan-9 result or inferential statistic.

## Original mistake

The first draft of `HYPOTHESIS_REGISTRATION.md` used through-plane reversal of the same phase-0 anchors as the shared-measurement control. The first-case smoke outputs are stored with suffix `smoke_pair`.

## Validity finding

For both I3Net and SAINT, through-plane reversal produced larger disagreement and lower error alignment than the disjoint phase intervention in the single smoke case. This is not interpreted as a scientific result. It demonstrates that z-direction reversal changes an architecture-relevant ordered input and therefore fails the requirement that only an innocuous view be changed.

## Frozen correction

The formal shared control uses an in-plane axis-0 flip, identical to the clean Plan-8 control:

1. retain A0 `{0,4,8,12}` in the same z order;
2. flip every acquired slice along in-plane axis 0;
3. run the frozen model;
4. flip the output back along axis 0;
5. compare with the unflipped A0 prediction at the same target.

This preserves physical anchor identity, z ordering, inter-anchor distance, target, model, and preprocessing. The change is protocol correction based on construct validity and prior Plan-8 evidence, not selection for a favorable cohort result.

## Exclusion

`p9_disjoint_shared_*_smoke_pair.*` is permanently excluded from the Plan-9 primary analysis and remains as an audit artifact.
