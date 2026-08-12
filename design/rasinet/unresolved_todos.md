# Unresolved Items

This file separates missing evidence from work already implemented or running. No placeholder below may be converted into a numerical claim without a traceable output file.

## 1. Comparable Online Neural Inference Cost

- Missing: per-examination latency, peak GPU memory, and hardware-matched parameter counts for I3Net, HAT, SwinIR, and ACSI under one benchmark protocol.
- Needed files/data: loadable checkpoints and inference entry points for every model, plus an idle GPU window.
- Command: to be added only after each model's exact checkpoint and preprocessing contract are verified; historical logs are not comparable enough for a single command.
- Expected output: `outputs/deployment_cost/model_inference_cost.csv`.
- Claim impact: prevents a quantitative statement that online committee deployment is cheap; does not invalidate stored-output retrospective scoring.
- Must resolve before submission: recommended, but not required if the paper clearly limits measured cost to post-hoc scoring and labels online cost unavailable.

## 2. Additional Factor or Contrast

- Missing: complete, case-matched outputs from at least two neural interpolators plus linear/cubic and ground truth at x2 or x8, or on T1/FLAIR.
- Needed files/data: validated prediction manifests for every committee member.
- Command: use `run_reliability_evaluation.py` after adding a profile to `committee_experiments.profile_sources` and a frozen YAML config.
- Expected output: `outputs/icassp_factor_or_contrast/summary.csv` and registry rows.
- Claim impact: current conclusions remain limited to factor-four T2 brain MRI.
- Must resolve before submission: no, provided title/abstract/conclusion remain narrowly scoped.

## 3. Reader Study and Diagnostic Endpoint

- Missing: reader annotations or a preregistered downstream clinical task.
- Needed files/data: ethics approval, readers, task labels, and analysis plan.
- Command: not applicable to the current retrospective reconstruction-error study.
- Expected output: a separate reader-study dataset and statistical report.
- Claim impact: prohibits claims of diagnostic safety, clinical correctness, or replacement of clinical validation.
- Must resolve before submission: no; it must remain an explicit limitation.

## 4. Dataset Ethics and Access Wording

- Missing: author-confirmed institutional wording for NingXia data access, de-identification, and ethics/waiver; final funding statement.
- Needed files/data: approval or waiver identifier and funding metadata from the authors.
- Command: none.
- Expected output: final compliance paragraph in both manuscripts.
- Claim impact: affects submission compliance, not numerical results.
- Must resolve before submission: yes.

## 5. Official ICASSP 2027 Template Release

- Missing: a downloadable ICASSP 2027 LaTeX kit. The official 2027 page states the 4+1 and 8+1 limits, but its template link was unavailable during this audit.
- Needed files/data: official 2027 `spconf.sty`, bibliography style, and author instructions when released.
- Command: replace the provisional official ICASSP 2026 style copies and compile both papers again.
- Expected output: final 2027-compliant PDFs and clean logs.
- Claim impact: current drafts use the latest available official ICASSP style, but final template compliance must be rechecked.
- Must resolve before submission: yes.
