# CVPR Plan-8B Mechanism-Paper Scorecard

Date: 2026-08-14. Scale: 1 (poor) to 5 (strong). The paper is scored as a mechanism-first computer-vision/medical-imaging paper, not as a reconstruction leaderboard paper.

## Recovered contribution

> Disagreement is only as informative as the independence of the information generating the compared predictions. In deterministic MRI slice interpolation, shared local estimator influence aligns reconstruction errors and cancels them in prediction differences; target-preserving measurement-disjoint contexts expose more of the error. Acquired-anchor cross-validation is a lightweight examination-level consequence, not a universally superior uncertainty estimator.

| Dimension | Score | Evidence and remaining risk |
|---|---:|---|
| Novelty | 4 | The algebra, ensemble diversity, MRI UQ, and leave-one-slice-out checks are known. The scoped novelty is the same-target physical measurement-dependence intervention plus analytical/neural shared-influence refinement and its link to error observability. MRI-only scope and overlap with the TMI study remain risks. |
| Importance | 4 | Reliability estimates built from dependent predictions are common; the work shows why agreement can be false reassurance. Clinical safety and prospective acquisition utility are not established. |
| Mechanistic depth | 5 | Exact error decomposition, controlled shared/disjoint contexts, coefficient influence, nonlinear finite-response influence, fixed-count tests, and arrow-wise associations form a coherent chain. The final global-ranking arrow is weaker and no causal mediation claim is made. |
| Experimental rigor | 4 | Three cohorts, two frozen neural architectures, linear/cubic analytical estimators, clustered intervals, registered gates, IXI with 115 examinations, and preserved negative results. NingXia has only eight patient clusters; the neural grid is not perfectly distance matched. |
| Predictive validity | 4 | Anchor-CV ranks x4 difficulty at rho .943/.955/.958 and tracks x4-to-x2 benefit on fastMRI/IXI (.871/.948). It is statistically similar to adjacent difference and output PC can be stronger. |
| Reproducibility | 5 | Frozen manifests, checkpoints, seeds, per-case outputs, scripts, decision rules, and claim traceability are present. Exact human metadata and external data-license confirmation remain submission-time tasks. |
| Reviewer resilience | 4 | The rewrite directly answers the obviousness, linear-only, perturbation-artifact, small-cohort, and method-superiority attacks. Venue breadth and related-paper sequencing remain the largest non-experimental risks. |
| Methodological consequence | 3 | Anchor-CV is simple, acquired-only, fast, and useful for examination triage, but not uniquely informative or universally best. This dimension is explicitly non-mandatory for viability. |

## Score history

| Evaluation frame | Novelty | Importance | Mechanism | Rigor | Reviewer resilience | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Plan 6 innovation score | 4 | 4 | 5 | 4 | 4 | Mechanism plus Anchor-CV was judged viable before the strongest baseline/capability stress tests. |
| Plan 7 adversarial method-paper review | 2 | 3 | 4 | 4 | 2 | Median reviewer score was 2/5 because failed selectors/corrections and no SOTA reconstruction method were treated as central acceptance gates. |
| Plan 8B mechanism-paper score | 4 | 4 | 5 | 4 | 4 | The failed branches still constrain claims, but they no longer define the scientific mechanism as failed. Plane dependence is correctly interpreted as a local-property boundary. |

The recovery is not a numerical reset. Novelty and resilience rise because the paper now asks the supported question and separates central falsifiers from abandoned method branches. Rigor remains 4 rather than 5 because NingXia is small, causal mediation is not identified, and no prospective study exists.

## Viability judgment

Mechanism-paper viability: **WEAK-ACCEPT CALIBER AFTER HUMAN POLICY/METADATA REVIEW**. The strongest positive case is the combined controlled intervention, cross-cohort shared-influence evidence, and practical examination-level consequence. The strongest negative case is venue breadth plus scientific overlap with the related TMI manuscript; the papers must not be submitted concurrently without a compliant sequencing/disclosure decision.
