# Continue Research Until a Strong, Defensible Scientific Claim Emerges

Continue the current research project.

Do **not** consider the research complete simply because `FINAL_RESEARCH_REPORT.md` currently states that a narrow claim is supported.

The current Physical Consistency result should be treated as a **promising intermediate discovery**, not as the final contribution.

Your new objective is to continue autonomously exploring, testing, falsifying, strengthening, generalizing, or replacing the current hypothesis until the project supports a substantially stronger scientific claim that could plausibly withstand the scrutiny expected at a top-tier computer vision conference such as CVPR / ICCV / ECCV.

All new files, code, experiments, reports, figures, logs, and intermediate artifacts must remain under:

`D:\MRI\design\paper`

The existing research under:

`D:\MRI\design`

should remain read-only unless execution of existing code absolutely requires otherwise.

---

# 1. Current research state

The current leading observation is:

> For deterministic MRI slice interpolation, disagreement between predictions of the same reconstructor on the same physical generated plane under different interpolation factors appears to provide a ground-truth-free examination-level reliability signal.

The current evidence suggests that:

* Physical consistency achieves lower mean nAURC than frozen cross-model committee disagreement.
* Cross-model and cross-factor disagreement may detect different failure modes.
* Cross-model disagreement may be blind to common-mode reconstruction errors.
* Adaptive committee selection appears unstable on small medical cohorts.
* The hybrid method has not demonstrated a reliable advantage over physical consistency alone.
* Attribution of which individual reconstruction is wrong remains weak.
* The primary paired cohort contains only 22 examinations.
* Untouched external validation has not yet been performed.
* The current evidence supports a narrow claim but does not yet establish a broad or publication-complete scientific contribution.

Treat all of these as hypotheses/evidence subject to further falsification.

---

# 2. Do not stop at the current result

The current research phase is now:

**CONFIRMATION + FALSIFICATION + MECHANISM DISCOVERY + GENERALIZATION**

Do not spend most of the remaining research budget making small variations of the current score.

Do not optimize the method against the existing NingXia results.

Do not tune parameters merely to obtain better numbers.

Instead, attempt to answer:

> Why does Physical Consistency work?

> Under what conditions does it work?

> Under what conditions must it fail?

> Is the useful signal truly caused by sampling-context instability?

> Is it fundamentally different from generic perturbation-based uncertainty?

> Does it detect failures that model disagreement cannot detect?

> Does the phenomenon replicate across datasets, models, factors, and acquisition conditions?

> Can the observation be generalized into a broader principle about reliability estimation for deterministic reconstruction systems?

The objective is not to protect the current hypothesis.

The objective is to try to destroy it.

If it survives serious falsification attempts, strengthen it.

If it fails, understand why and pivot.

---

# 3. Freeze the current method for confirmatory experiments

Before conducting new exploratory optimization, create a frozen specification of the current Physical Consistency method.

Write:

`FROZEN_METHOD.md`

It must fully specify:

* geometry matching;
* anchor exclusion;
* physical-plane matching tolerance;
* intensity preprocessing;
* discrepancy function;
* factor pairs;
* aggregation;
* examination-level score;
* evaluation protocol;
* ranking orientation;
* all relevant implementation details.

Assign this method a fixed identifier such as:

`PC-v1-FROZEN`

For all confirmatory experiments:

**do not modify PC-v1-FROZEN after observing results.**

If a modification is later proposed, treat it as a new exploratory method with a new identifier.

Never silently modify the frozen method to rescue a failed validation.

---

# 4. First priority: determine whether the existing result is fragile

Immediately perform case-level influence analysis on the current NingXia cohort.

## 4.1 Leave-one-examination-out influence

For each of the 22 examinations:

1. Remove the examination.
2. Recompute the aggregate comparison between Physical Consistency and the frozen committee baseline.
3. Record delta nAURC, Spearman, Kendall, and relevant risk-coverage quantities.
4. Identify whether the conclusion depends strongly on one or a small number of examinations.

Create:

`CASE_INFLUENCE_ANALYSIS.md`

