# Research Expansion Goal

## Expand TMI to a 20-Page Research Master and CVPR to a Full 8-Page Main Paper Through New Science — Not Padding

Continue the existing dual-track MRI inter-slice interpolation research program under:

`D:\MRI\design\paper`

Current state:

* TMI manuscript exists but is only approximately 6 pages.
* CVPR manuscript exists but uses only approximately 5 pages of true main-paper content before references.
* Both manuscripts are scientifically promising but currently too compressed to represent the full research program.
* The next objective is NOT prose expansion.
* The next objective is to conduct additional scientifically necessary experiments, theory, mechanism validation, robustness studies, ablations, statistical analyses, and failure analyses so that the papers become naturally longer because the evidence becomes substantially richer.

Remain entirely within:

**MRI inter-slice / through-plane interpolation.**

Do NOT introduce unrelated domains such as video, CT, natural-image super-resolution, or generic computer vision merely to broaden scope.

---

# 0. CRITICAL PAGE-POLICY DISTINCTION

Do not confuse a research master manuscript with a submission-compliant manuscript.

For TMI maintain TWO versions.

## TMI Research Master

Target:

**18–20 dense IEEE double-column pages including references.**

This is an internal complete scientific manuscript.

Its purpose is to preserve the entire scientifically valuable evidence chain.

It is NOT the initial submission PDF.

Path:

`TMI/TMI_MANUSCRIPT_MASTER/`

Target file:

`main_20page.pdf`

---

## TMI Submission Version

The current official TMI Regular Paper initial submission limit must be verified again before submission.

Under the currently verified policy, the initial Regular Paper must remain within:

**10 pages including references.**

Therefore after the 18–20 page master is complete, independently produce:

`TMI/TMI_MANUSCRIPT_SUBMISSION/main.tex`

and:

`TMI/TMI_MANUSCRIPT_SUBMISSION/main.pdf`

that satisfy the current official TMI initial-submission rules.

Do NOT reduce font size below the official minimum.

Do NOT change margins.

Do NOT hide core science in unreadable figures.

Do NOT treat the 20-page master as TMI supplementary material.

---

## CVPR Main Paper

Use the currently available official CVPR author kit for working purposes.

Target:

**8 full main-content pages excluding references.**

References should begin only after the eight-page main-paper allowance has been meaningfully used.

The objective is NOT to mechanically force exactly eight pages.

The objective is to produce enough scientifically necessary content that a strong CVPR manuscript naturally occupies approximately the full eight-page main-paper budget.

Path:

`CVPR/CVPR_UPGRADE/PAPER/`

---

# 1. ABSOLUTE ANTI-PADDING RULE

You are explicitly forbidden from reaching the target lengths primarily by:

* making the Introduction longer;
* adding generic background;
* bloating Related Work;
* repeating results in Discussion;
* increasing figure size without scientific reason;
* adding verbose implementation prose;
* repeating limitations;
* explaining textbook concepts unnecessarily;
* increasing whitespace;
* manipulating margins;
* reducing information density;
* adding redundant tables;
* reporting trivial hyperparameter sweeps.

If either manuscript is too short, the default interpretation must be:

> **The research evidence is not yet sufficiently complete.**

The response must therefore be:

**identify an evidence gap → formulate hypothesis → run experiment → analyze → add result**

rather than:

**write more prose**.

---

# 2. FIRST TASK: CONTENT GAP AUDIT

Before modifying either manuscript, create:

`PAPER_EXPANSION_GAP_AUDIT.md`

Analyze every current page, section, figure, table, and claim.

For each manuscript answer:

1. Which claims currently have only one experiment?
2. Which mechanisms are only partially demonstrated?
3. Which reviewer objections currently have verbal rather than experimental answers?
4. Which datasets/models/factors are underused?
5. Which statistical analyses are missing?
6. Which negative findings deserve formal analysis?
7. Which theoretical predictions remain untested?
8. Which results currently appear only as single numbers but deserve complete curves or decompositions?
9. Which conclusions rely too heavily on correlation?
10. Which claims could be converted into causal or predictive tests?
11. Which missing experiments would genuinely change reviewer confidence?
12. Which figures should exist if this were already a mature TMI/CVPR paper?

