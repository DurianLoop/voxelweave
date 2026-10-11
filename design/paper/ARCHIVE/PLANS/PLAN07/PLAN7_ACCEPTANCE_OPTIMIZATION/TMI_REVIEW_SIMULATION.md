# Adversarial TMI review simulation

Version reviewed: Plan6 submission candidate plus registered Plan7 outputs available on 2026-08-13. Scores use 1–5 research readiness: 1 reject, 2 weak reject, 3 borderline, 4 weak accept, 5 accept. These are diagnostic opinions, not acceptance probabilities.

## Reviewer 1 — MRI reconstruction / inverse problems

**Summary.** The paper shows that paired deterministic interpolators can agree because their contexts reuse physical slice anchors, and tests disjoint versus shared contexts across three MRI cohorts, two networks, seven endpoints and analytical sampling factors.

**Strengths.** The target-preserving intervention is more convincing than a generic ensemble comparison. The authors explicitly concede that the error-difference identity is elementary. Pairing by plane and clustering at examination/patient level are appropriate. Analytical x2/x4/x6 results and exact geometry audit triangulate the neural evidence.

**Weaknesses.** The maximal-shared reversal changes order along with overlap, so the cleanest causal contrast is imperfect. Two 2.5-D architectures may share training biases. The paper still spends too much conceptual space on algebra rather than the imaging decision enabled by the result.

**Novelty.** Consensus blindness and systematic MRI error are known; the controlled physical anchor-reuse characterization appears distinct in the audited literature. Novelty is moderate, not foundational.

**Experimental rigor.** Strong for retrospective methodology. A matched-order disjoint control or prospective interleaved acquisition is missing and likely cannot be recovered from current data.

**Scope/significance.** Relevant to MRI interpolation QA, especially when several reconstructions are used as a confidence proxy. It should not imply general MRI reconstruction calibration.

**Fatal issue if rejecting.** Residual order-equivariance confounding prevents clean attribution solely to anchor reuse.

**Score: 3/5 (borderline).** Could rise to 4 if the final paper foregrounds clean controls/limitations and operational QA consequences.

## Reviewer 2 — uncertainty and statistical validation

**Summary.** A reliability study of how dependent evidence suppresses output disagreement, with error-energy decomposition, endpoint sensitivity and selective-risk evaluation.

**Strengths.** Dense target is kept evaluation-only. The paper distinguishes ranking, calibration and correctness certification. All correlated endpoint rows are reported instead of counted as independent discoveries. NingXia uses eight patient clusters rather than 22 pseudo-independent series.

**Weaknesses.** Spearman and nAURC do not establish calibrated uncertainty. Stable-wrong prevalence is rare under a quartile definition. The proposed endpoint-family explanation fails: IXI and NingXia contrast directions disagree. Confidence intervals for small high-error counts can be very wide.

**Novelty.** The statistical principle is known; the imaging intervention and hierarchy are useful. Prior MRI uncertainty papers must be discussed more comprehensively.

**Experimental rigor.** High if the Plan7 false-retention counts and failed frequency-family hypothesis are included exactly. Multiple analyses are exploratory and should remain labeled as such.

**Scope/significance.** Appropriate as an imaging-method reliability characterization, not a clinical confidence system.

**Fatal issue if rejecting.** Overclaiming metric independence or clinical relevance would invalidate the paper's careful statistics.

**Score: 4/5 (weak accept)** conditional on claim narrowing.

## Reviewer 3 — clinical MRI / quality assurance

**Summary.** The work asks whether agreement among deterministic slice interpolation outputs can safely identify low-error studies and proposes measurement-disjoint comparison as a more informative QA construction.

**Strengths.** The study includes brain and knee data, reports examination-level selection, and compares a zero-call adjacent-anchor screen. The finding that different operating regimes prefer different scores is practically honest.

**Weaknesses.** There is no reader study, pathology enrichment, diagnostic endpoint, prospective scan, rescan decision, or site-specific threshold. “Quality assurance” may be interpreted more clinically than the evidence permits. False-retention reductions are clearest only in IXI at intermediate coverage.

**Novelty.** The physics of reused evidence is informative for method developers. Clinical novelty is limited.

**Experimental rigor.** Retrospective technical validation is substantial. Practical acquisition assumptions need a prominent table: disjoint grids may not exist in routine sparse acquisitions.

