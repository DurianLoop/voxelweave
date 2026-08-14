# PLAN 8B — CVPR Narrative Recovery and Evidence-Focused Rebuild

/goal

Re-open the strongest pre-Plan-7 CVPR research state and rebuild the CVPR manuscript around the strongest scientifically supported contribution.

The purpose of this phase is NOT to make every exploratory research branch successful.

The purpose is to construct the strongest truthful CVPR paper supported by the full evidence base.

The Plan-7 adversarial review was useful for identifying boundaries, but it should NOT automatically redefine the paper as unsuccessful merely because several exploratory capability branches failed.

A research paper is not required to report every failed exploratory idea in the main manuscript.

However:

**Do not suppress evidence that directly contradicts or materially qualifies the final central claim.**

The rule is:

> Select experiments according to relevance to the final hypothesis, not according to whether their numerical result is favorable.

---

# 1. Reset the CVPR evaluation philosophy

Do NOT require the paper to prove:

* Anchor-CV universally beats adjacent RMSE;
* every shared-influence experiment is monotonic;
* every dataset produces significance;
* every local plane behaves identically;
* every mechanism-derived method succeeds;
* a new reconstruction network must outperform existing methods.

These were overly restrictive Plan-7 method-paper gates.

Instead determine:

> What is the strongest coherent scientific contribution already supported by the evidence?

Evaluate the paper as a:

**mechanism-first computer vision / medical imaging methodology paper**

with a lightweight practical consequence.

---

# 2. Return to the strongest established scientific chain

The current strongest candidate narrative is:

### Observation

Deterministic MRI interpolation outputs can agree while being jointly wrong.

### Empirical decomposition

A large fraction of reconstruction error is shared across contexts.

### Mechanism

When two reconstruction contexts depend strongly on the same physical measurements, their errors become aligned.

### Consequence

Aligned error cancels when predictions are subtracted, producing disagreement blindness.

### Controlled intervention

Target-preserving measurement-disjoint phase grids reveal error substantially better than shared-measurement controls.

### Mechanism refinement

Integer measurement overlap is insufficient.

The important variable is:

**shared estimator influence**.

### Practical consequence

Acquired-anchor cross-validation provides a lightweight examination-level indicator of interpolation difficulty without dense targets at scoring time.

This is the candidate paper story.

Do not require the final practical method to universally dominate all trivial baselines for the mechanism contribution to remain valid.

---

# 3. Re-score the contribution using mechanism-paper criteria

Create:

`CVPR_MECHANISM_SCORECARD.md`

Score:

* Novelty
* Importance
* Mechanistic depth
* Experimental rigor
* Predictive validity
* Reproducibility
* Reviewer resilience

Do NOT include:

“universally superior method”

as a mandatory scoring dimension.

Separately score:

`Methodological consequence`

but allow the paper to remain viable if the central contribution is primarily scientific/mechanistic.

---

# 4. Audit all experiments by relevance to the final claim

Create:

`EXPERIMENT_RELEVANCE_AUDIT.md`

For every experiment from Plans 1–7 classify:

### CORE

Directly tests the final central claim.

### SUPPORTING

Provides robustness, generalization or mechanistic support.

### BOUNDARY

Shows an important limitation of the final claim.

### EXPLORATORY-NONCENTRAL

Tests an abandoned method/hypothesis that is not required to evaluate the final claim.

### REDUNDANT

Does not materially change the paper.

---

# 5. Manuscript inclusion policy

Use:

### CORE

Almost always include.

### SUPPORTING

Include strongest and most informative subset.

### BOUNDARY

Include when necessary to prevent overclaiming; often concise main-text statement with detailed results in supplement.

### EXPLORATORY-NONCENTRAL

Do NOT include in the main manuscript unless scientifically informative.

Preserve in internal research logs.

### REDUNDANT

Remove from manuscript.

Do not treat the CVPR paper as a chronological research diary.

---

# 6. Plan-7 failed methods

The following exploratory branches were tested:

* minimum-influence context selection;
* multi-anchor jackknife IQR;
* covariance residualization.

These methods are NOT part of the final central contribution unless new evidence justifies them.

Therefore:

do not devote significant main-paper space to these failed exploratory methods.

They may be:

