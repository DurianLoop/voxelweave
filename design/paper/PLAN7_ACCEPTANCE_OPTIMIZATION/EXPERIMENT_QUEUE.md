# Plan7 experiment queue

Priority is expected reviewer-risk reduction divided by scientific/compute cost. A result enters a manuscript only after its decision rule is frozen here or in a linked protocol.

| Priority | ID | Paper | Exact claim tested | Cheapest decisive test | Promotion gate | Status |
|---:|---|---|---|---|---|---|
| 1 | P7-CV-E01 | CVPR | Neural influence supports non-trivial context selection. | Development-freeze a minimum-influence rule; evaluate confirmation/transfer ranking and risk against random, minimum count, maximum diversity, PC/TTA/committee where compatible. | Beats count/random out of sample and adds value beyond trivial baselines on >1 dataset/architecture. | COMPLETE—FALSIFIED |
| 2 | P7-TMI-E01 | TMI | Consensus blindness changes MRI QA decisions. | Prespecified retained/missed high-error counts and clustered intervals for shared versus disjoint reliability at fixed coverage. | Consistent operational benefit with correct patient hierarchy in >1 cohort. | COMPLETE—PARTIAL SUPPORT; IXI at 70% coverage strongest |
| 3 | P7-CV-E02 | CVPR | Plan6 neural influence is stable. | Full-cohort central-plane grid: 0.5/1/2% amplitude, positive/negative field, Rademacher/Gaussian, 1/2/4/8 directions; reuse frozen three-plane outputs for plane audit. | Rank stability >=0.85 in at least 5/6 strata per condition and no stratum <0.70. | **COMPLETE—PARTIAL SUPPORT:** all 42 perturbation strata pass; 2/3 plane-pair gates fail |
| 4 | P7-CV-E03 | CVPR | Higher-order acquired jackknife adds beyond adjacent difference. | Derive non-arbitrary residual location/dispersion statistics; nested/LOCO prediction and partial ranks. | Incremental held-out value on >1 cohort without target tuning. | COMPLETE—FALSIFIED |
| 5 | P7-TMI-E02 | TMI | Endpoint heterogeneity has mechanistic structure. | Contrast blindness effects by intensity/low-frequency versus structural/high-frequency endpoint families using clustered within-case inference. | Directionally coherent across models and at least two cohorts. | COMPLETE—FALSIFIED; no universal spectral-family ordering |
| 6 | P7-CV-E04 | CVPR | Shared-influence correction improves observability. | Freeze the covariance-derived zero-fit form `median[d/sqrt(1-clip(I,0,0.95))]`; test on confirmation/transfers. | Positive locked gain over raw disagreement and over at least one of adjacent MAE/output PC in every dataset--model stratum. | COMPLETE—FALSIFIED |
| 7 | P7-TMI-E03 | TMI | Reliability/compute trade-off defines a practical operating regime. | Join Plan6 reliability, calls, latency, memory, storage, and acquisition assumptions into a Pareto audit. | Clear non-dominated regimes, with no generic efficiency claim. | COMPLETE—CONDITIONAL REGIMES |

## Stop rules

- Do not launch mechanism-derived training unless P7-CV-E01/E02/E04 show that shared influence is stable and operationally useful.
- Do not promote a new scalar if adjacent MAE/RMSE or output PC remains equivalent under locked evaluation.
- Negative results update the contribution and risk register; they are not rerun with new weights.
