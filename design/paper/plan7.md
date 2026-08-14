# PLAN 7 — Pre-Submission Acceptance Optimization Goal

## Adversarially Improve TMI and CVPR Until Remaining Reject Risks Are Minimized

/goal

Continue the complete MRI inter-slice interpolation research program under:

`D:\MRI\design\paper`

The current Plan-6 state is NOT the end of the research process.

Both manuscripts already have sufficient length.

Therefore:

**DO NOT optimize page count anymore.**

The objective of Plan-7 is:

> **Maximize the scientific strength, reviewer resilience, clarity, novelty positioning, experimental credibility, and practical relevance of both manuscripts by identifying the most likely reasons for rejection and resolving them through targeted new experiments, stronger theory, better controls, updated literature, or claim revision.**

The goal is NOT to guarantee acceptance.

Acceptance cannot be guaranteed.

The goal is to make each submission as scientifically defensible and competitive as the available data, compute, and evidence allow.

Remain entirely within:

**MRI inter-slice / through-plane interpolation.**

Do not add unrelated domains merely to make the papers appear broader.

---

# 0. CURRENT STATE

Plan-6 already produced:

## TMI

* approximately 19-page complete research master;
* compliant short submission manuscript;
* multi-endpoint robustness;
* consensus-error decomposition;
* geometry/intensity controls;
* x2/x4/x6 analytical factor analysis;
* full risk–coverage;
* retrospective densification;
* failure taxonomy;
* cost analysis.

## CVPR

* full eight-page scientific manuscript;
* supplementary material;
* three-cohort evidence;
* neural finite-difference shared influence;
* analytical shared-influence formulation;
* fixed-count control;
* mechanism-chain analysis;
* Anchor-CV;
* simple input baselines;
* risk–coverage;
* IXI x2 consequence;
* failure taxonomy;
* computational cost.

These are now **submission candidates**, not page-expansion drafts.

---

# 1. CREATE PLAN-7 WORKSPACE

Create:

`D:\MRI\design\paper\PLAN7_ACCEPTANCE_OPTIMIZATION`

Within it maintain:

`ACCEPTANCE_RISK_REGISTER.md`

`EXPERIMENT_QUEUE.md`

`NOVELTY_COLLISION_AUDIT.md`

`TMI_REVIEW_SIMULATION.md`

`CVPR_REVIEW_SIMULATION.md`

`VENUE_CALIBRATION.md`

`CLAIM_EVIDENCE_MATRIX.md`

`DECISION_LOG.md`

`RESEARCH_STATE.md`

`NEGATIVE_RESULTS.md`

`SUBMISSION_OVERLAP_AUDIT.md`

Do not overwrite Plan-1 through Plan-6 artifacts.

All Plan-7 work must be traceable.

---

# 2. FIRST PRINCIPLE

From now on, do not ask:

> “What more experiments can we run?”

Ask:

> **“What is the most likely reason a strong reviewer would reject this paper?”**

Then ask:

> “What is the cheapest decisive experiment, theoretical derivation, literature audit, figure, or claim correction that would reduce that risk?”

Prioritize by:

`expected acceptance impact / scientific cost`.

Do not maximize experiment count.

---

# 3. VENUE CALIBRATION

Before changing either manuscript, study the CURRENT official criteria for:

* IEEE Transactions on Medical Imaging;
* target-year CVPR, or the latest available CVPR rules if the target-year kit is unavailable.

Use only official venue documentation for policy.

Then construct two venue calibration sets.

---

## TMI calibration set

Identify approximately 20–30 recent high-quality TMI papers most related to:

* MRI reconstruction;
* MRI interpolation;
* reconstruction reliability;
* uncertainty;
* computational imaging;
* quality control.

Analyze—not imitate—their:

* problem significance;
* novelty level;
* experimental breadth;
* number of cohorts;
* statistics;
* clinical/imaging relevance;
* figure density;
* limitations;
* contribution structure.

---

## CVPR calibration set

Identify approximately 20–30 recent CVPR/ICCV papers related to:

