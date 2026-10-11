# MSD BrainTumour frozen first-pair header result

The [pre-request rule](MSD_TASK01_HEADER_PILOT_PLAN_2026-10-01.md) fixed `BRATS_001` before any NIfTI byte-range request. The [machine-readable report](literature/source_cache/msd_task01_official_2026-10-01/brats001_header_pilot.json) records the source tar ETag, exact member paths/sizes, 4,096-byte compressed-prefix hashes, 352-byte header hashes and parsed NIfTI fields. The request returned HTTP 206 and the expected exact ranges. No full member or voxel data was decompressed; the GPU and locked IXI test were not used.

| Field | T2-containing image | Paired label |
|---|---|---|
| NIfTI magic | `n+1` | `n+1` |
| Shape | `240 x 240 x 155 x 4` | `240 x 240 x 155` |
| Type | `float32` | `uint8` |
| Spatial voxel size | `1 x 1 x 1` mm | `1 x 1 x 1` mm |
| qform/sform codes | `1/1` | `1/1` |
| Best affine | identity | identity |

The first-pair same-release-grid gate **passes** within the prespecified `1e-4` affine tolerance. This proves neither that the remaining 483 pairs match nor that the image/label voxels are valid; a full header qualification and a frozen label-region protocol precede pixel analysis. The identity affine and isotropic grid describe BRaTS preprocessing, not native MRI slice acquisition or native T2 thickness.
