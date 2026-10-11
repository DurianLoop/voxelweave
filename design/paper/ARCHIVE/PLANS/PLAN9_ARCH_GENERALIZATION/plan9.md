/goal

PLAN 9 — Architecture-Family Generalization and Final Dual-Paper Upgrade

Continue the MRI inter-slice interpolation research program under:

D:\MRI\design\paper

The current Plan-8 CVPR paper has reached a scientifically credible weak-accept-level mechanism-paper state, and the TMI paper already has a mature medical-imaging methodology narrative.

The next objective is NOT to redesign either paper from scratch.

The objective is to resolve one of the most important remaining reviewer risks:

> Are the observed consensus-blindness and shared-measurement-influence phenomena specific to HAT and SwinIR, or do they persist across fundamentally different MRI slice-interpolation model families?

A substantial amount of historical baseline work already exists in this repository.

Do not assume HAT and SwinIR are the only available neural reconstruction models.

In particular, prioritize reintegration and controlled evaluation of:

- I3Net / I³Net
- SAINT
- CycleINR

and inspect all historical experiments for other usable baselines.

The goal is NOT to increase the number of rows in a table.

The goal is to turn architecture breadth into scientifically meaningful evidence.

Remain strictly within MRI inter-slice / through-plane interpolation.

Do not expand into unrelated domains.

--------------------------------------------------
0. PRESERVE THE CURRENT STRONG VERSIONS
--------------------------------------------------

Do NOT overwrite:

- the current TMI submission candidate;
- the current CVPR Plan-8 recovered paper;
- prior Plan-1 through Plan-8 evidence.

Treat both current manuscripts as frozen reference versions.

Create:

D:\MRI\design\paper\PLAN9_ARCH_GENERALIZATION

and new manuscript branches:

TMI\TMI_ARCH_GENERALIZED

CVPR\CVPR_ARCH_GENERALIZED

This allows the new experiments to fail without destroying the existing submission-ready candidates.

--------------------------------------------------
1. FIRST PERFORM A COMPLETE BASELINE RECOVERY AUDIT
--------------------------------------------------

Recursively inspect:

D:\MRI\design

and:

D:\MRI\design\paper

for all previously evaluated interpolation / reconstruction baselines.

At minimum search for:

- Linear
- Cubic
- I3Net / I³Net
- SAINT
- CycleINR
- HAT
- SwinIR
- ArSSR
- Res-SRDiff
- SMamba-UNet
- Pix2Pix-GAN 2.5D
- ResUNet
- ACVIT
- any other historical baseline.

Do not trust filenames alone.

For every method establish:

Method name
Exact implementation
Architecture family
Original paper/citation
Official/adapted/internal implementation
Training data
Training split
Inference data
Interpolation factors
x2 availability
x4 availability
x6 availability
fastMRI availability
IXI availability
NingXia availability
Stored predictions
Stored checkpoints
Preprocessing
Intensity normalization
Physical target definition
Input slice geometry
Output geometry
Evaluation mask
Metric implementation
Whether same-target phase-grid experiments are feasible
Whether measurement influence can be defined
Whether comparison is fair

Create:

PLAN9_ARCH_GENERALIZATION/BASELINE_RECOVERY_AUDIT.md

Never fabricate missing experimental provenance.

--------------------------------------------------
2. CLASSIFY EVERY BASELINE
--------------------------------------------------

Assign every recovered method one category:

CORE_MECHANISM_ELIGIBLE

ARCHITECTURE_GENERALIZATION_ELIGIBLE

RECONSTRUCTION_BENCHMARK_ONLY

SUPPLEMENT_ONLY

INCOMPARABLE

MISSING_OUTPUTS_BUT_REPRODUCIBLE

UNRECOVERABLE

The classification must be based on experimental compatibility, not whether the method produces favorable numbers.

Do not exclude an unfavorable valid baseline.

--------------------------------------------------
3. PRIORITY METHODS
--------------------------------------------------

Treat the following as P0 candidates:

I3Net
SAINT
CycleINR

The scientific purpose is architecture-family diversity.

Desired family coverage:

Analytical:
- Linear
- Cubic

Transformer / SR:
- HAT
- SwinIR

Dedicated medical slice interpolation:
- I3Net

Spatially aware medical slice synthesis:
- SAINT

Implicit neural representation / continuous volumetric interpolation:
- CycleINR

If ArSSR or another clearly different family is already fully compatible, it may also be included.

Do NOT add methods solely to maximize method count.

