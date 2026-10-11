# UCSF-PDGM v5 public package: one-case file listing

Following the [preselected file-list plan](UCSF_PDGM_SINGLE_CASE_FILE_LIST_PLAN_2026-10-01.md), the official TCIA v5 link authorized a read-only Faspex public session. The [nonsecret root listing](literature/source_cache/ucsf_pdgm_public_package_metadata_2026-10-01.json) returned HTTP 200 for `/` and `/UCSF-PDGM-v5`; the latter contains 501 directory entries. After removing the package's extra numeric zero padding and `_nifti` suffix, all 501 directory IDs match the 501 v5 CSV IDs exactly, including six `_FU...` visits. Authorization returned 302 and token exchange 201; no bearer token, authorization code or transfer specification was archived.

The exact [frozen `UCSF-PDGM-005` directory listing](literature/source_cache/ucsf_pdgm_005_file_list_2026-10-01.json) returned HTTP 200, 24 entries, with the expected same-directory symbolic links:

| Exact v5 member | Declared bytes |
|---|---:|
| `UCSF-PDGM-0005_T2.nii.gz` | 2,693,713 |
| `UCSF-PDGM-0005_tumor_segmentation.nii.gz` | 50,345 |

The case is the lexicographically first baseline v5 metadata ID with an empty `BraTS21 ID`. That emptiness is **not** an independence certificate. The listing confirms file-name presence and same-case package placement only. These entries are symbolic links; their targets, compressed payloads, NIfTI shape, orientation, affine and label values are untested. No file download or patient-pixel read occurred, and the GPU and locked IXI test were untouched.

The next gate is a vendor-supported, exact-two-file Connect transfer capped to these paths, followed by header-only validation and a separate overlap audit. Do not use the listed names to run a tumor ROI metric or to assert aligned labels. The [source qualification report](UCSF_PDGM_INDEPENDENT_T2_LABEL_SOURCE_GATE_RESULT_2026-10-01.md) contains the broader population, provenance and causal limits.
