# CVPR 2026 compliance and scientific gate

Verified: 2026-08-13 against the official CVPR 2026 Author Guidelines.

## Format

- Official working `cvpr.sty` and `ieeenat_fullname.bst`, anonymous review mode, 10 pt, two columns, US letter.
- Official rule: at most eight pages containing paper content; additional pages may contain cited references only.
- `main.pdf`: 9 total pages. All main-paper content ends on page 8; references begin at the bottom of page 8 and continue alone on page 9. No paper content follows the reference heading.
- `supplement.pdf`: 5 legible pages. Official policy permits optional proofs, figures/tables, and detailed analyses; the supplement contains no newly tuned method or corrected submission.
- Final main log: no undefined citations/references, overfull boxes, underfull boxes, float-only pages, LaTeX errors, or fatal errors.
- Final supplement log: no undefined references, overfull/underfull boxes, LaTeX errors, or fatal errors.

## Scientific gate

- New content is supported by P6-E04–P6-E10: neural finite-difference influence, fixed-count control, registered chain, exact Anchor-CV audit, strong baselines, intrinsic-difficulty decomposition, frozen three-cohort risk curves, IXI+fastMRI benefit allocation, failure taxonomy, and measured cost.
- Three-cohort results use fastMRI + IXI + NingXia. The x4→x2 consequence experiment follows the permitted IXI + fastMRI two-dataset rule.
- Negative results remain explicit: overlap nonmonotonicity, NingXia fixed-count null, incomplete ranking arrow, non-unique Anchor-CV, harmful scale normalization/feature stacking, lack of plane localization, and no universal risk/budget winner.
- NingXia inference is clustered at eight patients, not 22 series.
- `CLAIM_TRACEABILITY.md` maps every central paper claim to a machine-readable artifact.

## Human submission blockers

- Replace the placeholder paper ID at submission time.
- Confirm that CVPR 2026 is the intended cycle; refresh the kit if targeting a later year.
- Supply author/affiliation only for camera-ready mode.
- Confirm NingXia ethics/consent wording and fastMRI/IXI data-use statements.
- Complete the mandatory CVPR 2026 compute-reporting form separately.
- Resolve venue strategy: do not concurrently submit the TMI and CVPR manuscripts if their scientific overlap violates either venue's dual-submission rule.