--------------------------------------------------
4. FAIRNESS BEFORE PERFORMANCE
--------------------------------------------------

Before comparing any new model, audit whether:

- the physical target is identical;
- train/test units are identical;
- input information is comparable;
- interpolation factor has the same meaning;
- intensity preprocessing is compatible;
- masks are equivalent;
- metrics are identical;
- evaluation is patient/examination independent.

If historical outputs violate these requirements:

either regenerate them under the unified protocol

or classify the method as benchmark-only.

Do not silently compare incompatible experiments.

Create:

PLAN9_ARCH_GENERALIZATION/PROTOCOL_FAIRNESS_AUDIT.md

--------------------------------------------------
5. BUILD TWO DIFFERENT EVIDENCE LAYERS
--------------------------------------------------

Do NOT force every model into every experiment.

Use two layers.

LAYER A — Reconstruction benchmark breadth

Purpose:

demonstrate that the research environment contains competitive and diverse interpolation methods.

Include every scientifically fair method.

Report standard reconstruction endpoints such as:

MAE
RMSE
PSNR
SSIM

for relevant:

x2
x4
x6

and datasets.

This table answers:

> Are HAT and SwinIR cherry-picked weak/strong models?

It is NOT the main novelty experiment.

--------------------------------------------------
LAYER B — Mechanism generalization

Purpose:

test whether the central scientific mechanism survives architecture-family changes.

Only use methods satisfying the controlled protocol.

For every eligible architecture compute:

- shared error fraction;
- observable error fraction;
- error cosine;
- prediction disagreement;
- disjoint-versus-shared ranking effect;
- stable-wrong prevalence;
- factor dependence;
- risk–coverage when scientifically appropriate.

This is the critical layer.

--------------------------------------------------
6. PRIMARY NEW HYPOTHESIS
--------------------------------------------------

Register before observing new results:

H-ARCH-01

> Consensus blindness induced by measurement dependence is not specific to HAT/SwinIR. When deterministic MRI slice interpolators reuse influential physical measurements, their reconstruction errors become more aligned and prediction disagreement becomes less informative, across multiple fundamentally different interpolation architectures.

Falsification conditions:

- the effect disappears outside HAT/SwinIR;
- dedicated interpolation models behave qualitatively differently;
- INR models do not exhibit the phenomenon;
- measurement-disjoint intervention fails to improve observability in most new architecture families.

Do not modify this hypothesis after observing results.

--------------------------------------------------
7. SAME-TARGET DISJOINT VS SHARED TEST
--------------------------------------------------

For I3Net, SAINT and CycleINR wherever technically valid, reproduce the strongest Plan-8 controlled experiment.

Hold fixed:

- physical target;
- examination;
- model;
- interpolation factor;
- target plane;
- preprocessing;
- mask;
- endpoint.

Change only the available measurement/context dependence as closely as the architecture allows.

Compare:

measurement-disjoint context

versus

shared-measurement context.

Measure:

- reconstruction error;
- disagreement;
- error ranking Spearman;
- observable paired-error fraction;
- error cosine;
- stable-wrong rate.

Use examination/patient clustered inference.

This should be the first decisive architecture-generalization experiment.

--------------------------------------------------
8. DO NOT FORCE IDENTICAL INTERNAL ARCHITECTURE
--------------------------------------------------

I3Net, SAINT and CycleINR may not consume context identically.

Do not distort the model simply to imitate HAT/SwinIR.

Define the intervention at the PHYSICAL MEASUREMENT level.

The invariant scientific object is:

> Which acquired physical measurements influence prediction of the same missing target?

Not:

> whether every model has exactly the same tensor input interface.

Document architecture-specific context construction transparently.

--------------------------------------------------
9. CREATE A UNIFIED MEASUREMENT-INFLUENCE PROBE
--------------------------------------------------

For nonlinear architectures, build a model-agnostic local physical-measurement influence probe.

Preferred concept:

For each acquired anchor/measurement:

1. perturb, mask, replace, or infinitesimally modify that physical input measurement using a preregistered valid perturbation;
2. measure the resulting target-output change;
3. construct a local influence vector over physical measurements.

The implementation may use:

- finite differences;
- anchor occlusion;
- Jacobian-vector products;
- local response magnitude;

depending on model compatibility.

The definition must remain comparable at the PHYSICAL MEASUREMENT level.

Do not choose different influence definitions merely because one gives better numbers.

Freeze the protocol before cross-model evaluation.

Call the measurement:

Local Physical Measurement Influence

