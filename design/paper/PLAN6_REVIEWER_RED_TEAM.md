# Plan6 Reviewer Red Team

Date: 2026-08-13. Each attack below is mapped to evidence, a clarification, a limitation, or a rejected claim.

## TMI Reviewer 1 — “Is this clinically or medically relevant?”

Attack: The paper studies correlations between interpolators rather than diagnostic outcomes.

Response: Keep the claim at imaging-quality triage. Through-plane interpolation is used to densify anisotropic MRI; false confidence can conceal stable smoothing or anatomy loss. Three MRI cohorts include a public large IXI set and an external NingXia cohort. Risk–coverage and retrospective densification quantify operational consequences. Do not claim diagnostic safety, lesion detection, or prospective scan control without reader studies/prospective data.

Required manuscript action: state the intended use as reconstruction QA prioritization; place diagnostic validation in limitations.

## TMI Reviewer 2 — “This is an elementary algebraic curiosity.”

Attack: The disagreement identity is obvious.

Response: Agree that the identity is not novel. The contribution is identifying shared physical slice measurements as a controllable source of correlated error and testing it across neural/analytical estimators, factors, endpoints and cohorts. P6-E02/E03/E11/E12 convert the algebra into falsifiable predictions.

Required manuscript action: label the identity as a starting point; give novelty to the physical intervention and complete characterization.

## TMI Reviewer 3 — “Your patient statistics are inflated.”

Attack: NingXia has 22 sequences but only eight patients.

Response: All Plan6 NingXia intervals resample patient clusters; tables must report “22 series / eight patients.” Pixel and plane counts are descriptive, never independent clinical units.

Required manuscript action: repeat the hierarchy in Abstract/Methods/table captions; include cluster IDs in trace tables.

## TMI Reviewer 4 — “Does it survive error metrics and imaging conditions?”

Attack: The score is designed around MAE and may fail structurally.

Response: P6-E01 covers seven endpoints and all three cohorts. Direction is positive in 42/42 point comparisons, with stable intensity/frequency endpoints, but SSIM is weak or negative on fastMRI/NingXia. P6-E03 verifies geometry and common-scale normalization; P6-E11 covers x2/x4/x6.

Decision: claim broad, not metric-independent, reliability. Highlight SSIM as a boundary.

## TMI Reviewer 5 — “Measurement-disjoint reconstruction is impractical.”

Attack: It requires extra contexts/predictions and may be slower than a simple input score.

Response: P6-E10 quantifies two neural calls and 0.25–3.20 s per representative case versus 0.42–3.97 ms for acquired-only Anchor-CV. Measurement-disjoint is a mechanism probe and output-based reliability option, not always the cheapest method. Adjacent MAE wins NingXia risk ranking.

Decision: reject universal deployment-superiority language.

## CVPR Reviewer 1 — “Overlap dependence is obvious.”

Attack: Sharing inputs should make outputs similar.

Response: Similar outputs are not the central result. The count-only law is falsified; finite-difference neural influence improves alignment/observable-fraction association over overlap count in all broad-grid strata. Fixed-count contexts show continuous influence effects in fastMRI/IXI, with explicit NingXia nonreplication.

Required manuscript action: lead with count falsification and influence heterogeneity, not an obvious zero-vs-two comparison.

## CVPR Reviewer 2 — “Coefficient analysis applies only to linear estimators.”

Attack: Analytical weights do not prove neural behavior.

Response: P6-E04 perturbs physical anchors in frozen HAT/SwinIR networks using four registered Rademacher fields and three planes per case. Local response overlap predicts error alignment after case/geometry control. Label this a local finite-difference approximation, not a global neural theorem.

## CVPR Reviewer 3 — “Anchor-CV is just adjacent-slice difference.”

Attack: The method is a needlessly complex second difference.

Response: P6-E06 largely agrees. Anchor-CV is a foreground-masked local second-difference residual; adjacent MAE/RMSE are statistically indistinguishable and sometimes rank better. The independent-information claim is rejected.

Decision: retain Anchor-CV only as a simple acquired-data score with zero neural calls; do not sell complexity or superiority.

## CVPR Reviewer 4 — “Where is the causal mechanism?”

Attack: Correlation among influence, alignment and disagreement is not causal mediation.

Response: P6-E05 separately tests registered arrows with case/geometry controls. Three local arrows are stable in all strata; the final context-ranking arrow is only partial. Perturbing anchors is an intervention on model input, not anatomy or acquisition.

Decision: use “mechanism-consistent associations” and “finite-difference intervention,” never full causal mediation.

## CVPR Reviewer 5 — “Where is the method contribution?”

Attack: The paper mainly audits failures and Anchor-CV is not best.

Response: The method contribution is deliberately modest: an acquired-only examination difficulty score coupled to a design principle for constructing less-dependent reliability pairs. Its value is cost/availability, not best nAURC. The stronger contribution is diagnostic/mechanistic.

Risk: This may be below CVPR’s method novelty bar. The paper must devote sufficient space to neural influence definition, controlled ladder, and consequence evidence.

## CVPR Reviewer 6 — “This is a niche MRI observation.”

Attack: No evidence outside MRI.

Response: Do not add unrelated domains. State the general principle carefully: disagreement observes error components that differ between predictors; shared measurements can align the hidden component. Evidence and claims remain MRI inter-slice interpolation. Generalization elsewhere is a hypothesis, not an empirical claim.

## CVPR Reviewer 7 — “Why trust eight-patient NingXia?”

Attack: External evidence is underpowered and series are correlated.

Response: Cluster by eight patients, show wide intervals, and treat the null/mixed fixed-count result as heterogeneity rather than failure to report. Main confirmation also uses 24 fastMRI and 115 IXI examinations. NingXia supports broad-grid mechanism direction but limits universality.

## Cross-paper red-team decisions

1. Remove “first” claims unless limited to the physical measurement-overlap intervention in MRI interpolation.
2. Cite leave-one-slice-out interpolation and MRI systematic-error prediction as explicit precursors.
3. Do not call Anchor-CV independent confirmation on cohorts used during development.
4. Do not call x4→x2 a prospective policy or same-model causal effect; IXI uses frozen cross-estimator endpoints.
5. Do not upload the 20-page TMI master as manuscript-like supplemental material under current TMI rules.
6. Preserve all negative results in the master and the decisive ones in submission versions.
