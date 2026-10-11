# Plan6 Hypotheses and Experiment Registry

Registration date: 2026-08-13. No Plan6 endpoint below had been computed when its rule was written.

## Coverage invariant

Default confirmation coverage is fastMRI + IXI + NingXia. When an endpoint is structurally unavailable in one cohort, the only permitted two-dataset pair is IXI + fastMRI. Deviations are feasibility records, not confirmation.

## P6-H01 / P6-E01 — Multi-endpoint metric robustness

- Claim: measurement-disjoint disagreement identifies broadly poor reconstruction rather than only MAE.
- Competing explanation: association is induced by the exact intensity-domain endpoint used to define the score.
- Test: paired MAE, RMSE/MSE, SSIM-derived error, gradient MAE, Gaussian low-pass MAE and residual high-frequency MAE under the same physical planes and clustered units.
- Confirmation: error-ranking direction favors disjoint over shared contexts for a majority of justified endpoints in every eligible cohort; disagreements are reported without endpoint selection.
- Falsifier: direction depends on MAE or reverses systematically for structural/frequency endpoints.
- Result: **CONFIRMED UNDER THE REGISTERED MAJORITY RULE, WITH A STRUCTURAL-METRIC BOUNDARY.** Three physical planes per case, all three cohorts, HAT/SwinIR, and seven endpoints yielded positive disjoint-minus-shared ranking differences in all 42 strata. MAE/RMSE/MSE/low-frequency differences were stable across all cohorts and models; all seven IXI intervals excluded zero. SSIM error had weak or negative absolute ranking on fastMRI/NingXia and its improvement intervals crossed zero there; some gradient/high-frequency intervals also crossed zero in smaller strata. Measurement disjointness exposes broadly poor reconstruction, but pixelwise disagreement is not a universal surrogate for structural similarity.
- Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e01_metric_robustness*`.

## P6-H02 / P6-E02 — Consensus-error distributions and failure

- Claim: high shared fraction predicts small observable disagreement and stable-wrong failure across examinations.
- Test: full distributions of total/shared/observable energy, error cosine and disagreement by dataset/model/factor; clustered association with ranking residual and stable-wrong prevalence.
- Falsifier: shared fraction is unrelated to disagreement suppression after controlling error magnitude.
- Result: **CONFIRMED FOR DISAGREEMENT SUPPRESSION; STABLE-WRONG IS REAL BUT RARE UNDER A STRICT PLANE DEFINITION.** Across all three cohorts, two architectures, and both disjoint/max-shared conditions, shared fraction retained a strong negative partial association with disagreement normalized by RMSE after controlling total error and examination (`rho=-0.746` to `-0.975`). With pooled within-dataset/model thresholds (top-quartile plane MAE and bottom-quartile disagreement), disjoint contexts had zero stable-wrong planes; max-shared contexts had `0–0.32%` prevalence in fastMRI/IXI and `2.42–3.23%` in NingXia. NingXia intervals were wide under eight-patient clustering. The failure is mechanistically coherent but should not be presented as a high-prevalence clinical event.
- Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e02_*` and `figures/p6_e02_consensus_distributions.pdf`.

## P6-H03 / P6-E03 — Geometry and normalization operating range