unless a more precise non-marketing term is justified.

Do NOT claim this probe itself is the main innovation.

Its purpose is cross-architecture mechanism validation.

--------------------------------------------------
10. TEST SHARED INFLUENCE ACROSS ALL ELIGIBLE MODELS
--------------------------------------------------

For:

HAT
SwinIR
I3Net
SAINT
CycleINR

where feasible, calculate shared physical measurement influence between context pairs.

Test:

shared influence
    →
error cosine / error alignment

and:

error alignment
    →
normalized disagreement

and:

shared influence
    →
observable error fraction.

Use the same statistical hierarchy.

Do not pool millions of pixels as independent observations.

Primary inference remains examination/patient clustered.

--------------------------------------------------
11. COMPARE INFLUENCE AGAINST RAW OVERLAP
--------------------------------------------------

The current Plan-8 claim is:

shared influence explains the phenomenon better than simple anchor count.

This becomes substantially stronger if replicated across architecture families.

For every eligible model compare:

Anchor overlap count

versus

Shared measurement influence

for predicting:

- error cosine;
- shared-error fraction;
- observable-error fraction;
- disagreement suppression.

Report:

Δ|rho|

with clustered confidence intervals.

Do not require every architecture to produce statistical significance.

Report heterogeneity.

--------------------------------------------------
12. ARCHITECTURE-FAMILY FOREST PLOT
--------------------------------------------------

Create a primary analysis summarizing:

Disjoint − Shared effect

for every architecture.

Rows may include:

Linear
Cubic
HAT
SwinIR
I3Net
SAINT
CycleINR

and any other protocol-compatible model.

For each report:

effect size
95% clustered CI
dataset
factor

Create a forest-style figure.

The question should be visually obvious:

> Does the effect survive architecture changes?

Do not average away meaningful heterogeneity.

--------------------------------------------------
13. LEAVE-ONE-ARCHITECTURE-FAMILY-OUT ANALYSIS
--------------------------------------------------

Perform a robustness test:

remove one architecture family at a time

and recompute the aggregate mechanism effect.

Examples:

remove Transformers

remove medical interpolation networks

remove INR

remove analytical interpolators.

If the conclusion survives:

this is strong evidence that the result is not dominated by one family.

If it does not:

identify which family drives the result.

--------------------------------------------------
14. ARCHITECTURE-SPECIFIC ERROR CORRELATION
--------------------------------------------------

Use the expanded model pool to test a deeper question:

> Do fundamentally different architectures fail on the same examinations?

Compute cross-architecture error-rank correlations among:

HAT
SwinIR
I3Net
SAINT
CycleINR
and other eligible models.

Analyze:

- case-level error correlation;
- factor-level correlation;
- stable-wrong overlap;
- consensus-error intersection.

If substantially different architectures still fail on the same cases:

this strengthens the intrinsic-difficulty / consensus-error argument.

--------------------------------------------------
15. ARCHITECTURE DIVERSITY VS ERROR DIVERSITY
--------------------------------------------------

Test:

> Does architecture diversity automatically create useful error diversity?

Compare pair types such as:

Transformer–Transformer
Transformer–I3Net
Transformer–SAINT
Transformer–INR
medical-interpolation–INR.

Measure:

prediction diversity

versus

error cosine

versus

actual error observability.

A potentially important negative result would be:

> Architecturally different models can still share reconstruction error.

If true, this materially strengthens the consensus-blindness paper.

Do not force this conclusion.

--------------------------------------------------
16. STABLE-WRONG ACROSS MODELS
--------------------------------------------------

Define stable-wrong cases using a preregistered rule.

Ask:

- Are the same examinations stable-wrong across HAT/SwinIR/I3Net/SAINT/CycleINR?
- Are some failure cases architecture specific?
- Does measurement-disjoint intervention recover them consistently?

Produce a compact qualitative panel using a small number of representative MRI cases.

Do not select examples solely because they look visually dramatic.

Define selection rules first.

--------------------------------------------------
17. FACTOR × ARCHITECTURE INTERACTION
--------------------------------------------------

Analyze whether architecture-generalization depends on interpolation difficulty.

For:

x2
x4
x6

test:

architecture × factor

for:

- reconstruction error;
- shared-error fraction;
- disagreement observability;
- disjoint benefit.

Ask:

> Does consensus blindness become more severe as sampling becomes harder regardless of architecture?

If supported, this gives a deeper MRI-specific mechanism.

