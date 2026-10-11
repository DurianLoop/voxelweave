# UPENN-GBM processed T2: full-cohort released-plane context audit

**Frozen primary endpoint: confirmed for the selected processed stratum.** This is a later, informed check of the existing fixed IXI HAT/SwinIR pair, designed after the MSValid and ReMIND results were known. It tests the [pre-pixel protocol](UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md), not original acquisition identity, a new reconstruction method or a deployment risk score. The source's formal [TCIA/DataCite citation](literature/upenn_gbm_official_citation_audit_2026-10-01.md) is Bakas et al. (2021), UPENN-GBM Version 2, DOI `10.7937/TCIA.709X-DN49`, CC BY 4.0.

## Selection and verification

The official archived NBIA inventory supplied 402 literal `Axial T2 tse: Processed_CaPTk` series from 374 patients. One earliest `(StudyDate,SeriesInstanceUID)` series per patient was fixed before target pixels; all **374/374** official ZIPs downloaded, 1,105,660,913 bytes total, with zero download or header failures. Nonpixel qualification fixed four odd targets per patient. The separate [source verifier](experiments/verify_upenn_gbm_processed_t2_sources.py) returned `PASS` after rehashing every ZIP, checking CRC/member identities, rereading **23,702** DICOM headers with `stop_before_pixels=True`, checking orientation, matrix and PixelSpacing, physical slice sorting and the four frozen targets. All **374** series are `DERIVED/SECONDARY/OTHER`; 367 have 3.0 mm physical steps and seven 4.8 mm, although all carry a `SpacingBetweenSlices=1 mm` tag. These facts describe the selected stratum, not all UPENN sequences or the unknown exact DICOM processing lineage.

The [CPU-only run](experiments/upenn_gbm_processed_t2_context/summary.json) reused the ReMIND inference and scoring path, frozen checkpoints and observed-only normalization. It completed **374/374 patients, 1,496/1,496 targets, zero pixel/inference failures** in 3,085 seconds. The [independent endpoint verifier](experiments/verify_upenn_gbm_processed_t2_context.py) returned `PASS` for source/protocol hashes, target membership, fixed-reference equality, per-target formula, residue/patient aggregation, 5,000 patient bootstrap draws (seed `20261004`) and the success predicate. It does not independently rerun the neural networks; the fixed reference implementation and checkpoint hashes are recorded in the run summary. No GPU or locked IXI test image was used.

## Frozen primary result

| Patient-equal endpoint | Result |
|---|---:|
| Shared released-plane `O` | 1.3933% |
| Disjoint released-plane `O` | 29.5089% |
| `Delta O = O_disjoint - O_shared` | **+28.1156 percentage points** |
| 95% patient bootstrap CI | **+27.9006 to +28.3309 points** |
| Positive / negative patients | 374 / 0 |
| Residue 1 / residue 3 mean `Delta O` | +28.1494 / +28.0818 points |

The prewritten success rule required at least 300 complete patients and a strictly positive lower bootstrap bound; both conditions passed. All 1,496 individual target `Delta O` values were positive in the later descriptive check. This is an empirical effect for a selected, derived public series and one fixed model pair. A narrow CI measures sampling variation under this patient bootstrap; it does not correct source selection, model selection, processing confounding or prior knowledge of two positive cohorts.

## Descriptive diagnostics, not new success criteria

The [descriptive output](experiments/upenn_gbm_processed_t2_context/descriptive_summary.json) gives 367 patients at 3.0 mm with mean `Delta O=+28.1692` points and seven at 4.8 mm with `+25.3054` points, all positive; the seven-person subgroup is too small for a new generalization claim. Patient-equal raw-intensity MAE is 101.21 for fixed HAT, 101.94 for shared SwinIR and 101.78 for disjoint SwinIR. Patient-equal paired MSE is **29,510.46 shared versus 29,601.78 disjoint**; there is no paired MSE gain to advertise. These raw DICOM-intensity errors are not cross-dataset normalized performance numbers.

A [post-result algebraic decomposition](experiments/upenn_gbm_processed_t2_context/posthoc_decomposition.json) closes to numerical precision (`1.67e-16`): +0.1491 points of `Delta O` come from the partner-MSE imbalance term and +27.9665 points from the error-alignment term under this exact formula. Mean shared/disjoint error cosine is 0.9722/0.4117. Reusing the shared paired-error denominator yields a descriptive +28.4961-point difference. This is a re-expression of the same 1,496 predictions, **not** independent mechanistic evidence or a causal attribution. The partner sees different released planes and asymmetric target offsets; anatomy, geometry, phase, normalization and unknown processing change together.

## Claim boundary and next gate

The previous fixed IXI pair yielded +24.1856 points on MSValid (84 patients/479 targets) and +26.3999 on ReMIND (62/248); UPENN adds a larger, separately processed TCIA stratum, but no proof that every plane was independently acquired. ReMIND has `MPR` tags, MSValid lacks its DICOM acquisition chain, and **all 374 UPENN selected series are derived/secondary**. Anonymous collection IDs cannot prove absolute patient non-overlap. Thus the result strengthens the **same-target released-plane context audit**, not pure measurement-identity causality, real thin-slice anatomy recovery, calibrated patient risk or clinical safety. The earlier linear-partner control also means the effect is not specific to two deep networks.

The next scientific gate remains an official, licensed source with documented independent repeated acquisitions at matched slice centers, followed by a frozen motion/noise/geometry protocol; without that source, retain the narrow empirical framing. Before external submission, obtain Kuestner 2024 full text and a target-venue prior-art check, reconcile IXI-derived checkpoint redistribution, complete clean reproduction, and have the actual authors settle venue and rights. The [Savant 2026 full-text audit](literature/2026-10-01_savant_formulation_fulltext_result.md) further rules out broad claims that input-context importance itself is novel.

The immutable run artifacts are [per-target CSV](experiments/upenn_gbm_processed_t2_context/per_target.csv) (SHA-256 `75b8c57cec7cfee06fef80e2516ee0fecab8c35da825c22b51678a332b2aa23e`), [per-patient CSV](experiments/upenn_gbm_processed_t2_context/per_patient.csv) (`1798e5d560841d4e6b5720367cec9c767ecdb7cd506d2e3d73eb75560b0d7858`) and [summary JSON](experiments/upenn_gbm_processed_t2_context/summary.json) (`9c2787fe2fbf7fdcc61463d249502c7c1e511af6b8743ec161e338a9a04e3ba2`). The downloaded DICOM ZIPs remain git-ignored local research data and are not publication assets.
