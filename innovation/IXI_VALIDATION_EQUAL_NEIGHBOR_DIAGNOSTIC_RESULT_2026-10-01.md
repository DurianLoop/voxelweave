# IXI validation-only diagnostic: frozen models versus the same two-neighbor linear baseline

The [post-result protocol](IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_PROTOCOL_2026-10-01.md) used only the 58 frozen IXI T2 **validation** cases and four prespecified geometry-only targets per case. The [CPU script](experiments/ixi_validation_equal_neighbor_diagnostic.py) loaded the unchanged IXI HAT/SwinIR checkpoints with explicit `device="cpu"`, `CUDA_VISIBLE_DEVICES=-1` and two Torch threads. It did not open IXI test images or run training. All 58 cases and 232 targets completed; source SHA-256, exact target indices, checkpoint hashes, case outputs, [per-target CSV](experiments/ixi_validation_equal_neighbor_diagnostic/per_target.csv), [per-patient CSV](experiments/ixi_validation_equal_neighbor_diagnostic/per_patient.csv), [run contract](experiments/ixi_validation_equal_neighbor_diagnostic/run_contract.json) and [summary](experiments/ixi_validation_equal_neighbor_diagnostic/summary.json) are archived.

| Same acquired-only foreground, patient-equal MSE | 58-case IXI validation |
|---|---:|
| Raw two-neighbor linear0 | 6,868.34 |
| Model-pipeline linear0 | 6,868.34 |
| HAT0 | 4,945.28 |
| SwinIR0 | 5,014.36 |
| **HAT minus raw linear** | **-1,923.06** (95% patient bootstrap -2,622.95 to -1,293.59); 57/58 patients lower |
| **SwinIR minus raw linear** | **-1,853.99** (-2,530.54 to -1,251.82); 57/58 lower |

The sole patient where both models have higher MSE than linear is `IXI313`; it remains in all estimates. Raw and pipeline linear differ by only about `0.000006` MSE in the patient mean because IXI images here are already 256-square, while the registered MSD images required 240→256→240 resizing. A separate PowerShell read of all 58 patient rows reproduced the two paired means and 57/58 sign counts. The independent case/formula/bootstrap verifier is [here](experiments/verify_ixi_validation_equal_neighbor_diagnostic.py).

This verifies that the fixed code path and checkpoints can improve whole-support x4 interpolation over two-neighbor linear in a familiar IXI validation cohort. It also rules out treating the MSD tumor deficit as a universal failure of these checkpoints. **It does not isolate a causal domain-shift or tumor-specific effect:** these 58 validation cases selected model checkpoints, the IXI masks/target choice differ from MSD's tumor-positive target selection, and IXI has no matched tumor ROI here. In MSD's *same-case full foreground*, HAT is nearly tied and SwinIR has a mean advantage over raw linear, while both lose in tumor ROI; see the [MSD full-support result](MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md). Cross-source raw MSE magnitudes are in incomparable intensity scales.

The next evidence gate is an independent, aligned T2 pathology cohort or a prospective task-level evaluation with a frozen acquired-only predictor. A new model or fallback rule trained after these findings would require untouched confirmation data and comparisons to both raw and pipeline linear. Existing abnormality-fidelity papers already cover the broad “global metrics hide pathology error” point, so the present result is a diagnostic, not a publishable novelty certificate.