--------------------------------------------------
18. DO NOT REQUIRE ALL THREE NEW METHODS TO SUCCEED
--------------------------------------------------

Interpret results scientifically.

Possible outcomes:

A. all three reproduce the mechanism:
strong architecture-generalization evidence.

B. two reproduce and one differs:
identify an architecture-dependent boundary.

C. only one reproduces:
do not claim broad generalization.

D. none reproduce:
the current HAT/SwinIR mechanism claim must be narrowed.

Do not tune methods until the desired narrative appears.

--------------------------------------------------
PART A — TMI UPGRADE
--------------------------------------------------

19. TMI SCIENTIFIC ROLE OF THE NEW BASELINES

For TMI, use the expanded baseline set to strengthen:

**medical-imaging generality and QA characterization.**

Do NOT convert the TMI paper into a shared-influence method paper.

The TMI central question remains:

> Under what conditions can deterministic MRI interpolation agreement fail as a reconstruction-QA signal?

--------------------------------------------------
20. TMI BROAD RECONSTRUCTION BENCHMARK

Add a compact benchmark table with as many fair recovered methods as practical.

Priority ordering:

Linear
Cubic
I3Net
SAINT
CycleINR
HAT
SwinIR

then other fair baselines.

The table should establish:

- model competitiveness;
- architectural breadth;
- x2/x4/x6 behavior;
- dataset coverage.

Do not make leaderboard superiority the paper's main point.

--------------------------------------------------
21. TMI MECHANISM GENERALIZATION SECTION

Add a dedicated section such as:

“Generalization Across Interpolation Paradigms”

Report for representative families:

- disjoint/shared effect;
- consensus-error fraction;
- stable-wrong prevalence;
- factor interaction.

TMI does not need every detailed influence experiment.

Keep the emphasis on:

MRI reconstruction QA.

--------------------------------------------------
22. TMI NEW REVIEWER ATTACK TO RESOLVE

Simulate:

> “Both primary neural experiments use similar 2.5-D transformer/SR pipelines. How do we know the phenomenon is not architecture-specific?”

The new I3Net/SAINT/CycleINR experiments should directly answer this.

Rewrite the paper only after seeing the evidence.

--------------------------------------------------
23. TMI TABLE DESIGN

Prefer:

TABLE I
Dataset/model/factor configuration.

TABLE II
Broad reconstruction performance.

TABLE III
QA mechanism generalization across representative model families.

Avoid a 12-method × 30-metric unreadable table.

Full method matrices may go to internal master material or legitimate supplementary/appendix locations according to target policy.

--------------------------------------------------
24. TMI FIGURE UPGRADE

Consider one new figure:

Architecture-family generalization of consensus blindness.

Use:

forest plot or compact multi-panel visualization.

Do NOT duplicate the CVPR shared-influence figure.

TMI figure message:

> Different MRI interpolation paradigms exhibit the same QA blind spot.

--------------------------------------------------
25. TMI NEW CLAIM GATE

Only strengthen wording from:

“two frozen neural interpolators”

to:

“multiple interpolation paradigms”

if evidence actually supports it.

Do not write:

“architecture independent”

unless an unrealistically broad family set has been tested.

Prefer:

“observed across evaluated interpolation paradigms.”

--------------------------------------------------
PART B — CVPR UPGRADE
--------------------------------------------------

26. CVPR SCIENTIFIC ROLE OF THE NEW MODELS

For CVPR, architecture breadth must strengthen the MECHANISM.

Do NOT simply add three rows to the reconstruction table.

The critical new question is:

> Does shared physical measurement influence explain disagreement blindness across fundamentally different deterministic interpolation mechanisms?

This directly addresses the current CVPR breadth risk without leaving MRI.

--------------------------------------------------
27. CVPR PRIMARY NEW RESULT

Attempt to build one central architecture-generalization result:

For each architecture:

shared influence
versus
raw overlap count

for explaining:

error alignment.

A desirable table/figure structure:

Method
Family
Overlap→Error Alignment
Influence→Error Alignment
Δ
Clustered CI

Do not predetermine that Δ must be positive.

--------------------------------------------------
28. CVPR CROSS-FAMILY MECHANISM CHAIN

Repeat the local chain:

Shared influence
    ↓
Error alignment
    ↓
Disagreement cancellation
    ↓
Reduced observable error

across representative architecture families.

The new contribution is significantly stronger if the chain appears in:

Transformer

+

Dedicated slice interpolation

+

Spatial interpolation

+

INR.

