# Unified Local Physical Measurement Influence Protocol

Frozen: 2026-08-14, before Plan-9 cross-model influence results.

## Scientific object

The unit is an acquired physical slice measurement and its local effect on prediction of one fixed missing physical target. It is not an internal feature, attention weight, or architecture-specific channel.

## Perturbation

For every eligible context and every acquired anchor in that context:

1. use four deterministic centered Rademacher fields with seeds `6101, 6102, 6103, 6104`;
2. resize the field to the physical anchor plane;
3. add amplitude `0.01` in the model's normalized input range to that anchor only;
4. run the same frozen inference path;
5. subtract the unperturbed target prediction;
6. restrict the response to the fixed ground-truth-derived 1% target foreground used only for retrospective evaluation.

The perturbation definition, amplitude, and seeds are identical across models. Architecture-specific changes are limited to the normal input wrapper needed to present the perturbed physical anchor.

## Response and shared influence

Let `r(C,m,k)` denote the target-output response for context `C`, physical measurement `m`, and field `k`. For a context pair `A,B`, define:

- total response energy in A and B by summing squared response norms over their anchors and fields;
- shared response dot product by summing dot products only for physical anchors present in both contexts and matched perturbation fields;
- **Local Physical Measurement Influence cosine** as shared response dot product divided by the geometric mean of total response energies;
- common response mass as the sum of the smaller matched response norm divided by the mean total response norm.

If contexts share no physical measurements, shared influence is exactly zero by definition. This is a physical-measurement attribution statement, not a claim that their outputs are statistically independent.

## Context grids

### Pair-input models: HAT, SwinIR, SAINT

Use the frozen Plan-8 grid relative to target `z`:

- reference `(-2,+2)`;
- alternatives `(-2,+1)`, `(-2,+3)`, `(-1,+2)`, `(-3,+2)`, `(-1,+1)`, `(-1,+3)`, `(-3,+1)`, `(-3,+3)`.

### Four-anchor regular-grid models: I3Net and CycleINR

Use four equally spaced x4 anchors. The reference is `(-5,-1,+3,+7)`. Valid alternatives retain x4 spacing and keep the target inside the model output support, including left/right one-window shifts with three shared anchors and phase-shifted zero-overlap contexts. Unequal physical spacing is prohibited.

Because this grid has fewer overlap levels than the pair-input grid, count-versus-influence results are reported with that limitation and never pooled as though design support were identical.

## Primary associations

For each eligible model:

- shared influence → error cosine;
- shared influence → shared-error fraction;
- shared influence → observable-error fraction;
- error cosine → normalized disagreement.

Raw overlap count is evaluated against the same endpoints. Report `Δ|rho| = |rho_influence| - |rho_count|` with examination-clustered bootstrap intervals. Fixed-count analysis is required wherever at least two valid contexts share the same nonzero overlap count.

## Statistical hierarchy

- Pixel/plane measurements are not independent clinical samples.
- Primary resampling cluster is examination for fastMRI/IXI and patient for NingXia.
- Per-model effects remain separate.
- Cross-architecture summaries use joint case bootstrap and equal-weight descriptive family summaries; architectures are not treated as independent clinical subjects.
- Leave-one-family-out analysis recomputes the descriptive aggregate after excluding one family.

## Stability gate

Before interpreting a new model's influence result, compare the frozen four-field statistic under amplitude `0.005` and `0.02` and under sign reversal. A model passes if each alternative produces examination/configuration rank correlation at least `0.90` with the primary statistic. Failure does not permit tuning; it changes the model's classification to phenomenon-only for influence claims.