* inverse problems;
* reconstruction;
* reliability;
* uncertainty;
* algorithmic stability;
* disagreement;
* measurement dependence.

Analyze:

* what makes the contribution CVPR-level;
* whether the central contribution is mechanism, method, theory, benchmark, or capability;
* how much experimental evidence supports the main claim;
* what kind of novelty is required beyond a domain-specific observation.

Do not copy wording, structure, figures, or ideas.

Create:

`VENUE_CALIBRATION.md`.

---

# 4. ADVERSARIAL REVIEW BEFORE NEW EXPERIMENTS

Pretend both papers have already been submitted.

Simulate:

## TMI

* 4 expert reviewers;
* 1 Associate Editor.

## CVPR

* 5 skeptical reviewers;
* 1 Area Chair;
* 1 Senior Area Chair.

Each reviewer must independently answer:

### Summary

What does the paper actually contribute?

### Strengths

What is genuinely convincing?

### Weaknesses

What would justify rejection?

### Novelty

What is new versus closest work?

### Experimental rigor

What evidence is missing?

### Scope / significance

Why should the venue care?

### Fatal issue

If forced to reject the paper for one reason, what would it be?

### Score

Use an internal 1–5 research-readiness score.

Do not inflate scores.

The reviewers should actively disagree where reasonable.

Create:

`TMI_REVIEW_SIMULATION.md`

and:

`CVPR_REVIEW_SIMULATION.md`.

---

# 5. BUILD AN ACCEPTANCE RISK REGISTER

For every objection classify:

### Severity

* FATAL
* MAJOR
* MODERATE
* MINOR

### Probability

* HIGH
* MEDIUM
* LOW

### Resolution

* EXPERIMENT
* THEORY
* ANALYSIS
* LITERATURE
* WRITING
* LIMITATION
* HUMAN INPUT
* UNRESOLVABLE

Calculate an internal priority:

`risk priority = severity × probability × resolvability`.

Work on the highest-priority FATAL/MAJOR risks first.

---

# PART I — TMI ACCEPTANCE OPTIMIZATION

# 6. TMI CORE OBJECTIVE

The TMI paper must convince reviewers that this is:

> **a significant medical-imaging methodology contribution**

rather than:

> an elementary disagreement identity applied to MRI.

The current algebra alone is NOT novel.

The novelty must remain centered on:

* physical measurement reuse;
* correlated reconstruction error;
* consensus blindness;
* controlled measurement-overlap intervention;
* systematic MRI characterization;
* consequences for reconstruction quality assurance.

---

# 7. TMI RISK A — “THE THEORY IS OBVIOUS”

This is likely one of the strongest rejection attacks.

Do not defend novelty by claiming that:

`||e1-e2||`

cancels shared error is novel.

It is not.

Instead determine whether the following chain is sufficiently novel and demonstrated:

`MRI sampling geometry`

→

`shared physical measurements`

→

`aligned reconstruction failure`

→

`disagreement blindness`

→

`reliability failure`.

Perform an updated prior-art search specifically for:

* shared measurement uncertainty;
* correlated reconstruction error;
* disagreement under dependent estimators;
* leave-one-slice-out MRI QA;
* cross-validation reconstruction error;
* jackknife reconstruction reliability;
* interpolation reliability;
* MRI systematic error prediction;
* dependent ensemble uncertainty.

If a close prior result exists:

cite it and narrow the contribution.

If no close controlled physical-intervention study exists:

make this difference explicit and precise.

Never use unsupported “first” wording.

---

# 8. TMI RISK B — “WHY DOES THIS MATTER FOR MEDICAL IMAGING?”

Strengthen the imaging significance without inventing clinical claims.

Ask:

> What operational MRI reconstruction QA decision becomes better because we understand consensus blindness?

Use available retrospective data to quantify realistic consequences such as:

* examinations incorrectly retained by committee agreement;
* cases recovered by measurement-disjoint ranking;
* error reduction under selective retention;
* densification prioritization;
* high-error examinations missed by shared-context agreement.

