# Full-cohort nonpixel header qualification: UPENN processed axial T2

This is the **source/eligibility** stage of the [frozen published-plane context protocol](UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md), not the model endpoint. The selection uses the archived official NBIA series response, SHA-256 `bbae9a76f75a42cc35d460448c3afa87c55119d4ee5a84b9b18179fe28908de9`. Exactly one earliest `(StudyDate,SeriesInstanceUID)` row per patient was taken from the literal `Axial T2 tse: Processed_CaPTk` description, yielding 374 of 374 distinct candidate patients from 402 series. [Frozen inventory](literature/upenn_gbm_processed_t2_inventory.json).

Official NBIA `getImage` ZIPs were obtained for **374/374** selected series, including one copied from the earlier same-UID pilot ZIP after hash verification. There were zero transfer failures; combined ZIP bytes were `1,105,660,913`. Every ZIP was checked for member count and CRC and assigned a SHA-256 in the [download manifest](literature/upenn_gbm_processed_t2_download_manifest.json). Original DICOM ZIPs remain under git-ignored `innovation/data/upenn_gbm_processed_t2_audit/` and are not publication assets.

All **23,702** DICOM members were screened with `pydicom.dcmread(..., stop_before_pixels=True)`, with no `PixelData` loaded. The [qualification record](literature/upenn_gbm_processed_t2_qualification.json) reports **374/374 header eligible** under the frozen identity, 2D label, single-channel, matrix, orientation, pixel-spacing and physical-grid rules; it fixes exactly four odd-slice target indices per patient before decoding any target pixel. This verifies the *selected stratum*, unlike the earlier single-series pilot; it does **not** classify every other UPENN sequence.

| Header observation | Full selected stratum |
|---|---:|
| Uniform `ImageType=DERIVED/SECONDARY/OTHER` | 374/374 series |
| Physical adjacent-plane step about 3.0 mm | 367 series |
| Physical adjacent-plane step about 4.8 mm | 7 series |
| `SpacingBetweenSlices=1 mm` despite those physical steps | 374 series |
| 64-image series | 363 series |
| Other depths | 4 x 32, 3 x 60, 2 x 34, 1 x 59, 1 x 35 |
| Absent `SourceImageSequence` and `DerivationCodeSequence` | 23,702/23,702 headers |

The DICOM physical positions, rather than the contradictory nominal spacing tag, determine order and target geometry. The official collection page explains that its **NIfTI** derivatives were registered to an atlas and do not align with the DICOM images. It does not establish which exact transformations produced these DICOM series; their own `DERIVED/SECONDARY` flags and `Processed_CaPTk` label justify calling them processed, not claiming a specific registration step. The independent [read-only verifier](experiments/verify_upenn_gbm_processed_t2_sources.py) returned `PASS` for all 374 ZIP hashes, 23,702 nonpixel headers, physical ordering, PixelSpacing and frozen targets. The separate [CPU model result](UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md) is reported under its own endpoint and limitations.
