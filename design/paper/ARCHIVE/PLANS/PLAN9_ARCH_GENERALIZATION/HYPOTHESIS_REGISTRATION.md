# Plan 9 Architecture-Generalization Preregistration

Frozen: 2026-08-14, before any Plan-9 architecture-generalization result was computed.

## Primary hypothesis H-ARCH-01

> Consensus blindness induced by measurement dependence is not specific to HAT/SwinIR. When deterministic MRI slice interpolators reuse influential physical measurements, their reconstruction errors become more aligned and prediction disagreement becomes less informative, across multiple fundamentally different interpolation architectures.

## Primary falsification conditions

H-ARCH-01 is weakened or falsified if any of the following occurs:

1. the disjoint-minus-shared observability/ranking effect disappears in most eligible non-HAT/SwinIR families;
2. dedicated slice-interpolation models show the opposite direction;
3. the INR-style model shows the opposite direction under a valid physical-measurement intervention;
4. the cross-family local chain shared influence → error alignment → disagreement cancellation is absent outside the transformer/SR family.

No architecture will be omitted because its result is unfavorable.

## Frozen primary experiment

- Dataset: fastMRI brain T2, the existing patient/examination-independent 24-case test split.
- Factor: x4.
- Models: I3Net, SAINT, and CycleINR-style reproduction, with frozen historical checkpoints.
- Reference evidence: existing Plan-8 HAT/SwinIR and analytical results are not recomputed merely to change their values.
- Physical context A0: acquired planes `{0,4,8,12}`.
- Disjoint context A2: acquired planes `{2,6,10,14}`.
- Common missing targets: physical planes `{3,5,7,9,11}` for the 16-slice fastMRI test volumes.
- Shared control: A0 forward inference versus an in-plane axis-0 flip of the same A0 measurements, mapped back after inference. This preserves physical anchors, z order, distances, target, and preprocessing.
- Dense data are used only to synthesize the counterfactual A2 acquisition and evaluate held-out targets. They never enter the disagreement score.

## Frozen endpoints

For each target plane:

- paired reconstruction error;
- prediction disagreement;
- error cosine;
- shared-error fraction;
- observable-error fraction;
- stable-wrong status.

For each case/model, plane values are aggregated by the median. Primary ranking is examination-level Spearman correlation between disagreement and paired error. Inference resamples whole examinations. For NingXia follow-up, the patient prefix is the cluster.

The primary effect is:

`disjoint ranking rho - shared-control ranking rho`.

Secondary effects are disjoint-minus-shared observable fraction, shared fraction, error cosine, and stable-wrong prevalence.

## Stable-wrong rule

Within each dataset/model, thresholds are estimated once from the shared-control planes:

- error at or above the shared-control 75th percentile; and
- disagreement at or below the shared-control 25th percentile.

The same numerical thresholds are then applied to both shared and disjoint conditions. No example is selected by visual appearance.

## Architecture-specific context rule

- HAT/SwinIR/SAINT: two physical endpoint slices plus target-relative position; the existing pair-context grid is valid.
- I3Net: four ordered, equally spaced physical anchors, matching its trained x4 inter/intra-slice window. The target is extracted at its physical offset within the 13-plane output.
- CycleINR: four ordered, equally spaced physical anchors are linearly densified and passed to the frozen coordinate-based residual network. The query is mapped to the same physical target.

No model is given an irregular context it was not trained to interpret. Internal tensor layouts need not match; physical measurement identity must match.

## Protocol amendment 001

The original 2026-08-14 draft mistakenly specified a through-plane reversal shared control. A one-case implementation smoke test on I3Net and SAINT showed that this changes their z-direction response and is therefore not a clean dependence-preserving control. Before any cohort result or inferential statistic was computed, the shared control was restored to the already validated Plan-8 in-plane flip definition above. The invalid smoke outputs remain labelled `smoke_pair` and are excluded from all primary analyses. See `PROTOCOL_AMENDMENT_001.md`.

## Factor follow-up

x4 is primary. x6 may be tested with an analogous phase-0/phase-3 intervention if all target mappings and checkpoints pass the protocol audit. A regular-grid x2 phase shift has no integer target missing from both complementary phases, so a disjoint x2 test will not be fabricated. x2 remains eligible for reconstruction and cross-architecture difficulty analyses.

## Decision rule

- All three new paradigms support the direction: broad architecture-generalization evidence.
- Two support and one differs: report the differing family as a boundary.
- One supports: do not claim broad generalization.
- None support: narrow both manuscripts.

Statistical significance is not required in every architecture. Direction, effect size, clustered interval, and heterogeneity are all reported.
