# UPENN fixed-denominator sensitivity: result

**Status:** post-result algebraic sensitivity on the same frozen 374-patient, 1,496-target UPENN processed-DICOM predictions, not an independent cohort or new inference. The [formula and stop rule](UPENN_FIXED_DENOMINATOR_PLAN_2026-10-01.md) were written before this calculation but after the primary positive result. It used only archived target/patient metrics, no images, checkpoints or GPU.

For each target, `T_s` is the shared-condition paired MSE, and `D_s,D_d` are the shared/disjoint output-disagreement MSEs on the original fixed support. `Q_s=D_s/(4T_s)` and `Q_d=D_d/(4T_s)` use the **same denominator**. The script checked both original `O` identities against the stored `D` and `T`, reproduced the original patient-weighted `Delta O=0.2811561514882688`, averaged targets within residue then residues within patient, and resampled patients 5,000 times with fixed seed 20261001.

| Patients / targets | Shared Q | Disjoint Q | Delta Q | 95% post-result patient interval | Positive patients / targets | Original Delta O |
|---:|---:|---:|---:|---:|---:|---:|
| 374 / 1,496 | 1.3933% | 29.8894% | **+28.4961 points** | +28.2633 to +28.7296 points | 374/374; 1,496/1,496 | +28.1156 points |

The fixed-denominator contrast exceeds the original `Delta O` by 0.3805 points. A separate read-only pandas computation directly from the original per-target CSV reproduced patient-equal `Delta Q=0.2849607606634398` and both sign counts. The [analysis script](experiments/upenn_fixed_denominator.py), [summary](experiments/upenn_fixed_denominator/summary.json), [per-target](experiments/upenn_fixed_denominator/per_target.csv) and [per-patient](experiments/upenn_fixed_denominator/per_patient.csv) records preserve input hashes and exact values.

The target-level raw disagreement increase and positive fixed-denominator contrast rule out a changing paired-MSE denominator as the sole arithmetic explanation. They reuse the original predictions and do **not** prove acquisition identity or independent measurements. `T_s` uses withheld truth, so `Q` is retrospective and nondeployable; the disjoint partner still receives different neighboring images and signed geometry. The original UPENN selected DICOM series remain derived/secondary, paired MSE did not improve, and the expert tumor masks are aligned to a separate atlas NIfTI release.