* omitted from the main paper;
* briefly mentioned as negative exploratory evidence if relevant;
* retained in research logs;
* optionally summarized in supplementary material if useful.

Do NOT use them to downgrade the core measurement-dependence/shared-influence mechanism.

However, if any failed experiment directly falsifies a sentence in the final manuscript:

change the sentence.

Do not hide the contradiction.

---

# 7. Anchor-CV positioning

Do NOT claim:

> Anchor-CV is universally superior to adjacent-anchor difference, PC, TTA, or committee disagreement.

Instead evaluate the scientifically supportable statement:

> Anchor-CV provides a simple acquired-only examination-level cross-validation signal that tracks interpolation difficulty across multiple cohorts and can support retrospective triage/densification analysis.

Its value may be:

* simplicity;
* no dense target at scoring;
* no additional trained model;
* no x8 inference;
* examination-level predictive validity.

It does not need to be the central novelty.

Use it as:

**a practical consequence of the broader mechanism.**

---

# 8. Recover the strongest quantitative evidence

Construct a new:

`CORE_RESULT_TABLE.md`

Prioritize the strongest, most reproducible experiments.

At minimum inspect:

## Controlled measurement-dependence effect

fastMRI:

disjoint vs shared error-ranking difference.

NingXia:

same comparison.

## Cross-estimator support

HAT
SwinIR
linear
cubic

## Consensus error decomposition

shared versus observable error energy.

## Shared-influence refinement

coefficient / finite-response influence versus integer overlap count.

## Independent cohort

IXI.

## Predictive consequence

x4→x2 densification benefit where available.

## Anchor-CV

examination-level difficulty ranking.

Do not overload the paper with secondary experiments.

---

# 9. Main quantitative principle

The manuscript should emphasize effect size, not only significance.

Examples include:

* disjoint versus shared Δrho;
* shared-error fraction;
* improvement of influence-based explanatory variable over overlap count;
* cross-cohort Anchor-CV correlation;
* oracle-normalized densification gain.

Use confidence intervals.

Avoid excessive p-value presentation.

---

# 10. Reframe Plan-7 plane dependence correctly

Plan-7 found neural influence varies across physical planes.

Do NOT automatically interpret this as failure.

Ask:

> Does the central claim require plane invariance?

If the paper claims:

“shared influence is a global intrinsic property of the model,”

then plane dependence is fatal.

Do not make that claim.

Instead consider the more physically meaningful formulation:

> Shared influence is a **target- and context-dependent local property**.

Plane dependence may therefore be expected.

Analyze whether local influence still explains local error alignment.

If yes:

use plane dependence as part of the mechanism.

If no:

narrow the claim.

---

# 11. NingXia mixed results

Do not hide them if they directly test a main claim.

But do not let the smallest eight-patient cohort dominate the narrative.

Use appropriate hierarchy:

### Primary mechanism evidence

fastMRI + IXI where sample size is substantially larger.

### Small-cohort replication/boundary

NingXia.

Explicitly report patient-clustered uncertainty.

Use wording such as:

> the direction is preserved but evidence is less precise in the eight-patient NingXia cohort

only if this is actually supported.

If direction is not preserved:

state the actual result.

---

# 12. Distinguish universal claims from dataset-level evidence

Avoid:

“always”

“universally”

“all MRI”

“guarantees”

“proves correctness”.

Prefer:

“across the evaluated cohorts”

“under the controlled interpolation settings”

“supports”

“is associated with”

“provides evidence that”.

This allows a strong paper without pretending every stratum is identical.

---

# 13. Restore the strongest conceptual innovation

The paper should not be remembered as:

“another uncertainty metric.”

The reviewer-memory message should be:

> **Disagreement is only as informative as the independence of the information generating the compared predictions.**

In MRI slice interpolation:

shared measurements

→ shared estimator influence

→ aligned reconstruction errors

→ cancellation in disagreement.

This is the conceptual contribution.

---

# 14. Explain why overlap count was falsified

This is a strength.

The early hypothesis:

> more shared anchors monotonically causes worse observability

was too crude.

Experiments rejected it.

The refined mechanism is:

> Different measurements contribute unequally to the estimator.

Therefore:

**shared influence**

is more informative than:

**shared measurement count**.

This scientific progression should appear in the manuscript.

It demonstrates:

hypothesis → falsification → refined mechanism.

