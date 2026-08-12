Continue working from the current multiscale ICASSP delivery and enter an autonomous research-optimization mode.

The goal is no longer to mechanically test one predefined method, observe that it is imperfect on several models, and immediately narrow the claims. The goal is to conduct a broad but scientifically valid search over model roles, committee compositions, disagreement definitions, spatial aggregation strategies, and scale-aware configurations, then select a small number of strong and defensible finalists for the paper.

The target is to raise the simulated ICASSP 2027 overall score to approximately 4/5.

You must actively explore alternatives. Do not stop after the first negative result. Do not assume that the original median full-committee score is the final method. Use the current method as a baseline, not as an untouchable design.

However, exploration must not become undocumented test-set cherry-picking. Candidate selection must follow a reproducible development-and-validation procedure. Poor exploratory candidates do not need to appear in the regular paper, but they must remain traceable in the experiment registry and extended materials.

The final regular paper should present only:

1. The original frozen baseline;
2. One strong universal selected method;
3. Optionally one low-cost or scale-aware selected method;
4. The most informative comparison and failure analysis.

The full candidate sweep belongs in the extended report and machine-readable results.

---

# 1. Current Starting Point

The current multiscale delivery already contains:

- fastMRI-brain at ×2, ×4, and ×6;
- NingXia at ×2, ×4, and ×6;
- IXI at ×4;
- 24 fastMRI examinations;
- 22 NingXia examinations with eight-fold out-of-fold predictions;
- 115 IXI examinations;
- I3Net, HAT, SwinIR, Linear, and Cubic in the frozen primary bank;
- ArSSR, CycleINR, Pix2PixGAN, and SMamba-UNet in the currently audited expanded bank;
- additional ×4 methods that may include ACVTT, Res-SRDiff, ResUNet, SAINT, or other available predictions;
- 18 fixed dataset–scale–target primary profiles;
- 2,000-case bootstrap evaluation;
- cross-scale analysis;
- matched-target analysis;
- paired method comparisons;
- reconstruction-fidelity tables;
- generated-support auditing;
- common-mode stress testing.

The current aggregate baseline is approximately:

| Dataset | Scale | Case Spearman | nAURC | RRR50 |
|---|---:|---:|---:|---:|
| fastMRI | ×2 | 0.888 | 0.098 | 18.8% |
| fastMRI | ×4 | 0.912 | 0.073 | 19.8% |
| fastMRI | ×6 | 0.937 | 0.052 | 21.0% |
| NingXia | ×2 | 0.892 | 0.065 | 22.0% |
| NingXia | ×4 | 0.926 | 0.058 | 22.2% |
| NingXia | ×6 | 0.871 | 0.097 | 20.9% |

The current matched-target-minus-mismatched intervals include zero. This does not justify immediately abandoning all target-specific investigation. It means that the present unnormalized score captures substantial shared examination difficulty. You must now test whether a better decomposition can preserve overall case-risk ranking while extracting a stronger target-specific component.

The current expanded committee is not monotonically better. This also does not justify rejecting model-bank expansion. It means that indiscriminate expansion is weak; principled member selection or weighting must be explored.

---

# 2. Governing Research Principle

Use the following candidate funnel:

1. Generate a broad candidate set.
2. Screen candidates on designated development profiles.
3. Remove invalid, dominated, unstable, or unnecessarily expensive candidates.
4. Freeze a small finalist set.
5. Evaluate the finalists on held-out profiles without further tuning.
6. Report all finalist results, including any unfavorable held-out profiles.
7. Present only the finalists and essential baselines in the regular paper.
8. Preserve the full sweep, including failed candidates, in the extended report and CSV registry.

A candidate may be removed from the regular paper when it is:

- mathematically redundant;
- dominated on development data by a simpler candidate;
- unstable under bootstrap;
- incompatible with some required profiles;
- based on mismatched spatial or intensity representations;
- dependent on ground truth during deployment;
- computationally excessive without measurable benefit;
- unavailable across the intended validation profiles;
- consistently poor under the predefined development criterion.

A candidate must not be removed merely because it performs badly on a held-out validation profile after selection.

Do not silently delete a selected target, dataset, scale, or validation result.

---

# 3. Establish a Valid Development–Validation Strategy

All current baseline results have already been observed, so do not falsely describe any existing profile as completely untouched.

Use the strongest scientifically defensible selection strategy available.

## Preferred strategy

### Development profiles

Use:

- IXI ×4;
- fastMRI ×2;
- fastMRI ×4;
- fastMRI ×6.

