# Plan7 Final Acceptance Optimization Report

Date: 2026-08-14. Scope: MRI inter-slice / through-plane interpolation only. This report is an evidence audit, not an acceptance guarantee. No submission action has been performed.

## Executive decision

| Candidate | Scientific state | Submission recommendation |
|---|---|---|
| TMI | Controlled physical-overlap contribution, operational QA consequence, metric/factor boundaries and cost regimes are integrated and compiled. | **READY AFTER HUMAN METADATA**; also resolve submission sequence before upload. |
| CVPR | Neural influence robustness experiment is complete; mechanism evidence is credible but local/plane-dependent, and all three Plan7 capability branches failed. | **MERGE / CHANGE SUBMISSION SEQUENCE**; do not concurrently submit the current pair. |

All registered executable high-value Plan7 experiments are complete. Remaining weaknesses require exact human-study metadata, prospective/order-symmetric acquisition, reader/diagnostic validation, new independent external evidence, or a venue/submission-sequence decision. The registered stop rule excludes further scalar tuning and mechanism-derived training on the same test cohorts.

# TMI

## Current central claim

Reusing the same physical slice measurements can align deterministic MRI interpolation errors and make agreement-based reconstruction QA blind, whereas deliberately disjoint contexts expose more error under defined operating conditions.

## Strongest evidence

- 42/42 architecture–cohort–endpoint disjoint-minus-shared error-ranking contrasts are positive across seven endpoints, HAT/SwinIR and three cohorts.
- Shared error fraction is associated with suppressed normalized disagreement after controlling total error and examination (partial Spearman −.746 to −.975).
- Analytical x2/x4/x6 interpolation reproduces increasing shared fraction and decreasing reliability.
- At 70% IXI coverage, disjoint ranking retains 0/29 prespecified high-error examinations versus 2/1/3 for shared/committee/adjacent; smaller cohorts are explicitly uncertain.
- Full-cohort reliability joined to measured calls/latency/storage shows disjoint scoring is conditional, while adjacent-anchor difference is the zero-call default and strongest NingXia common-endpoint nAURC.

## Closest prior work

Closest families include systematic MRI reconstruction-error blindness, leave-one-slice-out interpolation QA, Bayesian/ensemble MRI uncertainty, acquisition perturbation and active MRI sampling. The ten-work matrix in `NOVELTY_COLLISION_AUDIT.md` found no audited work with the same target-preserving physical-anchor reuse intervention plus full geometry→aligned error→cancellation→QA chain. This supports a scoped distinction, never a “first” claim.

## Novelty risk

The error-difference identity and leave-one-slice-out operation are known. Novelty rests on controlled physical measurement dependence, systematic MRI characterization and operational consequence. Residual order-equivariance confounding prevents a pure causal coefficient claim.

## Major reviewer risks

1. Maximal sharing also reverses order; prospective order-symmetric acquisition is unavailable.
2. No reader, pathology, diagnosis or prospective scanner validation.
3. NingXia has only eight patient clusters.
4. Two neural architectures share a 2.5-D input template; scope remains through-plane T2 interpolation.
5. Exact ethics/consent and author metadata require humans.
6. Scientific overlap with the CVPR candidate requires sequencing/disclosure review.

## Experiments added during Plan7

- **P7-TMI-E01:** fixed-coverage high-error false-retention analysis with clustered intervals.
- **P7-TMI-E02:** prespecified endpoint-family mechanism contrast.
- **P7-TMI-E03:** six-way reliability/compute/storage/information operating-regime audit, including explicit N/A TTA reliability where definition-matched IXI evidence is unavailable.
- Ten-paper collision audit, current official venue calibration, paragraph-level overlap audit and four-reviewer/AE adversarial simulation.

## Hypotheses falsified

- Universal stronger blindness for intensity/low-frequency versus structural/high-frequency errors: sign changes across cohorts.
- Universal practicality or superiority of disjoint scoring: adjacent difference wins NingXia and is the zero-call default.
- Metric independence, calibrated uncertainty, clinical safety and plane-level localization remain rejected.

## Claims removed

- Any novelty claim for the elementary algebra or leave-one-slice-out operation.
- Universal metric/frequency law.
- Universal best reliability score or deployment recommendation.
- Diagnostic/patient-safety, calibrated uncertainty and causal identification wording.