---

# 15. Shared influence result

Build the mechanism section around the strongest valid evidence that:

shared-influence statistics correlate with:

* error cosine;
* error alignment;
* disagreement observability

more strongly than overlap count.

Use:

* analytical coefficient results;
* neural finite-response evidence.

Do not imply neural coefficients exist globally.

For nonlinear networks use language such as:

**local response / local influence approximation**.

---

# 16. Theory section

Use the error relation:

e_i = f_i - y

and:

# ||e_i - e_j||²

||e_i||²
+
||e_j||²
--------

2 <e_i,e_j>.

The important insight is not the identity itself.

The important question is:

> What determines <e_i,e_j>?

The paper's empirical answer is:

**shared measurement influence is one determinant of error alignment in MRI interpolation.**

This is the novelty bridge.

---

# 17. One-sided reliability boundary

Retain the earlier rigorous boundary:

large prediction separation can provide evidence that at least one reconstruction is inaccurate.

But:

small separation cannot prove correctness.

Use stable-wrong examples to demonstrate this.

Do not oversell disagreement as uncertainty calibration.

---

# 18. Figure hierarchy

Redesign the paper around approximately four central figures.

## Figure 1

Mechanism:

shared measurement influence

→ aligned error

→ disagreement cancellation.

## Figure 2

Controlled measurement-context intervention.

Show:

same target

different overlap/influence.

## Figure 3

Core mechanism evidence.

Across:

fastMRI
IXI
NingXia

show:

shared influence vs error alignment / observability.

## Figure 4

Practical consequence.

Anchor-CV / densification-benefit analysis.

Additional robustness goes to compact tables/supplement.

---

# 19. Avoid “everything table”

Do not put every experiment into the main manuscript.

CVPR readers should not need to reconstruct the entire seven-plan research history.

Main paper should answer:

1. Does consensus blindness exist?
2. Why?
3. Does measurement dependence cause/predict error alignment?
4. Is influence better than raw overlap count?
5. Does the insight enable something useful?

Everything else is secondary.

---

# 20. Revisit novelty audit

Perform a new literature audit specifically for the refined claim.

Search:

* correlated ensemble errors;
* dependent uncertainty estimators;
* disagreement under correlated predictions;
* measurement overlap;
* estimator influence;
* reconstruction sensitivity;
* self-consistency uncertainty;
* MRI slice interpolation;
* inverse-problem reliability;
* common-mode uncertainty failure.

For closest papers compare:

* Do they manipulate physical measurement dependence?
* Do they preserve the same missing target?
* Do they study error cancellation?
* Do they quantify shared influence?
* Do they connect influence to reliability observability?

Never claim absolute priority.

---

# 21. Reviewer simulation should match the actual paper type

Do not ask reviewers:

> “Does this introduce the best new reconstruction method?”

Ask:

### Reviewer A

Is the mechanism new and non-obvious?

### Reviewer B

Are the controlled experiments convincing?

### Reviewer C

Does the paper distinguish correlation from mechanism appropriately?

### Reviewer D

Does the finding matter for reliability research?

### Reviewer E

Is the practical consequence sufficient?

### Area Chair

Does the total scientific contribution justify CVPR publication?

Score the actual paper rather than an imaginary leaderboard method paper.

---

# 22. What unfavorable evidence MUST remain visible

Any result that directly limits the following must be retained somewhere in the submitted paper/supplement:

* plane invariance;
* universal cohort generalization;
* Anchor-CV superiority;
* local uncertainty localization;
* calibrated uncertainty;
* prospective acquisition benefit.

Use these results to constrain wording.

Do not bury them in inaccessible internal logs if the manuscript would otherwise imply the opposite.

---

# 23. What exploratory negative work may be removed from the main narrative

Experiments testing abandoned ideas may be omitted if the final paper does not depend on those claims.

Examples may include:

* failed arbitrary method combinations;
* rejected selectors;
* failed fusion attempts;
* unnecessary hyperparameter branches.

Do not write the paper as a laboratory notebook.

---

# 24. Rebuild title

Do not keep the Plan-7 overly negative title automatically.

Generate titles around the strongest positive scientific discovery.

Possible directions:

**Shared Measurement Influence Governs Disagreement Reliability in MRI Slice Interpolation**

or:

**When Agreement Hides Error: Shared Measurement Influence in MRI Slice Interpolation**

or:

**Shared Influence Explains Consensus Blindness in Deterministic MRI Interpolation**

Select the title only after final manuscript reconstruction.

Avoid sensational language.

---

# 25. Rebuild abstract

The abstract should primarily communicate:

* reliability problem;
* shared-error phenomenon;
* controlled measurement intervention;
* influence refinement;
* major cross-cohort evidence;
* practical consequence;
* boundary.

Do NOT spend abstract space on failed exploratory methods.

Do NOT say:

“our method universally outperforms...”

unless directly supported.

---

# 26. Contribution structure

Target approximately three contributions.

A plausible structure:

1. **Phenomenon and theory**

Identify consensus blindness caused by aligned reconstruction errors.

2. **Mechanism**

Show through controlled physical measurement interventions that shared estimator influence explains error alignment better than raw anchor overlap.

3. **Consequence**

Demonstrate an acquired-only examination-level reliability/triage signal and retrospective densification-value prediction derived from the mechanism.

Adjust according to final evidence.

---

# 27. Re-evaluate the previous 4/4/5/4/4 score

After rebuilding the manuscript, independently score:

Novelty
Importance
Mechanistic depth
Experimental rigor
Reviewer resilience.

Compare:

Plan-6 score
Plan-7 adversarial score
new mechanism-paper score.

Explain why scores changed.

Do not artificially restore 4/5 ratings.

The purpose is to determine whether Plan-7 downgraded the paper because of genuine weaknesses or because it judged the paper against an unnecessarily strict method-superiority objective.

---

# 28. Reconstruct a full 8-page CVPR manuscript

Only after the scientific narrative is settled:

create:

`CVPR/CVPR_RECOVERED/PAPER/main.tex`

`CVPR/CVPR_RECOVERED/PAPER/main.pdf`

`CVPR/CVPR_RECOVERED/PAPER/references.bib`

`CVPR/CVPR_RECOVERED/PAPER/supplement.tex`

`CVPR/CVPR_RECOVERED/PAPER/supplement.pdf`

`CVPR/CVPR_RECOVERED/PAPER/CLAIM_TRACEABILITY.md`

`CVPR/CVPR_RECOVERED/PAPER/EVIDENCE_SELECTION_AUDIT.md`

The main paper should use the full current eight-page scientific allowance where scientifically justified.

References follow the official target-year policy.

---

# 29. Evidence Selection Audit

Create:

`EVIDENCE_SELECTION_AUDIT.md`.

For every experiment excluded from the main manuscript state:

* experiment ID;
* result;
* reason for exclusion;
* whether it contradicts any final claim;
* where it remains documented.

If an excluded experiment materially contradicts a final claim:

either include it or weaken/remove the claim.

This guarantees that manuscript focus does not become misleading cherry-picking.

---

# 30. Final red-team

After rebuilding:

simulate:

* 5 reviewers;
* 1 AC;
* 1 SAC.

Give each ONLY the final manuscript and supplement.

Do not give them the entire research history.

This is important.

A reviewer evaluates the submitted paper, not every exploratory experiment ever conducted.

Ask:

> Based on the evidence actually necessary to evaluate the submitted claims, is the paper convincing?

Generate:

`FINAL_REVIEW_SIMULATION.md`.

---

# 31. Success condition

The recovered CVPR paper is viable if:

* central claim is precise;
* all material contradictory evidence is properly reflected;
* mechanism survives;
* shared influence provides a genuinely deeper explanation than raw overlap;
* cross-cohort/model evidence remains compelling;
* practical consequence exists;
* novelty audit remains favorable;
* final manuscript is substantially clearer than Plan-7;
* median simulated reviewer score reaches approximately weak-accept or better.

Do not require a universal superior reliability method unless the paper claims one.

---

# 32. Final principle

Do NOT optimize by hiding inconvenient evidence.

Optimize by:

**choosing the right scientific question.**

A paper can truthfully omit hundreds of failed exploratory experiments.

A paper cannot truthfully omit evidence that invalidates its stated conclusion.

The target is:

> the strongest, narrowest, most defensible and most interesting claim supported by the data.

Not:

> the most favorable subset of numbers.

Rebuild the CVPR paper around that distinction.
