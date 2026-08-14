# Codex Goal Mode Research Master Prompt — English Version

## Step 1 — Run this with `/plan`

/plan

Treat everything under `D:\MRI\design` as one existing research project, including source code, experiment outputs, logs, papers, PDFs, Markdown files, LaTeX, figures, tables, dataset documentation, model configurations, checkpoint information, and previous research attempts.

Do NOT begin by writing a paper.

Act as a rigorous computer-vision researcher and first perform a complete research audit. Design a scientific path toward a genuinely novel, experimentally defensible contribution with the level of rigor expected at venues such as CVPR, ICCV, or ECCV.

“Getting accepted to CVPR” is not itself a verifiable objective and must not be treated as guaranteed.

First:

1. Recursively inspect all research-relevant material under `D:\MRI\design`.
2. Reconstruct:

   * the research problem;
   * existing methods;
   * experiments already conducted;
   * verified findings;
   * unverified assumptions;
   * negative results;
   * strongest current baseline;
   * known bottlenecks;
   * possible contributions.
3. Distinguish genuine scientific contributions from engineering combinations, hyperparameter tuning, implementation improvements, or unsupported observations.
4. Read relevant recent literature and construct a literature map, emphasizing closely related work from CVPR, ICCV, ECCV, NeurIPS, ICLR, AAAI, MICCAI, and other relevant venues.
5. Determine whether similar ideas already exist.
6. Identify unresolved scientific gaps.
7. Formulate multiple falsifiable hypotheses.
8. Rank them by:

   * novelty;
   * scientific significance;
   * plausibility;
   * experimental cost;
   * expected impact;
   * risk of being incremental.
9. For every hypothesis specify:

   * why it may be true;
   * what observation would support it;
   * what observation would falsify it;
   * the minimum discriminative experiment;
   * the full experiment;
   * required ablations;
   * confounders;
   * strongest competing explanation.
10. Define explicit evidence-based stopping criteria for what would constitute a strong claim.

Do not launch expensive full-scale experimentation yet. First complete the audit and research plan so that the project is ready to enter Goal Mode.

---

## Step 2 — Run this with `/goal`

/goal

Starting from the existing research under `D:\MRI\design`, autonomously execute a hypothesis-driven scientific research loop until at least one non-trivial scientific claim is supported by a rigorous, reproducible, auditable body of experimental evidence competitive with the standards expected at a top-tier computer-vision conference.

Do not optimize for merely producing a paper.

Optimize for discovering and validating a real scientific insight.

---

# 0. Scientific principles

The objective is NOT to:

* maximize a benchmark number at any cost;
* endlessly stack modules;
* endlessly tune hyperparameters;
* select a lucky seed;
* exaggerate a tiny improvement into a contribution;
* force a positive conclusion;
* invent a paper story first and cherry-pick experiments afterward.

The objective is to identify and test meaningful scientific hypotheses.

Experiments are allowed to fail.

Initial hypotheses are allowed to be rejected.

Methods are allowed to be abandoned.

If all current directions are insufficient for a strong claim, return to literature analysis, failure analysis, and hypothesis generation rather than forcing a conclusion.

Preserve negative results and use them as evidence.

Never fabricate:

* experimental results;
* baselines;
* papers;
* citations;
* DOIs;
* measurements;
* statistical significance;
* experiments that were not actually executed.

Anything not executed must explicitly be marked `NOT RUN`.

---

# 1. Filesystem policy

Treat:

`D:\MRI\design`

as the existing research corpus.

Treat existing project material as read-only by default.

Do not modify original research artifacts unless executing the existing code absolutely requires it.

All newly created or modified research artifacts must live under:

`D:\MRI\design\paper`

This includes:

* research notes;
* experimental code;
* modified model implementations;
* scripts;
* configurations;
* evaluation harnesses;
* logs;
* checkpoint indices;
* numerical results;
* figures;
* plots;
* tables;
* LaTeX;
* literature notes;
* reviewer analyses;
* intermediate artifacts.

