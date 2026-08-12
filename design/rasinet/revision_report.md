# ICASSP 2027 Revision Report

Updated: 2026-07-22. The registered P0/P1 run, stress test, asset generation, validation, and final compilation are complete.

| Before revision | Actual modification | Files | Supporting evidence | Status | Expected submission impact |
|---|---|---|---|---|---|
| Main draft used a custom `article` geometry and occupied six technical pages | Created separate regular and extended sources using official ICASSP `spconf` and `IEEEbib`; original `main.tex` is untouched | `paper/paper_icassp_regular.tex`, `paper/paper_icassp_extended.tex`, `paper/spconf.sty`, `paper/IEEEbib.bst` | Final PDFs are 4+1 and 8+1 pages with clean error/reference/overfull checks | Complete | Removes a desk-reject formatting risk |
| Score was incorrectly called median absolute deviation / MAD | Renamed throughout new manuscripts and code as median target-to-committee disagreement or median target-to-member absolute difference | Both new TeX files; `icassp_scores.py` | Formula and tests | Complete | Removes a statistical terminology error |
| Contribution resembled a simple uncertainty estimator | Reframed as target-specific reliability ranking and selective-review protocol; clinical/probability claims removed | Title, abstract, Introduction, Discussion, Conclusion | Reviewer checklist | Complete in drafts | Makes the contribution defensible even if mean and median are similar |
| Target exclusion relied partly on NumPy object identity | Added explicit target-name exclusion and tests | `icassp_scores.py`, `tests/test_rasinet_icassp_scores.py` | 19/19 tests pass | Complete | Prevents self-committee leakage |
| Scoring/evaluation separation was implicit | Score and mask APIs have no ground-truth parameter; evaluator loads ground truth only for offline metrics | `icassp_scores.py`, `run_reliability_evaluation.py` | API inspection and unit test | Complete | Strengthens the ground-truth-free claim |
| No complete input-integrity checks | Added exact case-set, duplicate, missing, finite, shape, affine, orientation, and generated-slice validation | `run_reliability_evaluation.py` | Two-case real smoke; full run checkpoints | Implemented, full validation running | Reduces silent case/geometry mismatch risk |
| Only median/shared-std/linear/cubic proxies existed | Added mean, max, trimmed mean, committee-mean/median distance, pairwise mean/median, combined analytical residuals, gradient, and Laplacian variants | `icassp_scores.py`, primary YAML | Full `summary.csv` and paired comparisons | Complete | Directly addresses the simple-baseline critique |
| No intensity-normalization analysis | Added raw, p1--p99, median/IQR, and min--max prediction-only normalization | `icassp_scores.py`, primary YAML | Full normalization summaries and stability CSV | Complete | Shows independent normalization can destroy useful ranking |
| Foreground was one target threshold | Added 0.5/1/2/5% target masks, committee union/intersection/median, observed-input, and offline ground-truth masks | `icassp_scores.py`, primary YAML | Full mask summaries and stability CSV | Complete | Exposes target-mask omissions and background sensitivity |
| Leave-one-out used pre-aggregated scores | Enumerates every legal nonempty committee subset and recomputes voxel scores | `run_reliability_evaluation.py` | Full subset rows and committee-size CSV | Complete | Supports minimum-committee and redundancy analysis |
| Pixel correlation was averaged arithmetically | Added Fisher-z mean plus median/IQR; kept arithmetic mean as sensitivity | `icassp_statistics.py` | Smoke `summary.csv` | Complete in pipeline | Provides statistically appropriate aggregation |
| Ranking lacked Kendall and persisted bootstrap samples | Added Kendall tau, 2,000-replicate paired case bootstrap, bootstrap CSV, CIs, RRR25/50/75, and absolute retained MAE | `icassp_statistics.py`, runner | 504 full summaries and saved bootstrap samples | Complete | Improves statistical completeness and traceability |
| Mask variants were naively comparable under changed MAE supports | Excluded mask changes from paired endpoint-difference claims; retained their own point/CI sensitivity results | `run_reliability_evaluation.py` | Code audit | Complete | Avoids an invalid paired comparison |
| Shared-error limitation had no derivation or experiment | Added common-mode cancellation derivation and deterministic target-specific/shared corruption experiment over 20 fixed IXI cases and four targets | Both manuscripts; `shared_error_stress_test.py` | `outputs/shared_error_stress/summary.csv`: at maximum strength MAE rose 14.9%, target-specific disagreement rose 28.6%, and shared-error disagreement changed 0.0% | Complete | Turns a limitation into an explicit identifiability result |
| TTA used an older all-pixel, within-case risk protocol | Re-evaluated all 24 stored fastMRI SwinIR TTA variance maps with the same target mask, examination score, case-level risk--coverage, and 2,000 bootstrap replicates | `evaluate_tta_maps.py`, `configs/tta_fastmri.yaml` | Unified output and paired CI | Complete | Adds a strong single-model baseline without unfair cross-target averaging |
| Cost wording was qualitative | Runner records bytes and per-spec scoring time; fixed 30-examination benchmarks measure analytical interpolation and complete stored-output audit; manuscripts separate stored-output audit from online inference | Cost scripts; both manuscripts | Stored audit 1.184 s mean/2.872 s p95, 0.89 GiB observed RSS; analytical CSVs | Complete for post-hoc scenario; hardware-matched online neural benchmark remains unavailable | Prevents unsupported “almost free” wording |
| Tables were manually copied | Added CSV-to-LaTeX/figure generator and result macros used by both papers | `icassp_paper_assets.py`, `tables_icassp/`, `figures_icassp/` | Final assets regenerated from full CSV | Complete | Eliminates regular/extended numerical drift |
| No formal result governance | Added frozen primary specification, YAML configs, seed, partial checkpoints, and results registry schema | `configs/`, `outputs/results_registry.csv`, runner | Config and registry header | Complete in pipeline; registry fills at full completion | Limits test-set selection bias |
| Bibliography was narrow | Added verified selective-classification, learned MRI error prediction, deep-ensemble MRI uncertainty, and no-reference MRI IQA sources | `paper/references.bib` | Publisher/JMLR/MICCAI metadata audit | Complete for current citations | Improves positioning and avoids fictitious references |
| NingXia was ambiguously “external cross-validation” | Defined it as an eight-fold held-out out-of-fold internal cohort | Both new manuscripts | Fold directory and manifest audit | Complete | Removes a validation-design overclaim |
| No reviewer-facing risk audit | Added three simulated reviewer profiles with concerns, responses, residual risks, locations, and final scores | `reviewer_checklist.md` | Full-output and PDF inspection | Complete | Makes remaining weaknesses explicit |
| Reproduction required several ad hoc commands | Added one YAML entry point, requirements, README, shell orchestrator, tests, and output contract | `README_REPRODUCE.md`, `requirements.txt`, `reproduce_all.sh`, configs | Full run, validator, and 19 tests | Complete | Raises reproducibility |

