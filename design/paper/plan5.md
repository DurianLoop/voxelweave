# Dual-Track Research and Publication Goal

## TMI Full Manuscript + CVPR-Level Research Upgrade

Continue from all existing research under:

`D:\MRI\design`

and especially the complete research history under:

`D:\MRI\design\paper`

including Plan-1, Plan-2, Plan-3, Plan-4, experiment registries, statistical analyses, literature audits, theory files, machine-readable outputs, scripts, figures, negative results, and the latest `Publication Readiness Report`.

From this point onward, execute **two parallel but scientifically separated tracks**:

**TRACK A — Produce a complete submission-ready IEEE Transactions on Medical Imaging manuscript from the CURRENT FROZEN EVIDENCE.**

**TRACK B — Continue hypothesis-driven research to substantially strengthen the contribution into a CVPR/ICCV-level conference paper, while remaining entirely within MRI inter-slice interpolation.**

These tracks must share verified evidence but must not contaminate one another.

The TMI manuscript documents the strongest currently defensible research state.

The CVPR research branch is allowed to create new experiments, new contexts, new theory, new methods, and stronger claims.

Do not stop Track B merely because Track A becomes complete.

---

# PART 0 — Publication and research governance

Create:

`D:\MRI\design\paper\TMI_MANUSCRIPT`

and:

`D:\MRI\design\paper\CVPR_UPGRADE`

Do not overwrite the existing research records.

Treat all existing Plan-1 to Plan-4 results as immutable historical evidence.

If an existing result is found to be wrong, supersede it explicitly rather than silently rewriting history.

Maintain exact traceability from every number appearing in either manuscript to:

* dataset;
* examination IDs;
* experiment ID;
* code;
* configuration;
* statistical procedure;
* output file.

Never fabricate:

* experiments;
* citations;
* DOI;
* p-values;
* confidence intervals;
* sample sizes;
* baselines;
* clinical interpretations;
* ethics information.

Anything not actually executed must be labeled:

`NOT RUN`.

Anything exploratory must be labeled:

`EXPLORATORY`.

Anything frozen before evaluation must be labeled:

`CONFIRMATORY`.

---

# PART I — TRACK A: COMPLETE TMI MANUSCRIPT

## 1. Verify the latest official TMI requirements first

Before writing the manuscript, retrieve and read the CURRENT official:

* IEEE Transactions on Medical Imaging Information for Authors;
* TMI Submission Checklist;
* IEEE journal LaTeX template / IEEE Template Selector guidance;
* TMI scope/editorial criteria;
* IEEE human-subject and publication-ethics requirements.

Prefer official IEEE / TMI / EMBS sources.

Do not rely on a random third-party template when an official template is available.

Record the verified requirements in:

`TMI_MANUSCRIPT/TMI_REQUIREMENTS.md`

At minimum verify:

* article type;
* initial page limit;
* minimum font size;
* whether references count toward the page limit;
* abstract limit;
* index-term requirements;
* figure requirements;
* supplementary-material rules;
* ethics / IRB statement requirements;
* anonymity requirements;
* data/code statement requirements;
* current submission-system requirements.

As of the current working instructions, target a TMI Regular Paper initial submission and enforce:

* maximum 10 initial-submission pages including references;
* font size no smaller than 10 pt;
* abstract under 250 words;
* IEEE index terms.

If the CURRENT official TMI instructions differ, follow the current official instructions and document the difference.

---

# 2. Freeze the TMI scientific scope

The TMI manuscript must describe the evidence that already exists.

Do not invent additional positive findings merely to improve the paper.

The current central scientific result is approximately:

> In deterministic MRI slice interpolation, disagreement-based reliability is limited by shared reconstruction error. When two reconstruction contexts reuse measurements that induce similar failure directions, their agreement can conceal substantial target error. Target-preserving measurement-disjoint phase grids expose these hidden errors substantially better than maximal-shared-measurement controls. This motivates a reliability-design principle: useful consistency interventions should reduce shared error-generating information rather than merely maximize raw output diversity.

Refine this wording based on the actual evidence.

Do not overgeneralize beyond deterministic MRI slice interpolation unless the evidence supports it.

