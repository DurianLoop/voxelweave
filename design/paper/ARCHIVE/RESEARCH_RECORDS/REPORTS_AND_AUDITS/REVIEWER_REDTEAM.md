# Reviewer Red Team after Plan 2

## Novelty skeptic

**Attack:** This is generic perturbation consistency with MRI terminology.

**Evidence-based response:** Perturbation consistency is established prior art, so the paper must not claim otherwise. The distinct contribution is a physical, target-preserving intervention on identical world planes; a one-sided error-witness interpretation; multi-granularity replication; and explicit stable-error failures. Plan 3 shows PC beats flip-TTA in 18/18 profiles with cohort-clustered significance. This supports superiority over flips in scope, not over arbitrary perturbation families.

## Statistics skeptic

**Attack:** Repeated profiles were treated as independent and produced a false significant result.

**Response:** That attack is valid against the earlier analysis. The corrected analysis resamples examinations as clusters. NingXia delta nAURC is -0.0256 with 95% CI [-0.0957, 0.0092] and rank-permutation `p=0.164`; it is not significant. FastMRI is -0.0698 [-0.1597, -0.0183], `p=0.005`. All 22 and 24 leave-one-case analyses preserve direction, but this does not replace clustered inference.

## Mechanism skeptic

**Attack:** Correlation does not explain why disagreement tracks error.

**Response:** The triangle inequality proves only the valid direction: large separation lower-bounds at least one error. Controlled shared/factor-dependent blur and 14 natural consistent-but-wrong planes demonstrate the missing converse. The empirical signal therefore depends on intervention-induced error diversity; it is not a universal uncertainty estimator.

## Confounding skeptic

**Attack:** The result is merely intensity range in MAE units.

**Response:** Raw dynamic range correlates with raw PC (`rho=0.851`) and raw error (`rho=0.643`), so intensity scale is a material component. Under one pooled per-case range, normalized PC still associates with normalized error (`rho=0.593`) and improves over the normalized committee descriptively, but its clustered comparative interval includes zero. The paper must report both and label `PC-v2` exploratory.

## Geometry skeptic

**Attack:** Cross-factor differences arise from mismatched planes or resampling geometry.

**Response:** Across 1,518 records, in-plane shape, orientation, spacing, FOV, slice step, and affine match; maximum matched world-plane distance is 0 mm. Geometry mismatch is not supported by the audited artifacts.

## Clinical reviewer

**Attack:** MAE enrichment does not imply diagnostic risk.

**Response:** Correct. No reader, lesion, segmentation, registration, or outcome endpoint exists. The work supports retrospective error localization/ranking only and makes no clinical-safety claim.

## Generalization skeptic

**Attack:** fastMRI and NingXia do not establish deployment generality.

**Response:** Correct. They provide two-cohort replication within T2 brain interpolation, not an untouched external anatomy/site confirmation. This is the largest unresolved blocker.

## Fatal-flaw verdict

No fatal flaw remains for the scoped one-sided error-witness claim. Fatal gaps remain for accuracy certification, universal superiority, generic-perturbation uniqueness, external anatomy/site generalization, and clinical benefit; those claims are excluded.