Report:

* counts;
* effect sizes;
* clustered confidence intervals.

Do NOT convert these into diagnostic or patient-safety claims.

Frame them as:

**MRI reconstruction quality-control consequences.**

---

# 9. TMI RISK C — “IS THIS ONLY ONE PARTICULAR SCORE?”

Use existing Plan-6 multi-endpoint evidence.

But do not merely add another table.

Analyze WHY:

* MAE/RMSE/MSE/low-frequency endpoints agree;
* SSIM behaves differently;
* gradient/high-frequency endpoints are weaker.

Ask whether this is consistent with the proposed consensus-error mechanism.

If possible test:

> Is consensus blindness stronger for low-frequency / intensity-biased reconstruction failures than for structural-similarity endpoints?

Turn metric heterogeneity into scientific understanding.

Do not claim metric independence.

---

# 10. TMI RISK D — “THE TEST IS IMPRACTICAL”

Measurement-disjoint reliability may require additional reconstructions.

Quantify the trade-off explicitly.

Compare:

* committee;
* TTA;
* PC;
* disjoint phase-grid;
* acquired-only scores.

Construct a:

`accuracy / reliability / compute / storage / acquisition assumptions`

trade-off table.

Determine:

> When is measurement-disjoint disagreement worth the additional cost?

The paper need not claim it is always deployable.

It must clearly define the operating regime.

---

# 11. TMI RISK E — “NO TRUE CLINICAL VALIDATION”

Do not attempt to fake clinical validation.

Instead make TMI stronger through imaging-method validation.

If no reader study exists:

retain it as a limitation.

Investigate whether reconstruction error is concentrated in:

* high anatomical change;
* boundary regions;
* particular slice locations;
* high intrinsic difficulty examinations.

Only report anatomy-related findings supported by actual metadata.

The goal is:

**imaging relevance**

not:

**diagnostic outcome claims**.

---

# 12. TMI SUBMISSION-VERSION OPTIMIZATION

The current submission manuscript does not need to remain artificially short.

Verify the current official TMI initial submission page limit.

If up to 10 pages including references are allowed:

use the available space only if it materially improves reviewer understanding.

Do not add generic text.

Potential high-value additions include:

* one stronger consensus-error figure;
* one operational risk–coverage/densification figure;
* one compact metric/factor robustness table;
* stronger statistical hierarchy explanation;
* clearer failure-boundary panel.

Target:

**maximum information density, not maximum page count.**

---

# PART II — CVPR ACCEPTANCE OPTIMIZATION

# 13. CVPR CENTRAL PROBLEM

The largest current CVPR risk is NOT experimental rigor.

It is likely:

> **Where is the sufficiently strong method/capability contribution?**

The current evidence itself shows:

* Anchor-CV is strong;
* Anchor-CV is computationally cheap;
* but adjacent MAE/RMSE can be statistically indistinguishable or better;
* output PC can outperform it on some cohorts;
* fixed-count neural influence is heterogeneous on NingXia;
* the final context-ranking mechanism arrow is only partially supported.

Therefore:

**DO NOT protect Anchor-CV merely because it is already written into the paper.**

The CVPR paper may change.

---

# 14. CVPR RESEARCH QUESTION

The new highest-value question is:

> **Can the shared-influence mechanism produce a capability that cannot be obtained from trivial adjacent-slice difference or ordinary output disagreement?**

This must drive Plan-7 CVPR research.

Possible outcomes:

A. derive a genuinely stronger reliability estimator;

B. derive a context-selection method;

C. improve interpolation quality;

D. predict when additional measurements are valuable;

E. establish a sufficiently strong mechanism/findings contribution even without a superior score.

Let experiments decide.

---

# 15. DO NOT OPTIMIZE ANCHOR-CV BLINDLY

Freeze:

`ANCHOR_CV_V1`.

Do not tune it further on current test cohorts.

Its current result is evidence.

It is no longer an optimization target.

Any new method must receive a new ID.

---

