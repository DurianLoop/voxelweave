# Research Innovation Goal — Continue Until a Strong Publishable Contribution Emerges

Continue the research program from Plan-3.

The previous `PROJECT_EXHAUSTION_AUDIT.md` does **not** imply that the research objective has been achieved.

It only establishes that the obvious analyses of the currently stored artifacts have been substantially explored.

The overall research goal is different:

> **Iteratively generate scientific hypotheses, design discriminative experiments, create new experimental conditions and methods when justified, falsify competing explanations, and continue until the project contains at least one genuinely novel, experimentally strong, conceptually clear contribution that could plausibly serve as the central contribution of a high-level computer-vision paper.**

Do not optimize for endless experimentation.

Do not optimize for exhausting every possible analysis.

Optimize for discovering a **strong scientific contribution**.

---

# 1. Current scientific starting point

Plan-3 has produced a more important observation than the original Physical Consistency method.

The current evidence suggests that deterministic MRI slice interpolation error has a strong shared structure:

* examination identity explains a large fraction of reconstruction-error variance;
* sampling factor explains another substantial fraction;
* architecture explains comparatively little;
* x2 < x4 < x6 error holds for all observed case–architecture combinations;
* reconstruction-error ranking is highly correlated across neural architectures;
* most reconstruction error is shared consensus error rather than context-specific diversity;
* cross-context disagreement observes only a minority component of the total error;
* shared anchors can suppress observable disagreement even when reconstruction error is large;
* simple perturbation diversity is not sufficient for a useful reliability intervention.

This should now be treated as the starting point for **new theory and method discovery**, not as the endpoint of the project.

---

# 2. New central research question

The current strongest open question is:

> If most deterministic reconstruction error is shared across architectures and sampling contexts, can we identify, characterize, predict, or reduce this dominant consensus-error component without access to the missing target?

This question is potentially more important than Physical Consistency itself.

Investigate it aggressively.

Do not assume the answer must involve uncertainty estimation.

The final contribution may instead concern:

* intrinsic reconstruction difficulty;
* consensus bias;
* sampling-induced information loss;
* failure predictability;
* reconstruction limits;
* context design;
* adaptive acquisition;
* difficulty-aware interpolation;
* new reconstruction objectives;
* new reliability signals;
* or another mechanism implied by the evidence.

Let the evidence determine the direction.

---

# 3. Research loop

From now on repeatedly execute:

Observation

→ Scientific question

→ At least 2 competing explanations

→ Falsifiable hypotheses

→ Minimal discriminative experiment

→ Result

→ Reject / refine / support

→ Mechanistic interpretation

→ New method or new hypothesis if justified

→ Strong baseline comparison

→ Ablation

→ Generalization

→ Reviewer red-team

→ Next scientific question.

Do not stop after confirming a descriptive phenomenon.

A descriptive result should trigger:

> Can this phenomenon be explained?

An explanation should trigger:

> Can this mechanism predict something new?

A predictive mechanism should trigger:

> Can we derive a useful method from it?

A new method should trigger:

> Does it outperform strong alternatives for the reason predicted by the mechanism?

Continue this ladder.

---

# 4. Distinguish observation, mechanism, and innovation

Maintain three separate layers.

## Layer A — Observation

Examples:

* error is highly correlated across architectures;
* factor severity dominates architecture identity;
* consensus error dominates disagreement-visible error.

These observations alone are not yet sufficient as the main innovation.

## Layer B — Mechanism

Ask why these observations occur.

Candidate mechanisms may include:

* intrinsic information loss caused by slice spacing;
* examination-specific through-plane anatomical complexity;
* shared inductive bias across reconstructors;
* insufficient acquisition context;
* deterministic regression toward conditional expectation;
* low-frequency structural ambiguity;
* anchor geometry;
* correlated training objectives;
* shared interpolation priors.

Mechanisms must be tested against alternatives.

## Layer C — Innovation

A strong paper should ideally derive something new from the mechanism:

* a new estimator;
* a new reconstruction strategy;
* a new acquisition/context-selection strategy;
* a new loss;
* a new training paradigm;
* a new benchmark/evaluation formulation;
* a new theoretical characterization;
* or a new failure-detection principle.

Do not confuse a descriptive observation with a complete innovation.

---

# 5. Prioritize consensus error

The Plan-3 decomposition suggests that approximately 80–87% of error may be shared across reconstruction contexts.

This is now a high-priority target.

Create:

`CONSENSUS_ERROR_RESEARCH.md`

Investigate the decomposition:

`total reconstruction error`

≈

`shared / consensus component`

*

`context-sensitive component`

*

`architecture-specific component`

where statistically and mathematically appropriate.

Questions to test:

1. Is the consensus component stable across datasets?
2. Is it stable across factors?
3. Is it primarily examination-specific?
4. Is it predictable from acquired slices?
5. Is it related to anatomical through-plane curvature?
6. Is it related to missing-frequency content?
7. Does it reflect irreducible ambiguity or model bias?
8. Can its magnitude be estimated without the target?
9. Can training reduce it?
10. Can context selection reduce it?

The goal is not merely to quantify consensus error.

Try to **make it observable or reducible**.

---

# 6. Search for intrinsic reconstruction difficulty

The strong case variance and cross-model error correlation suggest a latent variable:

> intrinsic interpolation difficulty of an examination or physical plane.

Formally investigate whether a latent difficulty variable explains errors across:

* architecture;
* factor;
* slice;
* dataset;
* reconstruction method.

Possible approaches include:

* mixed-effects models;
* latent factor models;
* rank aggregation;
* variance decomposition;
* hierarchical models.

If a stable latent difficulty exists, identify observable predictors from acquired data.

Possible input-side predictors:

* adjacent-slice RMSE;
* SSIM between acquired anchors;
* through-plane gradient;
* curvature;
* low-frequency change;
* high-frequency change;
* anatomical deformation;
* local entropy;
* edge density;
* spectral change;
* contextual asymmetry;
* physical slice distance.

Do not simply fit a black-box predictor first.

Understand what determines difficulty.

---

# 7. Turn difficulty prediction into a scientific hypothesis

A potentially strong hypothesis is:

> Reconstruction failure is dominated by intrinsic target difficulty determined by the relationship between observed neighboring slices, rather than by architecture choice.

Test this explicitly.

Predictions may include:

* cases hard for one architecture should be hard for others;
* input-derived difficulty should predict errors across architectures;
* architecture switching should provide limited benefit on intrinsically difficult planes;
* reducing effective sampling distance should disproportionately benefit high-difficulty cases;
* difficulty should interact systematically with sampling factor.

Design experiments that could falsify this.

If supported, investigate whether this becomes a stronger central result than PC.

---

# 8. Explore whether interpolation has an empirical difficulty law

The universal observation:

`x2 < x4 < x6 error`

across all 138 case–architecture units is unusually strong.

Do not leave it as a table result.

Investigate whether reconstruction error can be modeled as a function of physical sampling distance.

Test candidate relationships between:

* slice distance;
* factor;
* anatomical change;
* target curvature;
* reconstruction error.

Examples:

`error ~ distance`

`error ~ distance²`

`error ~ curvature × distance`

or another physically motivated relationship.

Do not force a formula.

Compare competing models.

Ask whether a simple scaling relation exists across architectures.

A reproducible interpolation difficulty law could be a significant scientific contribution.

---

# 9. Investigate target curvature deeply

Plan-3 reports:

`rho = 0.936`

between retrospective target curvature and x4–x6 error.

This is potentially extremely important.

Do not treat it merely as an explanation of one boundary failure.

Investigate whether through-plane target curvature is a fundamental determinant of interpolation difficulty.

Define curvature carefully.

Test:

* pixel-level curvature;
* plane-level curvature;
* low-frequency curvature;
* structural curvature;
* gradient-domain curvature;
* curvature estimated only from acquired neighbors;
* true retrospective curvature.

