# Baseline Recovery Audit

Audit date: 2026-08-14. Scope: recursive inspection of `D:\MRI\design`, `D:\MRI\design\paper`, and implementation/provenance paths referenced from those records under `D:\MRI\baseline` and `D:\MRI\pre`.

## Recovery decision

The historical model bank contains 11 neural reconstructors plus Linear/Cubic. It also contains later ACSI/PastNet research lines. Stored common-support results are real and extensive, but protocol eligibility differs from simple output availability. The P0 architecture-generalization candidates are I3Net, SAINT, and the locally adapted CycleINR-style model.

## Common data and evaluation contract

- fastMRI brain T2 split: 112 train / 24 validation / 24 test examinations, seed 3407.
- IXI T2 split: 404 train / 58 validation / 115 test examinations, seed 3407.
- NingXia T2: eight patient-group folds; each fold uses six patients for training, one for validation, and one held-out patient for test, yielding 22 held-out series from eight patients.
- Historical broad fidelity audit: generated slices only, common ground-truth-derived 1% foreground, identical MAE/MSE/PSNR/global-SSIM/NCC implementation.
- NingXia neural predictions used by the broad bank are eight-fold out-of-fold.
- Dense targets are allowed for retrospective metrics, never for deployment scores.

## Recovered methods and classification

| Method | Exact local implementation | Family | Provenance | x2/x4/x6 and datasets | Stored predictions/checkpoints | Mechanism feasibility | Classification |
|---|---|---|---|---|---|---|---|
| Linear | `ixi_diffusion.baselines` / common run folders | Analytical interpolation | Internal SciPy-style linear interpolation | fastMRI and NingXia x2/x4/x6; IXI x4 | Complete predictions; no checkpoint | Exact arbitrary physical contexts and coefficients | `CORE_MECHANISM_ELIGIBLE` |
| Cubic | Same analytical pipeline | Analytical cubic interpolation | Internal cubic interpolation | fastMRI and NingXia x2/x4/x6; IXI x4 | Complete predictions; no checkpoint | Exact arbitrary physical contexts and coefficients | `CORE_MECHANISM_ELIGIBLE` |
| HAT | `fastmri_brain_hat_2p5d`, `ixi_hat_2p5d`, NingXia OOF modules | Transformer/SR residual pair interpolator | Adapted local implementation | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions and checkpoints complete | Plan-8 controlled and influence protocols already complete | `CORE_MECHANISM_ELIGIBLE` |
| SwinIR | `fastmri_brain_swinir_2p5d`, `ixi_swinir_2p5d`, NingXia OOF modules | Transformer/SR residual pair interpolator | Adapted local implementation | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions and checkpoints complete | Plan-8 controlled and influence protocols already complete | `CORE_MECHANISM_ELIGIBLE` |
| I3Net | `fastmri_brain_i3net` / `ixi_i3net` / NingXia OOF; architecture loaded by `ixi_i3net.train.I3NetInterpolator` | Dedicated inter-/intra-slice CNN | Official I3Net architecture locally reproduced and retrained; not official weights | fastMRI x2/x4/x6; IXI x2/x4 and partial x6 artifacts; NingXia x4 OOF plus incomplete x2/x6 | fastMRI and IXI x4 predictions/checkpoints complete; NingXia x4 OOF complete | Same-target phase grids are feasible only from full dense source, because stored phase-0 `eval_gt` is truncated. Four equally spaced anchors must be preserved | `ARCHITECTURE_GENERALIZATION_ELIGIBLE` |
| SAINT | `pre\ixi_diffusion\saint.py` with dataset wrappers in `fastmri_brain_saint`, `fastmri_brain_t2_saint_expanded`, NingXia OOF | Spatially aware attention/CNN pair interpolation | SAINT-style adapted implementation; not the official repository/weights | fastMRI x4 complete; x2/x6 checkpoints and outputs exist but shared run manifests were later overwritten by ResUNet metadata; NingXia x4 OOF complete; no audited IXI SAINT run | x4 predictions/checkpoints complete on fastMRI/NingXia | Direct two-anchor context grid and physical-anchor perturbation are valid | `ARCHITECTURE_GENERALIZATION_ELIGIBLE` |
| CycleINR | `fastmri_brain_cycleinr`, `ixi_cycleinr`, NingXia OOF; uses `ixi_arssr.model.ArSSRNet` with cycle-consistency training | Implicit coordinate-based volumetric interpolation | Internal CycleINR-style reproduction, not verified as an exact official implementation | fastMRI x2/x4/x6; IXI x4; NingXia x4 OOF | Complete for those profiles | Same-target phase-grid test is valid with regular anchors; rich arbitrary pair contexts are not | `ARCHITECTURE_GENERALIZATION_ELIGIBLE` |
| ArSSR | `fastmri_brain_arssr`, `ixi_arssr`, NingXia OOF | Implicit 3-D feature encoder + coordinate MLP | ArSSR-style adapted implementation | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions/checkpoints complete | Technically similar intervention to CycleINR; retained as P1 because it does not add a new local architecture beyond the INR encoder already tested | `SUPPLEMENT_ONLY` |
| SMamba-UNet | `fastmri_brain_smamba_unet_2p5d`, IXI and NingXia modules | State-space U-Net pair interpolation | Internal/adapted implementation | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions/checkpoints complete | Arbitrary pair inference appears feasible but the Plan-9 physical probe has not yet been validated for this wrapper | `RECONSTRUCTION_BENCHMARK_ONLY` |
| Pix2PixGAN 2.5-D | `fastmri_brain_gan_2p5d`, IXI and NingXia modules | Conditional GAN/CNN pair interpolation | Internal adapted Pix2Pix-style implementation | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions/checkpoints complete | Pair context could be implemented, but it is P1 and not needed to establish the requested P0 family test | `RECONSTRUCTION_BENCHMARK_ONLY` |
| ResUNet | `pre\ixi_diffusion\resunet.py`, fastMRI/NingXia wrappers | Residual U-Net pair interpolation | Internal baseline | fastMRI and NingXia x2/x4/x6 artifacts; no audited IXI profile | Predictions/checkpoints exist; some outputs share SAINT run roots | Feasible in principle, but provenance must be separated from overwritten shared manifests before mechanism use | `SUPPLEMENT_ONLY` |
| Res-SRDiff | `fastmri_brain_ressrdiff_2p5d`, IXI and NingXia modules | Diffusion/residual interpolation | Internal adapted implementation | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions/checkpoints complete | Historical prediction breadth is valid; controlled deterministic influence protocol is not yet established | `RECONSTRUCTION_BENCHMARK_ONLY` |
| ACVTT | `fastmri_brain_acvtt_2p5d`, IXI and NingXia modules | Attention CNN | Internal adapted implementation; historical files consistently use `acvtt` | fastMRI/NingXia x2/x4/x6; IXI x4 | Predictions/checkpoints complete | No Plan-9 mechanism wrapper audited | `RECONSTRUCTION_BENCHMARK_ONLY` |
| ACVIT | No implementation or historical output found under the requested spelling | Unknown | Unverified | None | None | Cannot evaluate | `UNRECOVERABLE` |
| ACSI-Net | `design\acsinet`, `acsinet_v2`, and IXI ACSI evaluation line | Learned reconstruction/consistency | Internal research method | Primarily IXI x4; not common x2/x4/x6 coverage | IXI results/checkpoints exist | Not on the common architecture-generalization protocol | `INCOMPARABLE` |
| PastNet variants | `design\fastmri_brain_pastnet_2p5d`, `ixi_pastnet_2p5d` | Learned 2.5-D interpolation | Internal research family | Dataset/profile-specific research sweeps | Multiple checkpoints and selected outputs | Training and evaluation line differs from the frozen common model bank; inclusion would not add a clean independent family test | `INCOMPARABLE` |

