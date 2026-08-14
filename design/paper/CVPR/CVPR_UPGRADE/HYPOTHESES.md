# CVPR Upgrade Hypotheses

All experiments remain within MRI inter-slice interpolation. Dense targets are evaluation-only. IXI-T2 test-115 is the third cohort from C5-E005 onward.

| ID | Frozen prediction / decision rule | Outcome | Status |
|---|---|---|---|
| C5-H01 | overlap up → error alignment/shared fraction up → observable fraction/ranking down | supported in NingXia/IXI reversal chain; fastMRI reversal contradicts several arrows and is labeled confounded | PARTIAL / BOUNDED |
| C5-H02 | valid overlap levels show lower observability as overlap rises | strict multi-level ladder infeasible; clean zero/max endpoint contrast supports ranking effect in all three cohorts | SUPPORTED FOR TWO VALID LEVELS |
| C5-H03 | low error-dependence context design should outperform raw diversity | acquired-anchor bipartition ranks error across cohorts; not universally best in allocation | PARTIAL |
| C5-H04 | disjoint signal predicts densification benefit at 10/20/30/50% budgets | above random on fastMRI; budget- and cohort-dependent on NingXia | PARTIAL |
| C5-H05 | a separated shared/context-sensitive two-component model improves held-out ranking and nAURC | frozen confirmation gate failed | REJECTED |
| C5-H06 | residualized input difficulty improves both fastMRI confirmation endpoints | endpoints identical to disjoint-only baseline | REJECTED (C5-E006) |
| C5-H07 | acquired-anchor bipartition ranks x4 error and x4→x2 benefit without new measurements | pilot passed; frozen neural extensions support error ranking in all cohorts and benefit association except uncertain NingXia/SwinIR | SUPPORTED WITH BOUNDARY |
| C5-H08 | context dropout/diversification improves reconstruction | not launched after method threshold audit | NOT RUN |
| C5-H09 | analytical bipartition reproduces the neural geometry signal | all three x4-error CIs and both available benefit CIs above zero | SUPPORTED |
| C5-H10 | analytical bipartition improves fixed-budget allocation | fastMRI all budgets; NingXia 20/30/50%, not 10%; not universally best | PARTIAL |
| C5-H11 | clean maximal overlap increases stable-wrong prevalence under zero-derived fixed thresholds | increases of 20.9–28.2 percentage points; all cluster CIs above zero | SUPPORTED |
| C5-H12 | acquired-anchor CV ranks error and benefit without x8 inference | all error CIs and both benefit CIs above zero; fastMRI local endpoint fails | SUPPORTED FOR EXAMINATION TRIAGE |
| C5-H13 | wide exact ladder is strictly monotone | IXI has a `0→1` exception; NingXia monotone; fastMRI ineligible | REJECTED AS STRICT LAW |
| C5-H14 | compact ladder preserves overall trend signs across cohorts | all trend signs reproduced; all cohorts retain `0→1` exception | SUPPORTED / NONMONOTONE |
| C5-H15 | coefficient influence explains configuration endpoints better than count | same direction in all cohorts; all clustered advantage CIs positive | SUPPORTED |

## Key derivations retained before evaluation

### C5-H06 — Orthogonal two-component risk

Disjoint disagreement was treated as context-sensitive evidence. Adjacent-anchor change was residualized against it on a fixed 12-case fastMRI development split, then entered a nonnegative error-rank regression. The complementary 12 cases were the frozen confirmation split. Failure to improve both Spearman and nAURC forced rejection regardless of transfer results.

### C5-H07 — Acquired-anchor bipartition

The acquired x4 lattice was divided into anchors `z=0,8,16,...` and `z=4,12,20,...`. At jointly bracketed targets, both contexts use two anchors with the same unordered distance pair `{2,6}` and share no measurement. The pilot gate—first eight lexicographic fastMRI cases, HAT, benefit rho >0.5 and positive plane-error rho—was fixed before inference. The neural stride-8 OOD limitation was also predicted before evaluation.

### C5-H09/H10 — Analytical and allocation consequences

Two-point linear interpolation was substituted without cohort-specific tuning to test whether C5-H07 was merely neural OOD behavior. After the positive association test, all four budgets and the full baseline set were registered before allocation results were computed.

