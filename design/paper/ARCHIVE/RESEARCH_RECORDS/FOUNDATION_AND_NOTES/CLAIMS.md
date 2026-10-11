# Claims after Plan-2 Falsification

## C101 — Central supported claim

- Exact claim: In deterministic T2 brain slice interpolation, disagreement of the same reconstructor on world-coordinate-identical planes under different sampling factors is a reproducible, ground-truth-free, one-sided error witness across pixel, plane, and examination granularity.
- Evidence: E009, E013, E014; three architectures, two cohorts, 46 cases total, 2,424 confirmation/replication planes plus 480 derivation planes.
- Confidence: high for association in the studied setting; not a calibrated interval or guarantee.

## C102 — Mechanistic claim

- Exact claim: context consistency is informative only when target-preserving context changes induce error diversity. Large discrepancy lower-bounds at least one context error; agreement does not imply correctness.
- Evidence: triangle-inequality formalization; E010 shared-blur counterexample; E014 real boundary-plane counterexamples.
- Confidence: high for the mathematical one-sided statement and demonstrated failure modes.

## C103 — Examination-ranking comparison

- Exact claim: PC-v1 improves examination ranking over the frozen committee consistently on fastMRI, while NingXia shows a directionally stable but heterogeneous and cluster-statistically uncertain effect.
- Evidence: fastMRI 9/9 profiles, CI excluding zero; NingXia 6/9, CI including zero, 22/22 leave-one-out direction.
- Confidence: high on fastMRI, moderate on NingXia.

## C104 — Intensity-scale decomposition

- Exact claim: raw PC reflects both absolute-intensity difficulty and context instability; a shared-range-normalized component remains associated with normalized error.
- Evidence: E011; dynamic-range correlations and endpoint sensitivity.
- Confidence: moderate; PC-v2 requires independent confirmation.

## Rejected or unsupported claims

- PC detects all shared/common-mode failures: rejected.
- Low PC certifies accuracy: rejected.
- PC identifies which factor or model is wrong: rejected.
- PC is uniquely superior to generic TTA: unsupported.
- PC-v1 universally improves every architecture/factor/cohort: rejected.
- Calibrated uncertainty, diagnostic safety, external anatomy/site generalization, or clinical benefit: unsupported.