## Claims strengthened

- Physical anchor reuse is now separated precisely from generic disagreement theory and closest prior MRI QA.
- The QA consequence has fixed-coverage counts rather than only mean correlations.
- Practicality is defined by information availability, calls, measured latency, storage and acquisition assumptions.
- Fig. 1 now passes the 30-second mechanism test without text/arrow collisions.

## Final recommended title

**Measurement Dependence Governs Disagreement-Based Reliability in Deterministic MRI Slice Interpolation**

## Final contribution bullets

1. Same-target physical measurement-overlap intervention across fastMRI, IXI and patient-clustered NingXia.
2. Multi-endpoint/two-architecture/analytical-factor characterization of shared-error observability and its boundaries.
3. Fixed-coverage MRI reconstruction-QA consequences and explicit operating regimes.

## Final reviewer simulation

- Reviewer 1: **4/5**
- Reviewer 2: **4/5**
- Reviewer 3: **3/5**
- Reviewer 4: **3/5**
- Associate Editor: **4/5 scientific readiness**

The disagreement is genuine: methodology rigor is strong, while clinical and broad reconstruction generality remain limited.

## Remaining human blockers

- Exact NingXia institution, ethics approval identifier and consent/waiver wording.
- Final authorship, affiliations, acknowledgments/conflicts and data-license statements.
- Author/editor decision on TMI-first sequencing and disclosure of related CVPR work.

## Submission recommendation

**READY AFTER HUMAN METADATA.** Scientifically bounded submission candidate exists; do not upload until metadata and sequence are resolved.

# CVPR

## Current central claim

Shared-anchor count is not neural estimator influence: finite-difference response similarity explains local error alignment and disagreement cancellation more precisely, but that mechanism is plane-dependent and does not automatically yield a better reliability score.

## Strongest evidence

- All 18 broad-grid absolute-correlation advantages of neural influence over overlap count are positive (0.036–0.089) with clustered intervals above zero.
- Fixed-count contexts support continuous influence on fastMRI/IXI while NingXia is mixed/null.
- All 42 amplitude/sign/field/direction stability strata pass the frozen gate; minimum rank stability is .942.
- Plane-pair rank stability is .779–.954 and only one of three plane-pair gates passes, establishing a local-analysis boundary.
- Three locked mechanism-derived methods fail without transfer retuning: minimum-influence context selection, multi-anchor jackknife IQR and covariance-derived residualization.

## Closest prior work

Closest families include systematic-error blindness, dependent ensemble uncertainty, leave-one-slice-out reconstruction, self-supervised error prediction, measurement/influence analysis and active acquisition. The distinct CVPR element is the same-physical-anchor finite-response cosine, fixed-count test and falsification portfolio—not consensus blindness, algebra or Anchor-CV alone.

## Novelty risk

The influence statistic may be viewed as an expected sensitivity diagnostic rather than a new capability. Experiments remain within MRI interpolation; no new restoration architecture, general inverse solver or benchmark is provided. Scientific novelty is plausible as a focused empirical finding but weak under a method-paper reading.

## Major reviewer risks

1. No tested capability consistently beats adjacent difference/output PC across cohorts.
2. Two of three physical-plane stability gates fail.
3. The context-ranking arrow is heterogeneous and not causal mediation.
4. NingXia fixed-count result is mixed/null with eight patient clusters.
5. MRI-only breadth and two related 2.5-D architectures limit CVPR-wide generality.
6. Moderate-to-high scientific overlap with TMI persists despite low textual similarity.

## Experiments added during Plan7

- **P7-CV-E01:** development-frozen minimum-influence context selection with random/count/diversity/PC/adjacent/Anchor controls.
- **P7-CV-E02:** full-cohort perturbation magnitude, sign/field, direction-count and three-plane stability audit.
- **P7-CV-E03:** development-selected multi-anchor jackknife with locked confirmation/transfer and conditional analysis.
- **P7-CV-E04:** zero-fit covariance-derived influence residualization.
- New findings-oriented Fig. 1, ten-paper collision audit, current venue calibration, final paragraph overlap audit and five-reviewer/AC/SAC simulation.