Do not duplicate large raw datasets.

Treat original datasets as read-only and reference them from their existing locations.

---

# 2. Establish durable research state

Create and continuously maintain the following files under `D:\MRI\design\paper`.

## `RESEARCH_STATE.md`

Maintain:

* current research question;
* current best hypothesis;
* current best method;
* current best result;
* established facts;
* unresolved questions;
* current bottleneck;
* next experiment;
* whether a defensible strong claim currently exists.

## `PLAN.md`

Maintain the current research strategy, priorities, and immediate next steps.

## `LITERATURE.md`

For every paper that is actually verified, record:

* title;
* authors;
* venue;
* year;
* verified URL or DOI;
* core idea;
* relevance;
* difference from our work;
* novelty threat.

Do not infer a paper's contribution from its title alone.

## `HYPOTHESES.md`

Give every hypothesis a stable identifier:

H001
H002
H003
...

For each hypothesis record:

Hypothesis
Motivation
Novelty rationale
Expected observation
Falsification condition
Minimum experiment
Full experiment
Potential confounders
Current evidence
Status

## `EXPERIMENTS.md`

Every experiment must receive a unique Experiment ID.

Record:

* Experiment ID
* Date
* Hypothesis ID
* Code/configuration
* Dataset
* Split
* Seed
* Baseline
* Modification
* Metrics
* Parameter count
* FLOPs when relevant
* Latency when relevant
* Memory when relevant
* Results
* Interpretation
* KEEP / REJECT / REFINE
* Artifact paths

## `EXPERIMENT_NOTES.md`

Keep a chronological scratchpad containing scientific reasoning, anomalies, failure analysis, and possible next ideas.

## `CLAIMS.md`

For every candidate claim maintain:

Claim
Supporting evidence
Contradicting evidence
Missing experiments
Alternative explanations
Related prior work
Confidence
Likely reviewer attacks

## `REVIEWER_REDTEAM.md`

Continuously attack the work from the perspective of skeptical top-tier reviewers.

---

# 3. Literature → Gap → Hypothesis

Do not begin by randomly modifying the model.

Reconstruct the research landscape.

Continuously reason through:

Problem

→ Existing paradigms

→ Their assumptions

→ Their failure modes

→ Missing capability

→ Candidate scientific explanation

→ Falsifiable hypothesis.

Focus especially on understanding WHY existing methods fail.

Prioritize gaps involving:

* unexplained empirical phenomena;
* mismatch between training objectives and desired behavior;
* representation bottlenecks;
* information loss;
* inappropriate inductive biases;
* optimization pathology;
* generalization failure;
* domain shift;
* scale-dependent behavior;
* previously conflated factors;
* hidden confounders;
* unnecessary complexity;
* overlooked simple mechanisms.

Whenever a newly discovered paper substantially overlaps with a hypothesis, reassess its novelty immediately.

If the core contribution already exists, either identify a genuinely deeper distinction or abandon the direction.

---

# 4. Hypothesis-driven experimentation

Every research iteration must follow:

Scientific question

→ Hypothesis

→ Prediction

→ Minimal discriminative experiment

→ Observation

→ Interpretation

→ KEEP / REJECT / REFINE

→ Next hypothesis.

Prefer experiments that maximally distinguish competing explanations.

Avoid changing many factors simultaneously.

In general, introduce only one major experimental variable per iteration so causal attribution remains interpretable.

---

# 5. Validate the baselines

Before making any strong claim, verify that the baselines are credible.

Audit:

* dataset splitting;
* preprocessing;
* augmentation;
* optimizer;
* learning-rate schedule;
* evaluation protocol;
* checkpoint selection;
* random seeds;
* metric implementation;
* train/validation/test leakage.

Whenever practical, reproduce at least two genuinely competitive baselines.