# 16. CVPR HYPOTHESIS PORTFOLIO

Maintain 3–6 active hypotheses.

At minimum consider the following research families.

---

## H-A — Influence-aware context selection

Hypothesis:

> Context pairs selected to minimize shared neural measurement influence will expose hidden reconstruction failure better than contexts selected by overlap count or raw diversity.

Derive candidate selection rules from:

* finite-difference influence;
* local Jacobian influence;
* leave-one-anchor influence;
* analytical coefficient influence.

Do not use target error to choose the context.

Freeze context-selection rules on development data.

Evaluate on untouched cases where possible.

Compare against:

* random context choice;
* minimum overlap count;
* maximum raw diversity;
* ordinary PC;
* TTA;
* committee.

---

## H-B — Multi-anchor jackknife reliability

Hypothesis:

> Reconstructing multiple acquired anchors as pseudo-targets from complementary context subsets produces a higher-order examination difficulty signal that captures failure information beyond direct adjacent-slice difference.

Construct a principled cross-validation residual using multiple internal anchors.

Potential statistics:

* residual mean;
* residual variance;
* upper quantile;
* context sensitivity;
* residual consistency across anchor positions.

Do not introduce arbitrary weighted sums.

Every statistic must correspond to a hypothesized failure mode.

Compare directly against:

* adjacent MAE;
* adjacent RMSE;
* adjacent SSIM;
* curvature;
* spacing;
* Anchor-CV V1.

Critical requirement:

demonstrate **incremental information beyond adjacent difference**.

Use conditional/partial analysis and out-of-sample prediction.

---

## H-C — Shared-influence residualization

Hypothesis:

> The observable disagreement can be corrected for expected shared influence to recover hidden error information.

Explore a formulation such as:

`observed disagreement / expected independent-error fraction`

or another theoretically motivated transformation.

Do NOT fit arbitrary test-set weights.

Derive the correction from the error covariance model.

Freeze on development data.

Test out-of-sample.

---

## H-D — Mechanism-derived training

Hypothesis:

> Randomizing or diversifying anchor/context dependence during training reduces common-mode reconstruction error.

Possible mechanisms, only if justified:

* context dropout;
* randomized anchor subsets;
* phase-grid augmentation;
* disjoint-context consistency;
* shared-influence penalty.

The objective is NOT merely to improve PSNR.

Test predictions:

1. shared-error fraction decreases;
2. error cosine decreases;
3. reconstruction quality remains stable or improves;
4. disagreement observability increases.

Begin with a cheap pilot.

Do not launch large training unless the pilot supports the mechanism.

This branch has potentially high CVPR value.

---

## H-E — Densification-benefit capability

Hypothesis:

> Acquired-data reliability can identify where additional through-plane sampling has the highest expected value.

Current evidence already suggests this.

Strengthen it into a proper capability.

Requirements:

* frozen score;
* no dense target at decision time;
* multiple budgets;
* multiple cohorts;
* strongest simple baselines;
* confidence intervals;
* calibration of benefit ranking if possible.

Do not call it prospective acquisition optimization.

Call it:

**retrospective value-of-densification prediction**

unless prospective evidence exists.

---

# 17. CVPR METHOD GATE

A new method is allowed into the CVPR main contribution only if it passes ALL of:

### Gate 1 — Mechanistic necessity

Which demonstrated failure does it address?

### Gate 2 — Non-triviality

Does it provide information beyond adjacent difference / ordinary PC?

### Gate 3 — Out-of-sample evidence

Was it tested without adapting to the evaluation labels?

### Gate 4 — Robustness

Does it survive more than one dataset / architecture where feasible?

### Gate 5 — Practicality

Can the required information exist at deployment time?

### Gate 6 — Reviewer value

Would a skeptical reviewer say:

> “This capability did not exist before”?

If not:

do not promote it as the main method.

---

# 18. NEURAL SHARED-INFLUENCE DEEPENING

Plan-6 finite-difference influence is promising but still vulnerable.

Perform robustness analysis of the neural influence approximation.

