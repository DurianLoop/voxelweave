# Plan6 final audit

Date: 2026-08-13

## Outcome

Plan6 is complete. Both paper tracks were expanded through new experiments and theory rather than prose padding. The required artifacts remain entirely under `D:\MRI\design\paper`.

## TMI track

- Research master: `TMI/TMI_MANUSCRIPT_MASTER/main_20page.pdf`, 19 dense IEEE double-column pages including references (within the requested 18–20 range).
- Independent submission version: `TMI/TMI_MANUSCRIPT_SUBMISSION/main.pdf`, 8 pages including references and below the verified 10-page TMI initial-submission ceiling.
- Evidence added: full consensus decomposition, factor/model/metric robustness, geometry and intensity controls, clustered statistical audits, risk–coverage, retrospective densification, error taxonomy, and measured deployment cost.
- Supporting ledgers: `PAGE_GROWTH_LEDGER.md`, `NEW_EXPERIMENTS.md`, and `CLAIM_TRACEABILITY.md` in the master directory.

## CVPR track

- Main: `CVPR/CVPR_UPGRADE/PAPER/main.pdf`, 9 pages total. All scientific content ends on page 8; references begin at the bottom of page 8 and continue alone on page 9, satisfying the official eight-content-page rule.
- Supplement: `CVPR/CVPR_UPGRADE/PAPER/supplement.pdf`, 5 pages of full strata, confidence intervals, frozen protocols, negative results, qualitative failures, and reproducibility mapping.
- Evidence added: neural finite-difference shared influence, exact fixed-count control, arrow-wise mechanism audit, frozen Anchor-CV reproduction and strong trivial baselines, architecture-independent difficulty, full risk curves, IXI+fastMRI x4→x2 consequence, failure taxonomy, and measured cost.
- Stale pre-Plan6 ranking/budget figures were replaced by `plan6_anchor_cv_audit.pdf` and `plan6_ixi_x2_budget.pdf`, generated directly from frozen CSV tables.
- Final main and supplement logs contain no undefined citations/references, overfull/underfull boxes, float-only pages, or fatal errors.

## Three-dataset rule

- Main mechanism and reliability experiments use fastMRI, IXI, and NingXia.
- The two-dataset densification consequence uses the permitted IXI + fastMRI pair.
- NingXia is always treated as eight patient clusters containing 22 series.

## Material negative results retained

- Integer overlap is not a monotone law.
- Fixed-count neural influence is null/mixed on NingXia.
- The local cancellation chain is stronger than the context-ranking chain; no causal mediation claim is made.
- Anchor-CV is strong but statistically indistinguishable from adjacent MAE/RMSE and is not uniquely informative.
- Scale normalization and naive feature stacking can harm performance.
- Examination scores do not localize the worst plane.
- No risk or benefit score is universally best.
- Densification results are retrospective, not prospective acquisition optimization.

## Policy and human-only blockers

- CVPR 2026 official guidance was rechecked: eight pages including figures/tables, with additional reference-only pages allowed; supplementary material may contain detailed analyses but not an improved/corrected method.
- Before an actual submission, humans must replace paper IDs, confirm ethics/data-use wording, complete the CVPR compute-reporting form, and choose a venue strategy compatible with dual-submission rules.
