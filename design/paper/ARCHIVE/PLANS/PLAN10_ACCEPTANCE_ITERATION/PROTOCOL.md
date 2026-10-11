# Plan 10 acceptance iteration: recovered-model-bank diversity audit

Date: 2026-08-27

## Motivation

The remaining executable reviewer risk is no longer the number of architectures. It is whether the manuscript's statement that architecture diversity does not guarantee independent error is supported broadly enough to be useful. The current paper reports five focused models on fastMRI; the recovered bank contains substantially broader per-case fidelity and target-to-member disagreement records across fastMRI, IXI, and NingXia.

## Status

This is an **exploratory breadth audit**, not a new confirmatory experiment. Aggregate outcomes were inspected while selecting the analysis, so no post-hoc confidence interval will be presented as preregistered confirmation. Five hundred deterministic case/patient-cluster bootstrap replicates quantify sampling uncertainty conditional on the recovered model bank only.

## Questions

### P10-Q1: common case difficulty

Across the full recovered method bank, how strongly do different reconstruction methods rank the same cases as difficult?

Primary descriptive endpoint: median pairwise Spearman correlation of per-case MAE within each dataset--factor stratum.

### P10-Q2: family labels as a proxy

Does choosing a member from a different architecture family reliably improve target-error ranking by cross-model disagreement?

Endpoint: for every target with at least one same-family and one cross-family member, the difference between the median cross-family disagreement--target-error Spearman correlation and the same-family median.

### P10-Q3: relation between common failure and disagreement reliability

Does target--member case-error dependence alone determine disagreement reliability?

Endpoint: across directed target--member pairs within each stratum, Spearman association between target--member error-rank correlation and disagreement--target-error correlation.

## Data and units

- fastMRI: 24 held-out examinations, factors 2/4/6;
- IXI: 115 held-out examinations, factor 4;
- NingXia: 22 out-of-fold series from eight patient folds, factors 2/4/6;
- bootstrap unit: examination for fastMRI/IXI and patient fold for NingXia;
- model family labels come from `design/rasinet/model_bank_registry.csv`; ACSI-Net is mapped to `attention_cnn`.

## Inclusion and exclusions

- Include every method with common-support per-case MAE in a stratum.
- Include every directed target--member pair with a recovered target-derived foreground disagreement score.
- Do not impute unavailable IXI factors or methods.
- Do not interpret repeated model pairs as independent draws from a population of architectures.
- Do not use this analysis to select a new committee or claim an operationally superior method.

## Decision rule for manuscript integration

Add the result only if it clarifies an existing claim without creating a new superiority narrative. A useful outcome is either: (a) high common case-difficulty dependence across the broad bank, or (b) a clear target-family-dependent sign change showing that family labels are not a universal design rule. Otherwise preserve the audit in Plan 10 without expanding the manuscripts.