### Validation profiles

Use:

- NingXia ×2;
- NingXia ×4;
- NingXia ×6.

This allows candidate design on a large public cohort and a separate multiscale cohort, followed by evaluation on the independent NingXia out-of-fold predictions.

Do not tune candidate parameters after seeing their NingXia validation results.

Because the original baseline NingXia results are already known, describe this honestly as a prospectively frozen candidate-selection stage within the revision, not as a completely untouched clinical trial.

## Secondary robustness strategy

Also run:

- leave-one-scale-out validation within fastMRI;
- leave-one-scale-out validation within NingXia;
- leave-one-dataset-out transfer:
  - select on fastMRI scales, evaluate on NingXia scales;
  - select on NingXia scales, evaluate on fastMRI scales.

These secondary analyses test whether a selected configuration transfers across scales and cohorts.

## If an unused cohort, contrast, or anatomy exists

Search the workspace for any genuinely unused dataset, contrast, anatomy, or interpolation scale.

If one exists and has sufficient predictions:

- reserve it as the final confirmation set;
- do not inspect its reliability results until finalists are frozen;
- document the freeze timestamp and configuration hash.

---

# 4. Separate Target Models from Committee Models

Do not assume that every available reconstruction method should be treated equally as both a deployment target and a committee member.

These are different roles.

## Target-model eligibility

A target model represents a reconstruction method that might realistically be deployed.

Define target eligibility using development data only.

A model may become a main target when it satisfies all of the following:

1. Per-case predictions exist for the required development and validation profiles.
2. Predictions pass geometry, intensity, support, and finite-value audits.
3. Reconstruction fidelity is competitive on development profiles.
4. It belongs to a relevant and sufficiently distinct model family.
5. It is not clearly dominated in all reconstruction metrics by another method with the same role and architecture family.

Use a transparent development criterion, such as:

- average reconstruction-fidelity rank within the top half;
- or MAE within a predefined percentage of the best development model;
- or Pareto non-dominance over MAE, SSIM, and NCC.

Do not define the threshold after inspecting validation results.

Likely target candidates include strong and deployment-relevant methods such as:

- I3Net;
- HAT;
- SwinIR;
- SMamba-UNet;
- SAINT;
- ACVTT;
- Res-SRDiff;
- another strong available architecture.

Only include a method when real per-case outputs exist.

The main paper does not need to evaluate weak or unrealistic reconstruction methods as targets merely because they exist in the workspace.

Keep their fidelity results in the extended report.

## Committee-member eligibility

Committee members serve as informative peers and do not need to be the strongest reconstruction methods.

A lower-fidelity model may remain useful if it contributes complementary errors.

Candidate committee members may include:

- I3Net;
- HAT;
- SwinIR;
- SMamba-UNet;
- ArSSR;
- CycleINR;
- Pix2PixGAN;
- ACVTT;
- Res-SRDiff;
- ResUNet;
- SAINT;
- Linear;
- Cubic;
- any other audited prediction source.

A member should remain in a selected committee only when it improves development performance, worst-profile stability, target attribution, or cost-performance trade-offs.

Do not retain a member solely because it increases committee size.

---

# 5. Create a Complete Model-Bank Audit

Create:

`MODEL_BANK_AUDIT.md`

and:

`model_bank_registry.csv`

For every available method, record:

- canonical method name;
- architecture family;
- analytical or neural;
- implicit, convolutional, transformer, diffusion, GAN, state-space, or classical;
- available datasets;
- available scales;
- case count;
- reconstruction metrics;
- prediction path;
- output shape;
- intensity range;
- whether output is out of fold;
- whether it can be a target;
- whether it can be a committee member;
- missing profiles;
- inference cost if known;
- audit status;
- exclusion reason if ineligible.

Create two explicit banks:

## Universal multiscale bank

Methods available across:

- fastMRI ×2/×4/×6;
- NingXia ×2/×4/×6.

## Expanded ×4 bank

All methods with valid outputs on one or more ×4 cohorts.

The regular paper should prioritize a method constructed from the universal bank.

The extended paper may contain the larger ×4 model-diversity study.

---

# 6. Explore Target-Specific Score Families

Do not restrict the search to median absolute target-to-member difference.

Implement and evaluate the following families.

## 6.1 Basic target-to-member aggregation

For voxel \(i\):

\[
d_{mb}(i)=|\hat y_m(i)-\hat y_b(i)|.
\]

Evaluate:

- median;
- mean;
- trimmed mean;
- winsorized mean;
- maximum;
- upper quantile, such as \(q=0.75\) or \(q=0.90\);
- mean of the largest \(k\) member differences.

## 6.2 Distance to a committee center

Evaluate:

\[
|\hat y_m-\operatorname{mean}_{b\in C_m}\hat y_b|,
\]

\[
|\hat y_m-\operatorname{median}_{b\in C_m}\hat y_b|.
\]

Also evaluate a geometric median or robust Huber center when computationally feasible.

## 6.3 Committee-normalized target deviation

The current raw distance may primarily reflect common case difficulty.

Test robust standardized deviations:

\[
Z_m(i)=
\frac{
|\hat y_m(i)-\operatorname{median}_{b\in C_m}\hat y_b(i)|
}{
\operatorname{MAD}_{b\in C_m}(\hat y_b(i))+\epsilon
}.
\]

Also test:

\[
Z^{\mathrm{IQR}}_m(i)=
\frac{
|\hat y_m(i)-\operatorname{median}_{b\in C_m}\hat y_b(i)|
}{
\operatorname{IQR}_{b\in C_m}(\hat y_b(i))+\epsilon
}.
\]

Clip extreme standardized values using a development-frozen threshold.

This is a priority candidate because it measures how unusual the named target is relative to the committee’s internal spread.

## 6.4 Shared-difficulty and target-deviation decomposition

For examination \(j\), after computing one score for every eligible target:

\[
d_j=\operatorname{median}_{m}s_{jm},
\]

where \(d_j\) represents shared examination difficulty.

Define target-relative attribution:

\[
a_{jm}=s_{jm}-d_j.
\]

Also test robust normalization:

\[
a^{z}_{jm}=
\frac{s_{jm}-\operatorname{median}_{k}s_{jk}}
{\operatorname{MAD}_{k}(s_{jk})+\epsilon}.
\]

Evaluate:

- shared difficulty \(d_j\);
- relative target attribution \(a_{jm}\);
- robust relative attribution \(a^z_{jm}\);
- combined target risk:

\[
r_{jm}=
\alpha\,\operatorname{rank}(d_j)
+
(1-\alpha)\,\operatorname{rank}(a^z_{jm}).
\]

Choose \(\alpha\) only on development profiles.

Test a small predefined grid:

\[
\alpha\in\{0,0.25,0.5,0.75,1\}.
\]

This decomposition is a priority because the current matched-target analysis suggests that shared case difficulty dominates the raw score.

The final method may explicitly produce two outputs:

1. examination-level difficulty;
2. target-relative deviation.

That can be a stronger and more honest technical contribution than forcing one scalar to perform both functions.

## 6.5 Residualized target score

Fit on development data only:

\[
s_{jm}=\beta_m d_j+r_{jm}.
\]

Use the residual \(r_{jm}\) as the target-attribution score.

Test:

- linear residualization;
- robust Huber residualization;
- rank residualization.

The fitted coefficients must be frozen before validation.

This optional variant uses development labels or development score statistics and therefore must be described as a lightweight calibrated extension, not as the fully training-free baseline.

## 6.6 Model-conditioned score normalization

Different targets may produce scores on different numerical scales.

Using development data only, test:

- target-specific percentile transformation;
- target-specific empirical CDF;
- target-specific robust z-score;
- target-specific rank normalization;
- scale-and-target-conditioned normalization.

Apply the frozen transformation to validation cases.

Do not normalize each validation cohort using its ground-truth errors.

## 6.7 Relative disagreement

Evaluate intensity-relative differences:

\[
\frac{|\hat y_m-\hat y_b|}
{|\hat y_m|+|\hat y_b|+\epsilon}.
\]

Also test local-energy normalization:

\[
\frac{|\hat y_m-\hat y_b|}
{\sqrt{\mathcal{G}(\hat y_m^2)+\mathcal{G}(\hat y_b^2)}+\epsilon},
\]

where \(\mathcal{G}\) is a fixed local averaging operator.

This may improve cross-scale comparability.

## 6.8 Structural-domain disagreement

Evaluate:

- gradient magnitude;
- Laplacian;
- Sobel edge maps;
- local SSIM distance;
- local NCC distance;
- wavelet high-frequency bands;
- low-frequency and high-frequency disagreement separately;
- fixed Gaussian-pyramid disagreement.

Do not introduce a large learned feature extractor unless it is pretrained, frozen, and clearly justified.

## 6.9 Hybrid scores

After screening atomic components, test only small interpretable hybrids:

\[
U=
w_1 U_{\text{intensity}}
+w_2 U_{\text{gradient}},
\]

or:

\[
U=
w_1 U_{\text{target deviation}}
+w_2 U_{\text{shared difficulty}}.
\]

Use nonnegative weights from a small predefined grid.

Do not fit a high-capacity supervised model on 22 or 24 cases.

Limit final hybrids to two or three components.

---

# 7. Explore Spatial and Examination-Level Aggregation

The current whole-foreground mean may dilute localized reconstruction failures.

For each voxel-level score, evaluate:

## Slice-level pooling

Compute one score per generated slice using:

- foreground mean;
- foreground median;
- 75th percentile;
- 90th percentile;
- 95th percentile;
- top 10% voxel mean;
- top 20% voxel mean.

## Examination-level pooling

Aggregate slice scores using:

- mean;
- median;
- maximum;
- 75th percentile;
- 90th percentile;
- mean of the worst two slices;
- mean of the worst 10% of generated slices;
- CVaR at 80%, 90%, and 95%.

The original mean remains a baseline.

Localized errors may be better detected by upper-tail or CVaR pooling.

Avoid testing an uncontrolled continuous range. Use a predefined discrete grid.

---

# 8. Explore Deployment-Compatible Masks

Evaluate:

- current 1% target mask;
- input-derived mask;
- committee-union mask;
- committee-median mask;
- observed-anchor propagated mask;
- soft foreground weights rather than a hard mask;
- edge-weighted foreground;
- central-brain region when a deployment-compatible brain mask exists.

When mask changes alter the ground-truth error support, do not make invalid paired claims against a different endpoint.

For score selection, either:

1. evaluate all methods against a fixed offline error support; or
2. report score-rank stability separately.

The preferred candidate should use a mask available at deployment.

---

# 9. Explore Committee-Selection Strategies

Do not evaluate only “full”, “neural”, and “analytical”.

Create a broad but structured committee candidate set.

## 9.1 Family-balanced committees

Select one or two members from distinct families:

- transformer;
- CNN;
- state-space or Mamba;
- implicit neural representation;
- GAN;
- diffusion;
- analytical interpolation.

## 9.2 Analytical-anchor committees

Test:

- Linear + Cubic + one neural peer;
- Linear + Cubic + two neural peers;
- one analytical + two architecture-diverse neural peers.

## 9.3 High-fidelity committees

Using development reconstruction metrics only:

- top two members;
- top three members;
- all members within a predefined MAE margin from the best.

Do not assume high fidelity always implies high committee value.

## 9.4 Accuracy–diversity Pareto committees

For each member, calculate on development data:

- reconstruction error rank;
- pairwise prediction-error correlation;
- pairwise output disagreement;
- architecture-family diversity;
- leave-one-member-out contribution to nAURC.

Construct a Pareto frontier over:

- accuracy;
- complementarity;
- runtime;
- committee size.

Do not reduce this to one unvalidated heuristic immediately.

## 9.5 Target-dependent committees

A target may benefit from peers with different error structures.

For each target model, select peers using development data only based on:

- low error correlation with the target;
- high complementary leave-one-out contribution;
- different architecture family;
- adequate reconstruction fidelity.

Freeze the target-specific committee before validation.

This is scientifically valid because the target model identity is known at deployment.

## 9.6 Scale-aware committees

The interpolation factor is known at deployment.

Test:

- one universal committee for all scales;
- one committee selected per scale using development data;
- a low-cost universal committee;
- a high-performance scale-conditioned committee.

For scale-conditioned selection:

- select ×2, ×4, and ×6 committees using development profiles;
- evaluate each on the corresponding NingXia scale;
- do not select a different committee for each validation dataset.

## 9.7 Weighted committees

Test robust weighted target-to-member aggregation.

Weights may be derived from development data using:

- inverse reconstruction MAE;
- normalized reconstruction rank;
- leave-one-out contribution;
- architecture-family balancing;
- error-correlation diversity;
- a convex combination of accuracy and diversity.

Normalize weights to sum to one.

Use a small predefined weighting family.

Do not optimize one free weight per member on 22 cases without strong regularization.

## 9.8 Low-cost committees

Construct candidates with:

- one neural peer + Linear + Cubic;
- two neural peers;
- two neural peers + one analytical reference;
- three total members;
- four total members.

Report the Pareto frontier of:

- nAURC;
- worst-profile nAURC;
- runtime;
- member count;
- storage.

---

# 10. Use the Reconstruction-Fidelity Table Properly