- Claim: the main overlap contrast survives reasonable affine/tolerance and fair common-scale normalization perturbations but not arbitrary independent rescaling.
- Test: registered tolerances and raw/pooled/independent normalization strategies, all cohorts when eligible.
- Falsifier: sign or material effect disappears under small legitimate perturbations.
- Result: **CONFIRMED WITH AN INTENSITY-CALIBRATION BOUNDARY.** Across 322 x4 HAT/SwinIR outputs, all three cohorts had identical prediction/target shapes, orientations and affines; corresponding physical planes matched at 100% for every tolerance from `1e-6` to `0.1` mm. Re-expressing both predictions and target under one shared per-case robust scale preserved positive disjoint-minus-shared reliability differences in all six dataset–architecture strata (`0.121–0.700`). It did not preserve examination ranks on IXI/NingXia, showing that raw dynamic range is part of absolute-error triage. Independent output normalization changed ranks further and is invalid for calibrated cross-output discrepancy. The valid operating range is raw common scale or one explicitly shared case transform, never separate output transforms.
- Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e03_*` and `figures/p6_e03_intensity_audit.pdf`.

## P6-H04 / P6-E04 — Neural shared influence

- Claim: a fixed finite-difference approximation of shared neural measurement influence explains error alignment and observable fraction beyond integer anchor overlap.
- Approximation: for a physical anchor shared by two target-preserving contexts, apply the same seeded Rademacher perturbation at 1% of the case robust range; compute centered output-response vectors for HAT and SwinIR; aggregate common response dot/cosine and norm overlap across shared anchors. Four frozen seeds are averaged.
- Minimal discriminative contexts: one central eligible plane per examination; reference offsets `(-2,+2)` and eight comparators `(-2,+2), (-2,+1), (-2,+3), (-1,+2), (-3,+2), (-1,+1), (-1,+3), (-3,+1), (-3,+3)`. Input count, target, model, mask and preprocessing are fixed. Span/asymmetry vary and are recorded explicitly; they are not claimed to be a distance-matched overlap ladder.
- Perturbation: four fixed seeds (`6101–6104`), centered Rademacher fields at 1% of the globally normalized case range; anchor perturbations are run separately and response-vector inner products are averaged across seeds.
- Stage gate: run the central-plane design in all three cohorts and both architectures. Expand to three planes per examination only if neural influence has the expected endpoint direction in every cohort and improves association over overlap count in at least two cohorts without a sign reversal in the third.
- Test coverage: all three cohorts and both architectures; clustered inference by examination/patient.
- Falsifier: neural influence does not improve absolute association with error cosine/observable fraction over overlap count, or directions disagree across cohorts.
- Result: **CONFIRMED FOR THE THREE PRIMARY ALIGNMENT/DECOMPOSITION ENDPOINTS.** The stage gate passed in every cohort and architecture, so the registered three-plane confirmation was run on fastMRI (24 examinations/72 planes), IXI (115/345), and NingXia (22 series/66 planes; eight patient clusters). Across all six dataset–architecture strata, neural-influence cosine improved absolute Spearman association over overlap count for error cosine, shared fraction, and observable fraction; all 18 cluster-bootstrap 95% intervals excluded zero. Improvements ranged `0.036–0.089`. Rank-residual correlations of neural influence after controlling overlap, span, asymmetry, and examination remained `|rho|=0.185–0.395`. Disagreement MAE improved in all strata, but both fastMRI intervals crossed zero, so it remains supporting rather than confirmatory evidence.
- Boundary: the comparator grid intentionally varies span/asymmetry. The controlled analysis reduces but does not eliminate all perturbation/model nonlinearities; the result supports a neural influence descriptor beyond integer overlap, not a causal statement that influence alone determines error dependence.
- Cleaner fixed-count result: restricting to the four contexts with exactly one shared anchor held integer overlap constant. After controlling span, asymmetry and examination, neural influence retained the expected association for every endpoint/model on fastMRI and IXI (`|rho|=0.135–0.587`, clustered intervals excluding zero). NingXia estimates were near zero or directionally mixed and all intervals crossed zero. Thus continuous influence beyond count is supported in the two larger cohorts, not universal across the eight-patient external cohort.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_neural_shared_influence_confirm3*` and `CVPR/CVPR_UPGRADE/PAPER/figures/plan6_neural_influence_forest.pdf`.

## P6-H05 / P6-E05 — Full mechanism chain

- Claim: shared influence is associated with alignment; alignment suppresses disagreement conditional on error energy; suppression reduces error-ranking quality.
- Test: report each arrow separately, cluster bootstrap CIs, dataset/architecture heterogeneity, and descriptive mediation-style decompositions without causal mediation wording.
- Falsifier: any central arrow changes sign in multiple cohorts or disappears after its necessary conditioning variable.
- Result: **PARTIALLY CONFIRMED.** In all six dataset–architecture strata, shared influence associated with error alignment after examination and geometry control (`rho=0.219–0.410`), alignment associated with suppressed normalized disagreement conditional on influence and geometry (`rho=-0.933` to `-0.889`), and influence associated with lower observable fraction (`rho=-0.412` to `-0.211`); every cluster-bootstrap interval excluded zero. At the context level, greater alignment predicted poorer disagreement–error ranking in all strata, but the interval excluded zero only for IXI (both models) and NingXia HAT. Influence-to-ranking was still less stable. Thus the local mechanism chain is supported, whereas the final ranking consequence remains context-limited descriptive evidence rather than a universal causal chain.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_mechanism_chain*`.

## P6-H06 / P6-E06 — Anchor-CV strong-baseline and explanation audit

- Claim: ANCHOR_CV_V1 contains information beyond direct adjacent-anchor difference, intensity range, spacing, curvature and spectral content.
- Test: Spearman/Kendall/nAURC/risk curves; paired cluster deltas; partial correlations and variance decomposition; no tuned combination unless trained on a separately declared development set.
- Falsifier: Anchor-CV advantage vanishes after scale/spacing/direct-difference control or a trivial baseline dominates consistently.
- Result: **FALSIFIED AS AN INDEPENDENT-INFORMATION CLAIM.** Error ranking remained very strong (`rho=0.943/0.955/0.958` on fastMRI/IXI/NingXia), but adjacent MAE/RMSE were statistically indistinguishable and adjacent MAE was slightly higher on IXI/NingXia. Partial rank association given adjacent MAE, robust intensity range and spacing was `0.333/-0.059/-0.100`. Scale normalization sharply reduced or reversed ranking. Anchor-CV V1 is retained as an interpretable acquired-data difficulty score, not claimed to contain unique information beyond direct anchor change.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_anchor_cv_explanation*`.

