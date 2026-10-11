# Case Influence Analysis

Status: CONFIRMATORY robustness analysis of PC-v1-FROZEN.

## NingXia, 22 OOF examinations

- All 22 leave-one-examination-out subsets preserve the favorable delta nAURC direction.
- Delta nAURC range: -0.0396 to -0.0153.
- Full delta: -0.0256.
- Largest favorable influence: removing `NX005_9805f678f318.nii.gz` changes delta to -0.0396.
- Largest unfavorable influence: removing `NX006_539c16575ab2.nii.gz` changes delta to -0.0153.
- No single examination reverses the result, but the maximum influence magnitude (0.0140) is large relative to the full effect.

The influential cases span both moderate and high average errors. Influence is therefore not explained by a single catastrophic outlier alone. Full values and case properties are in `plan2_outputs/ningxia_leave_one_case_out.csv`.

## fastMRI-brain, 24 examinations

- All 24 leave-one-examination-out subsets preserve the favorable direction.
- Delta nAURC range: -0.0868 to -0.0556.
- Full delta: -0.0698.
- All nine factor-target profiles favor PC-v1.

## Interpretation

The direction is not single-case dependent in either cohort. NingXia remains heterogeneous and statistically uncertain after correct clustering; fastMRI is substantially more stable. Leave-one-out stability does not replace an untouched external cohort.

Figures:

- `plan2_outputs/ningxia_forest.png`
- `plan2_outputs/fastmri_forest.png`
- `plan2_outputs/ningxia_risk_coverage.png`
- `plan2_outputs/fastmri_risk_coverage.png`

