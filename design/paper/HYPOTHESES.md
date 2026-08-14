# Hypotheses

## H001 — Physical cross-scale inconsistency predicts examination error

- Hypothesis: the same reconstructor's disagreement on physically identical generated planes across interpolation factors ranks examination-level reconstruction error.
- Motivation: sampling context changes with factor while the underlying world plane is fixed; unstable reconstructions should move more than stable ones.
- Novelty rationale: verified adjacent literature learns uncertainty/error, samples a posterior, uses ensembles, or assesses generic MRI quality. No materially equivalent physical-plane, cross-factor ranking protocol was found as of 2026-08-12.
- Expected observation: positive case-level rank correlation and lower nAURC than random ordering.
- Falsification condition: correlation near zero/negative or nAURC near/worse than random across fixed profiles.
- Minimum experiment: matched x2/x4/x6 outputs for one fixed target and cohort.
- Full experiment: multiple targets, examination-clustered inference, held-out/cross-cohort localization, robustness to factor pairs and masks.
- Potential confounders: factor-dependent preprocessing, mismatched planes, different intensity scales, shared case difficulty, unequal support.
- Current evidence: held-out fastMRI and NingXia OOF localization replicate at pixel, plane, and case-pair levels; all 1,518 geometry records match. Fourteen natural consistent-but-wrong planes delimit the converse.
- Status: KEEP as the one-sided witness claim H007; do not interpret agreement as correctness.

## H002 — Physical consistency adds information beyond cross-model disagreement

- Hypothesis: physical consistency improves ranking relative to the frozen target-excluded committee score.
- Expected observation: paired delta nAURC below zero with interval excluding zero.
- Falsification condition: interval includes zero or favors the baseline.
- Minimum experiment: examination-clustered paired inference across fixed profiles.
- Full experiment: repeat without tuning on an untouched external cohort.
- Potential confounders: reuse of cases across factors, profile averaging, post-hoc formula choice.
- Current evidence: the former profile-aligned NingXia interval is superseded. Correct clustered results are fastMRI delta -0.0698 [-0.1597, -0.0183], 9/9 profiles, and NingXia -0.0256 [-0.0957, 0.0092], 6/9 profiles. Hybrid complexity remains unnecessary.
- Status: KEEP on fastMRI; PARTIALLY SUPPORTED / statistically uncertain on NingXia.

## H003 — Flexible committee selection improves over a frozen simple rule

- Hypothesis: target/factor-conditioned selection over a large score-committee space transfers better than the fixed baseline.
- Expected observation: lower outer nAURC after leakage-free nested selection.
- Falsification condition: outer nAURC is worse than the frozen baseline.
- Current evidence: unconstrained 0.270 and amended 0.299 versus baseline 0.077; both fail.
- Strongest competing explanation: tiny inner folds make high-flexibility selection unstable and favor low-cost analytical members.
- Status: REJECT. Negative result retained.

## H004 — Target-to-committee disagreement attributes which model is wrong

- Hypothesis: after inner-only calibration, the target-specific score ranks the erroneous model within a case.
- Expected observation: strong positive within-case Spearman and top-1 accuracy clearly above 1/3 for three targets.
- Falsification condition: weak within-case ranking or chance-level top-1 accuracy.
- Current evidence: within-case Spearman about 0.126; top-1 27.3%.
- Status: REJECT as an attribution claim. Examination triage remains distinct.

## H005 — A lightweight ACSI model exceeds I3Net in 3D anatomy consistency

- Current evidence: ACSI-v1 loses to I3Net on all four audited 3D metrics; ACSI-v2.1 fails its mini gate against Linear on all four 3D metrics.
- Status: REJECT for current implementations; no full ACSI-v2.1 run was launched.

## H006 — Wider PastNet routing closes the full performance gap

- Current evidence: G07 improves to 24.29 dB but remains about 1.71 dB below the stated 26 dB aspiration; several structural variants were negative.
- Status: REFINE only if future work targets a new mechanism. No claim supported here.

## H007 — Sampling-context discrepancy is a one-sided error witness

- Hypothesis: for metric `d`, large `d(f_s1,y, f_s2,y)` implies at least one context reconstruction is inaccurate, while small discrepancy cannot certify correctness.
- Motivation: triangle inequality gives `max(error_s1,error_s2) >= discrepancy/2`.
- Expected observation: positive local and aggregated discrepancy-error association, plus consistent-but-wrong counterexamples.
- Falsification: no association after geometry/intensity controls, or inability to find the predicted agreement failure.
- Evidence: held-out fastMRI and NingXia localization replicate; controlled blur and 14 real NingXia planes demonstrate agreement failure.
- Status: SUPPORTED within T2 brain slice interpolation.

## H008 — The examination-level advantage is robust to case clustering

- Evidence: fastMRI delta nAURC -0.0698 [-0.1597,-0.0183], 9/9 profiles and 24/24 leave-one-case subsets favor PC. NingXia delta -0.0256 [-0.0957,0.0092], 6/9 profiles and 22/22 leave-one-case subsets favor PC.
- Status: SUPPORTED on fastMRI; PARTIALLY SUPPORTED on NingXia. The prior stronger NingXia significance statement is rejected.

