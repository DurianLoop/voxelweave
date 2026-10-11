# Public-source MIRA reproducibility supplement: internal draft

**Status:** Internal audit companion to the [three-source public-source manuscript text](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md), not a distributable submission bundle. The original sections below preserve the MSValid/TCIA ReMIND analysis history; the final addendum records the later informed TCIA UPENN-GBM processed-DICOM test. This file does not grant permission to redistribute downloaded images, patient-linked result rows or checkpoints.

## Evidence chronology

The MSValid IXI-weight pair was selected after a different fastMRI-weight pair had already been evaluated on the same 84 patients. Its [protocol](MSVALID_IXI_WEIGHTS_SECONDARY_PROTOCOL_2026-10-01.md) preceded this weight pair's MSValid inference, so it is a same-patient secondary result. The [ReMIND protocol](REMIND_NATIVE_T2_CONFIRMATION_PROTOCOL_2026-10-01.md) was written after MSValid results but before ReMIND pixels were decoded; it fixed the full TCIA series inventory, header exclusions, target layers, model pair, statistic and failure rule. The [common-scale/reverse](MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) [controls](REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md), [native-linear partner control](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md) and [matched-geometry synthetic-noise control](MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md) were designed after the corresponding main results. The noise plan was frozen before its own inference; neither it nor the other exploratory controls is an independent replication or a true repeated-acquisition test.

The [two-source fixed-denominator calculation](FIXED_DENOMINATOR_TWO_SOURCE_RESULT_2026-10-01.md) is another post-result algebraic sensitivity of the original prediction CSVs, with a [rule written before its calculation](FIXED_DENOMINATOR_TWO_SOURCE_PLAN_2026-10-01.md). It uses the shared paired MSE as both conditions' denominator. It adds no independent patient data, raw-image inference or deployable score.

The [two-source analytic PCHIP/linear falsification](TWO_SOURCE_ANALYTIC_CONTEXT_FALSIFICATION_RESULT_2026-10-01.md) was planned after the neural and linear-partner outcomes, then recomputed original released pixels on all 727 fixed targets without model inference. Its +29.2470/+30.9585-point `Delta O` and 146/146 positive patients show that a large phase-switch contrast is not learned-architecture-specific. The [read-only verifier](experiments/verify_two_source_analytic_context_falsification.py) independently checked all target metrics, patient/residue aggregations, four bootstrap intervals and one original NIfTI/DICOM pixel replay per source. These controls are exploratory falsifications on the same selected cohorts, not independent confirmations or a network contribution estimate.

The later [six-patient position-channel pilot](POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md) kept phase-0 anchor images, coarse image, normalization, reference, target and support fixed while changing SwinIR's relative-position input map to the phase-2 value. It is a post-result, out-of-contract sensitivity on 35 selected original targets, not a pure acquisition-identity intervention or independent validation. Its source-specific `Delta O_map` was +3.9182/+3.0666 percentage points, and companion MAE worsened. At that stage the two original full-source contrasts were the inferential endpoints; the later informed UPENN third-source test is recorded in the addendum.

The [within-patient target-error ranking check](TWO_SOURCE_TARGET_ERROR_RANKING_RESULT_2026-10-01.md) also reuses those original CSVs and the native-linear control. Its [rule](TWO_SOURCE_TARGET_ERROR_RANKING_PLAN_2026-10-01.md) preceded this association calculation but followed the positive main results. It is a target-level retrospective analysis, not an acquired-only or external deployment evaluation; the ReMIND improvement interval crosses zero.

The [equal-information interpolation controls](TWO_SOURCE_EQUAL_INFORMATION_CONTROLS_RESULT_2026-10-01.md) are further result-after analyses of the same 727 targets. Their sequential plans froze an algebraic ensemble consequence, a nearest-two-plane linear control and two four-plane cubic controls before each calculation. Source NIfTI/ZIP hashes, original targets and phase-0 support were checked; the disjoint ensemble did not clearly beat PCHIP on ReMIND. The [read-only verifier](experiments/verify_union_even_controls.py) rechecks 727 target records, 146 patient aggregates and all four cubic-control bootstrap intervals. No phase-2-based ensemble or score is available from phase-0-only x4 input, and the existing five-page PDF predates this new control paragraph.

## Inputs and fixed code