and the corresponding figures.

Explicitly answer:

* How many leave-one-out subsets preserve the direction of the effect?
* What is the minimum and maximum delta?
* Are specific cases disproportionately responsible for the aggregate result?
* What properties characterize influential cases?

Do not hide influential cases.

Investigate them.

---

# 5. Re-evaluate statistical validity

Audit the current bootstrap implementation.

The examination must be the independent sampling unit.

If multiple profiles belong to the same examination, they must remain clustered during resampling.

Never treat repeated architecture/factor measurements from the same examination as independent samples.

Perform appropriate robustness checks such as:

* clustered case bootstrap;
* BCa bootstrap if justified;
* paired permutation testing;
* sign-based or rank-based paired tests where appropriate.

Do not perform many tests merely to obtain significance.

The purpose is to determine whether the conclusion is robust to reasonable statistical choices.

Record all results, including unfavorable ones.

---

# 6. Analyze heterogeneity instead of hiding it in averages

Produce per-profile analyses.

For every target architecture and interpolation setting, report the effect of Physical Consistency versus the frozen baseline.

Create a forest-style analysis of:

`delta nAURC`

and, where useful:

* delta Spearman;
* delta Kendall;
* delta AURC;
* RRR across multiple coverage levels.

Determine whether the aggregate result reflects:

A. a broadly consistent effect across settings,

or

B. a small number of settings producing large improvements.

These imply very different scientific claims.

Update the claim accordingly.

---

# 7. Analyze the full risk-coverage behavior

Do not rely on a single RRR50 number.

Plot and analyze:

`risk versus coverage`

for every major method.

Determine:

* where Physical Consistency improves over the baseline;
* where the curves cross;
* whether improvements are concentrated in high-, medium-, or low-coverage regimes;
* why nAURC improves while RRR50 may not.

Compute risk reduction over several prespecified coverage values rather than selecting only favorable ones.

Use this analysis to refine the scientific interpretation.

---

# 8. External / independent replication is now a top priority

Investigate whether the existing fastMRI-brain cross-factor outputs can support a truly independent confirmation experiment.

If ground truth or retrospective error labels can be validly constructed:

freeze `PC-v1-FROZEN`

and apply it **without modification**.

Do not use the new cohort to choose:

* factor pairs;
* normalization;
* aggregation;
* thresholds;
* masks;
* hyperparameters;
* score formulas.

Evaluate the frozen method exactly as specified.

If fastMRI is unsuitable, identify the strongest available independent cohort already present in the project.

Clearly distinguish:

* development cohort;
* internal OOF evaluation;
* external-site validation;
* cross-dataset validation;
* prospective validation.

Never call an internal OOF cohort external validation.

If no usable independent dataset exists, document the blocker and continue strengthening the claim through other experiments rather than pretending external validation exists.

---

# 9. Directly test the proposed mechanism: common-mode blindness

The current conceptual argument is that model disagreement can miss errors shared by all committee members.

Do not leave this as verbal intuition.

Design controlled experiments.

Construct situations where several reconstructors share increasingly severe common-mode degradation while remaining mutually similar.

Possible controlled perturbations include, where scientifically appropriate:

* shared Gaussian smoothing;
* controlled high-frequency attenuation;
* shared detail suppression;
* low-pass filtering;
* common contrast distortion;
* controlled localized information removal;
* other degradations relevant to interpolation behavior.

For each degradation severity:

measure:

* retrospective reconstruction error;
* cross-model disagreement;
* Physical Consistency;
* other relevant uncertainty scores.

Test the prediction:

> Reconstruction error can increase while cross-model disagreement remains artificially low because all models fail similarly.

Determine whether Physical Consistency detects any part of this failure regime.

If it does not, report that honestly and refine the mechanism claim.

Create a dedicated mechanistic experiment report.

---

# 10. Determine whether the signal is sampling-specific

A skeptical reviewer may argue:

> “This is simply test-time augmentation uncertainty or perturbation consistency.”

Directly test this.