Test:

* perturbation magnitude;
* perturbation sign/field;
* number of perturbation directions;
* plane selection;
* HAT versus SwinIR;
* fastMRI versus IXI versus NingXia.

Determine whether the influence estimate is stable.

If unstable:

do not hide it.

Search for a more robust local sensitivity measure.

Potential alternatives:

* exact autograd Jacobian-vector products;
* finite-difference Jacobian-vector products;
* leave-one-anchor perturbation;
* integrated local sensitivity.

Do not use a method merely because it produces stronger correlation.

Predefine what stability means.

---

# 19. DIRECTLY TEST THE MECHANISM CHAIN

The final CVPR paper should ideally support:

`shared influence`

→

`error alignment`

→

`disagreement cancellation`

→

`lower error observability`.

For each arrow:

1. define the variable;
2. state a falsifiable prediction;
3. run a matched analysis;
4. report clustered CI;
5. identify counterexamples.

If the full causal chain is unsupported:

do NOT call it causal mediation.

Find the strongest truthful formulation.

---

# 20. SEARCH FOR A STRONGER CONTROL

A current reviewer can still argue that context construction changes more than shared influence.

Search for the cleanest physically valid MRI control where:

* same target;
* same case;
* same model;
* same anchor count;
* same anchor distances if possible;
* same preprocessing;
* same mask;

but:

`shared influence`

changes.

The cleaner this intervention becomes, the stronger the paper.

Do not force an impossible experiment.

Document feasibility constraints mathematically.

---

# 21. TURN NEGATIVE RESULTS INTO STRENGTH

Plan-6 contains important negative results:

* integer overlap count is not a monotonic law;
* Anchor-CV is not uniquely informative;
* fixed-count NingXia neural result is mixed/null;
* no universal best reliability score;
* local localization fails;
* fusion fails.

Do not bury these.

Ask what each falsifies.

Use them to produce a more precise theory.

For example:

> overlap count is insufficient because measurements have unequal estimator influence.

That is scientifically stronger than hiding the nonmonotonicity.

---

# 22. NOVELTY COLLISION AUDIT

Search aggressively for close prior work using combinations of:

* leave-one-slice-out MRI;
* acquired-anchor cross-validation;
* interpolation cross-validation;
* jackknife reconstruction;
* self-supervised error prediction;
* dependent ensembles;
* correlated uncertainty;
* common-mode ensemble error;
* measurement influence;
* influence functions in reconstruction;
* uncertainty from dependent views;
* MRI interpolation reliability;
* acquisition value prediction.

For the ten closest papers build:

| Prior work | Same target? | Same measurement intervention? | Shared influence? | Acquired-only CV? | Same endpoint? | Main difference |

If a collision appears:

do not defend the old story rhetorically.

Modify the contribution.

---

# 23. CLAIM COMPRESSION TEST

For each paper, force the entire contribution into:

### One sentence

### Three contributions

### One central figure

### One central quantitative result

If this cannot be done clearly:

the paper is still conceptually diffuse.

For TMI and CVPR these summaries MUST be substantially different.

---

# 24. CROSS-PAPER SEPARATION

Maintain:

`SUBMISSION_OVERLAP_AUDIT.md`.

For every:

* paragraph;
* figure;
* table;
* experiment;
* claim;

classify:

* TMI only;
* CVPR only;
* shared background;
* shared historical evidence.

Compute approximate textual and scientific overlap.

Do not allow optimization to make the papers more similar.

The intended difference is:

## TMI

**Comprehensive MRI imaging-science characterization of consensus blindness under measurement overlap.**

## CVPR

**Shared-influence mechanism plus a new capability/method derived from that mechanism.**

If CVPR cannot develop enough independent added value:

flag:

`MERGE_OR_SEQUENCE_REQUIRED`.

Do not pretend dual submission is safe.

---

# 25. PAPER WRITING OPTIMIZATION

Only after resolving the highest-value scientific risks should manuscript rewriting begin.

Optimize in this order:

