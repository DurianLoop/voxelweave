# Protocol Fairness Audit

Frozen protocol decision: 2026-08-14.

## Fair comparison requirements

| Requirement | Broad reconstruction layer | Mechanism layer |
|---|---|---|
| Same physical target | Same generated indices within dataset/factor | Exactly the same missing physical plane for both contexts |
| Independent units | Examination; NingXia patient-group OOF | Examination/patient-cluster bootstrap |
| Input information | Same nominal factor; architecture-native interface allowed | Physical measurement sets explicitly recorded; no target leakage into score |
| Preprocessing | Stored inverse-normalized outputs, common metric support | Frozen per-input normalization algorithm for both contexts |
| Geometry | Identical NIfTI shape/affine/orientation audit | Target index mapped back to original physical z |
| Mask | Common GT-derived 1% foreground, metrics only | Same target-derived 1% mask for both paired conditions, metrics only |
| Metrics | Common MAE/MSE/RMSE/PSNR/global SSIM/NCC implementation | Common error decomposition, disagreement, Spearman, stable-wrong rules |

## Layer A eligibility

The corrected common-support model-bank results are fair for fastMRI and NingXia x2/x4/x6 for the 13 methods in the registry. IXI x4 is fair only for methods with audited 115-case outputs; absence is reported rather than filled from a different cohort or split.

## Layer B eligibility

| Model | Same target | Comparable physical information | Frozen checkpoint | Context mapping valid | Decision |
|---|---:|---:|---:|---:|---|
| Linear/Cubic | Yes | Yes | N/A | Exact | Existing core mechanism evidence |
| HAT/SwinIR | Yes | Yes | Yes | Two-anchor | Existing core mechanism evidence |
| I3Net | Yes | Yes | Yes | Four equally spaced anchors, full source required | New primary eligible |
| SAINT | Yes | Yes | Yes | Two-anchor + relative position | New primary eligible |
| CycleINR-style | Yes | Yes | Yes | Regular sparse volume + coordinate query | New primary eligible |
| ArSSR | Yes in principle | Yes | Yes | Same INR wrapper family | Supplement/P1 only |
| Other recovered neural baselines | Not yet audited | Unknown | Mostly yes | Not frozen | Benchmark only in Plan 9 unless promoted before results |

## Known non-comparabilities

- The original three-case fastMRI SAINT run includes uncertain contrast metadata and is excluded. The strict T2 expanded 24-case run is used.
- SAINT x2/x6 shared manifests were overwritten by ResUNet metadata; their outputs are not used as primary mechanism evidence.
- IXI lacks a fully audited SAINT run and has no complete CycleINR x2/x6 series. Missing cells remain missing.
- ACSI and PastNet do not share the frozen broad model-bank protocol.
- No model is compared using its own foreground mask in the corrected benchmark.
- No pixel is treated as an independent patient.

## Broken-model gate

A model may enter mechanism analysis only if its frozen x4 reconstruction performance is finite on all 24 fastMRI test examinations and is not catastrophically worse than Linear under the same common-support MAE. Historical corrected means satisfy this gate for I3Net (70.87), SAINT (80.14 in the common-bank audit), and CycleINR (114.39), compared with Linear (134.54).

Passing this gate establishes a functioning baseline, not state-of-the-art performance.