Do not claim:

* calibrated uncertainty;
* correctness certification from low disagreement;
* clinical safety;
* prospective acquisition benefit;
* universal superiority;
* cross-domain generality;
* attribution of which output is wrong.

---

# 3. Reconstruct the entire evidence chain

Before drafting prose, read and reconcile:

* `FROZEN_METHOD.md`
* `RESEARCH_STATE.md`
* `CURRENT_BEST_CLAIM.md`
* `CLAIM_EVIDENCE_MATRIX.md`
* `HYPOTHESES.md`
* `EXPERIMENTS.md`
* `STATISTICAL_VALIDITY.md`
* `CASE_INFLUENCE_ANALYSIS.md`
* `MECHANISM_REPORT.md`
* `THEORY.md`
* `FALSIFICATION_REPORT.md`
* `NOVELTY_AUDIT.md`
* `PLAN4_LITERATURE_AND_NOVELTY.md`
* relevant Plan-1/2/3/4 reports
* machine-readable outputs
* analysis scripts.

Create:

`TMI_MANUSCRIPT/EVIDENCE_LEDGER.md`

For every major manuscript claim record:

Claim
Experiment IDs
Dataset
N
Statistic
CI
Figure/Table destination
Limitations
Whether confirmatory/exploratory

The paper must be written from this evidence ledger.

---

# 4. Literature review

Perform a fresh literature search before finalizing the paper.

Focus on:

### MRI slice synthesis / interpolation

* through-plane interpolation;
* anisotropic MRI super-resolution;
* slice synthesis;
* deterministic interpolation;
* deep MRI interpolation.

### Reconstruction uncertainty

* probabilistic MRI reconstruction;
* ensembles;
* heteroscedastic uncertainty;
* MC dropout;
* SURE;
* learned error prediction;
* conformal/selective prediction.

### Consistency-based reliability

* test-time augmentation uncertainty;
* self-consistency;
* perturbation consistency;
* disagreement;
* ensemble diversity.

### Inverse-problem reliability

* shared error;
* common-mode failure;
* data consistency;
* posterior ambiguity;
* algorithmic stability.

### Classical interpolation

* interpolation error;
* sampling spacing;
* derivatives / curvature;
* approximation error.

Use primary publications whenever possible.

Verify title, authors, venue, year and DOI/official URL.

Never generate a BibTeX record from memory.

Create:

`TMI_MANUSCRIPT/references.bib`

and:

`TMI_MANUSCRIPT/LITERATURE_TRACE.md`

Each reference must state why it is cited.

---

# 5. Paper positioning

The manuscript must NOT read like:

> “We propose yet another uncertainty score.”

The paper should instead establish:

### Problem

Deterministic interpolation reliability is difficult to assess without the missing dense target.

### Observation

Most reconstruction error is shared across contexts/architectures and is therefore poorly observed by ordinary disagreement.

### Mechanism

Shared measurements induce correlated error directions.

### Consequence

Subtracting two similarly biased reconstructions cancels much of their shared error.

### Controlled intervention

Change measurement overlap while keeping target, case, model, plane and evaluation support fixed.

### Finding

Measurement-disjoint contexts expose retrospective error substantially better.

### Principle

Reliability interventions should alter error-generating information, not merely increase prediction diversity.

### Boundary

Agreement remains incapable of certifying correctness when errors stay shared.

This causal/mechanistic story should drive the manuscript.

---

# 6. TMI manuscript structure

Write a complete scientific article, not an outline.

Recommended structure:

## Title

Generate 5 candidate titles.

Prefer precise, technical titles.

Avoid sensational wording.

Possible conceptual direction:

“Measurement Overlap Governs Disagreement-Based Reliability in Deterministic MRI Slice Interpolation”

Choose the strongest final title after the manuscript is written.

---

## Abstract

Single concise abstract below the TMI word limit.

It should contain:

* clinical/imaging-method motivation;
* methodological gap;
* central hypothesis;
* controlled measurement-overlap protocol;
* datasets/models;
* strongest quantitative results;
* mechanistic conclusion;
* explicit scope.