--------------------------------------------------
29. CVPR FIGURE 3 REPLACEMENT / EXPANSION

Current Figure 3 only emphasizes HAT/SwinIR neural influence.

Redesign it if the new experiments succeed.

Possible final Figure 3:

Panel A:
architecture families.

Panel B:
shared influence vs error cosine.

Panel C:
influence-minus-count effect across models.

Panel D:
leave-one-family-out robustness.

This figure should answer the Reviewer-3 breadth objection in under 30 seconds.

--------------------------------------------------
30. CVPR DO NOT OVERWEIGHT ANCHOR-CV

Anchor-CV remains a practical consequence.

Do NOT spend additional scientific budget trying to prove:

Anchor-CV > adjacent MAE/RMSE.

That question is already answered.

It is not universally superior.

Keep this boundary.

Use the new architecture experiments to strengthen the main mechanism instead.

--------------------------------------------------
31. CVPR OPTIONAL NEW PRACTICAL QUESTION

Only after architecture generalization succeeds:

ask whether acquired-anchor difficulty predicts error across the new architectures.

Test whether Anchor-CV / adjacent difficulty ranks examination difficulty similarly for:

I3Net
SAINT
CycleINR.

If yes:

this suggests examination difficulty is architecture-shared.

This is supporting evidence, not a new method claim.

--------------------------------------------------
32. CROSS-MODEL CONSENSUS ERROR

Use the expanded architecture set to revisit the earlier observation:

most reconstruction error may be shared across architectures.

Estimate:

architecture-common error component

versus

architecture-specific component.

Ask whether:

architecturally diverse models still share dominant failure directions.

If supported, this can significantly strengthen both papers:

TMI:
common MRI QA blind spots.

CVPR:
architectural diversity alone does not guarantee useful disagreement.

--------------------------------------------------
33. POTENTIALLY STRONG CVPR SUBCLAIM

Test the hypothesis:

> Architecture diversity is not equivalent to error independence.

This is directly connected to the central paper principle.

If:

HAT
SwinIR
I3Net
SAINT
CycleINR

look architecturally different but retain highly aligned case/plane errors,

then disagreement ensembles based merely on architectural diversity can still suffer consensus blindness.

This could become a strong secondary result.

Do not claim it unless empirically demonstrated.

--------------------------------------------------
34. BASELINE PERFORMANCE MUST STILL BE CREDIBLE

Before using a model in mechanism experiments verify that it is not catastrophically undertrained.

For each model report reconstruction performance relative to:

- its historical run;
- reasonable published/repository expectations where protocol allows;
- current HAT/SwinIR scale.

A broken implementation cannot serve as evidence of architecture generalization.

--------------------------------------------------
35. DO NOT CHERRY-PICK ARCHITECTURES

If I3Net supports the claim and CycleINR does not:

do not omit CycleINR merely to make the table cleaner.

If CycleINR is protocol-compatible and directly tests the claim:

report the heterogeneity.

You may move detailed results to supplement for space,

but final wording must reflect them.

--------------------------------------------------
36. LITERATURE UPDATE

Verify exact primary literature and BibTeX for:

I3Net
SAINT
CycleINR

and every baseline added.

Do not infer citations from filenames.

Update:

TMI references

CVPR references

NOVELTY_AUDIT.md

RELATED_WORK_MATRIX.md

Use primary sources.

--------------------------------------------------
37. RE-EVALUATE NOVELTY AFTER BASELINE EXPANSION

Search specifically for whether any of these methods already discuss:

- disagreement reliability;
- measurement overlap;
- shared measurement influence;
- common-mode interpolation error;
- same-target context interventions.

If a baseline's own paper contains closely related analysis:

adjust novelty claims immediately.

--------------------------------------------------
38. STATISTICAL META-ANALYSIS

Once multiple architectures are available, avoid reporting only dozens of individual rho values.

Construct architecture-stratified summaries.

Possible analyses:

- per-architecture clustered effect;
- random/fixed-effects descriptive meta-analysis where justified;
- leave-one-family-out;
- sign consistency;
- heterogeneity statistics.

Do not treat architectures as independent clinical subjects.

The clinical independent units remain examinations/patients.

--------------------------------------------------
39. DECISION RULE FOR MAIN PAPER METHOD SELECTION

Main papers should maximize:

scientific relevance
+
architecture diversity
+
protocol validity

not:

number of favorable results.

If space is limited, choose representative families.

Example candidate main set:

Linear
I3Net
HAT
SAINT
CycleINR

with:

