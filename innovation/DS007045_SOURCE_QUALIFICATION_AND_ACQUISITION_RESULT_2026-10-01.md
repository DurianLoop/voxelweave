# ds007045: whole-cohort label geometry and native-T2 metadata gate

Two CPU-only, outcome-independent screens completed before any ds007045 model inference. The [frozen label/header rule](DS007045_COHORT_LABEL_QUALIFICATION_PROTOCOL_2026-10-01.md), [all-case summary](experiments/ds007045_cohort_label_qualification/summary.json), [raw-sidecar rule](DS007045_RAW_T2_ACQUISITION_METADATA_PROTOCOL_2026-10-01.md), and [all 363 official JSON responses](literature/source_cache/ds007045_raw_t2_sidecars_2026-10-01/summary.json) preserve sources, hashes, failures and decisions. The complete public S3 filename inventory had 363/363 processed T2/mask pairs; these screens establish a narrower eligible set. No GPU, T2 target pixels, model inference, or locked IXI test were used.

| Gate | Result |
|---|---:|
| Current v2.0.1 filename pairs attempted | 363 |
| Mask/T2 header matching, nonempty labels, four tumor-positive targets | 359 |
| Failed exact-grid pairs | 4: `sub-FO14`, `sub-KA34`, `sub-KA78`, `sub-KA84` |
| Raw T2 sidecars available | 363 |
| Raw `MRAcquisitionType=2D` | 327 |
| Raw `MRAcquisitionType=3D` | 35 |
| Acquisition type missing | 1: `sub-BO69` |
| 3D and raw `SliceThickness<=1.5 mm` | 34, all label-qualified |
| 2D with both thickness and spacing `<=1.5 mm` | 0 |

All four grid failures had 181 mm maximum affine difference; saved masks use a reversed z affine relative to the ordinary processed T2 template. Their anatomical correctness has not been established. They remain failures under the frozen exact-grid rule; no after-the-fact axis flip, registration, or target substitution was performed. The 359 qualified patients are **not** all independent 1-mm acquisition references.

Among the 327 raw 2D T2 sidecars, source slice thickness is 4 mm in 228, 5 mm in 59, 3 mm in 18, 2 mm in 9, 4.5 mm in 6, 6 mm in 3, and other 2.5-4.3 mm values in four. This was independently recounted from the 363 archived JSON files, not inferred from the processed image affine. The previously downloaded `sub-BA3` raw sidecar records 2D, 5-mm thickness and 6-mm spacing while its processed image is a 1-mm MNI grid. Its single-case x4 result therefore used interpolated/reformatted target planes, not native 1-mm acquired truth.

The 34 thin-3D metadata cases come from only three site prefixes: NSK 31, BA 2, FO 1. One other 3D case has 2-mm thickness. A 3D Fourier volume is not a set of independently excited 2D slices, but its stated native high-resolution volume is a better source for a volumetric x4 withholding test than 4-5-mm 2D scans upsampled to 1 mm. Image headers and raw-sidecar metadata alone still do not prove that all processed T2 voxel information is faithful to native acquisition, and the source remains MNI registered.

**Decision before model outcomes:** hold the [prepared 363-case processed-grid model protocol](DS007045_MODEL_REPLICATION_PROTOCOL_2026-10-01.md) for the original missing-slice claim. Its 250-case success floor is numerically reachable only by including predominantly thick 2D resampled cases; that would not validate native thin-slice recovery. A separate predeclared [34-case thin-3D CPU pilot](DS007045_THIN3D_MODEL_PILOT_PROTOCOL_2026-10-01.md) may test whether the existing MSD sign discordance persists on the strongest available T2 source stratum. It remains exploratory because 31/34 are from one center, prior-art collision and patient identity are unresolved, and no downstream task is measured.