Compare sampling-factor consistency against generic perturbation-based consistency measures.

Potential controls, when valid for MRI reconstruction outputs, include:

* small intensity scaling;
* intensity offset;
* Gaussian noise;
* mild spatial perturbations;
* generic image augmentations;
* context-window perturbations;
* other target-preserving transformations.

The purpose is not to create dozens of baselines.

The purpose is to distinguish:

**generic perturbation sensitivity**

from

**sampling-context sensitivity**.

If generic perturbation consistency performs similarly, the claim must become more general.

If sampling-factor consistency is substantially better, investigate why.

Try to establish whether physical sampling context provides a uniquely meaningful intervention.

---

# 11. Formalize the underlying principle

Develop a mathematical formulation of target-preserving consistency.

Let:

* `y_p` be the unknown true image at physical plane `p`;
* `f(x_s, p)` be the reconstruction at the same physical plane under sampling context `s`.

Study the relationship between:

`d(f(x_s1,p), f(x_s2,p))`

and the unknown reconstruction errors:

`d(f(x_s1,p), y_p)`

and

`d(f(x_s2,p), y_p)`.

Where the discrepancy metric satisfies appropriate properties, explore inequalities derived from the triangle inequality.

For example, investigate whether:

`d(f_s1, f_s2) <= d(f_s1, y) + d(f_s2, y)`

can provide a useful interpretation.

Be mathematically precise.

Do not claim that disagreement proves which reconstruction is wrong.

Instead distinguish possible statements such as:

* disagreement implies at least one prediction must be inaccurate beyond a certain tolerance;
* agreement does not imply correctness;
* consistency therefore provides one-sided evidence rather than calibrated uncertainty.

Determine whether this formalization meaningfully explains the empirical results.

Do not force a theorem if assumptions are unrealistic.

---

# 12. Study the consistent-but-wrong regime

The central method has an obvious limitation:

A model may produce nearly identical predictions across factors and still be wrong.

Actively search for such examples.

Identify examinations/planes with:

* low Physical Consistency;
* high retrospective error.

Characterize them.

Ask whether these cases correspond to:

* shared smoothing;
* hallucinated but stable structure;
* low-frequency bias;
* systematic anatomical omission;
* preprocessing effects;
* unusual pathology;
* scanner/site effects;
* other mechanisms.

These examples may define the theoretical boundary of the method.

Do not hide them.

Use them to sharpen the claim.

---

# 13. Audit geometry more rigorously

Confirm that matched predictions correspond to the same physical imaging plane.

Do not rely only on matching world-coordinate origins.

Where metadata permits, verify:

* plane origin;
* plane normal;
* orientation;
* in-plane spacing;
* field of view;
* image dimensions;
* affine consistency;
* coordinate-system assumptions.

Quantify the maximum geometric discrepancy.

Create a reproducible geometry audit.

If geometry mismatches exist, determine whether they influence the score.

---

# 14. Audit intensity-related confounders

Determine whether the score is measuring true reconstruction instability or merely arbitrary intensity-scale differences across interpolation factors.

Compare scientifically justified variants such as:

* raw intensity;
* robust normalization;
* percentile normalization;
* z-score normalization;
* foreground-normalized intensity;
* other justified normalization procedures.

Do not optimize based on test performance.

Use these comparisons primarily as confounder checks.

If Physical Consistency remains useful across reasonable intensity handling choices, that strengthens the interpretation.

If performance changes dramatically, investigate why.

---

# 15. Search for deeper explanatory variables

Use the existing outputs to identify what causes high Physical Consistency.

Analyze associations with factors such as:

* reconstruction error;
* image-frequency content;
* anatomical complexity;
* slice location;
* interpolation distance;
* amount of missing information;
* local gradients;
* tissue boundaries;
* pathology if available;
* scanner/site metadata if available;
* acquisition parameters;
* factor severity;
* model architecture.

The purpose is not merely correlation mining.

Try to discover a mechanism.

For each promising relationship, formulate a falsifiable hypothesis and design a controlled test.

---