Include actual numbers where useful.

Do not include citations.

Do not claim clinical benefit.

---

## Index Terms

Choose appropriate IEEE index terms, e.g. concepts related to:

MRI
slice interpolation
image reconstruction
uncertainty estimation
reliability
sampling
consistency

Use the current TMI/IEEE convention.

---

## I. Introduction

Establish:

1. why through-plane interpolation matters;
2. why deterministic interpolation requires reliability assessment;
3. why conventional disagreement can fail;
4. the central measurement-overlap hypothesis;
5. concise contributions.

The contributions should correspond to actual evidence.

Avoid an excessive bullet list if TMI style favors prose.

---

## II. Related Work

Organize conceptually rather than as a paper list.

Potential subsections:

A. MRI Slice Interpolation and Reconstruction
B. Reconstruction Uncertainty and Failure Prediction
C. Consistency and Disagreement-Based Reliability
D. Sampling and Interpolation Error

Explicitly articulate the closest-work gap.

---

## III. Theory: Consensus Error and Disagreement Blindness

Formalize reconstruction error.

For two reconstructions:

`f_a = y + e_a`

`f_b = y + e_b`

then:

`f_a - f_b = e_a - e_b`.

Develop the squared-disagreement relation:

`||e_a - e_b||^2  = ||e_a||^2 + ||e_b||^2 - 2 <e_a,e_b>`.

Explain how positively aligned/shared errors reduce observable disagreement.

Connect this to the empirical consensus-error decomposition.

Also present the one-sided triangle-inequality interpretation where appropriate:

`d(f_a,f_b) <= d(f_a,y) + d(f_b,y)`.

Clarify:

large disagreement can witness error;

small disagreement cannot certify correctness.

Do not overstate theorem strength.

---

## IV. Measurement-Overlap Hypothesis

Define:

* target-preserving reconstruction context;
* acquired anchor;
* measurement overlap;
* shared versus disjoint measurement support;
* phase-grid construction;
* maximal-shared control;
* evaluation mask.

State the causal hypothesis:

> Increasing reuse of error-generating measurements increases alignment of reconstruction error and reduces the ability of disagreement to reveal target error.

Separate hypothesis from result.

---

## V. Materials and Methods

Describe:

### Datasets

fastMRI
NingXia
IXI where relevant

For each:

* cohort size;
* modality/contrast;
* preprocessing;
* splits;
* OOF handling;
* inclusion/exclusion;
* available factors;
* ethical/public-dataset status.

Never invent missing metadata.

### Reconstruction methods

HAT
SwinIR
other frozen models actually used
linear interpolation
cubic interpolation

Explain why each is included.

### Interpolation factors

x2
x4
x6

### World-coordinate matching

Explain NIfTI affine-based physical-plane matching rigorously.

### Reliability scores

committee
PC
TTA
measurement-disjoint phase-grid disagreement
input baselines

### Endpoints

MAE / MSE or exact endpoint actually used
Spearman
nAURC
risk-coverage
densification benefit

### Statistical analysis

Examination is the independent sampling unit.

Describe:

* examination-cluster bootstrap;
* number of replicates;
* permutation tests;
* LOO influence where used;
* paired analysis.

Avoid pseudoreplication.

---

## VI. Experiments and Results

Organize experiments around hypotheses.

### Experiment 1 — Consensus Error

Show shared versus observable error decomposition.

### Experiment 2 — Measurement Overlap Intervention

The main result.

Same:

* target;
* case;
* model;
* plane;
* evaluation mask.

Change:

* measurement overlap.

Report fastMRI and NingXia.

### Experiment 3 — Architecture Robustness

HAT and SwinIR separately.

### Experiment 4 — Analytical Interpolators

Linear and cubic.

### Experiment 5 — Raw Diversity Control

Demonstrate that larger raw disagreement is not sufficient.

### Experiment 6 — Predictive Consequence

Show relationship between the disjoint signal and x4→x2 densification benefit.

Explicitly call this retrospective predictive validity, not a prospective acquisition policy.

### Experiment 7 — Failure Boundary

Show:

* shared blur/common-mode failure;
* stable-wrong examples;
* boundary/shared-anchor behavior.

Negative results must remain visible.

---

# 7. Figure design

Create publication-quality figures programmatically where possible.

Every figure must answer a scientific question.

Prioritize approximately:

### Fig. 1 — Concept

Shared measurements

→ aligned reconstruction error

→ cancellation in disagreement

versus

measurement-disjoint contexts

→ less shared error direction

→ greater error observability.

### Fig. 2 — Phase-grid experimental design

Illustrate the same physical target with zero/one/maximal anchor overlap.

### Fig. 3 — Main controlled result

fastMRI + NingXia.

Show disagreement-error relationship for disjoint versus shared conditions.

### Fig. 4 — Cross-architecture / analytical generalization

### Fig. 5 — Consensus-error decomposition + raw diversity control

### Fig. 6 — Predictive consequence + failure boundary

Combine panels intelligently to stay inside TMI's page budget.

Do not produce decorative figures.

---

# 8. Tables

Prefer compact high-information tables.

Possible tables:

### Table I

Datasets and experimental configurations.

### Table II

Primary measurement-overlap results.

### Table III

Architecture/analytical generalization and ablations.

Do not duplicate information already obvious from figures.

---

# 9. Discussion

The Discussion should explain:

* why disagreement can fail;
* what measurement overlap changes;
* why prediction diversity alone is insufficient;
* why analytical and neural results matter;
* what the findings imply for MRI interpolation reliability;
* how the result relates to classical interpolation/sampling concepts;
* what cannot be inferred from low disagreement.

Do not repeat Results paragraph-by-paragraph.

---

# 10. Limitations

Explicitly include:

* retrospective phase grids;
* two primary T2 brain MRI cohorts;
* limited architectures for the decisive controlled neural experiment;
* no clinical reader study;
* no prospective adaptive acquisition;
* no universal superiority claim;
* maximal-overlap-control limitations;
* intensity comparability requirements;
* consistent-but-wrong regime;
* bounded novelty audit.

Strong limitations increase credibility.

---

# 11. Ethics and data statement

MRI data are human-derived.

Follow current IEEE/TMI requirements.

For public datasets:

cite the original dataset and describe its published consent/ethics status when verifiable.

For private/internal datasets:

retrieve the actual available IRB/ethics information from repository documentation.

Never fabricate an approval number.

If the required ethics information is not available, insert:

`[ETHICS INFORMATION REQUIRED FROM AUTHORS]`

rather than guessing.

---

# 12. Conclusion

Conclude with the narrow scientific principle.

Do not claim that the method guarantees reconstruction accuracy.

---

# 13. Compile the manuscript

Create:

`TMI_MANUSCRIPT/main.tex`

`TMI_MANUSCRIPT/references.bib`

`TMI_MANUSCRIPT/figures/`

`TMI_MANUSCRIPT/tables/`

`TMI_MANUSCRIPT/supplement.tex` if allowed/useful

`TMI_MANUSCRIPT/CLAIM_TRACEABILITY.md`

`TMI_MANUSCRIPT/TMI_COMPLIANCE_CHECK.md`

Compile:

`TMI_MANUSCRIPT/main.pdf`

Use an official-compatible IEEE/TMI LaTeX setup.

Resolve:

* broken references;
* undefined citations;
* overfull boxes where practical;
* figure readability;
* table overflow;
* page count.

The INITIAL TMI manuscript must satisfy the verified initial-submission page limit.

Do not shrink fonts below the permitted minimum.

Do not cheat margins.

Do not hide important methodological information in unreadably small figures.

---

# 14. TMI quality audit

Before calling the TMI manuscript complete, simulate:

### TMI Reviewer A — Imaging significance

Is this an imaging-method contribution rather than generic ML applied to MRI?

### Reviewer B — Novelty

Is measurement-overlap-induced disagreement blindness genuinely different from known consistency uncertainty?

### Reviewer C — Statistics

Are examinations correctly treated as independent units?

### Reviewer D — Medical rigor

Are data provenance, cohort descriptions and ethics accurate?

### Reviewer E — Mechanism

Does the overlap intervention actually support the proposed mechanism?