If reproduced performance differs substantially from reported performance, investigate the discrepancy before claiming an improvement.

---

# 6. Experimental ladder

For each promising hypothesis, proceed from inexpensive to expensive evidence:

smoke test

→ small controlled experiment

→ matched baseline comparison

→ multi-seed comparison

→ full-scale experiment

→ cross-dataset / robustness / generalization experiment.

If an inexpensive experiment clearly falsifies a hypothesis, do not waste compute on a full training run.

---

# 7. Minimum evidence for a strong claim

A leaderboard improvement alone is not sufficient.

A candidate central claim should satisfy as many of the following as are scientifically appropriate.

## Novelty

A current literature search reveals no materially equivalent method or explanation.

## Causal evidence

The central mechanism can be isolated through controlled experiments.

## Reproducibility

Critical results reproduce across multiple random seeds.

## Strong baselines

Comparisons use genuinely competitive and fairly configured baselines.

## Ablation

Ablations explain why each major component exists.

## Generalization

Whenever feasible, verify the effect across at least one additional dimension such as:

* another dataset;
* another architecture;
* another model scale;
* another data regime;
* another domain;
* another initialization.

## Efficiency

Report relevant trade-offs such as:

* parameters;
* FLOPs;
* GPU memory;
* training time;
* inference latency.

## Statistical reliability

Where appropriate report:

mean ± standard deviation,
confidence intervals,
and/or statistical tests.

Do not report only the best run.

## Failure analysis

Actively search for conditions under which the proposed method fails.

## Alternative explanations

Design experiments to distinguish the main claim from explanations such as:

* more parameters;
* more training;
* stronger augmentation;
* better learning-rate tuning;
* random variation;
* dataset-specific effects.

---

# 8. Additional rules for medical imaging

If the current MRI project concerns medical imaging, explicitly audit:

* patient-level splitting;
* subject leakage;
* repeated-scan leakage;
* scanner/site leakage;
* preprocessing leakage;
* demographic imbalance;
* class imbalance;
* cross-site generalization;
* external validation;
* clinical relevance.

Treat an image-level train/test split that allows the same patient to appear in multiple splits as a serious methodological flaw.

If multi-center data are available, prioritize external-site validation.

---

# 9. Prevent p-hacking and cherry-picking

Never:

* report only the best seed;
* tune against the test set;
* hide failed experiments;
* alter metrics because results are unfavorable;
* silently discard anomalous runs;
* select only datasets favorable to the method;
* rewrite a post-hoc observation as if it were an a-priori hypothesis.

Explicitly distinguish:

`EXPLORATORY`

from:

`CONFIRMATORY`

experiments.

When an interesting pattern is discovered during exploration, verify it with a new controlled experiment whenever feasible.

---

# 10. Autonomous research loop

Repeat continuously:

1. Read `RESEARCH_STATE.md`.
2. Inspect the newest experimental evidence.
3. Identify the largest remaining uncertainty.
4. Select the most informative next experiment.
5. Read additional literature if needed.
6. State the hypothesis being tested.
7. Implement the smallest coherent change.
8. Run relevant correctness tests.
9. Run the experiment.
10. Parse results automatically.
11. Compare with the matched baseline and historical best.
12. Investigate anomalies and confounders.
13. Update experiment records.
14. Decide:

* KEEP
* REFINE
* REJECT

15. Update `CLAIMS.md`.
16. Attack the interpretation as a skeptical reviewer.
17. Select the next research action.
18. Continue.

Do not stop after one successful experiment.

---

# 11. Periodically escape local optimization

After several iterations, explicitly ask:

“What have we learned that was not known before?”

If the answer is merely:

“This module improves metric X by Y%,”

continue asking:

“Why?”

Generate competing mechanistic explanations.

Design experiments that distinguish them.

Whenever possible, evolve the contribution from:

Method improvement

into:

Empirical phenomenon

→ scientific explanation