# 16. Localize the phenomenon

The current score is examination-level.

Investigate whether the phenomenon can be meaningfully localized to:

* slice level;
* region level;
* spatial maps.

Do this carefully.

Do not claim uncertainty localization merely because a heatmap looks plausible.

If local inconsistency maps correlate with local reconstruction error, quantify it.

If localization fails while examination-level ranking succeeds, that itself is informative.

Determine the natural granularity of the reliability signal.

---

# 17. Investigate factor-pair structure

Study the relationships among:

* x2 vs x4;
* x2 vs x6;
* x4 vs x6;

without selecting the best pair post hoc as the main result.

Ask:

* Does disagreement increase monotonically with sampling-context distance?
* Are distant-factor comparisons more informative?
* Is there a saturation effect?
* Does each architecture behave similarly?
* Is the score driven mainly by one pair?

Try to derive a scientific explanation rather than simply selecting the strongest pair.

If a new factor-based formulation is proposed, label it exploratory and validate it independently.

---

# 18. Search for a broader generalization of the idea

Do not assume the final contribution must remain “x2/x4/x6 MRI interpolation disagreement.”

Ask whether the underlying concept is more general:

> Reliability of deterministic reconstruction may be estimated by invariance under target-preserving changes in measurement or sampling context.

Explore whether this can be expressed as a broader framework:

**Target-Preserving Context Consistency**

or a similarly precise concept.

Potential contexts may include, only when supported by existing data/code:

* different sampling factors;
* different observed neighboring slices;
* different context widths;
* different subsampling patterns;
* different acquisition conditions;
* different admissible reconstructions of the same target plane.

Do not broaden the paper rhetorically unless experiments support the broader claim.

---

# 19. Compare against stronger conceptual baselines

Audit the literature again.

Identify the strongest realistic comparison methods for the exact setting.

Prioritize methods representing distinct uncertainty paradigms, not dozens of weak baselines.

Potential categories include:

* deep ensemble disagreement;
* test-time augmentation uncertainty;
* MC dropout where applicable;
* heteroscedastic prediction;
* learned error predictors;
* conformal/selective prediction methods;
* no-reference IQA;
* reconstruction consistency methods;
* self-consistency or perturbation-based uncertainty.

For each comparator:

determine whether a fair implementation is possible with the available data.

Do not implement methods requiring incompatible assumptions merely to increase baseline count.

Document excluded baselines and why they are not comparable.

---

# 20. Continue literature surveillance

Regularly search the most recent relevant literature.

Focus especially on terms related to:

* MRI reconstruction uncertainty;
* slice interpolation uncertainty;
* interpolation consistency;
* reconstruction consistency;
* test-time augmentation uncertainty;
* model disagreement;
* selective prediction;
* risk-coverage;
* no-reference reconstruction quality;
* self-consistency;
* perturbation-based confidence;
* measurement consistency;
* inverse-problem uncertainty;
* deterministic model reliability.

For each highly related paper, determine whether it threatens novelty.

Do not rely on memory.

Verify actual papers.

Update:

`LITERATURE.md`

and:

`NOVELTY_AUDIT.md`

Maintain a section:

`Closest Prior Work`

with explicit differences.

If prior work substantially overlaps with the proposed central mechanism, do not hide it.

Reframe or pivot.

---

# 21. Use negative results as research evidence

Preserve all failed hypotheses.

Especially preserve:

* adaptive selector failure;
* attribution failure;
* hybrid redundancy;
* factor-specific failures;
* cohort-specific failures;
* normalization failures;
* external replication failures.

For every important negative result ask:

> What does this teach us about the structure of the problem?

Use negative evidence to generate better hypotheses.

Do not repeatedly tune a failed idea unless there is a concrete mechanistic reason to believe a specific change should fix it.

---

# 22. Separate exploratory and confirmatory research

Every experiment must be labeled:

`EXPLORATORY`

or

`CONFIRMATORY`.

Exploratory experiments may generate new hypotheses.

Confirmatory experiments must test a frozen hypothesis/method.

