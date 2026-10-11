# Matched-geometry synthetic-noise control: full MSValid result

**Status:** Post-result, synthetic mechanism control. The [plan](MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_PLAN_2026-10-01.md) was frozen before this inference, but after the original MSValid/ReMIND context results were known. CPU float32 inference used two PyTorch threads and did not touch the running GPU job or locked test set.

## Question and contract

The original phase-0 versus phase-2 comparison changes the companion's neighboring image content and signed geometry. Here HAT receives synthetic magnitude observations A from the same phase-0 planes in both conditions. SwinIR receives either A (shared noise) or B (independent noise), with B generated from the **same clean published planes at the same locations**. Target, HAT prediction, phase-0 geometry, common clean-anchor normalization range and acquired-only support remain fixed. A and B differ only in their generated noise arrays within each level. This isolates one simulated noise-realization contrast, not original MRI acquisition identity.

All 84 qualified MSValid patients and the exact original 479 targets were scored at **each** of two prespecified noise levels. The scale for each patient is the median strictly positive phase-0 anchor intensity; `sigma` is 1% or 5% of that scale. Independent real/imaginary Gaussian arrays were combined with the clean magnitude signal before taking magnitude. The same random arrays were reused across levels; seed `20261003`. Zero noise would force A=B and `Delta O=0` by construction, so it was not run through the models separately. There were no failures.

## Patient-weighted results

`Delta O_noise = O(HAT(A), SwinIR(B), y) - O(HAT(A), SwinIR(A), y)`. Values below are percentage points, except the two `O` columns, which are percentages. Targets were averaged within residue, residues equally within patient, then 84 patients equally. Intervals are 5,000-draw patient-bootstrap percentiles with the seeds fixed in the plan.

| Noise level | Shared `O` | Independent `O` | `Delta O_noise` | 95% patient interval | Positive / negative patients | SwinIR shared / independent MAE |
|---|---:|---:|---:|---:|---:|---:|
| 1% | 1.043211% | 1.042872% | -0.000339 | -0.001348 to +0.000604 | 41 / 43 | 130.3501 / 130.3495 |
| 5% | 1.043296% | 1.045825% | +0.002529 | +0.000276 to +0.004900 | 46 / 38 | 130.5006 / 130.5043 |

At 5%, the sign of the patient mean is positive and its unadjusted bootstrap interval excludes zero, but its magnitude is very small. The 1% interval includes zero. Both values are tiny beside the original phase-switch `Delta O=+24.1856` percentage points on these patients. This observation does **not** estimate what fraction of the original effect is due to noise, geometry or anatomy: the interventions and denominators are different, and no additive causal decomposition was specified. It says only that independent noise realizations in this particular same-geometry synthetic setup did not reproduce the large phase-switch contrast.

The noise fractions are arbitrary; this magnitude construction approximates rather than measures a clinical MRI noise process. The clean published plane is used as both synthetic signal and withheld target. The normalization extrema come from clean observed anchors and would not be available in the same form during deployment. Synthetic B is not an independently acquired scan; motion, scanner drift, coil/reconstruction effects and registration are absent. The MSValid patients and model pair had already informed the research program, so this is a post-result sensitivity test, not a new confirmation cohort. No inference about true repeated acquisitions or raw acquisition identity follows.

## Reproduction and integrity

- [Frozen inference script](experiments/msvalid_matched_geometry_noise_control.py), SHA-256 `202d920240c1c639fe67a667eb4adbd2d6299bb933468ff0c0f11813df7f1951`.
- [Independent read-only verifier](experiments/verify_msvalid_matched_geometry_noise_control.py) passed: exact 479-target list at both levels, original support and residue, 84 patient/residue means, all summary values, bootstrap seeds/intervals and direction counts.
- [Summary](experiments/msvalid_matched_geometry_noise_control/summary.json), SHA-256 `2348fd70ebd892dcb0ac2e2f7549276252830c965623c31e8a7394546ddbc3d8`.
- [Per-patient CSV](experiments/msvalid_matched_geometry_noise_control/per_patient.csv), SHA-256 `8d940f289182c829be4eddac57e2e3d8ddb2f65dffaff32d92851e74c689b5db`; [per-target CSV](experiments/msvalid_matched_geometry_noise_control/per_target.csv), SHA-256 `54ba60d33d013fd23d601d56631be192bf0b5bcc97d3ef591bc06fc11c55d24c`.
- [Pre-inference plan](MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_PLAN_2026-10-01.md), SHA-256 `46520424d55ddb20dd1bc2a474ba41b47f73ad149bc14e4374dc5e0cd435afb4`.

The raw CSVs retain source patient labels and remain internal pending release review. Rerun the verifier from `D:\MRI` with `D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_msvalid_matched_geometry_noise_control.py`.
