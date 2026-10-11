# Project Exhaustion Audit

Audit date: 2026-08-13. This audit applies to the currently available repository, datasets, checkpoints, and scientifically motivated controlled tests. It does not assert that the field is exhausted.

## Required domain-by-domain audit

| Area required by Plan 3 | Work performed | Classification | Reason no high-value executable item remains |
|---|---|---|---|
| Current PC mechanism | localization, common-mode blur, intensity controls, formal bound, bound sharpness | EXECUTED | mechanism and one-sided limitation established; further score tuning would reuse outcomes |
| Alternative consistency interventions | 18-profile four-view flip-TTA; shared/factor-dependent blur | EXECUTED | other arbitrary TTA families would be post-hoc perturbation search without a frozen rationale |
| Pre-reconstruction signals | adjacent MAE/RMSE, dynamic range, gradients, spectrum, motion, scale control, IXI replication | EXECUTED | strongest normalized signal is domain-dependent; decisive next test needs untouched data |
| Architecture failure diversity | 3-model two-cohort panel; 13-method fastMRI; 6-method IXI | EXECUTED | shared ranking is stable; new architectures would duplicate the established pattern absent a new inductive-bias hypothesis |
| Factor geometry | continuous spacing, phase, shared anchors, x2/x4/x6 scaling | EXECUTED | x3/x5/x8 or offset anchors require missing predictions/checkpoints/acquisitions |
| Spatial localization | pixel/plane/case levels, relative position, first/interior/last | EXECUTED | anatomical labels or new site are required for stronger regional claims |
| Spectral mechanisms | low/high Gaussian-band and gradient-density analysis | EXECUTED | high-frequency-only hypothesis falsified; richer wavelets would be redundant metric proliferation |
| Common-mode failure | uniform/factor-dependent blur and exact shared-error decomposition | EXECUTED | additional arbitrary corruptions have lower information than new measurement contexts |
| Stable-error failure | 14 natural cases, boundary enrichment, anchor curvature, synthetic deletion | EXECUTED | prevalence/generalization requires another cohort |
| Statistical heterogeneity | cluster bootstrap/permutation, LOO, profile forest, risk curves, variance CIs | EXECUTED | correct independent unit and uncertainty are now explicit |
| Dataset heterogeneity | fastMRI/NingXia descriptors, shared fractions, spectrum, intensity, registration | EXECUTED | causal explanation needs scanner/protocol metadata not present |
| Latent difficulty | orthogonal variance split, peer consensus, full model-family correlations | EXECUTED | confirmed descriptively across three cohorts; prospective prediction needs new data |
| Error decomposition | exact squared-error consensus/diversity identity | EXECUTED | extension to new context families requires new outputs |
| Theoretical extensions | k-context diameter bound and empirical sharpness; exact MSE identity | EXECUTED | upper bounds require assumptions/data not justified by current evidence |
| Compatible uncertainty baselines | committee and flip-TTA over 18 profiles | EXECUTED | learned/calibrated methods would change scope and require training protocol/labels |
| Recent literature | MRI UQ plus inverse restoration, diversity theory, multi-measurement SSL, robustness | EXECUTED | no exact collision; broad consistency/diversity novelty explicitly rejected |
| Broader inverse-problem connections | JMLR diversity theory, ICML restoration robustness, self-supervised SR/imaging | EXECUTED | transferring empirically requires external task data |
| Synthetic mechanistic tests | common blur and asymmetric anchor deletion | EXECUTED | additional unmotivated corruptions would not discriminate live explanations |
| New hypotheses from negatives | diversity-alone, high-frequency, attribution, motion alternatives tested | EXECUTED | remaining successors require new interventions/metadata/data |

## Remaining ideas and formal disposition

| Idea | Classification | Blocking fact |
|---|---|---|
| Untouched anatomy/site shared-error replication | IMPOSSIBLE WITH AVAILABLE RESOURCES | no aligned multi-factor outputs |
| Reader/downstream endpoint | IMPOSSIBLE WITH AVAILABLE RESOURCES | no readers, labels, or approvals |
| Offset sampling grids / heterogeneous physical contexts | IMPOSSIBLE WITH AVAILABLE RESOURCES | acquisition/output protocol absent |
| Additional x3/x5/x8 scaling law | IMPOSSIBLE WITH AVAILABLE RESOURCES | no trained checkpoints or predictions |
| Scanner/protocol mediation of cohort gap | IMPOSSIBLE WITH AVAILABLE RESOURCES | metadata absent |
| Arbitrary TTA family sweep | SCIENTIFICALLY UNJUSTIFIED | would be post-hoc family selection after seeing flip results |
| More score mixtures | LOW INFORMATION VALUE | naive mixtures already fail; no new failure mechanism is addressed |
| More architecture modules/training | REDUNDANT | 11 neural families show shared case ranking; no mechanism predicts a useful new module |
| Retry factor attribution | FALSIFIED | constant x6 dominates every observed unit |
| High-frequency-only PC story | FALSIFIED | low-frequency association is stronger |
| Diversity maximization alone | FALSIFIED / NOVELTY COLLISION | empirical null plus established diversity trade-off theory |
| Clinical correctness from low disagreement | SCIENTIFICALLY UNJUSTIFIED | theorem and natural counterexamples prohibit it |

## Terminal-condition check

1. Formal audit completed: yes.
2. No high-value scientifically justified experiment remains executable with current data/code without post-hoc search: yes.
3. Major frontier successors require new acquisition contexts, untouched data, labels, factors, metadata, or a preregistered perturbation protocol: yes.
4. Continuing locally would mean duplicative decompositions, arbitrary perturbation/module search, or tuning on observed outcomes: yes.
5. Strong and negative findings are preserved in hypotheses, experiment registry, taxonomy, frontier, logs, machine-readable outputs, and milestone report: yes.
6. Remaining blockers are project-level: yes.

## Audit verdict

The **currently executable repository research frontier is exhausted** under Plan-3 rigor. This is not a claim that future research is unnecessary. The program should reopen when a new site/anatomy, offset acquisition context, additional factors, scanner metadata, downstream labels, or a prospectively frozen intervention family becomes available.