Rank gaps:

P0 — could threaten acceptance
P1 — materially strengthens claim
P2 — useful completeness
P3 — cosmetic

Execute P0 and P1 work before prose expansion.

---

# PART A — TMI SCIENTIFIC EXPANSION

The TMI paper should become the **deep, comprehensive medical-imaging characterization** of disagreement reliability in deterministic MRI slice interpolation.

Its additional pages should come primarily from:

* richer theory;
* multi-cohort medical imaging evidence;
* full statistical characterization;
* robustness;
* failure modes;
* geometry/intensity controls;
* factor/model analysis;
* clinically relevant interpretation boundaries;
* detailed retrospective densification analysis.

Do not turn it into the CVPR Anchor-CV paper.

Keep the TMI scientific center on:

**consensus blindness + measurement-overlap reliability mechanism.**

---

# 3. TMI EXPERIMENT FAMILY A

## Complete consensus-error decomposition

The current 81–87% shared-error result is scientifically important and deserves deeper validation.

For every eligible:

* dataset;
* reconstruction architecture;
* factor pair;
* examination;

compute and report:

* total squared error;
* shared consensus component;
* context-sensitive component;
* shared fraction;
* observable fraction;
* error cosine;
* disagreement magnitude.

Analyze distributions rather than only means.

Ask:

* Does shared-error fraction increase with interpolation factor?
* Is it examination dependent?
* Is it architecture dependent?
* Does high shared-error fraction predict disagreement failure?
* Does it explain PC/TTA/committee heterogeneity?

Use examination/patient-clustered inference.

Create a major TMI figure around this decomposition.

---

# 4. TMI EXPERIMENT FAMILY B

## Full overlap-response characterization

Do not report only zero versus maximal overlap.

Use every scientifically valid overlap configuration already available from Plan 1–4.

For each condition analyze:

* overlap amount;
* shared physical measurements;
* disagreement;
* retrospective error;
* error cosine;
* disagreement-error Spearman;
* AURC/nAURC where appropriate.

Explicitly distinguish:

`measurement overlap`

from:

`prediction diversity`.

If strict monotonicity fails, report it.

Do not import the later CVPR shared-influence claim into TMI unless authors deliberately decide to revise the frozen scope.

The TMI objective is comprehensive characterization, not post-hoc mechanism replacement.

---

# 5. TMI EXPERIMENT FAMILY C

## Metric robustness

The current claim should not depend on one error metric.

Where scientifically valid, evaluate reliability relationships using multiple reconstruction endpoints, for example:

* MAE;
* RMSE;
* MSE;
* PSNR;
* SSIM;
* gradient-domain error;
* low-frequency error;
* high-frequency error;

and any other already justified medical-imaging reconstruction metric.

Do NOT add perceptual metrics merely to increase count.

Ask:

> Does measurement-disjoint disagreement reveal broadly poor reconstruction or only the exact metric from which it was designed?

Report disagreements between endpoints honestly.

---

# 6. TMI EXPERIMENT FAMILY D

## Granularity analysis

Extend the existing reliability evidence across:

* pixel;
* physical plane;
* examination;
* patient where applicable.

For each granularity clearly define the independent statistical unit.

Do NOT infer clinical significance from pixel-level sample counts.

Investigate:

* where localization works;
* where it fails;
* whether examination-level triage is naturally more stable;
* whether the method detects concentrated local failures or diffuse examination difficulty.

Create visual examples of:

* high disagreement / high error;
* high disagreement / low error;
* low disagreement / high error;
* low disagreement / low error.

The stable-wrong category must be prominent.

---

# 7. TMI EXPERIMENT FAMILY E