Cubic
SwinIR
and remaining baselines

in expanded tables/supplement.

The exact choice should be evidence-driven.

--------------------------------------------------
40. TMI/CVPR SEPARATION AFTER PLAN 9

Do not accidentally make the two papers identical.

Final intended ownership:

TMI:

“Consensus blindness is a systematic MRI reconstruction-QA phenomenon across interpolation paradigms and operating regimes.”

CVPR:

“Shared physical measurement influence explains error alignment and disagreement cancellation across fundamentally different interpolation architectures.”

TMI focuses on:

QA behavior
metrics
factors
operating regime
reliability
failure cases
medical-imaging interpretation.

CVPR focuses on:

mechanism
influence
controlled intervention
architecture-family generalization
local error geometry.

Maintain:

SUBMISSION_OVERLAP_AUDIT.md

--------------------------------------------------
41. REWRITE ONLY AFTER EXPERIMENTS
--------------------------------------------------

Do not immediately edit either paper.

Sequence:

1. baseline recovery;
2. protocol fairness;
3. regenerate missing predictions if necessary;
4. reconstruction benchmark;
5. controlled mechanism experiments;
6. influence analysis;
7. statistics;
8. heterogeneity;
9. literature audit;
10. reviewer simulation;
11. manuscript rewrite.

--------------------------------------------------
42. NEW REVIEW SIMULATION
--------------------------------------------------

After integration, independently simulate reviewers.

TMI reviewer question:

> Is the phenomenon convincingly general across meaningful MRI interpolation paradigms?

CVPR reviewer question:

> Does architecture-family evidence elevate this beyond a narrow two-model medical-imaging observation?

Do not show simulated reviewers the desired scores.

Let them score independently.

--------------------------------------------------
43. TARGET IMPROVEMENT
--------------------------------------------------

Do NOT manipulate scores.

But determine whether new evidence genuinely changes:

TMI:
Reviewer 3/4 concerns around breadth and impact.

CVPR:
the current Reviewer-3 3/5 scope/breadth concern.

A scientifically successful Plan-9 should ideally make the remaining CVPR objection:

> “MRI-only”

rather than:

> “only two related architectures.”

MRI-only is an intentional scope choice.

Two-related-model evidence is an avoidable weakness.

--------------------------------------------------
44. FINAL DELIVERABLES
--------------------------------------------------

Produce:

PLAN9_ARCH_GENERALIZATION/FINAL_REPORT.md

with:

- recovered baselines;
- protocol eligibility;
- new experiments;
- I3Net results;
- SAINT results;
- CycleINR results;
- architecture heterogeneity;
- mechanism-generalization verdict;
- falsified hypotheses;
- revised claims;
- reviewer simulations.

Create final manuscript candidates:

TMI/TMI_ARCH_GENERALIZED/main.tex
TMI/TMI_ARCH_GENERALIZED/main.pdf

CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex
CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf
CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.tex
CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf

Do not automatically submit.

--------------------------------------------------
45. FINAL SUCCESS CONDITIONS
--------------------------------------------------

TMI upgrade succeeds if:

- multiple materially different interpolation paradigms support the QA phenomenon;
- the manuscript becomes less vulnerable to architecture-specificity criticism;
- medical-imaging QA interpretation remains coherent;
- no major contradictory evidence is hidden.

CVPR upgrade succeeds if:

- the central shared-influence mechanism survives at least multiple fundamentally different neural/interpolation families;
- raw overlap remains a weaker explanatory variable than influence in meaningful strata;
- error alignment/disagreement cancellation remains mechanistically supported;
- the paper's breadth improves without leaving MRI;
- final reviewer simulation shows improved confidence for the mechanism paper.

If the new architectures contradict the current claim:

do not tune them away.

Use the result to identify the true boundary of the mechanism and rewrite accordingly.

--------------------------------------------------
46. FINAL INSTRUCTION
--------------------------------------------------

The purpose of adding I3Net, SAINT and CycleINR is NOT:

“more baselines.”

The purpose is:

**stronger science through architecture-family falsification.**

Ask:

> If this mechanism is real, should it survive when the interpolation paradigm changes?

Then test that question rigorously.

For TMI:

use architecture diversity to establish that consensus blindness is a robust MRI reconstruction-QA phenomenon.

For CVPR:

use architecture diversity to establish that shared measurement influence, rather than a specific HAT/SwinIR design choice, governs local error alignment and disagreement observability.

Only after answering these questions should either manuscript be rewritten.

Begin now.