# ds007045 bounded two-header protocol

Purpose: check whether one current public processed T2 and expert-reviewed tumor mask have compatible NIfTI geometry. This is a source gate only, not a clinical endpoint or model experiment. No GPU, locked IXI test, or image pixels.

Source: OpenNeuro `ds007045`. Its current `dataset_description.json` identifies DOI `10.18112/openneuro.ds007045.v2.0.1`, CC0, and a 363-person cohort. The article cites v1.0.1/337; this pilot **does not** validate that earlier version. The current S3 listing and `CHANGES` are archived in `literature/source_cache/ds007045_pair_inventory_2026-10-01/`.

Freeze before request:

- Subject: first alphabetically listed available case, `sub-BA2`.
- Processed T2: `ds007045/derivatives/processing/sub-BA2/sub-BA2_t2_MNI152_brain.nii.gz` (listed size 5,993,091 bytes).
- Label: `ds007045/derivatives/segmentation/sub-BA2/sub-BA2_MNI152_tumor-mask.nii.gz` (listed size 18,910 bytes).
- Endpoint: official public S3 objects under `https://s3.amazonaws.com/openneuro.org/`.
- Send byte range `0-65535` for each object, single request and no retry. Abort if server ignores range and sends more than 65,536 bytes. Maximum aggregate retained compressed data: 131,072 bytes. Archive only status, content-range, SHA-256 of returned bytes, and parsed nonpixel header fields; discard returned bytes after parsing.
- Decompress only the first 352 uncompressed bytes of each gzip stream. Use nibabel's NIfTI header parser to record shape, voxel spacing, qform/sform code and affine. Compare shape and affine (`allclose` tolerance 1e-4 mm); report any difference. If either header cannot be decoded within the cap, stop. Do not decode voxel data or infer label validity from a matching header alone.

If the gate passes, a separate predeclared clinical protocol must choose version, exclude cross-cohort identity overlaps, fix eligible slices/patient denominator and task metrics, and obtain actual mask/image content before any task claim.
