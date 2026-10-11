# Plan6 New Experiments

## P6-E06 — Frozen Anchor-CV explanation and strong baselines

Coverage: fastMRI (24 examinations), IXI (115 examinations), NingXia (22 series / eight patient clusters). Score definition remained ANCHOR_CV_V1.

Anchor-CV error-ranking Spearman remained `0.943`, `0.955`, and `0.958`. Kendall tau was `0.812`, `0.831`, and `0.844`; nAURC was `0.023`, `0.015`, and `0.011`. However, adjacent-anchor MAE/RMSE were indistinguishable: clustered Anchor-CV-minus-adjacent-MAE intervals were `[-0.050,0.098]`, `[-0.005,0.003]`, and `[-0.133,0.000]`.

After rank-residualizing adjacent MAE, robust intensity range and spacing, Anchor-CV associations were `0.333`, `-0.059`, and `-0.100`. Dividing by robust intensity range reduced fastMRI/NingXia ranking and reversed IXI. Thus the predeclared independent-information explanation is rejected. Anchor-CV is exactly a foreground-masked local second-difference residual and is retained as a simple, target-free acquired-data difficulty score rather than a uniquely informative method.

Trace: `../outputs/plan6_anchor_cv_explanation.json`, `../outputs/plan6_anchor_cv_explanation_summary.csv`, `../outputs/plan6_anchor_cv_baseline_deltas.csv`, and `../outputs/plan6_anchor_cv_loo_influence.csv`.

## P6-E04 — Neural shared influence

The registered central-plane gate passed in fastMRI, IXI, and NingXia for both HAT and SwinIR. We therefore ran the frozen three-plane confirmation: 24/115/22 examinations or series, 72/345/66 physical planes, with NingXia inference clustered at eight patients. Each shared physical anchor received the same four 1%-range Rademacher perturbations, and neural influence was the cosine overlap of the paired finite-difference response vectors.

For error cosine, shared-error fraction, and observable-error fraction, neural influence improved absolute Spearman association over integer anchor overlap in every dataset–architecture stratum. The 18 improvements ranged `0.036–0.089`, and all patient/examination-clustered 95% bootstrap intervals excluded zero. After rank-residualizing examination identity, overlap count, context span, and asymmetry, neural influence retained `|rho|=0.185–0.395`. Thus the association is not exhausted by the coarse geometry labels used here. For disagreement MAE, all point improvements were positive, but both fastMRI intervals crossed zero; this endpoint is explicitly supporting evidence.

The design is a finite-difference association study, not an intervention on anatomy or a causal mediation experiment. Context span and asymmetry varied in the prespecified comparator grid; controlled estimates address these measured geometric variables but do not establish that neural influence is the sole mechanism.

In a cleaner fixed-count analysis, the four comparator contexts all shared exactly one reference anchor. Neural influence therefore varied while integer overlap was constant. After controlling span, asymmetry, and examination, all endpoint/model associations had the expected sign with intervals excluding zero in fastMRI and IXI (`|rho|=0.135–0.587`). NingXia estimates were near zero or mixed and all intervals crossed zero. This is positive evidence beyond overlap count in the two larger cohorts, with explicit external-cohort heterogeneity.

Trace: `../outputs/plan6_neural_shared_influence_confirm3.json`, `../outputs/plan6_neural_shared_influence_confirm3_summary.csv`, `../outputs/plan6_neural_shared_influence_confirm3_per_case_config.csv`, `../outputs/plan6_fixed_overlap_ladder.csv`, `../outputs/plan6_fixed_overlap_ladder.json`, and `figures/plan6_neural_influence_forest.pdf`.

## P6-E05 — Registered mechanism-chain audit

The three local association arrows survived examination/patient and measured-geometry control in all six dataset–architecture strata. Neural influence predicted aligned target errors (`rho=0.219–0.410`); alignment predicted lower disagreement normalized by paired error (`rho=-0.933` to `-0.889`); and influence predicted a lower observable-error fraction (`rho=-0.412` to `-0.211`). All clustered 95% intervals excluded zero.

The final ranking arrow was less universal. Across the eight non-self comparator contexts, greater median alignment had the expected association with poorer disagreement–error ranking in all strata, but intervals excluded zero only for both IXI models and NingXia HAT. Influence-to-ranking was even less stable. We therefore describe a strongly supported local cancellation mechanism and a partially supported context-level ranking consequence, not a fully identified causal mediation chain.

Trace: `../outputs/plan6_mechanism_chain.json`, `../outputs/plan6_mechanism_chain_summary.csv`, and `../outputs/plan6_mechanism_chain_context_ranking.csv`.

## P6-E08 — Architecture-independent examination difficulty