### C5-H11 — Stable-wrong endpoint

Within each dataset/model, high error is `>=` the zero-overlap error Q75 and low disagreement is `<=` the zero-overlap score Q25. Those same zero-derived thresholds are applied to both paired conditions. This definition was fixed before computing C5-E010.

## C5-H12 — Acquired-anchor cross-validation residual

- Observed failure: the neural bipartition score invokes x4-trained models at stride 8, while the analytical bipartition is an indirect disagreement witness.
- Derived intervention: for each interior acquired x4 anchor, withhold it, linearly reconstruct it from its two neighboring acquired x4 anchors, and measure the error against the withheld acquired anchor. This uses only measurements already available at deployment and turns an acquired slice into a local pseudo-target.
- Score: median masked leave-one-anchor-out MAE per examination. For local analysis, each missing x4 target receives the mean residual of its adjacent acquired anchors when both exist.
- Falsifiable predictions fixed before computation: (1) positive case-level association with stored x4 reconstruction error in fastMRI, NingXia, and IXI; (2) positive association with stored x4-to-x2 benefit in fastMRI and NingXia; (3) at least one cohort shows higher benefit correlation than adjacent-anchor RMSE and the analytical bipartition score.
- Failure rule: report all cohorts, both architectures, 5,000 case/patient-cluster intervals, and all 10/20/30/50% budget points; no cohort-specific transform or threshold.

## C5-H13 — Four-anchor exact overlap ladder

- Geometric advance: the two-anchor ladder is impossible, but a four-anchor estimator can hold the absolute distance multiset fixed while changing the sign/location of individual anchors.
- Frozen geometry: target-relative distances `{2,4,6,8}`; reference signs `(+,-,+,-)`. At overlap levels 0/1/2/3/4, enumerate every sign vector matching the reference in exactly that many positions, retain only vectors with anchors on both sides of the target, and average metrics across all retained configurations.
- Estimator: the same distance-weighted local linear regression at the target for every context, with weights `1/distance`. Four measured slices, preprocessing, target, distance multiset, and mask are constant.
- Falsifiable prediction: increasing overlap monotonically increases error cosine/shared fraction and decreases observable fraction/disagreement magnitude; reliability ranking should non-increase before becoming undefined at identical-context overlap 4.
- Failure rule: report all five levels and all three cohorts; no removal of nonmonotone levels. This is a retrospective analytical acquisition experiment, not the deployed neural protocol.

## C5-H14 — Compact four-anchor ladder replication

- Motivation fixed from eligibility, not endpoint values: C5-E012's `{2,4,6,8}` window exceeds the half-depth of every shallow fastMRI volume and four NingXia series. Use `{1,2,3,4}` so the same exact-overlap construction is evaluable in all cohorts.
- Geometry, reference signs, enumeration, estimator, masks, endpoints, and inference remain identical to C5-H13; only the prespecified absolute distance multiset changes.
- Prediction: the overall overlap trends have the same signs in all cohorts. Strict level-by-level monotonicity is reported but not required after C5-E012 revealed an IXI 0→1 exception.
- Failure rule: no case or level exclusion beyond the fixed bracketing/depth rule; retain the wide-window result as primary mechanistic evidence and label this as post-boundary exploratory replication.

## C5-H15 — Shared influence, not shared count

- Observation motivating the hypothesis: both four-anchor ladders show the same 0→1 exception, while their overall trends retain the predicted signs. Reliability rho stays uniformly high. Therefore integer overlap count is not a sufficient causal dose.
- Derived variable: express each local linear estimator as a coefficient vector over the union of physical anchor positions. Define shared influence as the cosine similarity of the two coefficient vectors; also report signed dot product and common absolute coefficient mass. These are target-free properties of the estimator and acquisition geometry.
- Falsifiable prediction fixed before computation: across every valid compact-ladder configuration (not level averages), coefficient-vector similarity ranks mean error cosine/shared fraction more strongly and observable fraction/disagreement more negatively than raw overlap count, in all three cohorts.
- Confirmation rule: same directional comparison in all cohorts and no tuning of the influence definition. Failure leaves C5-H13/H14 as a nonmonotone negative ladder result.