Never present an exploratory result as if it were preregistered.

If an exploratory experiment motivates a method change:

1. record the observation;
2. formulate the new hypothesis;
3. freeze the revised method;
4. test it on data not used to derive the change whenever possible.

Maintain this history transparently.

---

# 23. Research decision policy

At every iteration ask:

### Question A

What is the biggest uncertainty currently preventing a strong claim?

### Question B

What experiment would maximally reduce that uncertainty?

### Question C

Can that experiment falsify the current interpretation?

Prioritize experiments by expected information gain, not by probability of producing a positive result.

Prefer one decisive experiment over ten cosmetic ablations.

---

# 24. Periodically attempt to reject the entire project

After every major batch of experiments, perform a hostile review.

Ask:

* Is this effect just one cohort?
* Is it driven by one case?
* Is it driven by one architecture?
* Is it caused by intensity scaling?
* Is it caused by geometry mismatch?
* Is it merely generic perturbation sensitivity?
* Is it already known in prior literature?
* Is it statistically fragile?
* Does it only work because the target error metric resembles the proposed score?
* Does it fail for clinically important errors?
* Does agreement simply mean stable hallucination?
* Is extra multi-factor inference too expensive to matter?
* Is the contribution scientifically interesting beyond its implementation?

Write the answers to:

`FALSIFICATION_REPORT.md`

Update it repeatedly.

The purpose is to discover fatal flaws early.

---

# 25. Pivot criteria

Do not remain attached to Physical Consistency indefinitely.

Pivot away from it if strong evidence shows that:

* the effect disappears under proper case-level statistics;
* independent replication fails substantially;
* generic perturbation consistency performs equivalently and removes the claimed novelty;
* the score primarily measures an irrelevant preprocessing artifact;
* the effect is driven by very few cases;
* the mechanism cannot survive controlled tests;
* novelty is substantially covered by prior work;
* practical cost makes the setting unrealistic;
* a deeper alternative hypothesis better explains the observations.

If this happens:

1. document why the current direction failed;
2. preserve all evidence;
3. return to the complete project corpus;
4. identify the next most promising unexplained phenomenon;
5. formulate new falsifiable hypotheses;
6. continue the autonomous research loop.

A failed Physical Consistency hypothesis does NOT mean the Goal is complete.

It means the research search continues.

---

# 26. Search for stronger claims, not larger scores

A strong outcome would ideally evolve from:

“Physical Consistency improves nAURC.”

toward something like:

“Deterministic reconstruction reliability can be inferred from instability under target-preserving changes in sampling context.”

A still stronger outcome would establish:

1. the empirical phenomenon;
2. the mechanism;
3. why conventional disagreement misses part of it;
4. a mathematically interpretable reliability signal;
5. replication across multiple datasets/models/settings;
6. clear failure boundaries.

Do not adopt any of these claims until experimentally justified.

Let the evidence determine the final claim.

---

# 27. Maintain a live Claim–Evidence graph

Update:

`CLAIM_EVIDENCE_MATRIX.md`

For every claim record:

* Claim ID
* Exact wording
* Evidence required
* Supporting Experiment IDs
* Contradicting Experiment IDs
* Number of independent datasets
* Number of architectures
* Number of cases
* Statistical evidence
* Mechanistic evidence
* Relevant prior work
* Main confounders
* Remaining reviewer attacks
* Confidence level
* Current status:

  * speculative
  * promising
  * partially supported
  * supported
  * strongly supported
  * rejected

Never upgrade confidence without new evidence.

---

# 28. Maintain a research frontier

Create:

`RESEARCH_FRONTIER.md`

Continuously list the five most important open questions.

For each question include:

* why it matters;
* evidence currently available;
* possible explanations;
* cheapest discriminative experiment;
* expected information gain;
* estimated computational cost;
* priority.

After every major result, rerank the frontier.

Always work primarily on the highest-value unresolved question.

---

# 29. Figure-driven scientific thinking

As results mature, identify what figures would convince a skeptical reviewer.