The reconstruction table should not merely remain a descriptive appendix.

Use its per-model results to define candidate roles and exploratory hypotheses.

Investigate:

1. Whether reconstruction quality predicts usefulness as a target.
2. Whether reconstruction quality predicts usefulness as a committee member.
3. Whether the strongest reconstructor is always the most useful peer.
4. Whether a moderate-fidelity but architecture-diverse member improves ranking.
5. Whether analytical methods remain useful because their errors differ from neural methods.
6. Whether a poor model harms an unweighted committee but helps after robust weighting.
7. Whether fidelity–diversity Pareto selection outperforms full membership.

Use the original per-case predictions, not only cohort-average metrics.

Do not choose members based on the final validation table.

---

# 11. Stage the Candidate Search Efficiently

The candidate space can become large. Use a staged search.

## Stage A: Atomic screening

Evaluate all atomic combinations of:

- score family;
- voxel domain;
- mask;
- slice pooling;
- examination pooling.

Use:

- development profiles only;
- cached voxel differences;
- 300 bootstrap replicates for screening;
- case Spearman and nAURC.

Retain approximately the top 20–30 candidates according to the selection criterion.

## Stage B: Committee search

For the retained score/aggregation candidates, evaluate:

- universal committees;
- family-balanced committees;
- target-dependent committees;
- scale-aware committees;
- weighted committees;
- low-cost committees.

Use:

- 1,000 bootstrap replicates;
- all development profiles;
- mean and worst-profile metrics.

Retain approximately 8–12 candidates.

## Stage C: Finalist selection

Re-evaluate the retained candidates using:

- 2,000 bootstrap replicates;
- full development profiles;
- stability analysis;
- runtime;
- committee size;
- paired comparisons.

Select:

1. one universal high-performance finalist;
2. one low-cost finalist;
3. optionally one scale-aware finalist.

Use the one-standard-error rule:

If a simpler candidate is within one bootstrap standard error of the best development candidate, prefer the simpler candidate.

## Stage D: Validation

Freeze:

- score formula;
- mask;
- pooling;
- committee identities;
- target eligibility;
- weights;
- scale-specific settings;
- random seed.

Then evaluate on validation profiles.

Do not revise the finalist after validation.

---

# 12. Define the Candidate Selection Objective

Do not select solely by the best mean nAURC on one profile.

For candidate \(c\), calculate:

- mean development nAURC;
- median development nAURC;
- worst-profile development nAURC;
- mean case Spearman;
- mean RRR50;
- bootstrap instability;
- committee size;
- runtime;
- missing-profile count.

Use a predefined composite selection score such as:

\[
J(c)
=
\operatorname{meanRank}(\text{nAURC})
+
0.5\,\operatorname{worstProfileRank}(\text{nAURC})
+
0.25\,\operatorname{instabilityRank}
+
0.10\,\operatorname{costRank}.
\]

Lower is better.

Alternatively select from the Pareto frontier of:

- mean nAURC;
- worst-profile nAURC;
- runtime;
- committee size.

Record the selected rule before validation.

Create:

`selection_protocol.yaml`

containing:

- development profiles;
- validation profiles;
- candidate families;
- screening metrics;
- selection objective;
- complexity penalty;
- finalist count;
- seeds;
- bootstrap counts.

---

# 13. Revisit Matched-Target Specificity More Constructively

Do not repeatedly apply the same raw score and conclude that target specificity is absent.

Evaluate matched-target specificity for:

1. raw target disagreement;
2. committee-normalized deviation;
3. within-case target-relative attribution;
4. robust within-case target z-score;
5. residualized target score;
6. combined shared-difficulty plus target-attribution score;
7. target-dependent committee;
8. all-output spread baseline.

For every candidate, calculate:

- matched correlation;
- mismatched correlation;
- matched advantage;
- paired 95% CI;
- diagonal row wins;
- top-1 highest-error-model identification;
- within-case model-ranking correlation.

Separate two claims:

## Examination-risk ranking

Does the method rank difficult examinations for one target model?

## Model attribution

Does the method identify which model is relatively worse within an examination?

The original score may perform strongly for the first and weakly for the second.

A two-component method may improve both without pretending they are the same task.

If target attribution remains weak after a genuine candidate search, do not hide it. Present the decomposition itself as an empirical finding:

- shared difficulty is highly observable;
- model-specific attribution requires relative normalization;
- consensus-based scoring is stronger for triage than for assigning blame to one model.

---

# 14. Explore Cross-Scale Consistency as an Additional Signal