## Important provenance findings

1. `fastmri_brain_saint/runs/full_x2` and `full_x6` contain both SAINT and ResUNet checkpoints/outputs. Their single `run_manifest.json` currently records `resunet_residual`, because the later ResUNet invocation overwrote shared metadata. SAINT checkpoint payloads independently record `saint_spatial_aware`, strides 2/6, and epochs 26/29. These profiles are usable only with explicit per-checkpoint provenance, not by trusting the manifest alone.
2. CycleINR uses the same `ArSSRNet` class as the ArSSR baseline but a different cycle-consistency training objective. It is therefore an INR-style training/interpolation paradigm, not an independently recovered official CycleINR codebase.
3. The historical `model_bank_registry.csv` reports complete fastMRI/NingXia x2/x4/x6 availability for all 11 neural methods, but this establishes benchmark availability, not mechanism compatibility.
4. Earlier Plan-4 code marked I3Net phase-shift inference infeasible because it used truncated stored `eval_gt`. The original full 16-plane fastMRI sources contain four phase-2 anchors and permit a valid new test without padding.
5. ACVIT was requested in Plan 9, but the recovered historical method is ACVTT. They are not silently equated.

## Evidence paths

- `D:\MRI\design\rasinet\model_bank_registry.csv`
- `D:\MRI\design\rasinet\corrected_reconstruction_fidelity.csv`
- `D:\MRI\design\rasinet\MODEL_BANK_AUDIT.md`
- `D:\MRI\design\paper\ARCHIVE\PLANS\PLAN02_TO_PLAN04\plan3_outputs\full_model_bank_error_panel.csv`
- `D:\MRI\design\paper\ARCHIVE\PLANS\PLAN02_TO_PLAN04\plan3_outputs\full_model_pair_correlations.csv`
- per-run `run_manifest.json`, checkpoint payloads, `per_case_metrics.csv`, and NIfTI output directories under `D:\MRI\baseline`

## Audit boundary

Exact original-paper citations for every added model are not inferred from filenames. They will be verified from primary sources in the Plan-9 literature audit before either manuscript is rewritten.