## P6-H07 / P6-E07 — Frozen allocation confirmation

- Claim: ANCHOR_CV_V1 improves retrospective resource allocation above random across fixed budgets, but not necessarily every cohort/budget.
- Test: 10/20/30/50% with absolute gain, oracle-normalized gain and cluster CIs; all valid baselines.
- Falsifier: no dataset has a positive clustered gain at any prespecified budget.
- Result to date: **x4 TRIAGE CONFIRMED, SUPERIORITY REJECTED; x4→x2 CONFIRMATION BLOCKED BY IXI.** Full frozen risk–coverage curves across fastMRI, IXI and NingXia show strong risk stratification, but Anchor-CV was not the best nAURC method: output PC was better on fastMRI/IXI, while adjacent MAE was better on NingXia. The result is a frozen reanalysis of development cohorts, not independent external confirmation. Actual densification-benefit confirmation cannot satisfy the coverage invariant because IXI x2 checkpoints exist but all 115 definition-matched inference outputs remain absent; fastMRI+NingXia alone is prohibited as the two-dataset Plan6 pair.
- Updated result: **x4 TRIAGE CONFIRMED, SUPERIORITY REJECTED; x4→x2 CONSEQUENCE CONFIRMED ON THE PERMITTED IXI+fastMRI PAIR.** After freezing checkpoint, endpoint and budgets before any IXI x2 test output, 115 definition-matched IXI x2 reconstructions were generated. Anchor-CV versus benefit Spearman was `0.948` on IXI and `0.871` on fastMRI; adjacent MAE was `0.950/0.846` and output PC `0.970/0.843`. At 10/20/30/50% budgets, all three frozen policies had positive cluster-bootstrap gain above random. IXI Anchor-CV oracle-normalized gain was `0.920/0.936/0.972/0.973`. Anchor-CV therefore predicts retrospective densification benefit, but does not dominate strong baselines.
- Boundary: IXI benefit compares the existing mean HAT/SwinIR x4 error with frozen I3Net x2 error. It is a cross-estimator case-level consequence test, not a same-model causal treatment effect or prospective acquisition policy.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_frozen_risk_coverage*` and `PAPER/figures/plan6_frozen_risk_coverage.pdf`.

## P6-H08 / P6-E08 — Architecture-independent difficulty

- Claim: examination identity explains substantial error variance across architectures/factors, and acquired-data variables explain a nontrivial part of that case effect.
- Test: hierarchical variance decomposition and leave-one-cluster-out prediction with Anchor-CV, spacing, anchor change, curvature and spectral features.
- Falsifier: architecture/factor interactions dominate and acquired-data variables add no held-out explanation.
- Result: **CONFIRMED AT x4, WITH A NEGATIVE FEATURE-STACKING RESULT.** HAT–SwinIR case-error ranks were `0.989/1.000/0.997` on fastMRI/IXI/NingXia, and examination identity accounted for `99.1%/99.99%/99.78%` of the two-architecture squared-error variation. Frozen leave-one-patient/examination-cluster-out ridge using Anchor-CV alone achieved rank association `0.939/0.954/0.953` and held-out mean-baseline R² `0.789/0.900/0.837`. Adding correlated direct-difference/spectral features did not improve ranks and produced poor IXI calibration. Observable difficulty is strongly case-stable, but naïve acquired-feature stacking is rejected.
- Scope: x4 only; IXI x2/x6 outputs were not complete at analysis time.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_intrinsic_difficulty*`.

## P6-H09 / P6-E09 — Failure taxonomy and complementarity

