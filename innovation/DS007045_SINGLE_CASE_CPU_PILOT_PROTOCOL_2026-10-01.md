# ds007045 single-case clinical-metric feasibility pilot

Frozen before any full image fetch. This is exploratory protocol engineering, not a clinical or model-performance claim.

- Dataset: current public `ds007045` S3 objects, whose `dataset_description.json` names v2.0.1. Do not pool with the paper's v1.0.1/337 cohort.
- Subject: `sub-BA3`, because its processed T2 and tumor mask passed the [nonpixel geometry gate](DS007045_BA3_TWO_HEADER_RESULT_2026-10-01.json). Two exact objects are those in that result. This is a new full-content pilot, not a repeat of the header gate.
- Download only those two files to `innovation/data/ds007045_ba3_pilot/`. Require the S3-listed sizes 5,765,102 and 18,426 bytes; abort above 6 MB and 32 KB respectively. Record SHA-256. No other patient files.
- Use CPU only. Verify shape/affine and label values. Simulate x4 missing slices along image axis 2 with retained indices `0,4,8,...` and linearly interpolate each interior missing target from its two retained neighbors. The ground truth is the processed T2 on that same MNI grid, not independent native thin-slice anatomy.
- One volume-level intensity scale: observed positive-voxel 99th percentile, no access to withheld target for normalization. Report voxel counts and MAE separately in target-slice tumor labels (`mask>0`) and target-slice non-tumor brain (`mask=0` and target T2 positive). Report patient aggregate only and lesion-bearing target count. Do not compare these two MAEs causally or interpret mask-derived regions as a downstream segmentation result.
- Stop if download, geometry, finite intensity, or label checks fail. Do not run HAT, SwinIR or any GPU operation. Formal follow-up requires a frozen multi-patient denominator, independent-subject audit, an equal-observation comparator and a task endpoint with patient-level confidence intervals.
