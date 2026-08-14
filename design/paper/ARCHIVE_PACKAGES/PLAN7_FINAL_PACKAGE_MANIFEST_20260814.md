# Plan7 final package manifest

- Package: `plan7_final_artifacts_20260814.zip`
- Date: 2026-08-14 (Asia/Shanghai)
- Scope: final Plan7 scientific artifacts; no automatic submission performed.

## Included roots

1. `PLAN7_ACCEPTANCE_OPTIMIZATION/`
   - all required Plan7 registers, reviewer simulations, novelty/venue/overlap audits, rebuttal banks and final report;
   - scripts and complete machine-readable experiment outputs, including P7-CV-E02 three-cohort stability shards and strict aggregate;
   - `PLAN7_COMPLETION_AUDIT.md` and JSON evidence (50/50 checks passed);
   - 23 rendered pages used for final visual audit.
2. `TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/`
   - eight-page `main.pdf`, `main.tex`, bibliography, redesigned figures, claim traceability, reviewer-risk audit and cover-letter draft.
3. `CVPR/CVPR_UPGRADE/PAPER_FINAL/`
   - eight-page `main.pdf`, seven-page `supplement.pdf`, LaTeX/bibliography, distinct Plan7 Fig. 1, claim traceability, reviewer-risk audit and rebuttal bank.
4. `plan7.md`
   - authoritative execution requirements.
5. This manifest.

## Final evidence decisions

- TMI: **READY AFTER HUMAN METADATA**, also requiring a submission-sequence decision.
- CVPR: **MERGE / CHANGE SUBMISSION SEQUENCE**; experiments are complete, but no tested capability consistently exceeds trivial baselines.
- P7-CV-E02: all 42 perturbation-parameter strata pass (minimum rank stability .942); two of three physical-plane gates fail (minimum .779), so influence is a local rather than plane-invariant probe.
- Final paragraph diagnostic: 0/63 TMI paragraphs exceed TF–IDF cosine .45 against 47 CVPR paragraphs; scientific overlap remains moderate-to-high and still requires sequence/merge review.

## Deliberate exclusions

- raw MRI datasets and model checkpoints;
- conda environments, caches and training workspaces;
- earlier ZIP archives;
- any claim that ethics metadata are complete or that either venue will accept the work.
