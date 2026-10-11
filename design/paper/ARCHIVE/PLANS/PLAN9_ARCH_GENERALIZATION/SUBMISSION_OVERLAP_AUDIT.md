# Plan-9 TMI/CVPR submission-overlap audit

## Diagnostic result

The paragraph-level TF-IDF audit compares the final `TMI_ARCH_GENERALIZED/main.tex` and `CVPR_ARCH_GENERALIZED/PAPER/main.tex`, excluding tables, figures, and equations. Of 66 audited TMI paragraphs, three have maximum similarity at least 0.30 and one exceeds 0.45. The high-similarity diagnostic word fraction is 1.59%. This is not an iThenticate/CrossCheck score.

The single high-similarity paragraph is the numerical architecture-generalization result. Textual separation is therefore strong, but scientific overlap remains material because both manuscripts use the same fastMRI architecture experiment.

## Scientific ownership

- **TMI:** MRI reconstruction-QA behavior, broad reconstruction benchmark, metrics/factors/operating regimes, stable-wrong cases, selective risk, and the finding that multiple interpolation paradigms share a QA blind spot.
- **CVPR:** physical-measurement influence, count falsification, local error-alignment/cancellation chain, finite-response stability, and architecture-family mechanism boundaries.

## Governance decision

`MERGE_OR_SEQUENCE_REQUIRED`. Do not submit the two branches concurrently without checking both venue policies, disclosing shared cohorts/experiments, and obtaining an explicit authorship decision. Low textual similarity does not eliminate duplicate-publication risk.

Machine-readable evidence: `outputs/p9_submission_paragraph_overlap.csv` and `outputs/p9_submission_overlap.json`.

