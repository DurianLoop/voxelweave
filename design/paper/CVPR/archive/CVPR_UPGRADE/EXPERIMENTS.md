# CVPR Upgrade Experiment Registry

## C5-E001 — Manifest freeze

- Type: GOVERNANCE / CONFIRMATORY PREREQUISITE
- Script: `scripts/build_data_manifest.py`
- Output: `DATA_MANIFEST.csv`
- Rule: all subsequent scripts consume the manifest for cohort eligibility; no undocumented directory-order selection.
- Status: COMPLETE. Manifest contains 759 eligible model-factor rows spanning 161 case/series files and 147 patient clusters (24 fastMRI, 22 NingXia series/8 patients, 115 IXI).

## C5-E002 — Overlap/error-covariance chain

- Type: MECHANISTIC / RETROSPECTIVE
- Hypothesis: C5-H01
- Inputs: Plan-4 zero/maximal paired outputs plus dense targets for evaluation only.
- Prespecified endpoints: pixel error cosine, shared-energy fraction, observable-disagreement fraction, disagreement-error rho, stable-wrong prevalence.
- Independent unit: examination/patient cluster; 5,000 cluster bootstrap replicates.
- Result: the full predicted chain is supported in NingXia and IXI. The original reversal control increases covariance but reverses the cosine/shared/observable/disagreement arrows on fastMRI; it is retained as a confounded negative result. Exact energy-identity maximum residual `4.42e-10`.
- Status: COMPLETE.

## C5-E003 — Clean overlap-ladder feasibility and test

- Type: MECHANISTIC
- Hypothesis: C5-H02
- Constraint: same target/model/case/factor/measurement count/distance/mask/preprocessing. Invalid synthetic relocation is prohibited.
- Result: a strict multi-level ladder is geometrically infeasible under all fixed constraints. The clean horizontal-equivariance maximal-overlap control retains anchor identities, z ordering, distance, count, mask, and preprocessing; zero overlap ranks error better in all three cohorts, with cluster CIs excluding zero.
- Status: COMPLETE; see `OVERLAP_LADDER_FEASIBILITY.md` and clean-control outputs.

## C5-E004 — Prespecified budget-benefit curves

- Type: RETROSPECTIVE ACQUISITION SIMULATION
- Hypothesis: C5-H04
- Budgets: 10%, 20%, 30%, 50% (all reported).
- Baselines: random expectation, adjacent-anchor RMSE, ordinary PC, TTA, committee where compatible, maximal-shared score, oracle.
- Execution note: attempt 1 stopped before computation because the Plan-2 source root was resolved as `D:/MRI/rasinet` instead of `D:/MRI/design/rasinet`; no output was written. Path corrected without changing endpoints or budgets.
- Execution note: attempt 2 wrote the prespecified point curves but timed out during 5,000-replicate intervals because it concatenated pandas frames inside every replicate. No interval JSON was written or inspected. The identical cluster bootstrap was vectorized with NumPy indexing before rerun.
- Execution note: the first completed curve file used model-case rows as allocation units. Audit identified this as incompatible with the registered case/plane allocation question. It is superseded by examination/series-level curves that aggregate HAT/SwinIR scores before ranking; no budget or endpoint was changed.
- Result: phase-grid score is near oracle on fastMRI but not universally superior on NingXia, especially at low budgets. All budgets and patient-cluster intervals are retained.
- Status: COMPLETE.

## C5-E005 — IXI-T2 overlap replication

- Type: CROSS-COHORT REPLICATION / EXPLORATORY because IXI test outputs were previously inspected for other questions.
- Dataset: IXI-T2 x4 test-115, HAT and SwinIR frozen checkpoints.
- Protocol: identical C5-E002 covariance chain and C5-E003 clean flip control; no IXI-specific threshold or score tuning.
- Registration time: before IXI phase-grid/clean-control outputs were generated.
- Execution note: attempt 1 completed all 230 model-case inference loops but failed before writing outputs because the local prediction variable shadowed the parsed argument namespace (`AttributeError: ndarray has no attribute dataset`). No result was retained or inspected; the variable was renamed before the complete rerun.
- Result: IXI supports the covariance chain and clean-control ranking effect across 115 cases/two models; clean zero-minus-max rho `0.0949 [0.0783,0.1256]`.
- Status: COMPLETE.

## C5-E006 — Orthogonal two-component model