## Factor robustness

Analyze:

x2
x4
x6

systematically.

Questions:

* How does actual reconstruction error scale with factor?
* How does shared-error fraction scale?
* How does disagreement observability scale?
* Does measurement-overlap effect strengthen with missing information?
* Are x2–x4, x2–x6 and x4–x6 qualitatively different?
* Is one pair responsible for the main result?

Do not select only the strongest pair.

Use full factor-wise figures.

---

# 8. TMI EXPERIMENT FAMILY F

## Architecture and estimator generality

Expand the existing HAT/SwinIR/linear/cubic evidence.

For each estimator report not only final rho but:

* error distribution;
* shared-error fraction;
* error alignment;
* overlap effect;
* failure examples.

Where other already trained/frozen interpolation methods exist in the repository and can be evaluated fairly, include them.

Do NOT train arbitrary extra networks simply to increase method count.

The purpose is to determine whether consensus blindness is:

* neural-specific;
* architecture-specific;
* or intrinsic to interpolation contexts.

---

# 9. TMI EXPERIMENT FAMILY G

## Geometry stress audit

The current geometry audit is important enough to formalize in the paper.

Evaluate sensitivity to:

* physical-plane matching tolerance;
* affine precision;
* orientation;
* plane normal;
* in-plane spacing;
* field of view;
* common support definition;
* anchor exclusion.

Test reasonable tolerance perturbations.

Ask:

> Would a small geometry mismatch change the main result?

If not, demonstrate robustness.

If yes, state the valid operating regime.

---

# 10. TMI EXPERIMENT FAMILY H

## Intensity comparability

Plan-2 showed that intensity handling matters.

Perform a dedicated analysis comparing scientifically valid normalization strategies.

At minimum distinguish:

* raw common-scale intensities;
* pooled per-case normalization;
* independent per-factor normalization.

Determine:

* which transformations preserve the scientific meaning of cross-context discrepancy;
* which destroy comparability;
* whether raw dynamic range confounds examination ranking;
* whether overlap conclusions persist after fair normalization.

This should become a formal methodological section rather than a brief caveat.

---

# 11. TMI EXPERIMENT FAMILY I

## Statistical robustness

For every central result include appropriate:

* effect size;
* examination/patient-cluster bootstrap CI;
* paired permutation test where justified;
* leave-one-examination/patient-out influence;
* heterogeneity across architectures/factors;
* forest plots.

For NingXia, verify whether:

`22 sequences`

belong to:

`8 independent patients`

and always use the correct clustering hierarchy.

Never represent 22 series as 22 independent patients.

---

# 12. TMI EXPERIMENT FAMILY J

## Risk–coverage analysis

Do not summarize selective prediction using one nAURC.

Provide complete risk–coverage curves.

At prespecified coverage levels such as:

10%, 20%, 30%, 50%, 70%, 90%

analyze retained reconstruction risk.

Compare:

* committee;
* ordinary PC;
* TTA where available;
* measurement-disjoint reliability;
* relevant input baseline.

Explain curve crossings.

Determine which method is useful in which coverage regime.

---

# 13. TMI EXPERIMENT FAMILY K

## Retrospective densification consequence

The x4→x2 benefit result is valuable.

Develop it more completely while preserving the retrospective limitation.

Evaluate fixed budgets such as:

10%, 20%, 30%, 50%.

Compare:

* random;
* oracle;
* ordinary disagreement;
* PC;
* TTA where valid;
* disjoint signal;
* adjacent-anchor difficulty.

Report:

* absolute reduction in reconstruction error;
* oracle-normalized attainable gain;
* confidence intervals;
* budget–benefit curves.

Explicitly state:

**This is retrospective acquisition simulation, not prospective acquisition optimization.**

---

# 14. TMI EXPERIMENT FAMILY L

## Error taxonomy and qualitative evidence

Create:

`TMI_ERROR_TAXONOMY.md`