At x4, HAT and SwinIR examination errors were almost perfectly rank-stable (`rho=0.989/1.000/0.997` on fastMRI/IXI/NingXia). Examination identity explained `99.1%/99.99%/99.78%` of the two-architecture squared-error variation, while architecture after examination explained at most `0.19%`. Frozen leave-one-patient/examination-cluster-out ridge using Anchor-CV alone predicted mean architecture error with rank association `0.939/0.954/0.953` and held-out R² `0.789/0.900/0.837`.

A larger block of direct adjacent difference, gradient, frequency, spacing, and variability features did not improve rank prediction; on IXI it substantially harmed absolute calibration. This rejects indiscriminate feature fusion and supports the narrower claim that acquired-data observables expose a dominant case difficulty factor. The analysis is x4-only because definition-matched IXI x2/x6 outputs were not complete at analysis time.

Trace: `../outputs/plan6_intrinsic_difficulty.json`, `../outputs/plan6_intrinsic_difficulty_variance.csv`, and `../outputs/plan6_intrinsic_difficulty_loco.csv`.

## P6-E09 — Failure taxonomy and complementarity

Using a frozen 0.20 within-stratum absolute-rank-error margin, PC ranked x4 difficulty more accurately in three fastMRI and eight IXI model–cases, while Anchor-CV won in one fastMRI model–case; no NingXia model–case reached that margin. The large majority were concordant (44/48, 222/230, and 44/44). Rare IXI PC-winner cases had lower adjacent difference and dynamic range, but their count is insufficient to motivate a new fusion mechanism. Representative ground-truth, HAT reconstruction, and error panels also make the scope boundary concrete: both are examination-level scores and neither identifies the worst physical plane.

Trace: `../outputs/plan6_failure_taxonomy.json`, `../outputs/plan6_failure_taxonomy_per_case.csv`, `../outputs/plan6_failure_taxonomy_summary.csv`, `../outputs/plan6_failure_taxonomy_exemplars.csv`, and `figures/plan6_failure_exemplars.pdf`.

## P6-E07A — Frozen three-cohort risk–coverage

Full curves at every retained-case prefix and registered 10/20/30/50/70/90% coverages confirm that ANCHOR_CV_V1 stratifies x4 reconstruction risk. It is not the strongest available ranking method: output PC had lower nAURC on fastMRI and IXI, while adjacent MAE was lower on NingXia. Anchor-CV's role is therefore a reconstruction-free acquired-data difficulty score, not a state-of-the-art risk-ranking claim. These cohorts contributed to earlier method development, so this is a frozen reanalysis rather than independent external confirmation.

The x4→x2 consequence test was not generalized to a fastMRI+NingXia-only pair. Instead, checkpoint, hash, endpoint and budgets were frozen before any IXI x2 test output; the selected validation-only I3Net checkpoint then generated all 115 definition-matched IXI outputs and metrics. On IXI/fastMRI, Anchor-CV versus benefit Spearman was `0.948/0.871`, compared with adjacent MAE `0.950/0.846` and output PC `0.970/0.843`. All three policies exceeded random at 10/20/30/50% budgets. IXI Anchor-CV captured `0.920–0.973` of oracle gain above random. Because IXI x4 and x2 endpoints use different frozen estimators, this is a case-level retrospective consequence test rather than a same-model causal effect.

Trace: `../outputs/plan6_frozen_risk_coverage.json`, `../outputs/plan6_frozen_risk_coverage.csv`, `../outputs/plan6_frozen_risk_coverage_full_curve.csv`, `../outputs/plan6_frozen_risk_coverage_summary.csv`, `../outputs/plan6_ixi_x2_consequence*`, `../../../IXI_X2_FROZEN_EVALUATION.md`, and `figures/plan6_frozen_risk_coverage.pdf`.

## P6-E10 — Measured computational cost

On deterministic median-index cases from fastMRI/IXI/NingXia, Anchor-CV scoring required zero neural calls and `0.42/3.97/3.93 ms` of CPU time. Committee, flip-TTA and disjoint-phase pairs required two neural calls; their measured sequential end-to-end medians ranged `0.25–0.29 s`, `2.43–3.20 s`, and `0.49–0.60 s` across the three cohorts. Peak allocated GPU memory was approximately `271 MiB`, and paired prediction storage was `8.6–66.5 MiB`. Measurements used an RTX 5090 D v2, three post-warm-up GPU repetitions, and 100 CPU scoring repetitions.

This comparison distinguishes score-only from prediction-generation cost: output PC is cheap to compute only after two reconstructions exist. Anchor-CV is computationally attractive, but P6-E06/E07 show that this efficiency does not imply stronger ranking than adjacent difference or output PC.

Trace: `../outputs/plan6_efficiency.json` and `../outputs/plan6_efficiency.csv`.