- Type: EXPLORATORY METHOD DERIVATION.
- Hypothesis: C5-H06.
- Train: the fixed 12-case fastMRI Plan-4 development split.
- Internal confirmation: the complementary 12 fastMRI cases.
- Frozen transfer: NingXia 22 series (8 patients) and IXI 115 cases, HAT/SwinIR x4.
- Signals: within-dataset/model percentile ranks of zero-overlap disagreement and pre-inference adjacent-anchor RMSE. Dense target enters only the development regression and evaluation endpoint.
- Model: first residualize input rank against disjoint rank on development data; then nonnegative least-squares error-rank regression on disjoint rank and the orthogonal residual. No grid search, cohort-specific weights, or post-result coefficient rescue.
- Primary gate: improve both mean per-model Spearman and nAURC on the fastMRI confirmation split.
- Registration time: before C5-E006 outputs were computed.
- Execution note: initial completed table omitted IXI transfer because the IXI feature file has no dataset column; the decision gate had already failed on fastMRI confirmation. The source was assigned its known manifest dataset and rerun only to complete the registered IXI transfer report; the rejected gate cannot be reversed by this repair.
- Result: primary gate failed; confirmation Spearman/nAURC were identical to the disjoint-only baseline. Decision: REJECT, with IXI transfer retained only as the registered completeness check.
- Status: COMPLETE / NEGATIVE.

## C5-E007 — Acquired-anchor bipartition witness

- Type: ACTIONABLE PROTOCOL / PILOT THEN FROZEN EXTENSION.
- Hypothesis: C5-H07.
- Pilot: lexicographically first 8 fastMRI manifest cases, HAT, x4 acquired anchors only.
- Context A: anchors z=0,8,16,...; context B: anchors z=4,12,20,... .
- Targets: z mod 8 in {2,6} that are covered by both contexts. At each target the two anchor-distance multisets are identical, order-swapped, and overlap is zero.
- Score: masked MAE between the two sub-context predictions; no dense target in the score.
- Endpoints: stored x4 plane MAE and realized stored x4-to-x2 case benefit.
- Pilot gate: benefit Spearman >0.5 and plane-error Spearman >0.
- Registration time: before any C5-E007 inference.
- Result: pilot passed; frozen HAT remainder, SwinIR fastMRI, both models on NingXia and IXI all positively ranked x4 error. Benefit association is positive for fastMRI and NingXia/HAT; NingXia/SwinIR interval crosses zero. IXI benefit is `NOT RUN`.
- Status: COMPLETE.

## C5-E008 — Analytical acquired-anchor bipartition

- Type: ANALYTICAL FAMILY CHECK / FROZEN EXTENSION.
- Hypothesis: C5-H09.
- Cohorts: all eligible x4 fastMRI, NingXia, and IXI cases in `DATA_MANIFEST.csv`; one row per examination/series, with NingXia resampled by patient cluster.
- Contexts: the same even/odd x4-anchor bipartition as C5-E007, but with two-point linear interpolation rather than a learned model.
- Score: median masked MAE between the two sub-lattice reconstructions over jointly bracketed targets; dense targets are used only for evaluation.
- Endpoints: x4 reconstruction error in all cohorts and stored x4-to-x2 benefit for fastMRI/NingXia; 5,000 cluster-bootstrap replicates for Spearman intervals.
- Registration time: after C5-E007 neural pilot/fastMRI confirmation passed, before C5-E008 outputs were computed and while the frozen neural cross-cohort extension was still running.
- Execution note: the first full run completed and wrote all 322 model-case rows, then exceeded the 120-second cap during a pandas-concatenation bootstrap. The same 5,000-replicate cluster bootstrap was vectorized and run summary-only; endpoints were unchanged.
- Result: analytical score vs x4 error rho: fastMRI `0.8870 [0.7356,0.9422]`, IXI `0.9620 [0.9358,0.9754]`, NingXia `0.8238 [0.2522,0.9792]`. Benefit rho: fastMRI `0.7245 [0.4548,0.8439]`, NingXia `0.5979 [0.1520,0.7709]`.
- Status: COMPLETE.

## C5-E009 — Deployable bipartition budget curves

- Type: RETROSPECTIVE ACQUISITION SIMULATION / FROZEN FOLLOW-UP.
- Hypothesis: C5-H10.
- Inputs: C5-E008 per-case score and the same stored x4-to-x2 benefits, examination aggregation, budgets, random expectation, oracle definition, and 5,000 patient-cluster bootstrap used by C5-E004.
- Comparators: C5-E004 phase-grid score, maximal-shared score, PC, TTA, committee, and adjacent-anchor RMSE.
- Registration time: after C5-E008 associations were computed, before its budget curve was computed.
- Result: better than random at every fastMRI budget and NingXia 20/30/50%; NingXia 10% CI crosses zero. The policy matches the best existing result at several fastMRI budgets but is not universally best in NingXia.
- Status: COMPLETE.

## C5-E010 — Clean-overlap stable-wrong prevalence

- Type: MECHANISTIC ENDPOINT COMPLETION.
- Hypothesis: C5-H11.
- Inputs: paired zero-overlap C5-E002 rows and clean maximal-overlap C5-E003 rows.
- Registration time: after the Plan5 reproducibility audit identified that C5-E002 had not separately summarized this prespecified endpoint, before any prevalence result was computed.
- Result: zero-overlap prevalence was `0` under its own fixed joint-quartile definition; clean maximal overlap prevalence was fastMRI `0.2708 [0.1198,0.4375]`, IXI `0.2087 [0.1563,0.2623]`, and NingXia `0.2823 [0.1083,0.4390]` (paired cluster intervals on the prevalence increase).
- Status: COMPLETE.

