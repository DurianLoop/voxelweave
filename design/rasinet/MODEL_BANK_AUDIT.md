# Model Bank Audit

## Scope

- Audited neural reconstructors: 11.
- Audited analytical interpolators: Linear and Cubic.
- Availability contract: every listed model has complete finite predictions on fastMRI-brain and NingXia at x2, x4, and x6; NingXia predictions are eight-fold out-of-fold.
- All cross-model fidelity metrics use the same offline ground-truth-derived 1% foreground and generated slices only. This support is never used by deployment scoring.

## Corrected Selection

- Corrected rank changes relative to the old model-specific-mask comparison: hat 6->3, smamba_unet 3->4, pix2pixgan 4->5, swinir 5->6, arssr 10->9, cycleinr 9->10.
- Main targets, fixed before NingXia outer evaluation: i3net, saint, hat, smamba_unet, pix2pixgan, swinir.
- Candidate peer bank: i3net, saint, hat, smamba_unet, pix2pixgan, swinir, linear, cubic.
- Main-target rule: top half of neural reconstructors by the pre-defined composite rank over common-support MAE, MSE, PSNR, global SSIM, and NCC.
- Peer-bank rule: the six highest-ranked neural peers with at most two members from one architecture family, plus Linear and Cubic.
- Every target is removed from its own committee at scoring time.

## Terminology and Governance

The bank is a common-bank, availability-conditioned rule. It is not called a fixed universal committee because target exclusion changes membership and selected subsets may depend on the known interpolation factor and target identity. No NingXia outer-fold error, nAURC, or attribution label was used to define the bank or main targets.

The machine-readable source is `outputs/nested_optimization/model_bank_registry.csv`.