| Component | Current authoritative path / digest |
|---|---|
| IXI HAT checkpoint | `baseline/ixi_hat_2p5d/runs/full_test115/checkpoints/hat_epoch_best.pth`; SHA-256 `2fae831ab933cf260972260ebec4349f3895106ac7b4d1af3ba368f407498eae` |
| IXI SwinIR checkpoint | `baseline/ixi_swinir_2p5d/runs/full/checkpoints/swinir_epoch_best.pth`; SHA-256 `6a819e47e65bd96c2d6e5b6d3adc212e1a46347080a0a661c602367be8a6f323` |
| Current HAT wrapper source | `baseline/ixi_hat_2p5d/train.py`; SHA-256 `e10cd174b7aa366d1c281de4d611a2daa46ea4464bc1fde3a205d0d92e1f7e54` |
| Current SwinIR wrapper source | `baseline/ixi_swinir_2p5d/train.py`; SHA-256 `ad55a3f8404d16156b3d24b463978526d1dc9160059a3660da2145e005783e2f` |
| Current common normalization source | `pre/ixi_diffusion/common.py`; SHA-256 `fa7b57e5c58efd74a269c0e339feb9825ce729654adf4c636cd2bd03bb570818` |
| MSValid source qualification | [geometry snapshot](literature/msvalid_geometry_qualification.json) and [extracted NIfTI integrity manifest](literature/msvalid_extraction_manifest.json); the original inference script checks all 84 source file hashes |
| ReMIND source qualification | [63-series frozen inventory](literature/remind_native_t2_inventory.json), [header-only qualification](literature/remind_native_t2_qualification.json), [official ZIP download manifest](literature/remind_native_t2_download_manifest.json); the original inference script checks every eligible ZIP |

The three wrapper-source hashes are **current-state snapshots**, not hashes sealed in the original main-result JSON. They help locate code drift but alone cannot prove the historical state at the moment of inference. The frozen inference scripts, model hashes, source hashes, exact per-target outputs and read-only replay checks provide stronger provenance. Repository `HEAD` at this audit was `3fb5ebad44f509a67484239d9bcd5f9e4f8dcf97`; substantial research files were untracked, so that commit alone cannot reproduce these results.

## Patient and target contracts

MSValid uses the lexicographically first T2 NIfTI member for each of 84 RRMS patients from Zenodo DOI `10.5281/zenodo.10875606`, with 479 fixed residue-1/3 targets and native z spacing 3--6 mm. ReMIND uses every official preoperative `2D_AX_T2` and `2D_AX_T2_BLADE` series in the 63-series TCIA inventory (collection DOI `10.7937/3RAG-D070`), with one header-only exclusion for fewer than 24 layers, leaving 35 ordinary-T2 and 27 BLADE patients, each with four targets. Each dataset tests retrospective subsampling of **published native planes**. ReMIND DICOM `ImageType` contains `MPR`; no claim of independently acquired raw target planes follows from the 2D series labels.

ReMIND planes are ordered by physical z projection, not filenames or `InstanceNumber`. Phase 0 is `0,4,8,...`, phase 2 is `2,6,10,...`; targets have residue 1 or 3 and real bracketing planes in both phases. For each target, HAT phase 0 is the fixed reference `a`; SwinIR phase 0/2 supplies shared/disjoint partners. Inputs use all observed anchors for per-phase min/max and are resized to 256 x 256 for the local 2.5D models. The 1% absolute-intensity foreground support comes solely from the nearest phase-0 anchors and is shared between conditions. The native-linear negative control leaves `a`, `y`, support and target list unchanged and linearly combines each partner phase's two real native-intensity bracketing planes at the original quarter/three-quarter index offset. It does not correct for small allowed per-step z deviations in ReMIND.

For each target, `T=(MSE(a,y)+MSE(b,y))/2`, `O=mean((a-b)^2)/(4T)` on the fixed support. First average within residue 1 and residue 3, then average the two residue means within patient. Patient means, not slices, are the analysis units. MSValid uses 5,000 paired patient-bootstrap draws with seed `20261001`; ReMIND uses 5,000 draws with seed `20261002`, separately resampling ordinary T2 and BLADE at their completed patient counts and then weighting the groups 35/62 and 27/62. These intervals cover patient sampling conditional on the chosen model/cohorts; they do not cover research-history selection.

## Read-only checks in the current workspace