- Claim: Anchor-CV and output disagreement fail for different mechanistic reasons, despite failure of naive fusion.
- Test: predeclared high/low quartile cells, PC-versus-Anchor-CV discordance, boundary/local/global descriptors and representative MRI/error/disagreement panels.
- Falsifier: discordant cases have no reproducible descriptor difference.
- Result: **LIMITED COMPLEMENTARITY; NO FUSION JUSTIFIED.** With a predeclared 0.20 within-stratum absolute-rank-error margin, PC was closer to x4 error for three fastMRI and eight IXI model–cases, whereas Anchor-CV was closer for one fastMRI model–case; NingXia had no large-margin discordance. Most model–cases were concordant (44/48, 222/230, 44/44). The rare IXI PC-winner cases had lower adjacent difference and dynamic range than the cohort median, but sample counts were too small for a new mechanism. MRI/reconstruction/error panels demonstrate that neither examination-level score localizes the worst plane. Naïve fusion remains rejected.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_failure_taxonomy*` and `PAPER/figures/plan6_failure_exemplars.pdf`.

## P6-H10 / P6-E10 — Efficiency

- Claim: Anchor-CV avoids extra acquisition and has lower reconstruction-call/GPU cost than committee/TTA/phase-grid strategies.
- Test: warm-up plus repeated wall time, peak allocated GPU memory where available, CPU time, calls and stored arrays; hardware recorded.
- Falsifier: measured cost is comparable to or worse than the claimed alternatives after equalizing case count.
- Result: **CONFIRMED FOR COMPUTATIONAL COST, NOT FOR RANKING SUPERIORITY.** On deterministic representative fastMRI/IXI/NingXia examinations, Anchor-CV CPU scoring took `0.42/3.97/3.93 ms`, required zero neural reconstructions, and stored no predicted volume. Committee, flip-TTA and disjoint-phase pairs each required two neural calls; measured sequential end-to-end medians were `0.25–0.29 s`, `2.43–3.20 s`, and `0.49–0.60 s`, respectively, with about `271 MiB` peak allocated GPU memory and `8.6–66.5 MiB` output storage. Hardware was an RTX 5090 D v2; GPU medians use three post-warm-up repetitions. Output-PC score-only latency is small only after its two predictions exist. Efficiency does not override P6-E06/E07: Anchor-CV is cheaper but not a stronger ranker than all baselines.
- Trace: `CVPR/CVPR_UPGRADE/outputs/plan6_efficiency.*`.

## IXI x2 feasibility gate

Valid x2 benefit requires a completed, definition-matched IXI x2 reconstruction with frozen preprocessing/model and all 115 test examinations. Empty or partially trained run directories do not qualify. No proxy endpoint will be substituted. The gate is checked before any IXI benefit statistic is computed.

Status on 2026-08-13: the x2 gate was opened only after `IXI_X2_FROZEN_EVALUATION.md` fixed the checkpoint, SHA-256, endpoint and budgets before any test output. The selected validation-only checkpoint generated 115 I3Net outputs, 115 ground-truth/sparse inputs, 115 linear/cubic outputs and 115 I3Net metric rows. The x6 neural endpoint remains absent; the separate P6-E11 analytical experiment is not a substitute.

## P6-H11 / P6-E11 — Three-cohort analytical factor robustness

- Claim: increasing missing-slice factor raises shared error and reduces observable disagreement/reliability even outside neural architectures.
- Design: two-anchor linear versus nearest-anchor replication, which remain well defined on the shallow fastMRI/NingXia volumes at x6; all eligible physical planes and all three cohorts, clustered by examination/patient.
- Result: **CONFIRMED.** Pair MAE and shared fraction rose monotonically from x2→x4→x6 in all cohorts; observable fraction and disagreement–error Spearman fell monotonically. Shared fraction changed `0.843→0.940→0.953` (fastMRI), `0.750→0.886→0.923` (IXI), and `0.860→0.933→0.953` (NingXia). Reliability rho changed `0.955→0.833→0.798`, `0.961→0.947→0.947`, and `0.937→0.830→0.818`. Absolute disagreement generally decreased even as error increased; IXI showed a small x6 rebound without reliability recovery.
- Boundary: analytical estimator evidence, not a proxy for missing IXI neural x2/x6 outputs.
- Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e11_analytic_factor*`.

## P6-H12 / P6-E12 — Three-cohort TMI risk–coverage

- Claim: measurement-disjoint disagreement gives more useful examination triage than dependence-preserving disagreement, but need not dominate a strong acquired-input baseline in every cohort.
- Design: one common independently stored endpoint (mean HAT/SwinIR x4 examination MAE); compare measurement-disjoint, max-shared, HAT–SwinIR committee disagreement and adjacent-anchor MAE over complete curves and 10/20/30/50/70/90% coverages. TTA is excluded because IXI definition-matched output is absent and fastMRI+NingXia alone violates the coverage invariant.
- Result: **CONFIRMED AGAINST DEPENDENCE-PRESERVING OUTPUT SCORES; NOT UNIVERSALLY BEST.** Measurement-disjoint nAURC was `0.0119/0.0013/0.0107` on fastMRI/IXI/NingXia, versus max-shared `0.0684/0.0139/0.0306` and committee `0.0193/0.0140/0.0504`. Adjacent-anchor MAE was weaker on fastMRI/IXI (`0.0212/0.0143`) but stronger on NingXia (`0.0070`). This supports measurement disjointness as the output-based reliability mechanism, while preserving a cohort-specific input-baseline boundary.
- Trace: `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e12_*` and `figures/p6_e12_risk_coverage.pdf`.