### Reviewer F — Claims

Does every claim match the evidence?

Address fatal issues in the manuscript.

Do not invent experiments merely to answer stylistic reviewer concerns.

---

# PART II — TRACK B: CVPR-LEVEL RESEARCH UPGRADE

Track B begins immediately and continues even while Track A is being written.

Do not simply convert the TMI paper into eight pages.

The CVPR branch must become scientifically stronger and ideally contain a methodological consequence that goes beyond the current TMI evidence.

Remain strictly within:

**MRI inter-slice / through-plane interpolation.**

Do NOT expand into video, CT, natural-image SR, or unrelated domains.

---

# 15. CVPR research objective

Current core mechanism:

`Measurement overlap`

→ `shared / correlated reconstruction error`

→ `cancellation in disagreement`

→ `consensus blindness`.

The next research objective is:

> Turn this observed mechanism into a stronger, predictive and actionable framework for MRI interpolation reliability and/or reconstruction.

The final CVPR contribution should ideally establish:

1. a causal relationship;
2. a mathematical account;
3. a method or capability derived from the mechanism;
4. strong MRI experiments;
5. reviewer-resistant evidence.

---

# 16. Do not optimize for another heuristic score

Avoid:

`new score = 0.4 PC + 0.6 input RMSE`.

Naive fusion has already failed.

Any new method must follow:

`Observed failure`

→ `mechanistic explanation`

→ `derived intervention`

→ `falsifiable prediction`

→ `minimal experiment`

→ `full experiment`.

---

# 17. Priority Research Question A:

## Measurement overlap → error covariance → disagreement blindness

Develop a more complete mathematical and empirical account.

For reconstruction errors:

`e_i` and `e_j`,

study:

`E ||e_i - e_j||²
= E||e_i||² + E||e_j||²

* 2E<e_i,e_j>`.

Test whether increasing measurement overlap changes:

* error cosine similarity;
* error covariance;
* shared-error fraction;
* disagreement magnitude;
* disagreement-error correlation;
* stable-wrong prevalence.

The desired causal chain is:

`measurement overlap ↑`

→ `error alignment ↑`

→ `observable disagreement fraction ↓`

→ `reliability ranking ↓`.

Do not assume this chain is true.

Test every arrow.

---

# 18. Priority Research Question B:

## Clean measurement-overlap ladder

The current zero-versus-maximal comparison is powerful but the maximal control may contain ordering effects.

Design a cleaner controlled overlap experiment if possible.

Aim to construct same-target contexts with several overlap levels such as:

* zero overlap;
* low overlap;
* medium overlap;
* high overlap;
* maximal overlap.

Exact percentages need not be forced if the acquisition geometry does not permit them.

Hold constant as much as physically possible:

* target physical plane;
* model;
* case;
* factor;
* number of measurements;
* measurement distance;
* mask;
* preprocessing.

Measure a dose-response relationship between overlap and observability.

If a monotonic relation is not observed, investigate why.

Do not cherry-pick overlap levels.

---

# 19. Priority Research Question C:

## Independent-error context design

Ask:

> Can reconstruction contexts be deliberately designed to minimize shared error directions while preserving the same target?

Potential MRI-only interventions include:

* phase-shifted sampling grids;
* non-overlapping anchors;
* alternative anchor subsets;
* asymmetric anchor contexts;
* leave-one-anchor-out contexts;
* near-versus-far context;
* disjoint context windows;
* valid synthetic resampling of acquired slices.

For each candidate measure:

1. target preservation;
2. information overlap;
3. reconstruction-error correlation;
4. disagreement observability;
5. computational/acquisition cost.

The goal is not maximum output difference.

The goal is minimum harmful **error-direction dependence**.

---

# 20. Priority Research Question D:

## Can hidden consensus error become observable?

The current reliability signal observes mainly context-sensitive error.

Try to expose the dominant shared component.

Candidate observables must be mechanistically justified.

Potential directions:

### Input-side difficulty

* anchor RMSE;
* through-plane curvature proxy;
* physical spacing;
* structural change;
* low-frequency change;
* anatomical complexity.

