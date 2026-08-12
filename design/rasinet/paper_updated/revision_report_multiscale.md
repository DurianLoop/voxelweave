# Multiscale Revision Report

## Completed and verified

1. Audited the identical 24 fastMRI-brain and 22 NingXia examinations at factors
   two, four, and six. Every audited prediction passed case-ID, shape, affine,
   orientation, finite-value, generated-support, and duplicate checks. NingXia
   predictions matched their eight held-out fold lists.
2. Froze the primary intersection before evaluation to I3Net, HAT, SwinIR,
   linear, and cubic. Added ArSSR, CycleINR, Pix2PixGAN, and SMamba-UNet only as
   an explicitly retrospective expanded-diversity sensitivity.
3. Generalized generated support to `G_r={z:(z-anchor_start) mod r != 0}` with
   `anchor_start=0`; no observed anchor slice enters scoring or error evaluation.
4. Ran 18 dataset-factor-target profiles with 2,000 paired case bootstraps.
   Generated per-case scores, CIs, risk-coverage data, matched-target matrices,
   paired method comparisons, fidelity summaries, and the result registry.
5. Added the direct target-specificity test. All six matched-minus-mismatched
   intervals include zero, so the paper now states that shared examination
   difficulty dominates model attribution.
6. Added paired target-median comparisons with mean, all-output spread, and
   target-excluded spread. Median is retained as a pre-specified robust default,
   not claimed as a statistically dominant algorithm.
7. Rewrote both papers around observable-output selective review, cross-factor
   behavior, governance, common-mode failure, and deployment cost. The original
   `main.tex` and its PDF were not overwritten.
8. Regenerated all new tables and vector figures from CSV files. The regular
   paper is 4+1 pages; the extended paper is 8+1 pages.

## Main result changes

| Cohort | Factor | Case rho | nAURC | RRR50 |
|---|---:|---:|---:|---:|
| fastMRI-brain | x2 | 0.888 | 0.098 | 18.8% |
| fastMRI-brain | x4 | 0.912 | 0.073 | 19.8% |
| fastMRI-brain | x6 | 0.937 | 0.052 | 21.0% |
| NingXia | x2 | 0.892 | 0.065 | 22.0% |
| NingXia | x4 | 0.926 | 0.058 | 22.2% |
| NingXia | x6 | 0.871 | 0.097 | 20.9% |

The factor-six signal remains useful, but NingXia shows a scale-dependent
degradation. Expanded membership is not monotonically beneficial. Equal-profile
paired delta-nAURC is -0.001 [-0.008, 0.008] versus mean and 0.011 [-0.007,
0.031] versus all-output spread (negative favors median).

## Expected submission impact

Cross-factor validation, strict OOF auditing, paired statistics, and honest
negative results substantially improve technical quality and reproducibility.
The principal novelty risk remains because generic examination difficulty
explains much of the ranking signal; the paper now treats this as a measured
boundary instead of hiding it.