Ask:

1. Does target curvature predict reconstruction error across factors?
2. Does it explain case variance?
3. Does it explain x2/x4/x6 scaling?
4. Does it generalize across datasets?
5. Can curvature be estimated from acquired slices only?
6. Can curvature define a lower bound on interpolation difficulty?
7. Do all architectures fail similarly when curvature is high?

If acquired-data curvature can predict difficulty, this may yield a training-free pre-reconstruction reliability measure.

---

# 10. Derive new experiments from interpolation theory

MRI slice interpolation can be viewed as estimating an unknown intermediate function along the through-plane axis.

Explore connections to classical interpolation theory.

Investigate whether error relates to:

* second derivative / curvature;
* sampling interval;
* smoothness assumptions;
* interpolation error bounds.

For classical interpolation, error often depends on derivatives and sampling spacing.

Determine whether an analogous principle can explain the empirical findings.

Do NOT falsely apply classical bounds to neural networks.

Instead ask whether classical interpolation theory motivates testable hypotheses for deterministic neural interpolators.

For example:

> if anatomical through-plane curvature increases while sampling spacing increases, interpolation error should rise systematically regardless of architecture.

Test such predictions.

This could provide a powerful bridge between empirical deep-learning behavior and sampling theory.

---

# 11. Search literature around interpolation error theory

Expand literature beyond uncertainty.

Search:

* interpolation approximation theory;
* sampling theorem;
* image interpolation error;
* neural interpolation;
* video frame interpolation uncertainty;
* temporal frame interpolation;
* super-resolution error prediction;
* inverse-problem ambiguity;
* conditional mean regression;
* regression-to-the-mean;
* deterministic reconstruction bias;
* MRI slice interpolation;
* anisotropic medical image super-resolution.

Determine whether the observed curvature/sampling relationship has already been characterized.

Search adjacent domains such as video frame interpolation, where temporal distance and motion curvature may provide analogous phenomena.

A cross-domain theoretical connection may strengthen novelty substantially.

---

# 12. Investigate consensus bias theoretically

Suppose several deterministic models approximate a similar conditional expectation:

`f_m(x) ≈ E[y|x]`.

Then different architectures may agree while all differ from a particular ground truth target due to conditional ambiguity.

Investigate whether the observed shared error is consistent with this mechanism.

Potential predictions:

* architecture diversity will not eliminate shared errors;
* uncertainty from architecture ensembles will underestimate ambiguity when all models approximate the same conditional central tendency;
* difficult cases will exhibit high target ambiguity but high model agreement;
* errors may exhibit systematic smoothing or attenuation.

Test these where possible.

Do not claim conditional-expectation behavior without evidence.

---

# 13. Search for an observable proxy for consensus bias

This is a major innovation opportunity.

Physical Consistency mainly observes context-sensitive error.

Find signals that might observe shared error.

Potential sources:

### Input-side

* anchor discrepancy;
* estimated curvature;
* contextual nonlinearity;
* physical distance;
* spectral mismatch.

### Reconstruction-side

* local smoothness deficit;
* frequency attenuation;
* structural collapse;
* cross-scale inconsistency;
* inverse-consistency;
* cycle consistency;
* re-interpolation consistency.

### Acquisition-side

* alternative anchor subsets;
* asymmetric context;
* different context windows;
* leave-one-anchor-out reconstruction;
* virtual resampling.

Do not randomly combine them.

For every candidate signal state:

> Which invisible failure mode should this expose?

Then test it.

---

# 14. Invent new target-preserving interventions

Plan-3 showed that flips are weaker because they do not expose the relevant error directions.

Search systematically for interventions that preserve the physical target while perturbing information context.

Examples, if supported by available code/data:

* different anchor subsets;
* asymmetric anchor context;
* remove one neighbor;
* farther versus nearer anchors;
* different context widths;
* synthetic resampling of acquired slices;
* leave-one-context-out;
* context masking;
* factor-conditioned reconstruction;
* reversed context ordering;
* alternative valid sampling lattices.

For each intervention test:

1. target identity preserved?
2. does it change reconstruction errors?
3. does it expose errors not already shared?
4. is disagreement correlated with true error?
5. what failure modes remain invisible?

The goal is to discover an intervention that exposes the dominant consensus component better than current PC.

---

# 15. Search for a two-component reliability estimator

The current evidence suggests a natural decomposition:

`Reliability signal`

=

`input-derived intrinsic difficulty`

*

`output-derived context sensitivity`.

Instead of naive fusion, derive a principled combination.

Naive fusion already failed.

Do not retry arbitrary weighted averages.

First formulate a mechanism.

For example:

* input proxy may estimate shared consensus risk;
* PC may estimate context-sensitive risk.

If evidence supports this interpretation, design a model or rule that separately estimates these components before combining them.

Possible approaches:

* orthogonal decomposition;
* conditional modeling;
* residual prediction;
* monotonic model;
* calibration learned only on development data;
* analytically motivated combination.

Any learned combination must use proper held-out evaluation.

---

# 16. Consider modifying the reconstruction model

Until now, much of the project has analyzed stored outputs.

You are now authorized to create and train new methods when a clear mechanistic hypothesis justifies doing so.

Examples:

If high curvature causes shared failure:

* design curvature-aware context weighting;
* adaptive receptive field;
* curvature-conditioned interpolation;
* uncertainty-aware loss;
* factor-aware training.

If shared anchors cause hidden failure:

* train with randomized context subsets;
* context dropout;
* anchor diversification;
* consistency across non-overlapping contexts.

If shared architecture bias dominates:

* introduce objectives that explicitly diversify error directions or preserve high-curvature structures.

Do not invent architecture changes without a demonstrated failure mechanism.

---

# 17. Mechanism → method rule

Every proposed new method must satisfy:

### Demonstrated problem

A failure mechanism has been experimentally observed.

### Mechanistic hypothesis

There is a reason the method should address it.

### Prediction

State what should change if the hypothesis is correct.

### Minimal test

Run the smallest experiment capable of falsifying the hypothesis.

### Full test

Only if the minimal test succeeds.

Write every method proposal using:

`Failure`

→ `Mechanism`

→ `Intervention`

→ `Prediction`

→ `Experiment`

→ `Result`.

---

# 18. Do not demand SOTA immediately

A new mechanism may first be validated on a small subset.

Use an experimental ladder:

toy / synthetic

→ small cohort

→ one architecture

→ multiple architectures

→ full dataset

→ independent dataset

→ strong baselines.

Do not waste compute on full training before a mechanistic signal exists.

---

# 19. Search for predictive discoveries

A strong scientific theory should make predictions that were not used to construct it.

For every promising mechanism generate at least one new prediction.

Examples:

If curvature drives difficulty:

> high-curvature regions should degrade more rapidly as factor increases.

If shared-context bias dominates:

> using non-overlapping anchors should increase disagreement specifically in stable-wrong cases.

If architecture matters little:

> changing architecture should have less effect than reducing slice distance for difficult examinations.

Test new predictions.

A successful out-of-sample prediction substantially strengthens the contribution.

---

# 20. Strong-claim rubric

Do not stop merely because a phenomenon is statistically significant.

A candidate main contribution should be evaluated on:

## Novelty

Is the mechanism or method meaningfully distinct from existing work?

## Importance

Does it reveal something consequential about deterministic reconstruction?

## Generality

Does it hold across more than one model / factor / dataset where possible?

## Mechanistic depth

Do we understand why it occurs?

## Predictive power

Does the hypothesis correctly predict new observations?

## Methodological consequence

Can the insight improve reliability, reconstruction, acquisition, or evaluation?

## Experimental rigor

Are baselines, statistics, and ablations convincing?

## Reviewer resilience