Systematically categorize important reconstruction/reliability failures.

Examples, only when supported:

* stable smoothing;
* boundary-context failure;
* high-curvature anatomy;
* factor-specific failure;
* intensity-scale failure;
* shared-anchor failure;
* context-sensitive hallucination.

For each category provide:

* MRI slice example;
* error map;
* disagreement map;
* explanation;
* whether the reliability method detects it.

Use a compact multi-panel figure.

---

# 15. TMI EXPERIMENT FAMILY M

## Efficiency / deployment analysis

Measure actual computational requirements for the major reliability strategies where possible:

* number of reconstruction executions;
* wall-clock inference time;
* GPU memory;
* storage requirements;
* additional context generation;
* CPU cost for analytical scores.

Do not claim “efficient” without numbers.

Explain the practical distinction between:

* committee;
* TTA;
* ordinary PC;
* measurement-disjoint analysis.

---

# 16. TMI THEORY EXPANSION

Develop the theory section beyond the current short decomposition.

Study:

`e_a = c + r_a`

`e_b = c + r_b`

and more general correlated-error formulations.

Develop:

`||e_a-e_b||²`

as a function of:

* individual error energies;
* error inner product;
* error cosine;
* shared component.

Use this theory to predict experimentally observed behaviors.

Include:

### Extreme 1

Perfect shared error.

### Extreme 2

Opposing / independent error directions.

### Extreme 3

Stable-but-wrong agreement.

### Extreme 4

Large harmless diversity.

Clearly distinguish:

* diversity;
* observability;
* reliability ranking;
* calibration.

Theory must explain experiments rather than merely increase manuscript length.

---

# 17. TMI MASTER TARGET STRUCTURE

After new experiments are complete, construct the 18–20 page master approximately around:

1. Abstract
2. Introduction
3. Related Work
4. Theory of Disagreement Blindness
5. Measurement-Overlap Formulation
6. Datasets and Reconstruction Models
7. Experimental Protocol
8. Consensus-Error Decomposition
9. Controlled Measurement-Overlap Experiments
10. Multi-Architecture and Analytical Generalization
11. Metric and Factor Robustness
12. Geometry and Intensity Confound Controls
13. Multi-Granularity Reliability
14. Risk–Coverage Evaluation
15. Retrospective Densification Analysis
16. Failure Taxonomy
17. Computational/Deployment Analysis
18. Discussion
19. Limitations
20. Conclusion
21. References

Do not mechanically create 20 headings.

Combine sections according to scientific flow.

Target approximately:

**18–20 information-dense pages**

in IEEE double-column format.

---

# 18. TMI PAGE-GROWTH LEDGER

Create:

`TMI/TMI_MANUSCRIPT_MASTER/PAGE_GROWTH_LEDGER.md`

For every page added beyond the original six pages record:

* what new scientific information justified it;
* experiment IDs;
* figure/table added;
* claim strengthened.

If a new page cannot be linked to new evidence, theory, or necessary methodological detail:

remove it.

---

# 19. TMI SUBMISSION DISTILLATION

Only AFTER the 18–20 page master is complete:

derive the official 10-page TMI submission version.

Do not simply shrink everything.

Rank evidence into:

P0 main claim
P1 essential support
P2 secondary evidence

Move nothing into prohibited manuscript-like supplementary material.

Select the most decisive evidence for the 10-page initial submission.

Preserve the full 20-page master internally for:

* revision;
* rebuttal preparation;
* future extension;
* internal documentation.

---

# PART B — CVPR EXPANSION TO A TRUE 8-PAGE PAPER

The current CVPR paper should not be padded from approximately five main-content pages to eight.

The extra content must primarily come from **new mechanistic experiments and a stronger derived method**.

Current upgraded chain:

measurement overlap

→ shared influence

→ error alignment

→ disagreement blindness

→ Anchor-CV.

The goal is to make every arrow experimentally convincing.

---

# 20. CVPR PRIORITY A