### Alternative-context evidence

* non-overlapping phase grids;
* context masking;
* independent anchor subsets.

### Reconstruction-side

* spectral attenuation;
* local structural collapse;
* scale consistency;
* context sensitivity.

Do not use the dense target in the reliability score.

Dense target remains evaluation-only.

---

# 21. Priority Research Question E:

## A principled two-component reliability model

Current evidence suggests:

`total error`

≈

`shared intrinsic/context-independent component`

*

`context-sensitive component`.

Investigate whether:

* input-derived difficulty estimates the first component;
* disjoint-context disagreement estimates the second.

Do not combine them blindly.

Possible principled approaches include:

* residual modeling;
* orthogonalized signals;
* hierarchical modeling;
* monotonic risk model;
* two-stage decomposition;
* theoretically constrained combination.

All learned combinations require clean train/development/test separation.

Do not tune on final evaluation cohorts.

---

# 22. Priority Research Question F:

## Predict densification benefit

The current disjoint signal already predicts realized x4→x2 benefit.

This is a major potential methodological consequence.

Develop this carefully.

Hypothesis:

> Measurement-disjoint disagreement identifies examinations/planes whose reconstruction quality would benefit most from denser through-plane sampling.

Design a retrospective acquisition-allocation experiment.

For a fixed simulated budget, compare policies such as:

* random;
* adjacent-anchor RMSE;
* ordinary PC;
* TTA;
* committee disagreement;
* measurement-disjoint disagreement;
* any justified new method;
* oracle upper bound.

Example evaluation:

If only:

10%
20%
30%
50%

of cases or planes can receive additional sampling/densification,

which policy produces the greatest reduction in retrospective reconstruction error?

Use prespecified budget levels.

Report full budget–benefit curves.

Do not pick only favorable budget points.

Call this:

**retrospective acquisition simulation**

not:

clinical acquisition optimization.

No prospective or clinical claim is allowed without prospective evidence.

---

# 23. Priority Research Question G:

## Can the mechanism improve reconstruction itself?

If measurement-sharing is demonstrated to induce correlated error, investigate whether a mechanism-derived training or reconstruction strategy can reduce that error.

Only pursue this if justified.

Possible hypotheses include:

* randomized context subsets reduce shared-context bias;
* context dropout improves robustness to anchor dependence;
* phase-grid consistency training improves difficult-plane reconstruction;
* deliberately diversified context training reduces consensus failure;
* difficulty-aware interpolation allocates model capacity/context differently.

For any new training method:

### First

Run a small mechanistic test.

### Then

One architecture / small cohort.

### Then

Full architecture/dataset evaluation only if the hypothesis survives.

Do not launch expensive architecture search.

---

# 24. Intrinsic difficulty and curvature

Continue investigating the strong architecture-independent difficulty phenomenon.

Test whether error can be explained by:

* physical spacing;
* acquired-anchor difference;
* estimated through-plane curvature;
* low-frequency structural change;
* interactions among these variables.

Use hierarchical/mixed-effects models where appropriate.

Ask whether these interpretable variables explain the very large case effect and low architecture effect.

A useful scientific model would be stronger than another correlation table.

---

# 25. Dataset organization

Create a reproducible data manifest:

`CVPR_UPGRADE/DATA_MANIFEST.csv`

For every case record, where available:

* dataset;
* case ID;
* split;
* modality/contrast;
* factor;
* architecture;
* source file;
* physical spacing;
* matched planes;
* context type;
* overlap type;
* evaluation eligibility.

Do not move or duplicate raw MRI data unnecessarily.

All experimental scripts must consume the manifest rather than depend on undocumented filesystem ordering.

---

# 26. Experiment registry

Maintain:

`CVPR_UPGRADE/HYPOTHESES.md`

`CVPR_UPGRADE/EXPERIMENTS.md`

`CVPR_UPGRADE/RESEARCH_STATE.md`

`CVPR_UPGRADE/NOVELTY_AUDIT.md`

`CVPR_UPGRADE/REVIEWER_REDTEAM.md`

`CVPR_UPGRADE/CLAIM_EVIDENCE_MATRIX.md`

