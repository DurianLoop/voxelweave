# Plan7 research state

Last updated: 2026-08-14

## Objective and frozen constraints

Minimize avoidable scientific rejection risks for two MRI inter-slice interpolation submissions. Plan1–Plan6 evidence is preserved. `ANCHOR_CV_V1` is frozen; dense targets are evaluation-only; NingXia has eight independent patient clusters; no diagnostic, patient-safety, causal-mediation or prospective-acquisition claim is allowed.

## Hypothesis portfolio

| ID | Hypothesis | Frozen falsification rule | Current status |
|---|---|---|---|
| P7-CV-H01 | Minimum neural-influence context selection outperforms count/random/trivial scores. | No locked transfer advantage on >1 dataset/architecture. | **FALSIFIED** by P7-CV-E01. |
| P7-CV-H02 | Multi-anchor jackknife adds beyond adjacent MAE. | No conditional/held-out gain on at least two cohorts. | **FALSIFIED** by P7-CV-E03. |
| P7-CV-H03 | Zero-fit influence residualization recovers hidden error ranking. | Failure versus raw disagreement/simple comparators on locked confirmation/transfer. | **FALSIFIED** by P7-CV-E04. |
| P7-CV-H04 | Neural finite-difference influence is stable to perturbation and plane choices. | Per condition: rank stability >=.85 in >=5/6 strata and none <.70; report endpoint changes and counterexamples. | **PARTIALLY SUPPORTED:** all perturbation-parameter gates pass; plane invariance fails. |
| P7-TMI-H01 | Consensus blindness changes fixed-coverage QA decisions. | No clustered reduction in false retention. | **PARTIALLY SUPPORTED**; strongest IXI 70% regime. |
| P7-TMI-H02 | Metric heterogeneity follows a universal spectral-family ordering. | Directional incoherence across models/cohorts. | **FALSIFIED**. |

## Manuscript state

- **TMI:** Plan7 final candidate compiles to eight pages. Physical-intervention novelty, operational QA consequence, endpoint boundary and operating regime are integrated. Required traceability/risk/cover-letter files exist. Scientific recommendation is `READY AFTER HUMAN METADATA`, subject also to submission sequencing.
- **CVPR:** E02 is complete. The eight-page mechanism/findings candidate reports perturbation robustness and plane dependence alongside three failed method gates. Scientific experiments are complete, but the recommendation remains merge/change sequence rather than concurrent submission.
- **Cross-paper:** diagnostic paragraph overlap is low, but scientific overlap is moderate-to-high. `MERGE_OR_SEQUENCE_REQUIRED` remains active; no concurrent-submission approval is inferred.

## Completion state

Plan7 scientific work is complete and passes the 50-item audit in `PLAN7_COMPLETION_AUDIT.md`. All registered high-value experiments, manuscript integrations, final reviewer simulations, overlap analysis, compilation/log checks and page-level visual audits are complete. Remaining actions are human/external: exact ethics/consent and author metadata, submission sequencing/disclosure, or genuinely new prospective/external data.

## Stop-rule application

Mechanism-derived training is not launched because Plan7 required influence to be stable **and operationally useful** before that expense. Context selection and residualization failed the operational gate. Remaining non-E02 weaknesses require human ethics metadata, prospective acquisition/readers, new external cohorts, or a venue/sequence decision.