**Scope/significance.** TMI can publish imaging-method studies without clinical endpoints, but the manuscript must define QA as technical review prioritization.

**Fatal issue if rejecting.** The operational consequence may be too abstract if no actual missed-examination counts and acquisition requirements appear in the main paper.

**Score: 3/5 (borderline).** Add Plan7 false-retention and cost/assumption evidence; do not add clinical adjectives.

## Reviewer 4 — medical image reconstruction methods

**Summary.** A broad empirical audit of disagreement dependence in through-plane interpolation rather than a new reconstruction architecture.

**Strengths.** Negative results are unusually complete: SSIM heterogeneity, scale sensitivity, no universal best score, and limited localization. The factor ladder and two network families help separate the observation from a single architecture.

**Weaknesses.** The work remains confined to retrospective T2 through-plane interpolation. I3Net is absent from the decisive neural contrast. IXI dominates precision. Some figures/tables may overwhelm the single primary message.

**Novelty.** Sufficient only if the title, Fig. 1 and contribution bullets emphasize the physical intervention rather than disagreement algebra.

**Experimental rigor.** Good, with a concern that the two networks share related 2.5-D inputs. Reproducibility mapping appears strong.

**Scope/significance.** Relevant to deterministic interpolation pipelines and uncertainty audits; transfer to k-space reconstruction is unproven.

**Fatal issue if rejecting.** A reviewer may call it an extensive special-case characterization with limited methodological generality.

**Score: 3/5 (borderline).** The narrow but actionable scope must be argued explicitly.

## Associate Editor simulation

**Synthesis.** Reviewers agree that the algebra is not novel and that no clinical validation exists. They differ on whether the controlled physical intervention plus three-cohort characterization reaches TMI impact. The strongest differentiator is that a recorded acquisition variable—physical anchor reuse—is manipulated for the same target and linked to aligned error, cancellation and selective QA. The strongest avoidable weakness is that the current version underuses the operational evidence and does not state when the extra reconstructions are justified.

**Required before submission.** (1) incorporate P7 operational counts and conditional operating regimes; (2) explicitly report the failed spectral-family ordering; (3) cite the closest systematic-error, leave-one-slice-out and acquisition-perturbation work; (4) keep technical-QA wording; (5) disclose ethics/site metadata as a human blocker; (6) retain the reversal confound and lack of prospective/reader validation.

**AE fatal issue.** If dual submission overlaps materially with the CVPR mechanism paper or if human-study metadata are missing, editorial/ethical processing may fail irrespective of science.

**AE readiness: 3/5 (major revision before external submission).** Scientific revision is executable; prospective and clinical validation are not required to make the bounded technical claim.

## Consolidated TMI decision

Current mean reviewer score is 3.25/5; disagreement is genuine. No reviewer supports a “new uncertainty theory” framing. Three reviewers would be more favorable after inserting already-completed Plan7 analyses. The final gate is therefore manuscript integration and human metadata, not another retrospective score search.

## Plan7 final re-review — 2026-08-14

The final candidate now includes the requested operational false-retention counts, six-way information/cost regime, failed spectral-family explanation, closest-work audit, technical-QA boundary and redesigned impact-led Fig. 1. The reversal/order confound, absence of reader/prospective validation and eight-patient NingXia uncertainty remain explicit.

- **Reviewer 1: 4/5 (weak accept).** The physical intervention is distinct enough when algebraic novelty is disclaimed; residual order confounding remains the main limitation.
- **Reviewer 2: 4/5 (weak accept).** Statistical hierarchy and endpoint honesty are strong; no calibration or metric-independence claim remains.
- **Reviewer 3: 3/5 (borderline).** Operational counts and cost table resolve the avoidable QA objection, but clinical significance remains deliberately untested.
- **Reviewer 4: 3/5 (borderline).** Breadth and negative results are convincing, while domain/architecture generality remains limited.
- **Associate Editor: 4/5 scientific readiness.** The manuscript now meets a bounded medical-imaging methodology standard. Editorial processing still requires exact ethics/consent and submission-sequence review.

**Final TMI verdict: READY AFTER HUMAN METADATA**, with the additional policy condition that the authors resolve TMI/CVPR sequencing before submission. No further retrospective experiment has higher expected value than the unavailable prospective/order-symmetric/reader evidence.
