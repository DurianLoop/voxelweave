# Complete Research Audit

> **Plan-2 statistical correction:** This pre-Plan-2 audit is retained for provenance. Its profile-aligned NingXia interval and corresponding significance statement are superseded by examination-clustered E007: delta nAURC -0.0256, 95% CI [-0.0957, 0.0092], rank-permutation p=0.164. See `STATISTICAL_VALIDITY.md` and `FINAL_RESEARCH_REPORT.md`.

## Scope and corpus

The audit treated `D:\MRI\design` as one research corpus. Top-level lines include `acsinet`, `acsinet_v2`, `fastmri_brain_pastnet_2p5d`, `ixi_pastnet_2p5d`, `ixi_ecsinet_2p5d`, `rasinet`, and two historical RASINet copies. The canonical RASINet directory alone contains code, prediction-derived tables, nested-selection registries, statistical outputs, manuscripts, figures, and reproducibility checks. Raw datasets were not copied or modified.

## Reconstructed research problem

The shared application is through-plane MRI interpolation: sparse axial acquisitions are densified by predicting missing slices. Most model lines optimize reconstruction fidelity or z-axis continuity. The mature RASINet line addresses a downstream problem: after deployment, the missing dense target is unavailable, so cohort-average PSNR/SSIM cannot say which examination should be reviewed.

## Existing method families

| Family | Representative local methods | Scientific role |
|---|---|---|
| Learned interpolation | I3Net, HAT, SwinIR, SAINT, SMamba-UNet, PastNet variants, ACSI-Net | Produce missing slices |
| Analytical interpolation | Linear, cubic | Low-cost references and committee members |
| Learned/architecture consistency | ACSI group prediction, z-losses, shallow 3D refinement | Attempt volume coherence |
| Cross-model post-hoc reliability | Target-excluded target-to-committee disagreement | Rank cases without ground truth |
| Single-model sensitivity | SwinIR TTA variance | Auxiliary uncertainty proxy |
| Cross-factor physical consistency | Same-target disagreement on world-coordinate-matched planes | Strongest current scientific signal |

## Experiments already conducted

- IXI T2 x4: 115 examinations, multiple neural targets and analytical outputs.
- fastMRI-brain T2: 24 examinations at x2/x4/x6.
- NingXia T2: 22 examinations at x2/x4/x6, produced by eight-fold OOF evaluation.
- Fixed target-to-committee reliability across ten factor-four dataset-target profiles.
- Candidate search over 561,492 score-committee interactions, followed by nested outer evaluation.
- Common-support reconstruction fidelity audit across 13 methods where available.
- Physical world-plane alignment and cross-factor scores (1,518 pair records).
- 2,000-replicate profile-aligned paired bootstrap.
- Target-attribution calibration and stress/boundary analyses.
- ACSI-v1 full evaluation, ACSI-v2.1 mini gate, and multiple PastNet structural sweeps.

## Verified findings

1. Fixed disagreement strongly ranks examination MAE across several existing cohorts, but does not precisely localize all voxel errors.
2. Cross-model disagreement cancels common-mode error by construction.
3. Flexible committee selection can overfit cohort difficulty; both the initial and amended selectors fail external outer profiles relative to the fixed baseline.
4. Physical cross-factor consistency is geometrically feasible despite different array depths when matching NIfTI world coordinates.
5. On nine NingXia OOF profiles, the point estimate improves nAURC from 0.0772 to 0.0516, but the corrected examination-clustered interval includes zero.
6. A hybrid score does not establish improvement over physical consistency alone.
7. Target attribution is weak and must not be inferred from examination ranking.
8. ACSI-v1 is lightweight and competitive but worse than I3Net on all audited 3D consistency metrics; ACSI-v2.1 fails its mini gate.

## Negative results preserved

- Development-selected RASINet committee: strong development result, failed frozen validation.
- Unconstrained nested selector: analytical-only collapse and nAURC 0.270.
- Neural-peer amendment: nAURC 0.299; retained as exploratory, not a replacement.
- Target attribution: near-chance top-1 and weak within-case ranking.
- ACSI-v2.1: excessive adjacent-slice correlation and no full run.
- Several PastNet calibration, symmetry, teacher, strong-z, and MA4W directions were stopped.

## Unverified assumptions

- Reconstruction MAE is a meaningful proxy for review priority; no reader/downstream validation proves clinical relevance.
- The NingXia effect transfers to an untouched site.
- Multi-factor outputs would be available in the intended deployment setting.
- Demographic/scanner subgroup behavior is stable; subgroup metadata are not audited in the available result tables.

## Strongest current baselines

- Reconstruction: I3Net is the recurring strongest local fidelity/3D consistency baseline.
- Reliability ranking: frozen target-excluded median target-to-committee disagreement, nAURC 0.0772 on the nine NingXia profiles.
- Simpler comparator: mean disagreement, nAURC 0.0809; statistically similar to median.

## Bottlenecks

- Only 22 internal OOF NingXia cases for the main paired positive result.
- No untouched external site, reader study, or downstream diagnostic task.
- Multi-factor physical consistency has nontrivial inference/storage cost.
- No common-hardware latency/memory benchmark across all 11 neural models.

## Genuine contribution versus engineering

The 561,492-candidate optimization is engineering search and, empirically, a negative result. The defensible scientific contribution is the observed distinction between two error observables: cross-model disagreement loses shared error, whereas same-model cross-factor physical inconsistency probes sensitivity to sampling context on the same anatomy. The causal isolation is incomplete, but fixed comparisons, geometry checks, and failure analyses support this mechanism more strongly than a module-stacking story.

## Audit decision

Advance the narrow physical-consistency/selective-review claim. Do not advance adaptive committee selection, target attribution, calibrated uncertainty, or clinical-benefit claims. The next meaningful evidence is an untouched external multi-factor cohort; more tuning on existing NingXia profiles would be scientifically counterproductive.
