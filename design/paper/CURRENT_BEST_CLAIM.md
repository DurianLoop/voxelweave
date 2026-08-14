# Current Best Claim

Status: `CONFIRMED_IN_SCOPE`; the claim is preserved independently of project status.

> Deterministic through-plane MRI interpolation error is dominated by examination- and sampling-dependent structure shared across architectures and contexts. Cross-context separation exposes the smaller context-sensitive component as a ground-truth-free one-sided error witness, but necessarily misses dominant consensus error when contexts share anchors or inductive biases. Physical sampling interventions are more informative than flip-TTA in the tested fastMRI setting, while acquired-anchor change offers a cheaper but domain-dependent proxy for intrinsic difficulty.

## Evidence envelope

- Case main effect: 58.3% fastMRI, 83.9% NingXia balanced-panel variance.
- Factor main effect: 25.8% and 12.5%; every one of 138 case–architecture units obeys x2 < x4 < x6 error.
- Architecture main effect: 10.3% and 0.6%; median neural-model error rho is 0.961 on fastMRI, and six-method rho is 0.991 on IXI.
- Exact MSE decomposition: shared consensus fraction 80.9%/86.5%, context-diversity fraction 19.1%/13.5%.
- Shared-anchor x4–x6 first-plane failure: stable-wrong rate delta 0.147 [0.030,0.286] on NingXia; curvature and synthetic deletion support the mechanism.
- Physical context versus flip-TTA: PC wins 18/18 dataset–factor–architecture profiles. Mean delta nAURC is -0.0340 on fastMRI (`p=0.0035`) and -0.1143 on NingXia (`p=0.0015`), with examination-clustered swaps.
- Pre-inference adjacent-anchor RMSE predicts raw error across fastMRI, NingXia, and independent IXI, but scale-controlled strength is heterogeneous.

## Scope boundary

The evidence concerns retrospective T2 brain slice interpolation and one independent IXI replication for pre-reconstruction features. It does not establish calibrated uncertainty, correctness certification, clinical harm, external anatomy/site generalization, or universal superiority over arbitrary perturbations.