## H009 — PC detects errors shared by all models

- Prediction: when all models receive common degradation, committee disagreement stays low but PC rises.
- Evidence: shared uniform and factor-dependent blur make both committee disagreement and PC decrease as error rises.
- Status: REJECT. PC detects context-dependent separation, not shared error in general.

## H010 — Sampling context is uniquely better than generic perturbation consistency

- Evidence: fastMRI x4 SwinIR PC nAURC 0.011 versus TTA 0.034, but paired rank permutation p=0.170.
- Status: original one-profile test superseded by P3-H07/E025. Sampling context is supported over flip-TTA across 18 profiles, but uniqueness versus arbitrary perturbation families remains unsupported.

## H011 — Raw PC performance is not an intensity-scale artifact

- Evidence: normalizing the endpoint weakens raw PC substantially; dynamic range correlates with raw PC at rho=0.851. Shared-range-normalized PC retains association and descriptively beats the baseline on normalized error, but clustered CI includes zero.
- Status: REFINED. Raw PC contains both absolute difficulty and context-instability components.

## H012 — Physical inconsistency localizes reconstruction error

- Evidence: protocol derived on eight fastMRI cases, confirmed on 16 held-out cases, and replicated on 22 NingXia OOF cases. Pixel, slice, case-pair, and top-decile enrichment intervals are all positive.
- Status: SUPPORTED as association, not calibrated uncertainty.

## P3-H01 — x4–x6 first-plane failure is a context-geometry phenomenon

- Prediction: stable-wrong events concentrate at the first generated plane after correct world matching, and controlled asymmetric anchor deletion affects the corresponding interval rather than the full volume.
- Evidence: NingXia x4–x6 first-versus-other stable-wrong rate delta 0.147 [case-clustered 95% CI 0.030, 0.286]; source audit excludes uncovered/zero-filled output; four-case synthetic HAT anchor deletion raises first-interval error by 42.8 while interior error changes -0.21.
- Mechanism refinement: shared anchors suppress cross-context separation while nonlinear target trajectory remains difficult.
- Status: SUPPORTED MECHANISTICALLY; causal claim for every NingXia failure remains PARTIAL.

## P3-H02 — Examination difficulty dominates architecture identity

- Prediction: case variance and cross-architecture rank agreement exceed architecture main effects.
- Evidence: case effects explain 58.3% fastMRI and 83.9% NingXia error variance versus architecture effects 10.3% and 0.6%. Eleven fastMRI neural families have median pairwise error rho 0.961; IXI six-method median is 0.991.
- Status: SUPPORTED across three cohorts, with raw-MAE/intensity scope explicitly retained.

## P3-H03 — More error diversity alone produces a better witness

- Prediction: factor pairs with more decorrelated errors have higher disagreement-error association.
- Evidence: across nine profiles per cohort, diversity-quality rho is -0.244 fastMRI and 0.167 NingXia.
- Alternative: intervention quality depends jointly on target preservation, error scale, shared bias, and diversity—not diversity alone.
- Status: FALSIFIED in its simple monotonic form.

## P3-H04 — Acquired anchors predict reconstruction difficulty before inference

- Evidence: raw adjacent-anchor RMSE predicts raw error on fastMRI (rho 0.719), NingXia (0.780), and independent IXI (0.982 across six methods). Against range-normalized error, correlations are 0.503, 0.465, and 0.251. A fully normalized feature is robust only on IXI (0.644).
- Status: PARTIALLY SUPPORTED; signal is reproducible but substantially intensity- and domain-dependent.

## P3-H05 — PC is primarily a high-frequency error witness

- Evidence: low-frequency plane rho is 0.817/0.722, exceeding high-frequency 0.791/0.637 on fastMRI/NingXia; NingXia high-frequency median pixel rho is 0.192.
- Status: FALSIFIED. PC spans bands and is especially weak for NingXia high-frequency error.

## P3-H06 — Multi-context triangle shape enables factor attribution

- Evidence: all 138 case–architecture combinations have x6 as the worst factor. Triangle outlier accuracy 0.875/0.970 is worse than the constant-x6 baseline of 1.0.
- Status: FALSIFIED; attribution branch closed again.

## P3-H07 — Physical context is more informative than flip TTA

- Evidence: PC beats four-view flip-TTA in all 18 combinations of fastMRI/NingXia × x2/x4/x6 × I3Net/HAT/SwinIR. Mean delta nAURC is -0.0340 on fastMRI (`p=0.0035`) and -0.1143 on NingXia (`p=0.0015`); pooled delta -0.0741 (`p<0.0005`), using examination-clustered swaps.
- Status: SUPPORTED across the available cohorts, factors, and architectures for flip-TTA; not universal to other perturbation families.

## P3-H08 — Context diversity is the dominant error component

- Evidence: exact squared-error decomposition assigns median 19.1% fastMRI and 13.5% NingXia to context diversity; shared consensus error accounts for 80.9% and 86.5%.
- Status: REJECTED. Shared systematic error dominates; this formally explains consistency blind spots.
