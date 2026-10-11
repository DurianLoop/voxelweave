# Falsification Report

Last updated: 2026-08-12.

| Hostile question | Test | Result | Consequence |
|---|---|---|---|
| Is the NingXia effect one case? | 22 leave-one-case analyses | 22/22 retain direction | Not single-case driven |
| Are repeated profiles independent? | Examination-cluster bootstrap | NingXia CI includes zero | Earlier significance claim downgraded |
| Is it one architecture/factor? | Forest analysis | NingXia 6/9; fastMRI 9/9 | Heterogeneous on NingXia, broad on fastMRI |
| Is it one cohort? | Frozen formula on fastMRI | Delta -0.0698, clustered CI excludes zero | Cross-dataset replication succeeds, but not untouched external validation |
| Is geometry mismatched? | 1,518 full geometry checks | No spacing/FOV/orientation/affine discrepancy | Geometry artifact rejected |
| Is it only absolute intensity scale? | Normalized score and endpoint | Raw advantage shrinks; normalized association remains | Mixed signal; raw claim narrowed |
| Does it detect shared smoothing? | Controlled common-mode blur | Error rises while PC falls | General common-mode rescue claim rejected |
| Is it just generic TTA? | initial fastMRI x4 SwinIR TTA; Plan-3 18-profile extension | initial p=0.170; PC later wins 18/18 profiles with clustered p=0.0035 fastMRI and 0.0015 NingXia | Supported over flip-TTA only; arbitrary perturbation uniqueness unresolved |
| Does it localize error? | 8-case derivation, 16-case holdout, NingXia replication | Strong multi-granularity association | Localization supported as association, not calibrated uncertainty |
| Does agreement imply correctness? | Synthetic blur + real low-PC/high-error planes | Clear counterexamples | Only one-sided evidence is valid |
| Are distant factor pairs always better? | Pair decomposition | No monotonic relationship | Simple factor-distance explanation rejected |
| Is extra inference free? | Deployment audit | Requires multiple factors | Practical limitation remains |

## Attempt to reject the entire direction

The broad statement “consistency estimates reconstruction uncertainty” is rejected. The narrower scientific principle survives: target-preserving sampling-context disagreement is a reproducible one-sided error witness whose usefulness depends on error diversity across contexts. It localizes errors across two cohorts but cannot certify low-error reconstructions and is partly coupled to intensity scale.

## Pivot decision

Do not pivot back to module optimization. Retain the direction but center the contribution on one-sided evidence and failure boundaries, not universal uncertainty estimation or an unqualified nAURC improvement.