1. title;
2. one-sentence claim;
3. abstract;
4. Fig. 1;
5. contributions;
6. experiment ordering;
7. results emphasis;
8. related work;
9. discussion;
10. sentence-level polishing.

Do not start by polishing prose.

---

# 26. FIGURE-1 TEST

For both papers independently ask:

> Can a reviewer understand the problem, mechanism, and contribution from Fig. 1 in 30 seconds?

If not:

redesign Fig. 1.

TMI Fig. 1 should communicate:

`shared measurement → shared error → consensus blindness`.

CVPR Fig. 1 should communicate:

`shared influence → error alignment → hidden error → mechanism-derived capability`.

Do not reuse effectively identical figures across both papers.

---

# 27. ABSTRACT STRESS TEST

Every abstract must answer:

1. What problem?
2. What existing assumption fails?
3. Why?
4. What is proposed/discovered?
5. What is the strongest evidence?
6. Why does it matter?
7. What is NOT claimed?

Remove adjectives such as:

* novel;
* significant;
* powerful;
* superior;
* comprehensive;

unless directly justified.

Let evidence communicate strength.

---

# 28. REVIEWER MEMORY TEST

After reading the paper, a reviewer should remember ONE message.

For TMI:

> Shared physical measurement reuse can make deterministic MRI interpolators agree while being wrong.

For CVPR:

The final message must be stronger than Anchor-CV alone.

Discover what it should be from Plan-7 evidence.

Do not finalize the CVPR title until this message is clear.

---

# 29. REBUTTAL PREPARATION AS A RESEARCH TOOL

Before declaring final readiness, write a simulated rebuttal to the five hardest reviewer criticisms.

If the answer requires saying:

> “We will run this experiment later,”

then determine whether the experiment is feasible NOW.

If feasible:

run it before submission.

If impossible:

make the limitation explicit in the paper.

Create:

`TMI_REBUTTAL_BANK.md`

and:

`CVPR_REBUTTAL_BANK.md`.

---

# 30. TMI ACCEPTANCE GATE

The TMI paper is ready only when a simulated AE and reviewers agree that:

### Novelty

The controlled physical measurement-overlap contribution is clearly distinguished from generic disagreement theory and prior MRI QA.

### Quality

Statistics and experiments withstand adversarial audit.

### Appropriateness

The work is clearly a medical-imaging methodology contribution.

### Impact

The paper establishes an actionable insight for MRI reconstruction QA rather than an algebraic curiosity.

### Reproducibility

Claims map to scripts/results.

### Ethics

Human-data requirements are either complete or clearly marked as human blockers.

Do not invent missing ethics information.

---

# 31. CVPR ACCEPTANCE GATE

The CVPR paper is ready only when:

### Novelty

Closest prior work does not subsume the central contribution.

### Mechanism

Shared influence has strong neural as well as analytical evidence.

### Non-obviousness

Raw overlap/diversity explanations have been falsified.

### Method/capability

At least one contribution provides meaningful information or capability beyond trivial adjacent-difference baselines.

### Robustness

The main claim survives major dataset/model strata.

### Evidence

The decisive experiments are already in the submitted main/supplement, not left for rebuttal.

### Scope

The paper explains why the result is scientifically important even though experiments remain within MRI interpolation.

### Failure boundaries

NingXia heterogeneity and negative results are explicit.

If the method/capability gate cannot be passed:

do not fabricate one.

Re-evaluate whether the strongest CVPR paper should instead be positioned as a mechanism/findings paper.

---

# 32. STOPPING RULE

Do NOT stop because:

* manuscripts compile;
* page limits are met;
* a paper is “good enough”;
* one simulated reviewer accepts;
* one experiment is positive.

Continue while a:

`FATAL` or `MAJOR`

reviewer risk exists AND there is a scientifically meaningful experiment/analysis capable of resolving it.

Stop only when remaining risks are primarily:

* unavailable prospective data;
* ethics metadata requiring humans;
* truly new external cohorts;
* irreducible venue taste;
* or experiments whose expected scientific value is lower than their cost.