`CVPR_UPGRADE/INNOVATION_SCORECARD.md`

Every experiment receives a unique ID.

---

# 27. Statistical rigor

The examination remains the independent sampling unit unless a different unit is scientifically justified.

Use:

* clustered bootstrap;
* paired comparisons;
* permutation tests;
* mixed-effects analysis where appropriate;
* effect size and confidence interval.

Do not flatten plane/profile observations and pretend they are independent patients.

Separate:

pixel-level descriptive relationships

from:

examination-level statistical inference.

---

# 28. Strong baselines

Maintain fair MRI-only comparisons to compatible methods such as:

* committee disagreement;
* ordinary Physical Consistency;
* TTA;
* adjacent-anchor input difficulty;
* analytical interpolation reliability;
* learned predictor only if a fair training split exists;
* any closely related method found in literature.

Do not implement incompatible baselines just to increase table size.

---

# 29. New novelty audit

Continuously search:

* MRI interpolation uncertainty;
* medical image interpolation reliability;
* MRI super-resolution uncertainty;
* reconstruction confidence;
* measurement consistency;
* inverse-problem uncertainty;
* ensemble/shared error;
* self-consistency reliability;
* perturbation uncertainty;
* sampling-grid interventions;
* phase-shift reconstruction;
* acquisition-aware uncertainty;
* interpolation error estimation.

Also search adjacent theoretical literature relevant to the mechanism.

For every closest paper answer:

* same problem?
* same intervention?
* same target-preserving design?
* explicitly manipulates measurement overlap?
* studies error observability?
* derives measurement-overlap / error-covariance relation?
* predicts densification benefit?

If a novelty collision appears, update the research direction immediately.

---

# 30. CVPR publication threshold

Do not declare the upgraded paper ready simply because one result is significant.

A candidate CVPR-level contribution should ideally reach:

Novelty >= 4/5
Importance >= 4/5
Mechanistic depth >= 4/5
Experimental rigor >= 4/5
Reviewer resilience >= 4/5

and preferably include:

### Scientific discovery

Why disagreement fails.

### Causal mechanism

How measurement overlap changes shared error.

### New principle

Why error-generating-information independence matters.

### Methodological consequence

A protocol, estimator, acquisition-allocation capability, or reconstruction strategy derived from the mechanism.

### Prediction

At least one nontrivial prediction generated before evaluation and confirmed afterward.

### Breadth within MRI

Multiple cohorts, architectures, factors and estimator families where possible.

Do not inflate the score to terminate.

---

# 31. CVPR reviewer red team

Repeatedly simulate:

### Reviewer A

“This is only an MRI-specific phenomenon.”

Answer within the MRI interpolation setting through depth, not by adding unrelated domains.

### Reviewer B

“This is obvious: independent measurements give different outputs.”

Demand quantitative error-covariance and controlled overlap evidence.

### Reviewer C

“This is just more perturbation diversity.”

Use raw-magnitude and matched-perturbation controls.

### Reviewer D

“Where is the method?”

Require an actionable consequence or derived protocol.

### Reviewer E

“Your maximal-overlap control is confounded.”

Build a cleaner overlap ladder/control.

### Reviewer F

“Your acquisition experiment is circular.”

Ensure reliability signals do not access unavailable dense targets.

### Reviewer G

“This is a medical application paper, not CVPR.”

Strengthen mechanism, theory, prediction and method.

Convert substantive criticism into experiments.

---

# 32. CVPR manuscript generation

Only after the upgraded contribution reaches the research threshold:

1. retrieve the CURRENT target-year CVPR/ICCV official author guidelines;
2. download/use the official LaTeX author kit;
3. build an anonymized conference manuscript.

Create:

`CVPR_UPGRADE/PAPER/main.tex`

`CVPR_UPGRADE/PAPER/references.bib`

`CVPR_UPGRADE/PAPER/figures/`

`CVPR_UPGRADE/PAPER/supplement.tex`

`CVPR_UPGRADE/PAPER/CLAIM_TRACEABILITY.md`

`CVPR_UPGRADE/PAPER/main.pdf`

