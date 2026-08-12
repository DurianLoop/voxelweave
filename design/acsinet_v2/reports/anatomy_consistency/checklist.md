# ACSI-v2 Anatomy-Consistency Paper Checklist

Updated: 2026-07-14

## Paper Position

ACSI-v2 is a lightweight residual interpolation component for anisotropic MRI. It preserves observed sparse slices, starts from explicit linear coarse anatomy, and learns a bounded correction across a multi-anchor window. The claim is not generic reconstruction SOTA. The claim under test is whether explicit 3D supervision can improve through-plane structural fidelity at a small complexity budget.

This distinction matters. Through-plane MRI super-resolution is ill posed and can hallucinate plausible-looking detail; a smooth sagittal or coronal reformat alone is not evidence of anatomical correctness. We therefore evaluate prediction-to-GT agreement of z-gradients, z-Laplacians, edge changes, and adjacent-slice NCC profiles, together with reconstruction and visual QC. Sources: Sander et al., 2022 (semantic through-plane interpolation); Remedios et al., 2026 (cycle-consistent zero-shot through-plane MRI SR and hallucination concern); Geifman & El-Yaniv, 2019 (risk-coverage evaluation).

## 0. Claim Gate

- [x] Preserve ACSI-v1 evidence and do not overwrite its full_test115 results.
- [x] Preserve ACSI-v2's explicit coarse prior and observed-anchor preservation.
- [x] State that ACSI-v2 mini reconstruction slightly exceeds linear/cubic on two held-out cases.
- [x] State that the same mini result does **not** yet establish a 3D-consistency advantage: it is slightly worse than linear on ZGE/ZLE/EdgeZ and worse than cubic on NCC-z-MAE.
- [ ] Do not claim anatomy-consistency superiority over I3Net unless a paired full-set comparison and visual QC support it.
- [ ] Do not claim clinical anatomical validity without an anatomical downstream endpoint or expert evaluation.

## 1. ACSI-v2.1 Correction

- [x] Add a target-matched adjacent-slice NCC profile loss. It penalizes disagreement with the GT correlation profile rather than simply maximizing smoothness.
- [x] Add a dedicated `mini_consistency` profile: same data scale as mini, longer training, explicitly stronger z-aware weights.
- [x] Keep reconstruction and anatomy-weighted losses active to avoid trading away slice fidelity.
- [x] Train and evaluate `mini_consistency` (8 epochs, 8 train / 2 validation / 2 test cases).
- [x] Compare ACSI-v2.1 with linear and cubic on PSNR/SSIM/MAE/NCC plus ZGE/ZLE/EdgeZ/NCC-z-MAE.

### mini_consistency Result (2026-07-14)

| Method | PSNR | SSIM | MAE | NCC | ZGE | ZLE | EdgeZ | NCC-z-MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ACSI-v2.1 | 23.9142 | 0.7656 | 54.0037 | 0.8802 | 0.02095 | 0.03199 | 0.01194 | 0.10473 |
| Linear | 23.8926 | 0.7638 | 54.6535 | 0.8756 | 0.02086 | 0.03194 | 0.01187 | 0.10246 |
| Cubic | 23.3145 | 0.7435 | 60.9144 | 0.8548 | 0.02219 | 0.03276 | 0.01266 | 0.09518 |

Decision: do **not** promote this configuration to `full_test115`. It improves all listed reconstruction metrics against both interpolation baselines, but loses all four 3D metrics to linear and loses NCC-z-MAE to cubic. Its mean adjacent-slice NCC is `0.97949` while GT is `0.87477`, so the current target-matching NCC term did not resolve the observed over-smoothing at volume level. This is a screening result on two held-out cases, not a paper claim.

## 2. Decision Rule After Mini

- [ ] Promote to IXI full_test115 only if ACSI-v2.1 beats both linear and cubic on at least 3/4 consistency metrics, does not materially regress PSNR/SSIM, and has per-case evidence rather than one outlier-driven mean. Current result: **not met**.
- [ ] If it improves reconstruction but not consistency, retain it as a lightweight coarse-prior ablation, not the paper's anatomy-consistency method.
- [ ] If it improves consistency only by raising NCC above GT, reject the configuration as over-smoothing.

## 3. Full-Set Evidence Needed Before a Strong Claim

- [ ] Pair all methods on identical IXI full_test115 cases: ACSI-v2.1, linear, cubic, I3Net, and available strong baselines.
- [ ] Report paired bootstrap confidence intervals and per-case win rates for reconstruction and every 3D metric.
- [ ] Produce sagittal and coronal panels for best, median, and worst ACSI-v2.1-vs-I3Net cases, with GT and absolute-error views.
- [ ] Add a downstream anatomy proxy only if its preprocessing and failure modes can be audited; otherwise state that downstream validation is future work.
- [ ] Run loss/component ablations: coarse only; residual only; residual + z-refine; full without NCC-z; full ACSI-v2.1.

## 4. Paper Tables and Figures

- [ ] Main reconstruction and 3D-consistency table with identical cases and complexity (parameters and per-generated-slice FLOPs).
- [ ] Pareto plot: complexity vs ZGE/EdgeZ, clearly separating interpolation baselines from learned models.
- [ ] Per-case paired-difference plot and confidence intervals.
- [ ] Sagittal/coronal visual QC, selected by quantitative rule before visual inspection.
- [ ] Ablation table that shows which component changes consistency and whether reconstruction is retained.

## 5. Reviewer Attack List

- [ ] "NCC is just smoothness." Response: compare predicted NCC profile to GT and report ZGE/ZLE/EdgeZ; reject configurations with NCC above GT but worse target matching.
- [ ] "This is not a SOTA comparison." Response: frame the contribution as a low-complexity, coarse-prior component and report a transparent complexity-consistency Pareto comparison.
- [ ] "Metrics do not prove anatomy." Response: use the modest term `through-plane structural fidelity`, include visual QC, and state absence of a clinical endpoint as a limitation.
- [ ] "The method may hallucinate detail." Response: preserve anchors exactly, use residual bounded around a deterministic coarse prior, and show error panels on difficult cases.

## 6. Commands

Smoke after the code change:

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B design\acsinet_v2\tests\test_losses.py
D:\conda\envs\MRI\python.exe -B -c "import sys; sys.path.insert(0, r'D:\MRI\pre'); sys.path.insert(0, r'D:\MRI\design'); from acsinet_v2.run_all import run; run('smoke')"
```

Mini-consistency screening:

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -c "import sys; sys.path.insert(0, r'D:\MRI\pre'); sys.path.insert(0, r'D:\MRI\design'); from acsinet_v2.run_all import run; run('mini_consistency')"
```

Full evaluation is deliberately gated by Section 2 and is not launched automatically.
