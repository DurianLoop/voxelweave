# ANCHOR_CV_V1 Frozen Protocol

Freeze time: 2026-08-13, before Plan6 confirmation and explanation analyses.

## Score

For acquired x4 anchors `x_0, x_4, x_8, ...`, withhold every interior acquired anchor `x_4j`, predict it by the unweighted mean of its immediately adjacent acquired anchors, and compute foreground-masked MAE against the actually acquired withheld slice. The examination score is the median residual across eligible interior anchors.

Foreground is `abs(target) > 0.01 * max(abs(target))`. There is no cohort-specific normalization, score transform, weighting, threshold, or model input. Dense targets do not enter the score.

## Locked endpoints

- examination-level x4 reconstruction error;
- retrospective x4→x2 benefit where a valid x2 output exists;
- Spearman, Kendall tau, nAURC, full risk–coverage curve;
- 10/20/30/50% retrospective allocation budgets;
- leave-one-examination/patient-cluster-out influence.

## Locked scope

The supported use is examination-level triage. Plane/pixel localization is not supported and will not be optimized. Existing fastMRI, IXI and NingXia examinations have already contributed to method development; they are not relabeled as untouched confirmation data. A genuinely unused cohort is required for independent-data confirmation.

## Dataset coverage

All compatible analyses use fastMRI, IXI and NingXia. Benefit endpoints omit a cohort only when no valid x2 reconstruction exists. If a two-cohort test is required, it must use IXI and fastMRI; NingXia-only or fastMRI+NingXia confirmation is not permitted under Plan6.

## Change control

No result observed after this freeze may change the score. Any future variant receives a new version and must be developed without using the locked confirmation partition or endpoint.
