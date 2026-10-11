# Reconstruction benchmark report

The machine-readable tables are `outputs/p9_reconstruction_benchmark.csv` and `outputs/p9_reconstruction_benchmark_compact.csv`.

## Broken-model gate

On the common fastMRI x4 support, P0 MAE is 70.87 for I3Net, 80.14 for SAINT, and 114.39 for CycleINR, versus 134.54 for Linear. Every P0 output is finite on all 24 examinations and each beats Linear under the identical mask/metric contract. I3Net is the strongest recovered method in this slice of the bank; SAINT is competitive with HAT/SwinIR; CycleINR is weaker but not catastrophically undertrained.

Published headline metrics are not numerically compared because original datasets, intensity scales, downsampling formation, and implementations differ. I3Net uses official-architecture lineage with local training, SAINT is adapted, and CycleINR is an internal style reproduction. The fair performance reference is therefore the local common-support bank, not an incompatible paper number.

## Factor behavior

All five representative neural models have higher fastMRI MAE at x6 than x2. The x6/x2 ratios are 1.42 HAT, 1.49 SwinIR, 1.79 I3Net, 1.26 SAINT, and 1.60 CycleINR. This establishes difficulty sensitivity without implying a common mechanism slope.

The full 13-method table preserves Linear, Cubic, HAT, SwinIR, I3Net, SAINT, CycleINR, ArSSR, SMamba-UNet, Pix2PixGAN, ResUNet, Res-SRDiff and ACVTT. Absences are not filled from incompatible runs.

