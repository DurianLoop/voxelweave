# Plan-3 Research Report

## Central discovery

The repository supports a broader account than Physical Consistency alone. Deterministic MRI interpolation failure is largely an intrinsic examination-and-sampling problem shared across architectures. Cross-context disagreement observes a smaller context-sensitive error component; dominant consensus error remains invisible, especially when contexts share anchors.

## Quantitative evidence

- Case variance fraction: fastMRI 0.583 [0.428,0.667], NingXia 0.839 [0.588,0.880].
- Factor fraction: 0.258 [0.194,0.383] and 0.125 [0.087,0.358].
- Architecture fraction: 0.103 [0.080,0.146] and 0.006 [0.004,0.015].
- All 138 case–architecture units satisfy x2 < x4 < x6 error.
- Eleven fastMRI neural families have median pairwise error rho 0.961; six IXI methods have 0.991.
- Exact context MSE split: shared consensus 80.9%/86.5%; observable diversity 19.1%/13.5%.

## Boundary mechanism

NingXia x4–x6 stable-wrong events concentrate at the first generated plane. Source tracing rules out missing coverage and zero filling. The two contexts share their left anchor, which lowers separation despite higher error. Retrospective target curvature has rho 0.936 with error for x4–x6 and median 260 versus 168 on stable-wrong versus other planes. In a four-case frozen HAT synthetic intervention, replacing the first left anchor raises first-interval error by 42.8 while leaving interior error essentially unchanged. This supports local boundary-context sensitivity; cohort prevalence still requires new data.

## Intervention specificity

Four-view flip-TTA was generated for every available combination of two cohorts, three factors, and three primary architectures. PC wins all 18 profiles. Mean delta nAURC is -0.0340 on fastMRI (`p=0.0035`) and -0.1143 on NingXia (`p=0.0015`) under examination-clustered swaps. The result supports physical sampling context over flips, not over every imaginable perturbation.

## Pre-reconstruction difficulty

Adjacent acquired-slice RMSE predicts raw reconstruction error on fastMRI (rho 0.719), NingXia (0.780), and independent 115-case IXI (0.982 averaged across six methods). After normalizing the endpoint, correlations fall to 0.503, 0.465, and 0.251. Fully normalized anchor change remains strong on IXI (0.644) but uncertain on the two smaller cohorts. This is a reproducible yet domain-dependent input proxy, not a universal reliability score.

## Falsifications

- Diversity alone does not rank intervention quality.
- High-frequency-only explanations fail; low-band consistency is more predictive.
- Triangle geometry does not attribute the bad factor; x6 is always worst.
- Translation magnitude is not a common driver.
- Naive input/PC fusion degrades ranking.

## Broader principle

A reliability intervention should not merely maximize output diversity. It must preserve target identity and expose error directions that are not already shared by the reconstruction contexts. Observable disagreement is scientifically meaningful, but its ceiling is determined by consensus bias. In the present setting, sampling-factor changes satisfy this criterion better than flips, while shared anchors explain a concrete failure boundary.

## Status

All high-value experiments executable from present artifacts have been run. Remaining successors require new acquisition contexts, sites/anatomies, factors, metadata, clinical labels, or a prospectively frozen additional perturbation protocol. The formal decision is documented in `PROJECT_EXHAUSTION_AUDIT.md`.