Potential high-value figures include:

### Figure A

Conceptual comparison of:

cross-model disagreement

versus

cross-factor physical consistency.

### Figure B

Risk-coverage curves across major methods.

### Figure C

Per-profile forest plot.

### Figure D

Common-mode failure experiment.

### Figure E

Independent dataset replication.

### Figure F

Consistent-but-wrong failure cases.

### Figure G

Physical-plane matching geometry.

Do not create decorative figures merely for presentation.

Every figure should answer a scientific question.

---

# 30. Stop optimizing when the mechanism is understood

Do not make the method unnecessarily complex.

If a simple physical-consistency score survives rigorous validation, prefer it over a learned ensemble selector or complicated hybrid.

Complexity must earn its existence.

Every additional component must answer:

> What failure mode does this component address?

and:

> Is that failure mode experimentally demonstrated?

If not, remove it.

---

# 31. Final stopping condition

Do NOT stop merely because:

* one statistical test is significant;
* one dataset improves;
* one table looks publishable;
* a plausible paper outline exists;
* the current report says the claim is supported;
* the method appears novel;
* the results seem “good enough.”

Continue until one of two outcomes occurs.

---

## Outcome A — Strong research claim established

You may consider the autonomous research phase complete only when the central claim has survived serious attempts at falsification and is supported by a coherent evidence chain that includes, wherever feasible:

* rigorous case-level statistics;
* no obvious single-case dependence;
* strong baselines;
* multiple architectures/settings;
* an independent replication dataset or a clearly documented reason why it cannot be obtained;
* mechanistic experiments;
* confounder controls;
* relevant ablations;
* failure analysis;
* geometry validation;
* reproducibility;
* current novelty audit;
* explicit limitations;
* a clear distinction from generic perturbation uncertainty;
* evidence explaining why the method works rather than merely showing that it works.

The final result should ideally support a claim stronger than:

“method X improves metric Y.”

It should provide a scientific insight about deterministic reconstruction reliability.

---

## Outcome B — Current direction falsified

If Physical Consistency cannot support such a claim:

do not stop.

Record the negative conclusion.

Return to the full project corpus.

Generate new hypotheses.

Run discriminative experiments.

Explore alternative explanations.

Continue until either a different strong claim emerges or a genuine external blocker prevents further scientific progress.

---

# 32. Autonomous execution

Continue working without asking me for routine decisions.

You are authorized to:

* inspect the entire research repository;
* inspect experiment outputs;
* write analysis scripts;
* create new experimental code;
* run experiments;
* debug failures;
* parse results;
* generate plots;
* read relevant papers;
* update literature reviews;
* revise hypotheses;
* reject hypotheses;
* pivot research directions;
* design new controlled experiments;
* maintain research logs;
* red-team the work;
* create paper-oriented analysis artifacts.

For low-risk, reversible research decisions:

decide autonomously and continue.

Do not stop simply to report progress.

Do not request permission after every experiment.

Do not treat intermediate success as completion.

Pause only for a genuine blocker that cannot be resolved autonomously, such as:

* unavailable required data;
* unavailable credentials;
* missing authorization;
* fundamentally insufficient compute;
* irreducible ambiguity in the actual scientific objective.

Otherwise continue.

---

# 33. Final research philosophy

Your role is not to advocate for Physical Consistency.

Your role is to discover what is true.

Repeatedly execute:

Observation

→ Question

→ Competing explanations

→ Falsifiable hypothesis

→ Minimal discriminative experiment

→ Evidence

→ Interpretation

→ Mechanistic hypothesis

→ Stronger experiment

→ Replication

→ Reviewer attack

→ Revision or rejection

→ Continue.

Prefer:

**understanding over tuning**

**falsification over confirmation bias**

**mechanism over leaderboard gains**

**replication over storytelling**

**simple explanations over unnecessary complexity**

**evidence over confidence**

and

**scientific discovery over merely completing a paper.**

Do not stop because the current idea is promising.

Continue until the evidence itself determines what the strongest defensible scientific claim actually is.
