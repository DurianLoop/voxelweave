# Revision Report: Nested Optimization

## Outcome

The revision corrects the old optimization methodology and changes the paper's strongest refinement from adaptive committee selection to physically matched cross-scale consistency. All numbers below are generated from `outputs/nested_optimization/`.

## Corrected Issues

| Before | Actual correction | Evidence | Status |
|---|---|---|---|
| Cost and one-SE were declared but not implemented | Added cost rank and executable one-SE selection | `nested_selection.py`, manifests | Complete |
| Model fidelity used different target-derived masks | Recomputed MAE/MSE/PSNR/SSIM/NCC on one common offline GT support | `corrected_reconstruction_fidelity.csv` | Complete |
| Paper called a mixed committee neural-only | Linear and Cubic are explicit in config, registry, and prose | `MODEL_BANK_AUDIT.md` | Complete |
| Availability-varying committee called universal | Renamed common-bank / availability-conditioned rule | papers and audit | Complete |
| Aggregate bootstrap flattened profiles | Profile deltas now average inside each of 2,000 aligned replicates | `nested_paired_bootstrap.csv` | Complete |
| Raw attribution scales and errors were incomparable | Common error support, inner-only target calibration, relative centering, attribution objective | attribution CSVs | Complete |
| Shape mismatch ended cross-scale analysis | Matched full affine world-plane origins on generated slices | physical audit | Complete |
| ZIP omitted imported modules | Final package includes every local import, configs, tests, and precomputed CSVs | delivery manifest | Complete |

## Experiments Actually Run

- Common-support development fidelity: 187 profile cases, 13 methods where available.
- Common-support NingXia OOF labels/features: 66 factor cases and 8,712 target-member records.
- Broad interaction search: 561,492 candidates; 1,320 stratified finalists.
- Nested selection: 8 outer folds x 3 factors x 11 targets x 2 roles; every profile has 22 out-of-selection predictions.
- Protocol-amendment sensitivity: same outer structure with mandatory neural peers; retained separately.
- Target attribution: four inner-only calibration transforms x two relative transforms, selected by attribution metrics.
- Physical alignment: 1,518 records, 1,518 matched.
- Frozen transfer: 132 profile rows across both dataset directions and leave-one-factor-out analyses.
- Statistics: 2,000 paired case bootstraps with profile-, factor-, target-, and aggregate summaries.
- Unit/integration tests: 11 passed.

## Main Result Changes

- Correct point estimates use original profile metrics rather than bootstrap means.
- Frozen baseline: nAURC 0.077, rho 0.884, RRR50 21.9%.
- Physical consistency: nAURC 0.052, rho 0.911, RRR50 21.4%.
- Paired delta nAURC: -0.026 [-0.063, -0.001].
- Fixed rank hybrid: nAURC 0.050; it is not conclusively different from physical consistency.
- Unconstrained nested selection failed (nAURC 0.270); amended selection also failed (0.299). Neither is promoted as an improvement.
- Attribution remains weak: matched advantage 0.060, within-case rho 0.126, top-1 27.3%.

## Expected Submission Impact

The physical-coordinate result adds a distinct signal-processing contribution and removes the inaccurate shape-mismatch claim. Common-support selection, nested governance, calibrated attribution, and aligned bootstrap materially improve technical defensibility and reproducibility. The main residual limitations are intrinsic simplicity, small labeled cohorts, multiscale execution cost, and absence of clinical-task validation.