Can obvious alternative explanations be rejected?

Score each candidate claim from 1–5 on each dimension.

Maintain:

`INNOVATION_SCORECARD.md`

---

# 21. Publication threshold

The research goal should only be considered successful when a candidate contribution reaches approximately:

* Novelty: >= 4/5
* Importance: >= 4/5
* Mechanistic depth: >= 4/5
* Experimental rigor: >= 4/5
* Reviewer resilience: >= 4/5

and there is no obvious fatal novelty collision.

This score is a research management heuristic, not proof of acceptance.

Never inflate scores merely to terminate.

Justify every score with evidence.

---

# 22. Simulate a top-conference reviewer

For every candidate main claim, ask:

### Reviewer 1 — Novelty

“So what? Isn't this obvious from interpolation theory or existing uncertainty work?”

### Reviewer 2 — Method

“What new method or scientific capability does this enable?”

### Reviewer 3 — Evidence

“Is this just correlation on a few datasets?”

### Reviewer 4 — Generality

“Why should anyone outside this exact MRI setup care?”

### Reviewer 5 — Simplicity

“Could a trivial baseline explain the same phenomenon?”

### Reviewer 6 — Statistics

“Are repeated measurements being treated correctly?”

### Reviewer 7 — Mechanism

“Do the experiments actually distinguish your explanation from alternatives?”

Record responses and design experiments to answer them.

---

# 23. Allow the central claim to change

Do not stay attached to:

* Physical Consistency;
* uncertainty estimation;
* disagreement;
* selective prediction.

If evidence supports a stronger story such as:

* intrinsic interpolation difficulty;
* sampling-curvature law;
* consensus bias;
* reconstruction error decomposition;
* context design;
* architecture-invariant failure;

pivot the central research question.

The objective is the strongest truthful discovery.

---

# 24. Keep multiple hypotheses alive

Maintain:

`HYPOTHESIS_PORTFOLIO.md`

At any time, keep approximately 3–7 serious candidate hypotheses.

For each:

* hypothesis;
* evidence;
* falsification condition;
* novelty;
* potential contribution;
* next experiment;
* cost;
* status.

Do not tunnel into one idea too early.

However, once one hypothesis becomes substantially stronger, allocate more compute to it.

---

# 25. Literature should influence experiments

Continue reading papers throughout the research cycle.

For every close paper ask:

* What mechanism does it propose?
* What experiment could distinguish its explanation from ours?
* Does it provide a baseline?
* Does it suggest a new intervention?
* Does it reveal a novelty collision?
* Does another field contain an analogous theory?

Do not produce literature summaries for their own sake.

Use papers to generate experiments.

---

# 26. Current immediate research priorities

Start from the Plan-3 findings.

High-priority directions include:

### A. Intrinsic difficulty

Determine whether examination/plane difficulty is a stable architecture-independent latent variable.

### B. Curvature mechanism

Test whether through-plane curvature plus sampling distance explains reconstruction failure.

### C. Sampling law

Determine whether a quantitative relationship exists between physical sampling spacing and error.

### D. Consensus bias

Explain why architectures fail similarly.

### E. Consensus-error observability

Design an input-side or alternative-context signal capable of detecting errors invisible to PC.

### F. Context intervention design

Test alternative target-preserving contexts that do not share anchors.

### G. Two-component reliability

Develop a principled estimator for shared difficulty plus context-sensitive instability.

### H. Mechanism-derived reconstruction

If a mechanism is established, design a reconstruction method that directly addresses it.

Do not execute these mechanically in order.

Use evidence to prioritize.

---

# 27. A particularly important experiment

Plan-3 indicates that shared anchors may suppress disagreement.

Design a controlled experiment comparing context pairs with different levels of anchor overlap while preserving the same target plane.

Hypothesis:

> The ability of cross-context disagreement to reveal reconstruction error decreases as the contexts share more information responsible for the same failure.

Test:

* zero shared anchors where feasible;
* one shared anchor;
* maximal shared context.