## Hypotheses falsified

- Minimum-influence selection transfers as a superior context-selection capability.
- Multi-anchor jackknife adds incremental information beyond adjacent MAE.
- Covariance residualization yields consistent reliability gain.
- Neural influence is invariant across physical planes.
- Integer overlap is a monotone dose, Anchor-CV is uniquely informative, and a universal best reliability score exists.

## Claims removed

- Anchor-CV or any Plan7 branch as a superior method.
- Plane-invariant/global attribution.
- Universal fixed-count effect across all cohorts.
- Causal mediation, calibrated uncertainty, prospective acquisition optimization and cross-domain generalization.

## Claims strengthened

- Perturbation-parameter robustness is now directly demonstrated in all six dataset–architecture strata.
- Plane dependence is quantified rather than hidden.
- The distinction between measurement count and estimator response is sharpened by exact fixed-count controls.
- Failed method gates are in the main paper and supplement, preventing a misleading method narrative.
- Title, abstract, redesigned Fig. 1 and conclusion now reinforce one reviewer-memory message.

## Final recommended title

**Measurement Count Is Not Influence: When Disagreement Hides MRI Interpolation Error**

## Final contribution bullets

1. Neural shared-influence response statistic with a full perturbation/plane robustness boundary across three cohorts and two architectures.
2. Fixed-count and arrow-wise tests of influence→alignment→cancellation/observability, with explicit NingXia and ranking counterexamples.
3. Three locked capability falsifications delimiting why mechanistic explanation does not imply a useful reliability method.

## Final reviewer simulation

- Reviewer 1: **2/5**
- Reviewer 2: **3/5**
- Reviewer 3: **1/5**
- Reviewer 4: **3/5**
- Reviewer 5: **3/5**
- Area Chair: **2/5**
- Senior Area Chair: **MERGE_OR_SEQUENCE_REQUIRED**

## Remaining human blockers

- Author/editor decision to merge or sequence; current concurrent submission is not recommended.
- Exact ethics/consent, authorship, affiliation and conflict metadata.
- A materially independent future capability/broader external evaluation would be new research, not a missing executable control on the current data.

## Submission recommendation

**MERGE / CHANGE SUBMISSION SEQUENCE.** Recommended path: prepare TMI first; then either merge the nonlinear influence audit into the journal workflow or retain CVPR as a later, substantially re-scoped and disclosed findings submission. Do not present the current CVPR candidate as a superior reliability method.

# Cross-paper and stopping audit

- Final paragraph diagnostic: 63 TMI versus 47 CVPR paragraphs; 2 TMI paragraphs exceed TF–IDF cosine .30, none exceed .45, and 0/4,015 audited TMI words fall in matches above .45. This is not CrossCheck or policy clearance.
- Scientific overlap remains moderate-to-high because both depend on the same cohorts, models and measurement-dependence phenomenon. Verdict: `MERGE_OR_SEQUENCE_REQUIRED`.
- TMI owns comprehensive physical-intervention imaging science, endpoint/factor characterization and technical QA consequences.
- CVPR owns nonlinear response influence, fixed-count analysis, arrow-wise mechanism and failed capability gates.
- Mechanism-derived training is not launched: the registered stop rule required operational usefulness, while E01/E04 failed. Further tuning would not remove the core venue/sequence risk.
- No FATAL/MAJOR risk remains with a scientifically meaningful, low-cost experiment executable on the current evidence. Remaining risks require human input, new prospective/external data or venue judgment.

# Verified final artifacts

- TMI: `main.tex`, `main.pdf`, `references.bib`, `CLAIM_TRACEABILITY.md`, `REVIEWER_RISK_AUDIT.md`, `COVER_LETTER_DRAFT.md`.
- CVPR: `main.tex`, `main.pdf`, `supplement.tex`, `supplement.pdf`, `references.bib`, `CLAIM_TRACEABILITY.md`, `REVIEWER_RISK_AUDIT.md`, `REBUTTAL_BANK.md`.
- Compiled layout: TMI main 8 pages; CVPR main 8 pages; CVPR supplement 7 pages. Critical log search finds no undefined references/citations or Overfull boxes after final fixes.