## Neural shared-influence approximation

Current shared-influence evidence uses analytical estimator coefficients.

A major reviewer risk is:

> “Your coefficient mechanism is exact for linear/cubic estimators but not demonstrated in HAT/SwinIR.”

Address this directly.

Investigate neural approximations of measurement influence using scientifically valid methods such as:

* input Jacobian norms;
* gradient-based sensitivity;
* integrated gradients if justified;
* finite-difference anchor perturbation;
* leave-one-anchor-out influence;
* occlusion/context ablation;
* local linearization around the observed input.

Do NOT choose an attribution method merely because it produces attractive heatmaps.

Define a measurable neural shared-influence quantity.

Test whether it predicts:

* neural error cosine;
* shared-error fraction;
* disagreement observability.

Compare it against simple anchor-overlap count.

This is a P0 CVPR experiment.

---

# 21. CVPR PRIORITY B

## Test the full causal chain

Test separately:

### Arrow 1

Measurement overlap/shared influence

→ error alignment.

### Arrow 2

Error alignment

→ disagreement suppression.

### Arrow 3

Disagreement suppression

→ poorer error ranking.

### Arrow 4

Reduced shared influence

→ improved reliability observability.

For every arrow report:

* effect;
* CI;
* case-cluster inference;
* architecture heterogeneity;
* dataset heterogeneity.

Where appropriate perform mediation-style analysis, but do not make causal mediation claims unless assumptions are justified.

The objective is a coherent mechanism chain, not four disconnected correlations.

---

# 22. CVPR PRIORITY C

## Cleaner neural overlap ladder

Construct the cleanest possible overlap ladder for HAT and SwinIR.

Where physically feasible vary:

* shared anchor count;
* shared influence;
* anchor identity;
* context distance;

while holding fixed:

* target physical plane;
* model;
* case;
* input count;
* evaluation mask.

The current result has already falsified a simple overlap-count law.

Use the new experiment to demonstrate:

> shared influence explains reliability better than integer overlap.

Do not attempt to restore monotonic overlap-count behavior.

A falsified simple hypothesis is part of the contribution.

---

# 23. CVPR PRIORITY D

## Anchor-CV independent confirmation

Anchor-CV currently has extremely strong examination-level correlations.

Do not keep optimizing it on the same evidence.

Freeze:

`ANCHOR_CV_V1`.

Write:

`ANCHOR_CV_FROZEN.md`.

Then find the cleanest unused evaluation subsets available.

If feasible, create frozen evaluation partitions from:

* fastMRI;
* IXI;
* NingXia;

without leakage from earlier method development.

Do not modify Anchor-CV after observing held-out results.

Report:

* rho;
* Kendall;
* nAURC;
* risk–coverage;
* densification-benefit prediction;
* LOO influence.

---

# 24. CVPR PRIORITY E

## Generate IXI x2 evidence if scientifically and computationally feasible

IXI currently lacks the x2 densification-benefit endpoint.

Inspect available raw data and frozen reconstruction pipelines.

If valid x2 reconstructions can be generated without changing the experimental definition:

generate them.

Before observing results freeze:

* models;
* preprocessing;
* score;
* evaluation metric;
* budget levels.

Then test:

> Does Anchor-CV predict actual x4→x2 reconstruction benefit on the 115-case IXI cohort?

This would provide a substantially stronger independent consequence test.

If technically impossible, document the exact blocker.

Do not fabricate or substitute an incomparable endpoint.

---

# 25. CVPR PRIORITY F

## Budget-policy confirmation

Using frozen scores, evaluate:

10%
20%
30%
50%

densification budgets.

For every dataset with valid dense outcomes compare:

* random;
* oracle;
* committee;
* TTA;
* ordinary PC;
* disjoint phase-grid;
* adjacent-anchor difficulty;
* Anchor-CV;
* any new frozen mechanism-derived score.

Report:

* absolute benefit;
* oracle-normalized benefit;
* clustered CI;
* full budget curve.

Do not claim deployment policy without prospective acquisition.

Position the result as:

**retrospective resource-allocation validity**.

---

# 26. CVPR PRIORITY G

## Why does Anchor-CV work?

Anchor-CV currently performs extremely well.

Do not let it remain a black-box empirical trick.

Test hypotheses such as:

### H1

Anchor-CV measures intrinsic through-plane nonlinearity.

### H2

Anchor-CV estimates examination-specific interpolation difficulty.

### H3

Anchor-CV captures consensus-error magnitude invisible to output disagreement.

### H4

Anchor-CV mainly captures raw intensity scale.

### H5

Anchor-CV is a proxy for slice spacing or anchor RMSE.

Design experiments to distinguish these explanations.

Use:

* normalized endpoints;
* factor controls;
* mixed-effects models;
* partial correlations;
* variance decomposition;
* curvature measures;
* anchor RMSE;
* spacing;
* spectral content.

Reject explanations unsupported by data.

---

# 27. CVPR PRIORITY H

## Anchor-CV versus trivial input baselines

Because Anchor-CV uses acquired slices only, reviewers will ask whether it is simply a complicated version of adjacent-anchor difference.

Compare against strong simple baselines:

* adjacent-anchor MAE/RMSE;
* adjacent-anchor SSIM;
* gradient difference;
* low-frequency difference;
* curvature proxy;
* spacing;
* simple combinations frozen on development data.

Anchor-CV must earn its complexity.

Show where leave-one-anchor reconstruction provides information unavailable to direct anchor difference.

---

# 28. CVPR PRIORITY I

## Architecture-independent difficulty

Use all available models to test whether examination difficulty is a stable latent variable.

Perform variance decomposition / hierarchical modeling:

`error ~ examination + factor + architecture + interactions`

Then include:

* Anchor-CV;
* spacing;
* anchor difference;
* curvature;
* shared influence.

Ask:

> How much of the dominant case effect can observable acquired-data quantities explain?

This connects Plan-3 intrinsic difficulty to the final method.

---

# 29. CVPR PRIORITY J

## Failure analysis

Anchor-CV is examination-level triage and fails at local localization.

Study this explicitly.

Identify:

* high Anchor-CV / low error;
* low Anchor-CV / high error;
* cases where PC succeeds but Anchor-CV fails;
* cases where Anchor-CV succeeds but PC fails.

Ask whether these correspond to:

* local versus global difficulty;
* stable bias;
* boundary effects;
* factor-specific phenomena.

This may justify why input-derived and output-derived reliability signals are complementary even if naive fusion failed.

Do not create a fusion method without mechanism.

---

# 30. CVPR PRIORITY K

## Computational analysis

Measure:

* Anchor-CV CPU/GPU cost;
* reconstruction calls;
* memory;
* latency;
* comparison against PC/TTA/committee/disjoint phase-grid.

Quantify why Anchor-CV is deployable.

Do not merely say:

“no extra acquisition.”

Report actual computational requirements.

---

# 31. CVPR THEORY

Upgrade the theory to distinguish:

### Measurement overlap

binary/count notion.

### Shared influence

weighted estimator dependence on common measurements.

### Error alignment

similarity of resulting target-error directions.

### Observable disagreement

residual after shared components cancel.

Potential chain:

`shared influence`

→

`aligned reconstruction error`

→

`small residual disagreement`

→

`consensus blindness`.

Formalize exact statements for linear estimators.

For nonlinear neural estimators, clearly label local-linearization or sensitivity approximations.

Do not present a local Jacobian statement as a global theorem.

---

# 32. CVPR FIGURE PLAN

The full 8-page paper should contain approximately 5–7 scientifically dense figures/tables, not oversized decoration.

Potential main figures:

### Fig. 1

Consensus blindness concept and shared-influence mechanism.

### Fig. 2

Controlled overlap/shared-influence ladder.

