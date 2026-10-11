# UPENN-GBM corrected-label thin-T2 header pilot

The [pre-download plan](UPENN_GBM_THIN_T2_HEADER_PILOT_PLAN_2026-10-01.md) fixed the lexicographically first patient/series among 83 NBIA T2 SAG SPACE: Processed_CaPTk candidates whose subject prefix appears in the 86 corrected-label baseline rows with an approximately 0.9 mm T2 thickness field. Only that official NBIA ZIP was downloaded. The [header result JSON](literature/upenn_gbm_thin_t2_header_pilot.json), SHA-256 0cd80441ab70a7f5a959e3417c8485d1fe8e0325243ee9c7f49fd3a0d85aef36, records URL, frozen source/plan/script hashes and all technical summaries. The 7,880,691-byte ZIP (SHA-256 32663a8b7887d070f5d1267cb8a9c9be8400a8b6b6ea66bd1beb7d64ddc057ae) remains in the git-ignored local pilot directory; no patient image is in the publication artifacts.

| Nonpixel check | Frozen first series |
|---|---:|
| DICOM members / unique SOP UIDs / CRC failures | 192 / 192 / 0 |
| ImageType | DERIVED/SECONDARY/OTHER, 192/192 |
| MRAcquisitionType | 3D, 192/192 |
| Physical projected layer step | 0.900000016 mm throughout |
| SliceThickness / nominal SpacingBetweenSlices | 0.900000036 / 1 mm |
| Matrix / in-plane PixelSpacing | 320 x 256 / 0.896875 x 0.896875 mm |
| SourceImageSequence / DerivationCodeSequence present | 0/192 / 0/192 |
| PixelData decoded | no |

The [independent nonpixel verifier](experiments/verify_upenn_gbm_thin_t2_header_pilot.py) returned PASS after rehashing the ZIP, checking its CRC, rereading all 192 headers with stop_before_pixels, and independently recalculating the physical step and UID uniqueness. The inference models and GPU were not used; locked IXI test data were not touched.

**Decision:** the official release contains at least one real, regular 0.9 mm **published 3D T2 grid** in the corrected-label subject-prefix pool. It does **not** establish that the released DICOM planes are original measurements: all 192 are explicitly derived/secondary, and no source-image chain is present in these headers. This single selected case cannot classify the other 82 series or prove its atlas NIfTI/mask is present, aligned or geometrically equivalent. It cannot support a native thin-reference, original-acquisition identity or lesion-outcome claim for the existing 374-patient DICOM audit.

The [atlas-NIfTI task feasibility gate](UPENN_GBM_NIFTI_LABEL_FEASIBILITY_RESULT_2026-10-01.md) remains conditional on obtaining the official package and verifying each exact T2/label grid. Any new x4 target evaluation on this processed release must report its 3D acquisition/registration history, compare equal-information baselines and avoid calling atlas-resampled planes independent acquired slices. If package access or same-grid pairing fails, stop the task-level branch and retain the narrow released-plane audit.