For planning purposes, the latest verified CVPR format uses an eight-page main paper excluding references, but always replace this with the actual target-year official requirement when available.

The CVPR paper must NOT simply be a shortened TMI manuscript.

It must foreground the upgraded innovation.

---

# 33. Desired upgraded paper shape

A strong eventual conference narrative might become:

## Discovery

Deterministic MRI interpolators exhibit large shared reconstruction error that ordinary disagreement cannot observe.

## Theory

Disagreement removes aligned error components; measurement overlap controls error alignment.

## Controlled causal evidence

Target-preserving overlap manipulation changes error observability.

## Design principle

Useful reliability interventions should reduce shared error-generating information, not maximize raw output diversity.

## New method/capability

A mechanism-derived disjoint-context protocol, risk estimator, densification-benefit predictor, or reconstruction strategy.

## Evidence

Multiple cohorts + models + analytical interpolators + overlap ladder + strong baselines + statistical inference + failure cases.

Do not force this narrative if experiments contradict it.

The evidence determines the final story.

---

# 34. Relationship between TMI and CVPR drafts

These are research artifacts, not instructions to submit simultaneously.

Do not submit anything.

Maintain:

`SUBMISSION_STRATEGY.md`

Document scientific overlap between the two drafts.

The CVPR upgrade must be tracked carefully so that any future submission complies with the target venues' policies on:

* dual submission;
* prior publication;
* conference/journal extension;
* disclosure of overlapping work.

If the eventual CVPR manuscript remains substantially similar to the TMI manuscript, flag:

`SUBMISSION_CONFLICT_RISK`

rather than pretending both can be submitted concurrently.

---

# 35. Execution behavior

Work autonomously.

For Track A:

continue until the complete TMI LaTeX manuscript compiles and passes the compliance/evidence audit.

For Track B:

continue hypothesis-driven research after the TMI manuscript is complete.

Do not stop Track B to report that the TMI manuscript is finished.

Do not repeatedly ask for routine technical decisions.

If one research hypothesis fails:

record it → explain it → generate the next discriminative hypothesis.

If the current reliability direction reaches a ceiling:

investigate a mechanism-derived reconstruction or acquisition consequence.

If a new paper threatens novelty:

reassess immediately.

If a script fails:

debug and continue.

Only request human intervention for irreducible blockers such as:

* inaccessible required data;
* missing private-dataset ethics information;
* unavailable credentials;
* impossible compute requirement;
* author names/affiliations that cannot be inferred;
* a submission-policy decision that requires the authors.

---

# 36. Required deliverables

TRACK A is complete only when the following exist and compile:

`TMI_MANUSCRIPT/main.tex`

`TMI_MANUSCRIPT/main.pdf`

`TMI_MANUSCRIPT/references.bib`

`TMI_MANUSCRIPT/figures/`

`TMI_MANUSCRIPT/EVIDENCE_LEDGER.md`

`TMI_MANUSCRIPT/CLAIM_TRACEABILITY.md`

`TMI_MANUSCRIPT/TMI_REQUIREMENTS.md`

`TMI_MANUSCRIPT/TMI_COMPLIANCE_CHECK.md`

and all major manuscript claims are supported.

TRACK B continues until a meaningfully stronger research contribution is established.

At that point additionally produce:

`CVPR_UPGRADE/PUBLICATION_READINESS_REPORT.md`

and, if the threshold is genuinely met:

`CVPR_UPGRADE/PAPER/main.tex`

`CVPR_UPGRADE/PAPER/main.pdf`

`CVPR_UPGRADE/PAPER/references.bib`

`CVPR_UPGRADE/PAPER/supplement.tex`

---

# 37. Final instruction

Do two different jobs simultaneously:

**Preserve and communicate what is already true at TMI quality.**

and

**Continue discovering something stronger at CVPR quality.**

Do not weaken scientific rigor to make either manuscript look better.

Do not let paper writing terminate research.

Do not let new exploratory experiments silently alter the frozen TMI evidence.

Do not optimize for more experiments.

Optimize for:

**mechanism → falsifiable prediction → controlled evidence → methodological consequence → strong scientific contribution.**

Begin now.