→ mechanism

→ method derived from that mechanism

→ controlled experimental validation.

---

# 12. Reviewer red team

Periodically simulate at least three skeptical reviewers.

## Reviewer A — Novelty skeptic

Primary question:

“Is this just a recombination of known techniques?”

## Reviewer B — Experimental-rigor skeptic

Primary question:

“Are these improvements fair, reproducible, statistically credible, and free from leakage?”

## Reviewer C — Scientific-contribution skeptic

Primary question:

“What did the community learn beyond a leaderboard improvement?”

Record all substantive criticism in:

`REVIEWER_REDTEAM.md`

Resolve criticism through evidence and experiments rather than rhetorical reframing.

---

# 13. Claim–Evidence Matrix

Continuously maintain:

`CLAIM_EVIDENCE_MATRIX.md`

For each candidate claim record:

Claim
Required evidence
Available evidence
Missing evidence
Counter-evidence
Relevant Experiment IDs
Confidence

Every eventual claim must be traceable to actual experimental artifacts.

---

# 14. Abandon weak directions

If a direction shows:

* repeated failure across controlled experiments;
* tiny unstable gains;
* substantial novelty collision with prior work;
* dependence on a narrow hyperparameter setting;
* inability to explain why it works;
* large complexity increases for negligible gains;

do not endlessly optimize it.

Record it as a negative result.

Diagnose the failure.

Return to:

Literature

→ Gap

→ New hypothesis

and continue the scientific search.

---

# 15. Stopping condition

Only consider the main research-search phase complete when ALL critical evidence is sufficiently strong that the following are true:

There is at least one clear central scientific claim.

The claim is falsifiable.

The claim is supported by actual experiments.

The central effect is reproducible.

Strong and fairly configured baseline comparisons exist.

Key ablations have been completed.

Major competing explanations have been tested.

At least one meaningful generalization or robustness test has been completed whenever feasible, or an objective inability to perform it is explicitly documented.

A current related-work audit reveals no fatal novelty collision.

Negative experiments have been preserved.

Major numerical results are traceable to code, configurations, and logs.

`CLAIM_EVIDENCE_MATRIX.md` contains no unresolved evidence gap that directly invalidates the central claim.

The reviewer red-team analysis contains no unresolved fatal methodological or novelty flaw.

At that point create:

`FINAL_RESEARCH_REPORT.md`

containing:

1. Research question
2. Prior work
3. Identified gap
4. Main hypothesis
5. Key scientific insight
6. Proposed method
7. Experimental protocol
8. Main results
9. Ablation studies
10. Robustness/generalization
11. Failure cases
12. Efficiency analysis
13. Claim–evidence matrix
14. Limitations
15. Remaining reviewer risks
16. Recommended paper narrative

Also create:

`PAPER_OUTLINE.md`

Do not write a full paper merely to satisfy the goal.

The research must become defensible before the manuscript becomes polished.

---

# 16. Autonomy policy

Once Goal Mode begins, do not stop merely because one stage has completed.

Do not ask me about ordinary reversible technical decisions.

Make reasonable low-risk research decisions autonomously.

If an experiment fails:

diagnose → document → update the hypothesis → continue.

If an entire direction fails:

summarize negative evidence → pivot → continue.

If code fails:

debug → verify → continue.

If important new literature is discovered:

update the literature map → reassess novelty → continue.

Pause for human input only when facing a genuine blocker such as:

* a required dataset is unavailable;
* non-substitutable credentials are missing;
* explicit human authorization is required;
* required compute is fundamentally unavailable;
* the research objective itself requires a value judgment that cannot be resolved from existing evidence.

Otherwise, continue working toward the goal.

The objective is not to “run many experiments.”

The objective is:

**systematically reduce scientific uncertainty through literature, falsifiable hypotheses, controlled experimentation, failure analysis, and iteration until the project supports a genuinely meaningful and defensible scientific claim.**