## Real Runs So Far

1. Unit tests: 19 tests passed in the MRI conda environment, including deployment rejection of the offline ground-truth mask and failure-metric checks.
2. Real IXI smoke: two sorted examinations, all configured smoke variants; 64 per-case rows and 32 summary groups in the original smoke configuration.
3. Primary-score equivalence: maximum absolute difference against the prior evaluator was zero for examination score, foreground MAE, foreground pixel correlation, and all-generated-pixel correlation on both smoke cases.
4. Shared-error stress test: 20 fixed IXI examinations, four target models, two corruption modes, and five strengths completed; all reported values are generated from saved CSV files.
5. Unified TTA evaluation: all 24 fastMRI-brain SwinIR maps completed with 2,000 bootstrap replicates and a paired comparison against the primary score.
6. Analytical cost benchmark: fixed first 10 examinations per cohort completed for linear and cubic CPU interpolation, excluding NIfTI I/O.
7. Full P0/P1 evaluation: completed for 161 examinations, 33,672 rows, 504 groups, and 2,000 bootstrap replicates; validator passed with 5,631 registry rows.
8. LaTeX: regular is 5 total pages (4 technical + references/compliance); extended is 9 total pages (8 technical + references/compliance). Every page was rendered and inspected.

## Final Empirical Findings

- The pre-specified score yields foreground pixel $r_z=0.277$--$0.520$, examination Spearman $\rho=0.890$--$0.966$, nAURC 0.024--0.092, and RRR50 19.3--52.1% over all ten fixed profiles.
- Median is not a universal algorithmic winner. Mean and shared/pairwise spread are often similar; NingXia favors analytical/shared scores, while IXI favors the median at cohort-mean level.
- Committee composition is not portable: neural peers are strongest on IXI/fastMRI-brain, whereas analytical-only is strongest on NingXia. No no-reference diversity proxy safely selects a universal compact subset.
- Independent per-output normalization sharply degrades ranking; input/committee mask choices are much more stable, with threshold sensitivity concentrated on fastMRI-brain.
- At maximum stress strength, target MAE rises 14.9%; target-specific disagreement rises 28.6%, whereas shared corruption raises committee MAE 11.8% but changes disagreement by 0.0%.
- Stored-output audit costs 1.184 s mean/2.872 s p95 per examination on CPU. Comparable online neural inference cost remains unresolved.

## Title Audit

Five scoped candidates were compared:

1. **Target-to-Committee Disagreement for Ground-Truth-Free Reliability Ranking of MRI Slice Interpolation**: selected; names the target-specific operation and ranking claim directly.
2. **Ground-Truth-Free Reliability Ranking of MRI Slice Interpolation via Heterogeneous Model Disagreement**: clear but less explicit about self-exclusion.
3. **Selective Review of MRI Slice Interpolation Using Target-Specific Reconstructor Disagreement**: strongest workflow emphasis, but omits the ground-truth-free property.
4. **When MRI Interpolators Disagree: Target-Specific Reliability Ranking without Ground Truth**: readable but slightly less conventional for ICASSP indexing.
5. **Heterogeneous Reconstructor Disagreement for Quality Control of MRI Slice Interpolation**: concise, but `quality control` could imply broader clinical validation.

The selected title avoids `uncertainty`, does not imply safety or calibration, and matches the target-specific signal-processing formulation.

## Failed or Superseded Runs

- The first one-case smoke reached the bootstrap guard requiring at least two cases. The config was corrected to two cases; no one-case statistic was registered.
- The first full evaluator recomputed complete 3-D arrays and had no checkpoint. It was stopped after seven cases before writing result files. The replacement evaluates non-structural scores only on generated slices, preserves full z neighborhoods for structural scores, appends per-case checkpoints, and reproduces the default score exactly.
- Initial MiKTeX compilation was blocked by an optional missing `hycolor.sty` dependency from `hyperref`. `hyperref` was removed; it is not needed for ICASSP formatting or content.

## Still Open

See `unresolved_todos.md`. The remaining submission-critical author action is the NingXia ethics/access and funding wording; the 2027 template must replace the provisional official 2026 style when released. Comparable online neural latency/GPU memory and broader factor/contrast evidence remain desirable but are not represented as completed.
