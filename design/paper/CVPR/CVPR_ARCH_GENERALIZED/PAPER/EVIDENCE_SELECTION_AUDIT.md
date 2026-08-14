# Evidence Selection Audit — CVPR Recovered

This audit covers experiments excluded from the main manuscript. “Contradicts final claim?” refers to the final narrow mechanism claim, not an abandoned broader hypothesis.

| Experiment ID / branch | Result | Why excluded from main | Contradicts final claim? | Preserved at |
|---|---|---|---|---|
| Plan2 factor-pair and endpoint-sensitivity branches | No single factor-pair or monotone-distance explanation | Secondary discovery history; does not decide shared-influence mechanism | No | `plan2_outputs/`, `PLAN2_EXECUTION_SUMMARY.md` |
| Plan2 localization | Pixel/plane evidence heterogeneous | Final claim is examination-level; localization failure is summarized in supplement | No; limits localization | `plan2_outputs/localization/`, supplement Sec. 8 |
| Plan2 TTA uniqueness test | Inconclusive for universal perturbation superiority | Final paper does not claim superiority over every perturbation | No | `plan2_outputs/`, Plan2 logs |
| Plan3 spectral/high-frequency hypothesis | High-frequency-only account fails | Abandoned mechanism; final claim is measurement influence, not spectral law | No | `plan3_outputs/spectral_spatial*`, `PLAN3_RESEARCH_REPORT.md` |
| Plan3 motion proxy | No common dominant motion explanation | Noncentral to measurement-dependence claim | No | `plan3_outputs/motion_proxy*` |
| Plan3 triangle/joint witness | Does not attribute the bad factor | Noncentral geometry diagnostic | No | `plan3_outputs/*triangle*`, `joint_witness*` |
| Plan3 diversity-only hypothesis | More diversity alone does not predict witness quality | Final paper explicitly rejects “maximize diversity” | Supports boundary | `plan3_outputs/diversity_validation*` |
| Plan3 naive input/PC fusion | Harms ranking | Abandoned fusion; no fusion claim remains | No | `plan3_outputs/`, `PLAN3_RESEARCH_REPORT.md` |
| C5-E002 order-reversal covariance chain | Full chain on IXI/NingXia; several arrows reverse on fastMRI due to confounding | Clean horizontal-equivariance control is the valid main contrast; confound is explained in supplement | No; prevents use of reversal as pure causal evidence | `overlap_covariance*`, supplement Sec. 3 |
| C5-E004 initial budget curves | Near oracle fastMRI, not universally best NingXia | Superseded by frozen Plan6 consequence and stronger baselines | No | `budget_benefit_curves.*` |
| C5-E006 orthogonal two-component model | Frozen confirmation gate fails | Abandoned method; no combined-score claim | No | `orthogonal_two_component*`, experiment registry |
| C5-E007–E009 acquired-anchor bipartition | Positive but not universally best | Secondary method; Anchor-CV is simpler and main practical consequence | No | `acquired_anchor_bipartition*`, `bipartition_budget_curves*` |
| P6-E01 full seven-metric table | Direction positive 42/42; SSIM and some smaller-stratum intervals weak | Too detailed for main; necessary boundary is in supplement | No; limits metric-independence | TMI master experiments; supplement Sec. 3 |
| P6-E03 geometry/intensity grids | Geometry exact; common scaling preserves contrast; normalization changes ranks | Validation detail, not central result | No; limits invariance | TMI master experiments; supplement |
| P6-E07 full risk–coverage curves | Strong triage, no universal winner | Main uses representative consequence; complete curves remain supplementary | No; limits superiority | `plan6_frozen_risk_coverage*` |
| P6-E08 naive feature stacking | Does not improve ranks; poor IXI calibration | Abandoned combination method | No | `plan6_intrinsic_difficulty*` |
| P6-E09 failure taxonomy | Rare discordance; scores do not localize worst plane | Main is examination-level; localization boundary summarized | No; limits localization | `plan6_failure_taxonomy*`, supplement Sec. 8 |
| P6-E11 x2/x4/x6 analytical factor robustness | Shared fraction rises and observability falls with factor | Strong but secondary robustness; prevents an everything-table | Supports claim | TMI master experiments |
| P6-E12 full three-cohort risk–coverage | Disjoint beats shared output scores; adjacent MAE wins NingXia | Main focuses mechanism; the unfavorable baseline remains in supplement | No; limits deployment superiority | TMI master experiments |
| P7-CV-E01 minimum-influence selector | Strong fastMRI confirmation; below random/PC IXI; heterogeneous NingXia | Abandoned capability, not required for mechanism | No; contradicts prescriptive selector claim only | Plan7 outputs; supplement Sec. 8 |
| P7-CV-E03 multi-anchor jackknife IQR | Development .629→confirmation .399; adjacent MAE .944; poor transfer | Abandoned capability | No | Plan7 outputs; supplement Sec. 8 |
| P7-CV-E04 influence residualization | Tie/loss fastMRI, negligible IXI gain with CI crossing zero, mixed NingXia | Abandoned capability | No | Plan7 outputs; supplement Sec. 8 |
| Plan7 TMI metric/operational/regime experiments | Relevant to the companion journal narrative | Not evidence needed to evaluate this CVPR shared-influence claim | No | `PLAN7_ACCEPTANCE_OPTIMIZATION/outputs/p7_tmi_*` |

## Material counterevidence retained in the submitted package

The following cannot be omitted because doing so would invite a stronger false inference: the count-ladder reversal, NingXia fixed-count null/mixed result, physical-plane dependence, weak global-ranking arrow, Anchor-CV baseline equivalence, failed localization, lack of calibration, and retrospective-only densification. Each appears in the main paper or supplement and is mapped in `CLAIM_TRACEABILITY.md`.

## Audit verdict

No excluded experiment invalidates the submitted central claim. Exclusions remove chronological and redundant branches, not unfavorable evidence needed to evaluate that claim.