## C5-E011 — Acquired-anchor cross-validation

- Type: MECHANISM-DERIVED DEPLOYABLE METHOD / FROZEN EVALUATION.
- Hypothesis: C5-H12.
- Cohorts: all x4 fastMRI, NingXia, and IXI cases/models in `DATA_MANIFEST.csv`.
- Available information: simulated acquired slices at z multiples of four only. Dense unacquired planes and target errors are evaluation-only.
- Estimator: linear midpoint prediction of each withheld interior acquired anchor from its two neighboring acquired anchors; masked MAE to the withheld acquired anchor.
- Comparators: adjacent-anchor RMSE, C5-E008 analytical bipartition, original phase-grid score, maximal-shared, PC, TTA, committee, random, and oracle where endpoints exist.
- Inference: examination-level or NingXia patient-cluster bootstrap, 5,000 replicates.
- Registration time: before any C5-E011 score or endpoint association was computed.
- Result: x4-error rho was fastMRI `0.937 [0.816,0.975]`, IXI `0.955 [0.926,0.972]`, and NingXia `0.955 [0.747,0.980]`. Benefit rho was fastMRI `0.799 [0.605,0.899]` and NingXia `0.615 [0.159,0.807]`. It significantly exceeded adjacent-anchor RMSE for fastMRI error and benefit, and analytical bipartition for fastMRI benefit. Within-case plane localization failed on fastMRI (median rho `-0.264`), limiting the method to examination-level triage.
- Status: COMPLETE.

## C5-E012 — Four-anchor exact overlap ladder

- Type: CLEAN MECHANISTIC DOSE RESPONSE / ANALYTICAL.
- Hypothesis: C5-H13.
- Cohorts: one manifest row per fastMRI, NingXia, and IXI examination/series; model outputs are not used.
- Independent unit: examination or NingXia patient cluster. Plane statistics are descriptive; monotonic endpoint intervals use 5,000 cluster bootstrap replicates.
- Primary endpoints: error cosine, shared/observable energy fraction, disagreement MAE, and disagreement-versus-pair-error Spearman at overlap 0/1/2/3; overlap 4 is the exact identical-context boundary.
- Registration time: before any C5-E012 output was computed.
- Execution note: the first run processed all fastMRI cases and part of IXI but reached the 120-second command cap before writing any output. The experiment was restarted from the unchanged manifest with a longer runtime allowance; geometry, endpoints, and inference were unchanged.
- Result: the wide ladder was evaluable in IXI 115 and NingXia 18/22 series but not shallow fastMRI. NingXia was strictly monotone; IXI had a 0-to-1 reversal but overall signed endpoint trends were `|rho|=0.9`. Raw overlap count was therefore not accepted as a sufficient dose.
- Status: COMPLETE / PARTIAL FALSIFICATION.

## C5-E013 — Compact exact overlap ladder

- Type: ELIGIBILITY-DRIVEN REPLICATION / EXPLORATORY.
- Hypothesis: C5-H14.
- Distance multiset: `{1,2,3,4}`; all other C5-E012 definitions unchanged.
- Registration time: after C5-E012 showed that the wide window excludes fastMRI and four NingXia series, before C5-E013 computation.
- Result: all fastMRI 24, IXI 115, and NingXia 22 cases/series were eligible. Overall error-cosine/shared-fraction trends were `+0.9`, observable-fraction trends `-0.9`, and disagreement trends `-0.9/-0.9/-1.0`; every cohort retained the 0-to-1 exception. Reliability rho remained `0.958–0.992` across nonidentical levels rather than decreasing monotonically.
- Status: COMPLETE / NONMONOTONE.

## C5-E014 — Shared-influence mechanism

- Type: MECHANISM REFINEMENT AFTER A PRESERVED FALSIFICATION.
- Hypothesis: C5-H15.
- Configurations: all 14 valid compact four-anchor sign configurations, including the identical reference; no selection by observed image result.
- Outputs: case-by-configuration means, acquisition-only coefficient similarity, and cohort-level rank associations with error alignment/observability.
- Inference: 5,000 case/patient-cluster bootstrap replicates for the difference between influence-based and count-based absolute rank association.
- Registration time: after observing C5-E012/E013 nonmonotonicity, before computing coefficient similarities or configuration-specific image metrics.
- Result: coefficient common-absolute-mass association with error alignment was fastMRI `0.815`, IXI `0.789`, NingXia `0.855`, versus raw-count `0.503`, `0.466`, `0.630`. Its associations with disagreement were `-0.833`, `-0.811`, `-0.842`. Across every endpoint and cohort, the 5,000-cluster-bootstrap interval for the absolute-rho advantage over count was above zero (`0.189–0.283`).
- Status: COMPLETE / SUPPORTED.
