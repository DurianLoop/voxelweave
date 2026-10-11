# Plan-8B Core Result Table

All intervals are 95% examination- or patient-cluster bootstrap intervals unless noted. Dense targets are used for retrospective evaluation, never in the test-time scores.

| Question | Frozen evidence | Effect size | Role |
|---|---|---|---|
| Does physical measurement dependence hide error? | Same target, model, anchor count/distances, mask and preprocessing; zero-overlap phase grids versus clean maximal-sharing flip control | Disjoint-minus-shared error-ranking rho: fastMRI .092 [.043,.176], IXI .095 [.078,.126], NingXia .193 [.111,.371] | CORE |
| How much error is hidden under clean sharing? | Exact paired-error decomposition | Shared error fraction: 97.39% fastMRI, 98.42% IXI, 99.75% NingXia; observable fraction: 2.61%, 1.58%, .25% | CORE |
| Are stable-wrong cases an operationally visible consequence? | Fixed zero-condition joint-quartile thresholds | High-error/low-disagreement prevalence rises by 27.1 pp [12.0,43.8], 20.9 pp [15.6,26.2], and 28.2 pp [10.8,43.9] on fastMRI/IXI/NingXia | SUPPORTING |
| Does the intervention generalize across estimators? | HAT/SwinIR disjoint contexts plus analytical linear/cubic estimators | Disjoint case-level error rho: HAT/SwinIR .961/.955 fastMRI and .910/.903 NingXia; linear/cubic .977/.974 fastMRI and .958/.967 NingXia | SUPPORTING |
| Is raw shared-anchor count a sufficient dose? | Exact compact four-anchor analytical ladder | Overall endpoint trends have |rho|=.9--1.0, but every cohort reverses at 0→1 overlap; strict monotonicity is falsified | CORE BOUNDARY |
| Is analytical influence better than count? | All 14 valid compact configurations | Common coefficient mass versus error alignment rho: .815/.789/.855 versus count .503/.466/.630 on fastMRI/IXI/NingXia; all advantage intervals above zero (.189--.283) | CORE |
| Is nonlinear local influence better than count? | Frozen HAT/SwinIR finite responses, three planes/exam, 24 fastMRI, 115 IXI, 8-patient NingXia | Error-alignment rho, influence/count: .838/.799 and .851/.796 fastMRI; .797/.714 and .787/.712 IXI; .786/.743 and .772/.735 NingXia. Across 18 primary alignment/decomposition endpoints, advantages .036--.089 with intervals above zero | CORE |
| Does influence add beyond a fixed overlap count? | Exactly one shared anchor, geometry/examination partial ranks | Supported for every endpoint/model on fastMRI and IXI (|rho|=.135--.587); null/mixed on NingXia, all intervals cross zero | CORE BOUNDARY |
| Is local neural influence numerically stable? | Plan-7 amplitude/sign/field/direction audit | All 42 perturbation strata pass; minimum rank stability .942. Only one of three physical-plane gates passes; plane-pair rho .779--.954 | SUPPORTING / BOUNDARY |
| Does the proposed local chain hold? | Arrow-wise partial ranks | Influence→alignment .219--.410; alignment→normalized disagreement −.933 to −.889; influence→observable fraction −.412 to −.211; every local-arrow interval excludes zero | CORE |
| Does local alignment guarantee globally worse ranking? | Eight context configurations | Expected direction in all six strata, but intervals exclude zero in only 3/6; no mediation or universal-ranking theorem | BOUNDARY |
| Is examination difficulty architecture-stable? | HAT/SwinIR x4 error | Case-error rank .989/1.000/.997 and examination identity explains 99.1%/99.99%/99.78% across fastMRI/IXI/NingXia | SUPPORTING |
| Does Anchor-CV track x4 difficulty? | Acquired-only leave-one-anchor residual | Spearman .943 fastMRI, .955 IXI, .958 NingXia. Adjacent MAE is .934/.956/.973; Anchor-CV is not uniquely informative | PRACTICAL CONSEQUENCE / BOUNDARY |
| Does acquired-only triage track densification value? | Frozen retrospective x4→x2 endpoint | Anchor-CV versus benefit rho .871 fastMRI and .948 IXI; IXI oracle-normalized gains .920/.936/.972/.973 at 10/20/30/50% budgets | PRACTICAL CONSEQUENCE |
| Is Anchor-CV universally best? | Adjacent MAE/RMSE, output PC, risk curves and budgets | No. Adjacent difference is statistically indistinguishable; output PC reaches .970 versus IXI benefit and .996 oracle-normalized gain at 50% | REQUIRED BOUNDARY |

## Main-text priority

The main paper should lead with the first, second, fifth, sixth, seventh, ninth, and thirteenth/fourteenth rows. Exact strata, metric robustness, stability details, and all material counterevidence belong in the supplement. Failed minimum-influence selection, jackknife IQR, and covariance residualization are audit results, not main-paper contributions.