### Fig. 3

Shared influence versus error alignment across three cohorts.

### Fig. 4

Neural influence approximation validation.

### Fig. 5

Anchor-CV method.

### Fig. 6

Three-cohort Anchor-CV reliability results.

### Fig. 7

Budget–benefit curves + failure cases.

Tables should cover:

* core quantitative comparison;
* ablations;
* efficiency.

Combine panels intelligently.

---

# 33. CVPR 8-PAGE TARGET STRUCTURE

Aim approximately:

Page 1:
Introduction + central concept + contributions

Page 2:
Related work + formal mechanism

Page 3:
Controlled shared-influence design

Page 4:
Mechanism experiments

Page 5:
Anchor-CV method

Page 6:
Main three-cohort results

Page 7:
Budget experiments + ablations

Page 8:
Failure analysis + limitations + conclusion

This is only a planning heuristic.

Do NOT force page breaks mechanically.

References should follow after the main eight-page allowance.

---

# 34. CVPR PAGE-GROWTH LEDGER

Create:

`CVPR/CVPR_UPGRADE/PAPER/PAGE_GROWTH_LEDGER.md`

For each page of main-paper content beyond the current manuscript record:

* new experiment;
* new theoretical result;
* new figure/table;
* reviewer objection resolved.

No page may exist merely because additional prose was written.

---

# 35. MANUSCRIPT WRITING COMES AFTER RESEARCH

For BOTH tracks, use this sequence:

### Stage 1

Gap audit.

### Stage 2

Hypothesis portfolio.

### Stage 3

Minimal discriminative experiments.

### Stage 4

Full confirmation.

### Stage 5

Statistical audit.

### Stage 6

Novelty audit.

### Stage 7

Reviewer red team.

### Stage 8

Figure/table generation.

### Stage 9

Rewrite manuscript.

Do not start by expanding the LaTeX paragraphs.

---

# 36. EXPERIMENT DECISION STANDARD

Every proposed new experiment must answer:

1. Which exact claim does this test?
2. What competing explanation does it distinguish?
3. What result would falsify our hypothesis?
4. What reviewer objection does it answer?
5. If positive, how would the paper change?
6. If negative, what would we learn?

If these cannot be answered:

do not run the experiment.

---

# 37. DO NOT HIDE NEGATIVE RESULTS

Negative results that materially delimit the method belong in the research record.

Examples already known include:

* low disagreement cannot certify correctness;
* overlap count is not a strict monotonic law;
* Anchor-CV does not provide useful local localization;
* NingXia low-budget evidence is weaker;
* naive fusion fails;
* curvature is not universal.

Use these to sharpen the contribution.

Do not remove them merely to produce a cleaner story.

---

# 38. LITERATURE UPGRADE

Before final rewrite, perform a new literature audit.

Search particularly for prior work on:

* MRI interpolation uncertainty;
* slice interpolation quality prediction;
* acquired-slice cross-validation;
* interpolation cross-validation;
* leave-one-slice-out reconstruction;
* self-supervised reconstruction error prediction;
* measurement influence;
* leverage/influence in inverse problems;
* shared error / correlated ensemble error;
* uncertainty under dependent ensembles;
* perturbation dependence;
* interpolation error estimation;
* MRI acquisition triage.

Update:

`NOVELTY_AUDIT.md`.

If Anchor-CV or shared-influence ideas have close prior work, immediately reassess novelty.

---

# 39. REVIEWER RED TEAM

Before final page expansion, simulate at least:

## TMI Reviewer 1

“Is this clinically/imaging relevant?”

## TMI Reviewer 2

“Is this only a mathematical curiosity?”

## TMI Reviewer 3

“Are the patient-level statistics correct?”

## TMI Reviewer 4

“Does the result survive different error metrics and imaging conditions?”

## TMI Reviewer 5

“Why should measurement-disjoint reconstruction be feasible?”

---

## CVPR Reviewer 1