At that point produce:

`FINAL_ACCEPTANCE_OPTIMIZATION_REPORT.md`.

---

# 33. FINAL REPORT FORMAT

For each paper report:

## Current central claim

## Strongest evidence

## Closest prior work

## Novelty risk

## Major reviewer risks

## Experiments added during Plan-7

## Hypotheses falsified

## Claims removed

## Claims strengthened

## Final recommended title

## Final contribution bullets

## Final reviewer simulation

Reviewer 1 score
Reviewer 2 score
Reviewer 3 score
Reviewer 4 score
Reviewer 5 score / AE or AC assessment

## Remaining human blockers

## Submission recommendation

One of:

* READY
* READY AFTER HUMAN METADATA
* NEEDS ONE MORE SCIENTIFIC EXPERIMENT
* NEEDS MAJOR RESEARCH REVISION
* MERGE / CHANGE SUBMISSION SEQUENCE

Never output an invented numerical acceptance probability.

---

# 34. REQUIRED FINAL ARTIFACTS

Produce updated final candidates separately.

## TMI

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/main.tex`

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/main.pdf`

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/references.bib`

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/CLAIM_TRACEABILITY.md`

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/REVIEWER_RISK_AUDIT.md`

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/COVER_LETTER_DRAFT.md`

Do not submit automatically.

---

## CVPR

`CVPR/CVPR_UPGRADE/PAPER_FINAL/main.tex`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/main.pdf`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/supplement.tex`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/supplement.pdf`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/references.bib`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/CLAIM_TRACEABILITY.md`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/REVIEWER_RISK_AUDIT.md`

`CVPR/CVPR_UPGRADE/PAPER_FINAL/REBUTTAL_BANK.md`

Do not submit automatically.

---

# 35. EXECUTION PRIORITY — START HERE

Based on the current Plan-6 evidence, initially prioritize:

## TMI P0

1. Updated closest-prior-work collision audit.
2. Strengthen medical-imaging operational consequence.
3. Convert metric heterogeneity into mechanistic interpretation.
4. Decide whether the 8-page submission should use additional space up to the official limit.
5. Redesign the paper around impact rather than algebra.

## CVPR P0

1. Determine whether the central contribution can survive without claiming Anchor-CV superiority.
2. Search for a mechanism-derived capability that contains information beyond adjacent MAE/RMSE.
3. Strengthen neural shared-influence estimation and fixed-count validation.
4. Test the full shared-influence → alignment → cancellation → observability chain.
5. Attempt one high-value mechanism-derived method branch.
6. Perform an aggressive novelty audit.
7. Re-run reviewer simulation before manuscript rewrite.

Reorder only when evidence shows a higher-value acceptance risk.

---

# 36. IMPORTANT RESEARCH PHILOSOPHY

Do not optimize the papers to look impressive.

Optimize them to survive skepticism.

Every positive result should invite:

> What simpler explanation could produce this?

Every mechanism should invite:

> What experiment could falsify it?

Every new method should invite:

> Does a trivial baseline already do this?

Every strong sentence should invite:

> Which exact experiment supports this wording?

Every paper should invite:

> If I were a hostile reviewer, what would I attack first?

Then address that attack before submission.

---

# 37. FINAL INSTRUCTION

Plan-7 is not another manuscript expansion phase.

It is the final scientific adversarial phase.

The objective is:

**remove avoidable reasons for rejection.**

For TMI:

make the work unmistakably significant as an MRI imaging-methodology contribution.

For CVPR:

turn the shared-influence mechanism into a sufficiently non-trivial scientific capability or method—or, if evidence refuses to support that, construct the strongest truthful mechanism paper instead of forcing a weak method claim.

Preserve negative results.

Preserve statistical honesty.

Preserve TMI/CVPR separation.

Use experiments only when they materially change reviewer confidence.

Continue until the remaining weaknesses require genuinely unavailable human information, new prospective acquisition, or irreducible external resources rather than another executable scientific test.
