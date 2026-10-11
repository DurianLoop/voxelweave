# MIRA internal manuscript revision (2026-10-01)

This directory is an independent scientific-review copy of `design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER`, not a submission package. The original manuscript was not modified. `main.pdf` is an 11-page, letter-size CVPR-style internal draft. It is three pages over the prior eight-page content target, and the historical supplement has not been synchronized.

## What changed

- The abstract and main text now distinguish the original fastMRI/IXI architecture matrix from the protocol-frozen, separately sourced MSValid single HAT-to-SwinIR comparison (84 patients, 479 targets, disjoint-minus-shared observability +19.7565 percentage points, patient-bootstrap 95% interval +19.3276 to +20.1605).
- MSValid methods specify the patient and target selection, x4 retrospective subsampling of native 3--6 mm T2 slices, acquired-only support, observed-only normalization, CPU FP32 inference and patient-level inference. This does not assert genuine thick-to-thin recovery.
- Post-result phase, linear and common-normalization checks are separate from the prespecified confirmation. The algebraic error-alignment decomposition is labeled descriptive.
- The SAINT response-mismatch counterexample and the 60-patient MSValid heldout influence-prediction failure are explicit. Continuous response influence is no longer presented as an externally validated actionable score.
- A later, post-result IXI-T2-trained HAT/SwinIR pair on the same MSValid patients is now reported separately: 84 patients/479 targets, disjoint-minus-shared `O` +24.1856 percentage points (exploratory 95% patient-bootstrap interval +23.7150 to +24.6726). It is explicitly not a second independent patient cohort or another prespecified confirmation.
- A subsequent source-specific protocol-frozen test on TCIA ReMIND preoperative T2 reports 62/63 patients and 248 targets, `Delta O` +26.3999 percentage points (95% stratified patient-bootstrap interval +25.6945 to +27.1686). Ordinary T2 and BLADE point estimates are separately positive. The protocol followed the MSValid finding, and the released DICOMs carry an MPR flag; neither a full architecture replication nor independent original-slice acquisition is claimed.
- Related work now names supervised MRI error intervals and intrinsic ambiguity decomposition as prior art. The MSValid dataset citation was checked against the live Zenodo record; author, title, date, DOI and license are recorded in `../literature/msvalid_zenodo_citation_audit_2026-10-01.md`.
- The old statement that no untouched source was available has been replaced. An internal-draft notice and unresolved data-rights/ethics notice appear on page 1.

## Evidence binding

- Protocol and primary MSValid result: `../MSVALID_CONFIRMATION_PROTOCOL_2026-09-30.md` and `../MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md`.
- Exploratory controls: `../MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md`, `../MSVALID_COMMON_NORM_RESULT_2026-09-30.md`, `../MSVALID_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-09-30.md`.
- SAINT mixed specificity: `../SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md`.
- Remaining-patient negative result: `../MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md`.
- Secondary IXI-weight result: `../MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md`.
- Second patient-source result and protocol: `../REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md` and `../REMIND_NATIVE_T2_CONFIRMATION_PROTOCOL_2026-10-01.md`.
- Prior-art boundary: `../literature/2026-09-30_hu_mira_overlap.md` and `../literature/2026-09-30_mira_uncertainty_neighbours.md`.

## Build and review

Built with MiKTeX `pdflatex`, `bibtex` and final `pdflatex` passes after adding the ReMIND source test. The final pass exited successfully; `main.log` has no undefined references, LaTeX errors or overfull boxes. `pdfinfo` reports 11 letter-size pages. All final pages were rendered to `remind_final_page-*.png` and checked in `remind_final_contact.png`, with a close review of the conclusion/reference transition; no clipping or overlapping text was seen. SHA-256 of `main.pdf`: `FDD5F0E362C989C560D4B8AFE52B12BC2EAAD6B94D55152524C3FF177A87BD30`.

MiKTeX's `latexmk` wrapper cannot run because Perl is absent; direct `pdflatex` and `bibtex` work. MiKTeX reported an AppData log-write warning under the sandbox, but the TeX commands exited zero and produced the verified PDF. No GPU process was touched.

## Before any submission

1. Obtain the author's actual fastMRI download/release mapping and image-publication permission; establish NingXia provenance, de-identification, ethics/consent and publication authorization, or remove the corresponding material after a new scientific and layout review.
2. Verify target venue/year, template, page and data policies. The MSValid dataset citation has been checked against the official Zenodo record. This internal header must not be mistaken for a conference submission.
3. Reconcile every old figure/table and the full supplement with the narrowed claim, including the MSValid result and negative response study; then reduce the scientific content to the target length and rebuild/inspect all pages.
4. Audit the final source package for patient imagery and data redistribution rights before sharing outside the project.
