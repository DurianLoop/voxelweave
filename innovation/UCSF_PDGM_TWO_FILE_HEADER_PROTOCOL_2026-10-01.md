# Frozen UCSF-PDGM two-file header pilot (not yet executed)

This protocol follows the official [single-case file list](UCSF_PDGM_SINGLE_CASE_FILE_LIST_RESULT_2026-10-01.md). No transfer should start until a documented IBM Connect workflow is available. The source is TCIA UCSF-PDGM v5, public Faspex package `1065`, case `UCSF-PDGM-005` in `/UCSF-PDGM-v5/UCSF-PDGM-0005_nifti`. This case is a baseline visit and has no v5 `BraTS21 ID`; that does not prove identity independence.

The only allowed source members are the exact package paths below. The listing declares a combined 2,744,058 bytes. Set a 10 MB local byte cap and a 120-second transfer deadline, use an empty destination under `innovation/data/`, and abort if the returned transfer specification contains any additional path, package-wide ZIP instruction or unexpected source root. Do not archive credentials, cookies, signed URLs or a complete transfer specification. Record sanitized status, byte counts and SHA-256 of any complete files.

| Member path | Declared bytes |
|---|---:|
| `/UCSF-PDGM-v5/UCSF-PDGM-0005_nifti/UCSF-PDGM-0005_T2.nii.gz` | 2,693,713 |
| `/UCSF-PDGM-v5/UCSF-PDGM-0005_nifti/UCSF-PDGM-0005_tumor_segmentation.nii.gz` | 50,345 |

First validate that each downloaded gzip/NIfTI container is complete, then read headers only. Record dimension, voxel size, datatype, qform/sform codes and matrices, orientation codes and affine. The pair passes this preliminary spatial gate only if both are 3D, have exactly matching voxel-array shape and axis orientation, and the chosen world-space affine differs by no more than `1e-4` in every matrix element. A missing or contradictory qform/sform, unreadable file, absent mask or symlink failure is a recorded pilot failure, not a reason to substitute another case after seeing results. Do not resample a mask to force passage.

Header agreement does not prove valid tumor content, annotation coverage, or disjointness from MSD/BraTS/model development. Before any pixel-level metric, separately verify label nonemptiness and legal compartment values, complete an identity-overlap review, and freeze a new target-slice/ROI protocol with all patients and failures accounted for. Keep the original MSD cohort, this processed UCSF release and any UPENN DICOM study separate unless image-specific transforms have been established.
