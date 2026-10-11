# CVPR Upgrade Research State

Audit freeze: 2026-08-13. All results here are post-Plan-4 exploratory work and do not alter the frozen TMI evidence.

## Established upgrade

1. Clean same-target controls show that zero-overlap contexts rank error better than maximally shared contexts in fastMRI, IXI, and NingXia by `0.0923`, `0.0949`, and `0.1934`; every clustered interval excludes zero.
2. Acquired-anchor cross-validation (C5-E011) withholds an already acquired x4 anchor and reconstructs it from neighboring acquired anchors. It uses no dense target, additional phase grid, learned x8 model, or new acquisition. Its x4-error rhos are `0.9374`, `0.9549`, and `0.9547`; benefit rhos are `0.7990` and `0.6147` where x2 evidence exists.
3. Exact five-level four-anchor ladders (C5-E012/E013) hold target, anchor count, distance multiset, estimator, and mask fixed. Overall trends have the expected sign, but a repeated `0→1` exception falsifies strict count monotonicity.
4. Shared estimator influence (C5-E014) resolves the exception. Common absolute coefficient mass correlates with error cosine by `0.815/0.789/0.855`, versus `0.503/0.466/0.630` for raw overlap count. Every clustered coefficient-cosine advantage interval is positive (`0.189–0.283`).
5. Full Anchor-CV allocation curves beat random at all fastMRI budgets and NingXia 20/30/50%; NingXia 10% crosses zero. The supported capability is examination triage, not a slice heatmap or calibrated uncertainty.

## Preserved negative and bounded results

- C5-E006 two-component fusion failed its frozen confirmation gate.
- The original order-reversal covariance chain is confounded on fastMRI; causal language relies on the clean control and exact analytical ladders.
- The wide ladder cannot cover shallow fastMRI volumes. The eligibility-driven compact ladder includes every cohort and preserves the nonmonotone result.
- Anchor-CV fastMRI within-case localization has median rho `-0.264` and is explicitly rejected.
- IXI has no frozen x2 output, so benefit and allocation evaluation are `NOT RUN`.
- No claim permits calibrated uncertainty, prospective benefit, autonomous reacquisition, clinical safety, or universal superiority.

## Decision

The updated score is novelty `4/5`, importance `4/5`, mechanistic depth `5/5`, rigor `4/5`, and reviewer resilience `4/5`. The Plan5 threshold is **MET**. A review-format CVPR manuscript is present in `PAPER/`; its remaining blockers are human metadata/ethics, target-year author-kit refresh, and the documented TMI/CVPR dual-submission conflict.