Because ×2, ×4, and ×6 predictions exist, investigate whether overlapping generated locations provide a new ground-truth-free consistency signal.

For the same target architecture, identify voxel or slice locations reconstructed by more than one scale.

After exact spatial alignment, define cross-scale target consistency:

\[
C_m(i)
=
\operatorname{median}_{r\neq r'}
|\hat y_m^{(r)}(i)-\hat y_m^{(r')}(i)|.
\]

Only use locations that are genuinely synthesized under both compared configurations.

Test:

- cross-scale target consistency alone;
- cross-model disagreement alone;
- a hybrid of cross-scale and cross-model disagreement.

This is potentially more novel than another elementary aggregation rule.

Before using it:

1. verify that predictions share the same source volume and physical grid;
2. verify that overlapping slice positions are valid;
3. ensure that observed anchors are not incorrectly compared with generated slices;
4. define the deployment scenario clearly, since multiple scale-specific predictions are required.

Use it as an optional extended experiment unless it produces a strong and stable validation improvement.

---

# 15. Explore Pseudo-Holdout Anchor Consistency When Feasible

Investigate whether an observed-slice consistency signal can be obtained without the missing target.

Possible strategies:

- compare predicted anchor values with observed anchors if the model does not copy anchors by construction;
- pseudo-remove one observed anchor and reconstruct it;
- compare forward and backward interpolation consistency;
- compare independently reconstructed overlapping intervals.

This signal must not be included if it is trivial because the network directly copies observed anchors.

If pseudo-holdout inference is computationally practical, test it on a development subset and evaluate whether it complements committee disagreement.

Do not make it a required final method unless it can be applied consistently at deployment.

---

# 16. Candidate Registry and Transparent Pruning

Create:

`candidate_registry.csv`

Each row must include:

- candidate_id;
- score_family;
- domain;
- normalization;
- mask;
- voxel_pooling;
- slice_pooling;
- examination_pooling;
- committee_type;
- committee_members;
- target_model;
- scale_conditioning;
- weighting;
- development_profiles;
- validation_status;
- mean_dev_nAURC;
- worst_dev_nAURC;
- mean_dev_rho;
- validation_nAURC;
- validation_rho;
- runtime;
- committee_size;
- bootstrap_stability;
- selected_stage;
- exclusion_reason;
- source_commit;
- timestamp.

Use explicit exclusion reasons:

- `invalid_geometry`;
- `missing_required_profile`;
- `deployment_ground_truth_leakage`;
- `dominated_on_development`;
- `unstable_bootstrap`;
- `excessive_cost`;
- `redundant_definition`;
- `failed_validation`;
- `not_selected_by_frozen_rule`.

Candidates with `failed_validation` must not be retroactively replaced by a candidate selected after inspecting that validation result.

---

# 17. What May Be Omitted From the Regular Paper

The regular paper does not need to present every exploratory failure.

It may focus on:

- the frozen original baseline;
- the selected universal finalist;
- the selected low-cost or scale-aware finalist;
- one shared-spread baseline;
- one single-model baseline;
- the central validation results;
- the main failure boundary.

Move the following to the extended report:

- complete candidate leaderboard;
- all weak score variants;
- every committee subset;
- every mask;
- every pooling quantile;
- all target-specificity matrices;
- all model-bank fidelity results;
- all negative validation candidates;
- all secondary AUROC/AUPRC results.

The regular paper must still disclose:

1. how finalists were selected;
2. which profiles were used for development;
3. which profiles were used for validation;
4. whether validation performance was weaker than development;
5. whether the method was retrospectively selected;
6. all validation results for the selected finalists.

This is selective presentation, not selective reporting.

---

# 18. Desired Final Method Structure

Aim to produce a method with a clearer contribution than:

“Take the median absolute difference.”

A strong possible final structure is:

## Component 1: Shared examination difficulty

\[
d_j=\operatorname{median}_{m}s_{jm}.
\]

## Component 2: Target-relative deviation

\[
a_{jm}=
\frac{s_{jm}-\operatorname{median}_{k}s_{jk}}
{\operatorname{MAD}_{k}(s_{jk})+\epsilon}.
\]

## Component 3: Robust target risk

\[
r_{jm}
=
\alpha\,\operatorname{rank}(d_j)
+
(1-\alpha)\,\operatorname{rank}(a_{jm}).
\]

## Component 4: Selected heterogeneous committee

A development-selected, architecture-diverse committee with frozen identities.

This structure explicitly separates:

- “Is this examination difficult for most models?”
- “Is this named model unusually inconsistent on this examination?”

Do not force this exact design if another candidate validates better, but test it thoroughly.

---

# 19. Statistical Evaluation

For every finalist, report:

- foreground pixel Fisher-\(z\) correlation;
- case Spearman;
- Kendall tau;
- raw AURC;
- normalized AURC;
- RRR25;
- RRR50;
- RRR75;
- MAE50;
- 2,000-case bootstrap CI;
- paired \(\Delta\)nAURC against the frozen baseline;
- paired \(\Delta\)nAURC against all-output spread;
- paired \(\Delta\)nAURC against mean target difference;
- target-attribution matched advantage;
- runtime;
- committee size.

For development screening, fewer bootstrap samples are acceptable.

For finalists and validation, use the full bootstrap.

Use the same case-bootstrap identities for paired comparisons.

Do not claim equivalence when a CI includes zero.

Use:

- “no conclusive difference”;
- “within the resolution of this sample”;
- “validation did not establish superiority”.

---

# 20. Decide Whether a New Candidate Is Worth Publishing

A selected candidate should improve at least one important dimension without causing unacceptable degradation elsewhere.

Useful improvement patterns include:

## Performance improvement

- lower mean validation nAURC;
- better worst-profile validation nAURC;
- higher validation RRR50;
- stronger matched-target advantage.

## Robustness improvement

- less scale degradation;
- lower profile-to-profile variance;
- fewer catastrophic committee subsets;
- reduced dependence on intensity scale.

## Efficiency improvement

- similar nAURC with fewer models;
- lower CPU/GPU cost;
- fewer stored volumes.

## Conceptual improvement

- separates shared case difficulty and target attribution;
- adds cross-scale consistency;
- provides a stronger target-specific interpretation;
- produces a clearer deployment contract.

Do not require one candidate to win every metric.

Use Pareto-frontier reasoning.

---

# 21. Rewrite the Paper Around the Selected Finalists

Do not write the paper as a chronological record of every failed experiment.

Use the following narrative:

## Motivation

Average reconstruction metrics cannot identify examinations requiring review.

## Baseline insight

Cross-model disagreement provides a strong examination-level ranking signal.

## Limitation of the raw score

Raw disagreement mixes:

- shared examination difficulty;
- target-relative deviation.

## Proposed refinement

Introduce the selected robust score, decomposition, committee-selection rule, or cross-scale consistency component.

## Selection protocol

Explain that the method was selected on predefined development profiles from a registered candidate family.

## Validation

Report performance on NingXia ×2/×4/×6 and other held-out analyses.

## Findings

State whether the selected method improves:

- nAURC;
- worst-scale performance;
- target attribution;
- committee cost;
- cross-scale stability.

## Boundary

Common-mode errors remain undetectable.

This creates a stronger contribution than merely reporting dozens of unrelated ablations.

---

# 22. Regular-Paper Content Priorities

Maintain four pages of technical content plus one references page.

Recommended visual elements:

1. Compact method figure showing:
   - target;
   - committee;
   - shared difficulty;
   - target-relative deviation;
   - selective-review score.

2. Main validation table:
   - frozen baseline;
   - selected universal method;
   - selected low-cost or scale-aware method;
   - validation across ×2/×4/×6.

3. Cross-scale plot:
   - nAURC or RRR50 across scales.

4. One compact target-attribution or common-mode figure.

Move qualitative MRI cases to the extended report unless space remains.

Do not fill the regular paper with candidate-search details.

Use one short paragraph for the search protocol and place the full registry in the supplement.

---

# 23. Extended-Paper Content

The extended paper should include:

- complete model-bank audit;
- reconstruction-fidelity table;
- candidate funnel;
- atomic score sweep;
- spatial aggregation sweep;
- committee search;
- weighted committee results;
- scale-aware selection;
- universal versus profile-specific selection;
- matched-target matrices;
- cross-scale consistency;
- pseudo-anchor consistency if implemented;
- all finalist validation results;
- failed finalist results;
- full bootstrap comparisons;
- full cost Pareto frontier;
- qualitative examples;
- common-mode stress test;
- reproducibility details.

---

# 24. Required Deliverables

Create at least:

- `MODEL_BANK_AUDIT.md`;
- `model_bank_registry.csv`;
- `selection_protocol.yaml`;
- `candidate_registry.csv`;
- `candidate_screening_results.csv`;
- `committee_search_results.csv`;
- `score_search_results.csv`;
- `pooling_search_results.csv`;
- `finalist_development_results.csv`;
- `finalist_validation_results.csv`;
- `finalist_paired_bootstrap.csv`;
- `target_attribution_results.csv`;
- `cross_scale_consistency_results.csv`, if feasible;
- `pareto_frontier.csv`;
- `candidate_funnel.md`;
- `final_method_definition.md`;
- `paper_icassp_regular_optimized.tex`;
- `paper_icassp_regular_optimized.pdf`;
- `paper_extended_optimized.tex`;
- `paper_extended_optimized.pdf`;
- `revision_report_optimization.md`;
- `final_reviewer_simulation.md`;
- `unresolved_before_submission.md`;
- one complete ZIP package.

---

# 25. Acceptance Criteria

The work is complete only when:

1. More than one score family has been genuinely evaluated.
2. More than one committee-selection strategy has been evaluated.
3. Target and committee roles have been separated.
4. Weak reconstruction models are not automatically treated as main targets.
5. Additional models are retained only when they provide measurable value.
6. Candidate selection uses development profiles.
7. Finalists are frozen before validation.
8. Validation results are not used to replace a failed finalist.
9. Poor exploratory candidates are omitted from the regular paper but preserved in the registry.
10. The original frozen baseline remains visible.
11. The final method has a clearer technical contribution than a simple median difference.
12. The shared-difficulty versus target-attribution decomposition has been tested.
13. Cross-scale consistency has been assessed for feasibility.
14. Selected finalists have full paired bootstrap intervals.
15. The main validation includes NingXia ×2/×4/×6.
16. The regular paper remains four technical pages plus one references page.
17. The fifth page is filled with verified relevant references.
18. No Type 3 fonts are present.
19. No internal TODO or ethics placeholder appears in the PDF.
20. Every reported number is traceable to a CSV.
21. The final simulated novelty score is at least approximately 3.5/5.
22. The final simulated technical-quality score is at least approximately 4.2/5.
23. The final simulated overall score approaches 4/5.
24. Any remaining reason for a score below 4 is explicitly identified.

---

# 26. Final Reviewer Simulation

Simulate four reviewers.

## Reviewer A: ICASSP computational imaging

Focus on:

- algorithmic novelty;
- whether the method is more than a heuristic;
- cross-scale signal-processing contribution;
- committee design.

## Reviewer B: uncertainty and selective prediction

Focus on:

- target specificity;
- shared difficulty;
- calibration claims;
- paired risk–coverage evaluation;
- candidate-selection leakage.

## Reviewer C: medical imaging

Focus on:

- cohort validity;
- OOF NingXia predictions;
- deployment relevance;
- fidelity of selected target models;
- clinical overclaiming.

## Reviewer D: skeptical reproducibility reviewer

Focus on:

- whether candidates were cherry-picked;
- whether selection and validation are separated;
- whether negative results remain accessible;
- whether every number is reproducible.

For each reviewer, report:

- strengths;
- weaknesses;
- fatal concerns;
- novelty score;
- technical-quality score;
- significance score;
- clarity score;
- reproducibility score;
- overall score.

Continue revising until the principal remaining concern is the inherent simplicity or bounded clinical scope, rather than avoidable experimental design, weak model selection, poor presentation, or incomplete search.

---

# 27. Final Response Format

At completion, report:

1. Number of candidate methods evaluated.
2. Number of committee configurations evaluated.
3. Number of score and pooling variants evaluated.
4. Development profiles used.
5. Validation profiles used.
6. Target models selected and why.
7. Committee members selected and why.
8. Candidates excluded and the main exclusion reasons.
9. Frozen baseline performance.
10. Selected universal method performance.
11. Selected low-cost method performance.
12. Selected scale-aware method performance, if retained.
13. NingXia ×2/×4/×6 validation results.
14. Improvement in mean and worst-profile nAURC.
15. Improvement in RRR50.
16. Matched-target advantage before and after refinement.
17. Runtime and committee-size trade-off.
18. Whether cross-scale consistency was useful.
19. Whether any finalist failed validation.
20. Final paper title.
21. Final three contributions.
22. Final simulated ICASSP score.
23. Remaining three submission risks.
24. Reproduction command.
25. LaTeX compilation command.
26. Final ZIP path.

Begin by auditing the full model bank and building the candidate registry. Then implement the shared-difficulty/target-deviation decomposition and committee-normalized target score before expanding into weighted and scale-aware committees. Do not stop after the first negative result, and do not rewrite the claims until the structured candidate search and frozen validation are complete.