Run from `D:\MRI` in the existing environment. These commands read results and source hashes but do not start training or use the GPU:

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_msvalid_ixi_weights_secondary.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_remind_native_t2_ixi_pair.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_msvalid_ixi_weight_postresult_controls.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_remind_postresult_controls.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_public_linear_partner_control.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_msvalid_matched_geometry_noise_control.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_fixed_denominator_two_source.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_two_source_target_error_ranking.py
D:\conda\envs\MRI\python.exe -B innovation\verify_archive.py
```

All eight checks passed in the current workspace on 2026-10-01. Main `Delta O` values were MSValid `0.2418562290` (84 patients/479 targets) and ReMIND `0.2639991206` (62/63 patients, 248 targets). Native-linear partner values were `0.2054446587` and `0.2293858634`, respectively; its verifier replayed the exact target set and HAT MAE for all 727 targets. The matched-geometry noise verifier checked both 479-target sets, patient/residue aggregation and bootstrap intervals. The fixed-denominator verifier checked all 727 target formulae, 146 patient/residue means and both bootstrap intervals. Full summaries and target/patient rows are linked from the [MSValid result](MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md), [ReMIND result](REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md), [linear-control result](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md), [synthetic-noise result](MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md) and [fixed-denominator result](FIXED_DENOMINATOR_TWO_SOURCE_RESULT_2026-10-01.md). The raw result CSVs contain source patient labels and remain internal until release review.

An additional [observed runtime/source check](PUBLIC_ONLY_RUNTIME_PROVENANCE_2026-10-01.md) now records the Python and nine package versions actually present during CPU inference, verifies ten local model/normalization source hashes and reports the root `environment.yml` mismatch. It passed locally together with `pip check`; no clean new environment has been created or tested, so it is provenance rather than a distributable lock.

An anonymous [patient-level control figure](figures/PUBLIC_LINEAR_CONTROL_COMPARISON_NOTE_2026-10-01.md) joins each source's original and linear partner `Delta O`; its source manifest records the four CSV hashes. This figure is a descriptive comparison, not a controlled estimate of a neural-network contribution.

## Environment and external release gaps

This CPU audit ran under Windows Python 3.12.13, PyTorch 2.11.0+cu128 (CPU device only), NumPy 2.4.3, nibabel 5.4.2, pydicom 3.0.2 and scikit-image 0.26.0, with two torch threads. The repository [environment.yml](../environment.yml) says `numpy<2` and omits `pydicom`; it is **not an exact environment lock for this audit**. Before external reproduction, generate and test a clean environment lock, make the full model-code snapshot available, specify permitted access to IXI/MSValid/TCIA files, review IXI CC BY-SA implications for derived weights, and confirm each source's preferred formal citation. The [official ReMIND data citation](literature/remind_official_citation_audit_2026-10-01.md) has now been captured and inserted into the manuscript. No patient DICOM/NIfTI, original source ID table or checkpoint is declared publicly redistributable by this supplement. The [five-page PDF](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.pdf) is an internal scientific draft, not a venue-formatted submission.

## Later three-source addendum: processed UPENN-GBM

The [pre-pixel UPENN protocol](UPENN_GBM_PROCESSED_T2_CONTEXT_PROTOCOL_2026-10-01.md) was written after the MSValid and ReMIND positive results. It selected one literal Axial T2 tse: Processed_CaPTk series per patient from the official [NBIA inventory](literature/upenn_gbm_processed_t2_inventory.json), fixed all 374 patients and four targets per patient, then ran one IXI-trained HAT/SwinIR pair with CPU float32. The source record is [Bakas et al., UPENN-GBM Version 2](literature/upenn_gbm_official_citation_audit_2026-10-01.md), DOI 10.7937/TCIA.709X-DN49, CC BY 4.0. The [run summary](experiments/upenn_gbm_processed_t2_context/summary.json) seals the protocol, inference and source hashes, both checkpoint hashes and the 374/1,496 success count. The [result report](UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md) gives patient-equal Delta O 0.2811561515, 95% patient-bootstrap interval [0.2790058845, 0.2833088590], zero failures and all positive patient differences. The interval is conditional on this informed selection and fixed source.

Two independent read-only checks cover different risks: [source verification](experiments/verify_upenn_gbm_processed_t2_sources.py) rehashes every selected ZIP, checks CRC/member identity and rereads all 23,702 nonpixel DICOM headers, UID/geometry/target qualification; [endpoint verification](experiments/verify_upenn_gbm_processed_t2_context.py) replays target formulae, frozen HAT reference, patient/residue aggregation and bootstrap draws from stored outputs. Both returned PASS again in the present workspace on 2026-10-01. Neither reruns both neural networks in a fresh environment. Run from the repository root:

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_upenn_gbm_processed_t2_sources.py
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_upenn_gbm_processed_t2_context.py
```

All 374 selected DICOM series are DERIVED/SECONDARY/OTHER. The official [label alignment check](UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md) confirms expert-corrected atlas NIfTI segmentation does not align with the DICOM series by design; no label metric was run. A separate [metadata feasibility audit](UPENN_GBM_NIFTI_LABEL_FEASIBILITY_RESULT_2026-10-01.md) and one [thin-grid nonpixel pilot](UPENN_GBM_THIN_T2_HEADER_PILOT_RESULT_2026-10-01.md) prepare, but do not execute, a distinct atlas-NIfTI task study. The old five-page PDF cited above predates this third source and is a **two-source snapshot**. A clean environment reproduction, final venue manuscript build, rights review and real-author approval remain open.