Measure:

* context disagreement;
* target error;
* error correlation;
* stable-wrong prevalence;
* uncertainty ranking.

If supported, this could lead to a general principle:

> Reliability interventions should maximize **error-direction independence**, not raw prediction diversity.

This is potentially stronger than the current PC formulation.

Investigate rigorously.

---

# 28. Another high-priority hypothesis

Test:

> Architecture contributes little because reconstruction difficulty is dominated by examination-specific signal curvature and sampling geometry.

Fit hierarchical models comparing:

`error ~ case + factor + architecture`

against models incorporating:

* estimated curvature;
* physical spacing;
* anchor difference;
* spectral properties.

Ask whether interpretable physical/input variables explain the large case variance.

If they do, this could transform a descriptive variance result into a mechanistic model.

---

# 29. Aim for a paper-shaped contribution

An ideal final scientific contribution should look more like:

### Discovery

Deterministic MRI interpolation errors are overwhelmingly shared across architectures and governed by examination-specific sampling difficulty.

### Mechanism

The dominant difficulty arises from target variation/curvature relative to available through-plane sampling context.

### Consequence

Standard ensemble/context disagreement observes only the non-shared residual and therefore systematically misses consensus failures.

### New principle

A useful reliability intervention must preserve target identity while changing the information responsible for shared error.

### Method

A new difficulty estimator / intervention / reconstruction strategy derived from this mechanism.

### Evidence

Cross-dataset, cross-model, factor-controlled experiments, ablation, theory, failure analysis, and strong baselines.

Do not force this narrative.

But use it as an example of the level of completeness desired.

---

# 30. Intermediate reports are milestones, not terminal states

You may generate:

`PLAN_4_REPORT.md`

`PLAN_5_REPORT.md`

etc.

Each report should contain:

* discoveries;
* falsified hypotheses;
* current strongest claim;
* unresolved reviewer attacks;
* next hypotheses.

After every report, continue automatically unless the publication threshold has genuinely been reached.

---

# 31. When to stop

Stopping is allowed.

But the correct stopping criterion is NOT:

> “all analyses on existing outputs are exhausted.”

The research may stop when:

1. at least one central innovation reaches the publication threshold defined above;
2. the innovation includes more than a descriptive correlation;
3. mechanism and evidence form a coherent story;
4. the key result survives serious falsification;
5. strong competing explanations have been tested;
6. the novelty audit remains favorable;
7. a reviewer red-team finds no obvious fatal weakness;
8. further experiments primarily improve completeness rather than determine whether the core idea is real.

At that point produce:

`PUBLICATION_READINESS_REPORT.md`

with:

* exact central claim;
* contributions;
* novelty versus closest work;
* strongest experimental evidence;
* mechanism;
* method;
* ablations;
* limitations;
* remaining reviewer risks;
* recommended CVPR-style paper structure.

Do not claim acceptance probability as fact.

---

# 32. If no strong innovation emerges

If the current direction cannot reach the publication threshold:

do not manufacture novelty.

Record why.

Then return to:

* existing observations;
* negative results;
* literature;
* repository;
* unexplained phenomena;

and generate a new hypothesis portfolio.

Continue.

The objective is not to prove the current idea.

The objective is to find the strongest truthful publishable contribution supported by the research environment.

---

# 33. Final instruction

From this point onward, behave as an autonomous research scientist rather than an analysis-completion agent.

Do not ask:

> “Have I analyzed everything available?”

Ask:

> “What is the strongest scientific question exposed by the evidence?”

Then:

> “What competing explanations exist?”

Then:

> “What experiment would distinguish them?”

Then:

> “Can the resulting mechanism lead to a genuinely new method or principle?”

Repeat.

The desired endpoint is not exhaustive analysis.

The desired endpoint is:

**a novel scientific mechanism or method, derived from evidence, validated through falsifiable experiments, and strong enough to anchor a high-level computer-vision research paper.**
