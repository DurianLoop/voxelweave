# Statistical Validity Re-audit

## Independent unit

The examination is the independent sampling unit. All 3 factors x 3 architectures for the same examination are deleted, resampled, or score-swapped together.

## Corrected results

| Cohort | Cases | Delta nAURC | Clustered case-bootstrap 95% CI | Rank-scale clustered permutation p |
|---|---:|---:|---:|---:|
| NingXia OOF | 22 | -0.0256 | [-0.0957, 0.0092] | 0.164 |
| fastMRI-brain | 24 | -0.0698 | [-0.1597, -0.0183] | 0.005 |

The earlier profile-aligned bootstrap interval for NingXia excluded zero because it did not preserve all repeated factor/architecture measurements as one case cluster. That interval is superseded for inferential claims by the clustered result above.

The score-swap permutation operates on within-profile ranks because raw committee and physical scores have different units. Swapping raw magnitudes is not exchangeable and was rejected during the audit.

## Heterogeneity

- NingXia: 6/9 profiles favor PC; all x6 profiles favor it, while x2 HAT and SwinIR are slightly worse. Profile delta range: -0.1023 to +0.0152.
- fastMRI: 9/9 profiles favor PC. Profile delta range: -0.1368 to -0.0296.

## Risk-coverage behavior

- NingXia: PC is better at 14/22 discrete coverage points; curves cross three times. It is better near 25% and 75% coverage but slightly worse near 50%. This explains improved nAURC with worse RRR50.
- fastMRI: PC is better at 20/24 coverage points; curves cross once and PC is better near 25%, 50%, and 75%.

## Statistical conclusion

The strongest statistically stable examination-level comparison is fastMRI cross-dataset replication. NingXia provides directionally stable, architecture/factor-heterogeneous evidence but not a clustered interval excluding zero. No claim should use repeated profiles as independent observations.

