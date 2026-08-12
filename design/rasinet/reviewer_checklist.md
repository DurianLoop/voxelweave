# ICASSP 2027 Simulated Review Checklist

Review date: 2026-07-22. Scores reflect the completed registered run and final PDF inspection. Scale: 1 (poor) to 5 (excellent); overall recommendation follows strong reject / reject / borderline / weak accept / accept / strong accept.

## Reviewer A: Medical Imaging

### Major concerns

1. MAE and disagreement are not equivalent to diagnostic harm; there is no reader study or downstream task.
2. fastMRI-brain (24) and NingXia (22) are small, and NingXia must not be mislabeled as an independent external validation cohort.
3. The target-derived foreground may exclude tissue suppressed by the target itself.
4. T2 brain MRI at factor four is a narrow setting.
5. Clinical safety language and ethics provenance could be overstated or incomplete.

### Current response

- The abstract, Introduction, Discussion, Limitations, and Conclusion explicitly restrict claims to retrospective error ranking and selective review.
- The Experiments section identifies NingXia as an eight-fold held-out out-of-fold internal cohort.
- Mask sensitivity includes four target thresholds, committee union/intersection/median, and observed-input masks; ground-truth masks are offline only.
- All ten fixed profiles remain in the main table with bootstrap confidence intervals.
- The manuscript states that MAE is not diagnostic harm and that no clinical decision was made from the score.

### Residual risks

- No reader or lesion-preservation study can be added from current files.
- Dataset-specific ethics/access wording requires author confirmation before submission.
- No validated T1/FLAIR or non-brain committee output set is currently connected.

### Locations

- Regular: Experiments; Results and Discussion; Limitations; Compliance statement.
- Extended: Foreground aggregation; Cohorts and reconstructors; Mask sensitivity; Limitations.
- Evidence: `outputs/icassp_primary/summary.csv`, `input_manifest.csv`, and `paired_primary_comparisons.csv`.

### Final simulated score

| Dimension | Score |
|---|---:|
| Novelty | 3.0 |
| Technical quality | 4.0 |
| Significance | 3.0 |
| Clarity | 4.5 |
| Reproducibility | 4.5 |
| Overall | Borderline / weak accept |

## Reviewer B: Signal Processing / ICASSP

### Major concerns

1. Median cross-model disagreement is elementary and may look like standard ensemble spread applied to slice interpolation.
2. The paper needs a signal-processing interpretation, strong elementary baselines, and exact committee subset analysis.
3. Running multiple neural reconstructors may cost more than the quality-control benefit.
4. The main paper must satisfy the official 4+1 format without hidden margin or font changes.

### Current response

- The contribution is reframed as a target-specific reliability-ranking and selective-review protocol, not a new uncertainty estimator.
- The error decomposition `prediction = truth + shared error + member-specific error` exposes exact common-mode cancellation.
- Median, mean, maximum, trimmed mean, committee-mean/median distance, shared standard deviation, pairwise disagreement, analytical residuals, and gradient/Laplacian scores share one evaluator.
- Every legal committee subset is recomputed from voxel outputs; member removal is not approximated from pre-aggregated scores.
- Stored-output and online deployment scenarios are separated. Scoring runtime and bytes are measured; unavailable historical neural latency is not invented.
- The new regular paper uses official `spconf.sty` and `IEEEbib.bst`; no custom geometry or negative spacing is used.

### Residual risks

- The protocol remains incremental because simple target-specific variants perform similarly; the manuscript now reports this rather than claiming median as an algorithmic innovation.
- Complete online latency, peak GPU memory, and model parameter benchmarking are unavailable from comparable historical logs.
- Committee subset quality is strongly cohort dependent, so no universally minimal deployment committee can be claimed.

### Locations

- Regular: Introduction contributions; Method error decomposition; Experiments comparators; Results composition/cost.
- Extended: Score variants; Committee size/diversity; Shared-error stress test; Deployment cost.
- Evidence: `summary.csv`, `scoring_runtime.csv`, `figure_source_data/committee_size_aggregate.csv`.

### Final simulated score

| Dimension | Score |
|---|---:|
| Novelty | 2.5 |
| Technical quality | 4.5 |
| Significance | 3.5 |
| Clarity | 4.5 |
| Reproducibility | 5.0 |
| Overall | Weak accept |

## Reviewer C: Machine Learning / Uncertainty

### Major concerns

1. Heterogeneous reconstructors are not posterior samples, and disagreement is not calibrated uncertainty.
2. Shared and correlated errors can create false reassurance.
3. External test results may have been used to choose a score, mask, normalization, or committee.
4. Risk--coverage definitions, random/oracle normalization, and paired confidence intervals must be reproducible.
5. Mask variants change the definition of error and cannot be naively paired against the default endpoint.

### Current response

- Terminology is consistently `disagreement score`, `reliability ranking`, and `estimated reconstruction risk`; probability calibration is explicitly disclaimed.
- The common-mode error decomposition and controlled target-specific/shared corruption experiment state the identifiability boundary.
- The all-member median/raw/1% target-mask specification is frozen. All observed cohorts retain all fixed profiles, and variants are labeled retrospective sensitivity analyses.
- The evaluator emits raw/oracle/random AURC, nAURC, RRR25/50/75, absolute retained MAE, bootstrap samples, and risk curves.
- Paired score comparisons reuse resample indices. Mask variants are excluded from paired difference claims because their MAE support differs.
- Unit tests verify self-exclusion, no ground-truth score argument, oracle/random behavior, case-order invariance, and missing-case errors.

### Residual risks

- The shared-error stress test is synthetic and does not cover pathology removal or all common preprocessing failures.
- Committee members may share training data and architectural priors; a deployment diversity proxy cannot prove independent errors.
- Multiple exploratory comparisons are not presented as confirmatory significance tests; Holm-adjusted claims are intentionally avoided.

### Locations

- Regular: Method score/failure boundary/selective review; Experiments governance; Limitations.
- Extended: Related Work uncertainty/error prediction; Error decomposition; Governance/statistics; Stress test.
- Evidence: `shared_error_stress/summary.csv`, `bootstrap_samples.csv`, and `outputs/results_registry.csv`.

### Final simulated score

| Dimension | Score |
|---|---:|
| Novelty | 3.0 |
| Technical quality | 4.5 |
| Significance | 3.5 |
| Clarity | 4.5 |
| Reproducibility | 5.0 |
| Overall | Weak accept |

## Required Final Audit

- [x] Replaced provisional ranges and tables with full registered outputs.
- [x] Verified the 4+1 regular and 8+1 extended page split after final assets.
- [x] Confirmed no version-history wording, calibrated-probability claim, or clinical-safety claim remains; the statistical MAD term appears only in an explicit disambiguation sentence.
- [x] Confirmed all used citations resolve and bibliography metadata was checked against primary/publisher sources.
- [x] Confirmed no LaTeX errors, undefined references/citations, or overfull boxes.
- [x] Inspected every PDF page after raster rendering; vector plots remain legible and line styles distinguish curves without color alone.
- [x] Re-scored all reviewers after full experimental results.

## Aggregate decision

Simulated ICASSP recommendation: **weak accept, 3.5/5**. The strongest evidence is reproducible examination ranking and selective review across all fixed profiles with explicit common-mode failure analysis. The principal acceptance risk remains limited algorithmic novelty; medical breadth and comparable online neural cost are secondary concerns.
