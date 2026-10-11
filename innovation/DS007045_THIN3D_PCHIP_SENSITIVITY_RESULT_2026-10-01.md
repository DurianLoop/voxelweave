# Thin-3D T2 PCHIP sensitivity: HAT signal persists, confirmation remains open

The [protocol](DS007045_THIN3D_PCHIP_SENSITIVITY_PROTOCOL_2026-10-01.md) was fixed **after** the original model outcomes but before any PCHIP values. The [CPU script](experiments/ds007045_thin3d_pchip_sensitivity.py) reused the 33 completed patients/132 frozen targets, exact source hashes and original ROI/normalization. `sub-NSK47` remains the original 34th attempted case with a network timeout. No model inference, download, GPU or locked IXI test was used. A first software run failed in all 33 cases because a list of preprocessed planes was indexed by a NumPy array; its [failure record](experiments/ds007045_thin3d_pchip_sensitivity/software_failure_before_fix.json) was retained. After a one-line indexing fix, all 33 completed. The [read-only independent verifier](experiments/verify_ds007045_thin3d_pchip_sensitivity.py) passed 33 case/132 target linkage, original-model score equality, eight bootstrap intervals and four sign counts.

Positive difference means model error is worse than PCHIP. Values are patient-equal normalized MSE differences with 5,000 patient-bootstrap 95% percentile intervals, seed 20261005. Raw PCHIP uses four phase-0 measured anchors on the released grid; pipeline PCHIP uses the same 256-pixel normalization/resize path as the fixed models. Both receive exactly the same observed slices as the models.

| ROI and comparison | Mean difference | 95% interval | Positive patients |
|---|---:|---:|---:|
| Tumor, HAT - raw PCHIP | +0.00020531 | [+0.00013636, +0.00027485] | 29/33 |
| Full support, HAT - raw PCHIP | -0.00078275 | [-0.00091335, -0.00065311] | 0/33 |
| Tumor, HAT - pipeline PCHIP | +0.00024992 | [+0.00018593, +0.00031319] | 30/33 |
| Full support, HAT - pipeline PCHIP | -0.00061310 | [-0.00072034, -0.00050779] | 0/33 |
| Tumor, SwinIR - raw PCHIP | +0.00004948 | [-0.00000510, +0.00010509] | 21/33 |
| Full support, SwinIR - raw PCHIP | -0.00077035 | [-0.00089206, -0.00065032] | 0/33 |
| Tumor, SwinIR - pipeline PCHIP | +0.00009410 | [+0.00004612, +0.00014544] | 22/33 |
| Full support, SwinIR - pipeline PCHIP | -0.00060069 | [-0.00069687, -0.00050592] | 0/33 |

Simultaneous tumor-worse/full-better signs: HAT versus raw/pipeline PCHIP 29/33 and 30/33; SwinIR 21/33 and 22/33. Raw/pipeline PCHIP themselves improve mean tumor normalized MSE relative to the original model-pipeline linear baseline by 0.00005288/0.00009750, respectively. The principal interpretation is **model- and baseline-dependent regional ranking**: HAT's secondary lesion deficit is not explained by using a weak linear comparator in this cohort. SwinIR's original predeclared tumor-harm test against pipeline linear failed, and the raw-PCHIP sensitivity interval also crosses zero; its post-result pipeline-PCHIP positive interval cannot replace that failed primary test.

This is one processed OpenNeuro release: 30/33 patients come from NSK, labels were informed by multiple MRI modalities, and the T2 targets were MNI-registered. Original metadata identified 3D T2 thickness <=1.5 mm, but the released planes are still resampled voxels rather than independent native acquired sections. Tumor-region MSE is not segmentation failure or clinical harm. The next meaningful test needs a second source with original thin-3D T2 provenance, exact same-grid labels, independent patient identity and a frozen task endpoint. UCSF-PDGM describes 3D T2 but its two-file Faspex transfer failed before headers; UPENN has thin-metadata leads but the available series are marked derived. Neither is currently an eligible confirmation.

The complete [per-target/per-patient CSV and summary](experiments/ds007045_thin3d_pchip_sensitivity/summary.json) and the original [pilot report](DS007045_THIN3D_MODEL_PILOT_RESULT_2026-10-01.md) should be read together. This sensitivity is useful for choosing a stronger future baseline, not for selecting a new primary result after seeing data.