“Overlap dependence is obvious.”

## CVPR Reviewer 2

“Your coefficient analysis only applies to linear estimators.”

## CVPR Reviewer 3

“Anchor-CV is just adjacent-slice difference.”

## CVPR Reviewer 4

“Where is the causal mechanism?”

## CVPR Reviewer 5

“Where is the actual method contribution?”

## CVPR Reviewer 6

“Why is this more than a niche MRI observation?”

## CVPR Reviewer 7

“Why should I trust 8-patient NingXia?”

Every substantive attack should produce either:

* an experiment;
* a theoretical clarification;
* a limitation;
* or a rejected claim.

---

# 40. REQUIRED FINAL OUTPUTS

## TMI

Produce:

`TMI/TMI_MANUSCRIPT_MASTER/main.tex`

`TMI/TMI_MANUSCRIPT_MASTER/main_20page.pdf`

Target:

**18–20 dense pages including references.**

Also produce:

`TMI/TMI_MANUSCRIPT_MASTER/PAGE_GROWTH_LEDGER.md`

`TMI/TMI_MANUSCRIPT_MASTER/NEW_EXPERIMENTS.md`

`TMI/TMI_MANUSCRIPT_MASTER/CLAIM_TRACEABILITY.md`

Then independently produce the current-policy-compliant:

`TMI/TMI_MANUSCRIPT_SUBMISSION/main.tex`

`TMI/TMI_MANUSCRIPT_SUBMISSION/main.pdf`

Target:

**official TMI initial-submission page limit.**

---

## CVPR

Produce:

`CVPR/CVPR_UPGRADE/PAPER/main.tex`

`CVPR/CVPR_UPGRADE/PAPER/main.pdf`

with:

**approximately the full 8 pages of actual main-paper content before references.**

Also produce:

`CVPR/CVPR_UPGRADE/PAPER/PAGE_GROWTH_LEDGER.md`

`CVPR/CVPR_UPGRADE/PAPER/NEW_EXPERIMENTS.md`

`CVPR/CVPR_UPGRADE/PAPER/CLAIM_TRACEABILITY.md`

and a complete supplementary manuscript as permitted by the official target-year policy.

---

# 41. FINAL QUALITY GATE

Do not declare completion merely because:

TMI reaches 20 pages

or

CVPR reaches 8 pages.

Page count is NOT the scientific stopping condition.

Completion requires that the added pages are supported by meaningful additions in at least the following categories:

### TMI

* deeper theory;
* complete consensus-error characterization;
* factor/model generalization;
* metric robustness;
* statistical robustness;
* geometry/intensity controls;
* risk-coverage;
* retrospective densification;
* failure analysis;
* deployment/efficiency interpretation.

### CVPR

* neural shared-influence evidence;
* stronger causal mechanism chain;
* cleaner controlled shared-influence experiment;
* frozen Anchor-CV validation;
* strong trivial-baseline controls;
* budget consequence;
* intrinsic-difficulty explanation;
* failure analysis;
* efficiency;
* updated novelty audit.

If meaningful evidence remains missing:

continue the research loop.

---

# 42. FINAL INSTRUCTION

The current six-page manuscripts are not templates to be padded.

Treat them as compressed summaries of an unfinished scientific program.

Expand the science first.

Then let the manuscripts grow naturally.

For every additional page ask:

> What new fact does the reader learn here?

For every additional experiment ask:

> What uncertainty about the central claim does this remove?

For every method component ask:

> Which demonstrated failure mechanism requires it?

For every theoretical statement ask:

> What experiment does this theory explain or predict?

The desired outputs are:

**a ~20-page complete TMI research master from which a compliant TMI submission can be distilled,**

and

**a genuinely full 8-page CVPR main paper whose additional space is earned by stronger mechanism, method, experiments, and validation.**

Do not pad.

Do not stop at manuscript editing.

Continue conducting MRI interpolation research until the scientific content itself justifies the target lengths.
