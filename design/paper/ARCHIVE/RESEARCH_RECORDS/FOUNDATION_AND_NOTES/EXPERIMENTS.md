# Experiments

## E001 — Corpus and methodology audit

- Date: 2026-08-12
- Hypothesis: all
- Code/configuration: read-only recursive audit of `D:\MRI\design`
- Dataset: existing artifacts only
- Results: RASINet identified as strongest evidence chain; ACSI anatomy claim and several PastNet directions already falsified or incomplete.
- Decision: KEEP RASINet; retain other lines as negative/secondary evidence.
- Artifacts: `FINAL_RESEARCH_REPORT.md`, `RESEARCH_STATE.md`.

## E002 — Independent evidence-table audit

- Date: 2026-08-12
- Hypothesis: H001-H004
- Code/configuration: `audit_evidence.py`
- Dataset/split: existing NingXia eight-fold OOF outer predictions; fastMRI/NingXia geometry records
- Seed: inherited 20260821 for registered nested results; audit itself deterministic
- Baseline: frozen target-excluded median committee disagreement
- Modification: physical-plane cross-scale consistency
- Metrics: nAURC, Spearman, RRR50, paired bootstrap interval, geometry completeness
- Parameters/FLOPs/latency/memory: not applicable to table audit; online model cost NOT RUN uniformly
- Results: the original 18 checks passed and the expanded audit passes 21/21; 1,518/1,518 physical matches. The original profile-aligned interval -0.0256 [-0.0633, -0.0006] is retained only as historical provenance and superseded by E007 examination-clustered inference.
- Interpretation: supports H001 narrowly; H002 must be read through E007; rejects H003/H004.
- Decision: KEEP H001/H002; REJECT H003/H004.
- Artifacts: `audit_outputs/evidence_audit.json`, `audit_outputs/evidence_audit.csv`.

## E003 — Full RASINet unit-test verification

- Date: 2026-08-12
- Hypothesis: correctness prerequisite
- Code/configuration: Python `unittest`; 10 RASINet test modules; `PYTHONPATH=D:\MRI\design;D:\MRI\baseline;D:\MRI\pre;D:\MRI`; bytecode disabled
- Results: 64 tests passed in 0.375 s.
- Decision: KEEP implementation evidence.
- Artifact paths: console result recorded in `EXPERIMENT_NOTES.md`.

## E004 — External untouched-site confirmation

- Type: CONFIRMATORY
- Hypothesis: H001/H002
- Dataset: independent multi-factor T2 brain MRI site
- Split/seed: to be preregistered
- Results: NOT RUN — required dataset is unavailable.
- Decision: required before any universal/external-generalization claim.

## E005 — Reader/downstream validation

- Type: CONFIRMATORY
- Results: NOT RUN — readers, approvals, task labels, and protocol are unavailable.
- Decision: required before clinical-workflow or diagnostic-harm claims.

## E006 — PC-v1 freeze

- Type: CONFIRMATORY governance.
- Artifact: `FROZEN_METHOD.md`.
- Result: geometry, support, aggregation, factors, endpoint, orientation, and prohibited rescue changes frozen before plan2 analyses.

## E007 — Case influence and clustered statistics

- Type: CONFIRMATORY.
- Results: NingXia 22/22 and fastMRI 24/24 leave-one-case subsets preserve direction. Clustered NingXia interval includes zero; fastMRI interval excludes zero.
- Decision: downgrade NingXia significance; KEEP cross-dataset phenomenon.

## E008 — Per-profile and risk-coverage heterogeneity

- Type: CONFIRMATORY.
- Results: NingXia 6/9 profiles, three curve crossings; fastMRI 9/9 profiles, one crossing.
- Decision: reject universal per-profile improvement.

## E009 — Extended geometry audit

- Type: CONFIRMATORY correctness check.
- Results: 1,518/1,518 records have identical in-plane shape, orientation, spacing, FOV, slice step, and affine; maximum matched-plane distance 0 mm.
- Decision: geometry mismatch explanation rejected.

## E010 — Common-mode smoothing mechanism

- Type: EXPLORATORY controlled falsification.
- Results: shared and target-specific blur increase MAE while reducing both committee and PC scores.
- Decision: REJECT general common-mode detection; establish stable-error boundary.

## E011 — Intensity and endpoint sensitivity

- Type: EXPLORATORY confounder check.
- Results: raw PC partly follows dynamic range; pooled shared-range PC retains normalized-error association but lacks independent confirmation.
- Decision: REFINE mechanism; PC-v2 remains exploratory.

## E012 — TTA conceptual comparator

- Type: EXPLORATORY, one fastMRI x4 SwinIR profile.
- Results: PC nAURC 0.0113, TTA 0.0339, baseline 0.0850; PC-vs-TTA permutation p=0.170.
- Decision at Plan 2: uniqueness unresolved. Superseded by E025's 18-profile comparison; the broader claim remains limited to flip-TTA.

## E013 — Localization derivation and held-out confirmation

- Type: first 8 fastMRI cases EXPLORATORY; remaining 16 cases CONFIRMATORY.
- Results: held-out pixel rho median 0.693 [0.649,0.743], slice rho 0.799 [0.659,0.867], case-pair rho 0.915 [0.805,0.942], top-10% enrichment 2.49x [2.32,2.72].
- Decision: KEEP multi-granularity association.

## E014 — NingXia localization replication

- Type: CONFIRMATORY cross-dataset replication with fixed local protocol.
- Results: 22 OOF cases, 1,464 planes; pixel rho 0.489 [0.477,0.500], slice rho 0.727 [0.618,0.810], case-pair rho 0.883 [0.775,0.937], enrichment 2.06x [2.00,2.15]. Fourteen consistent-but-wrong planes found.
- Decision: KEEP with explicit failure boundary.

## E015 — Boundary position and implementation trace

- Type: MECHANISTIC / RETROSPECTIVE.
- Result: x4–x6 first-plane stable-wrong rate exceeds other positions by 0.147 [0.030,0.286] on NingXia; no event appears on fastMRI. Source paths use bilateral anchors or coverage-checked sliding windows.
- Decision: reject plane-matching/zero-fill artifact; investigate shared-anchor anatomy mechanism.

## E016 — Orthogonal variance decomposition

- Type: EXPLORATORY hierarchical interpretation.
- Result: case / factor / architecture fractions are 58.3% / 25.8% / 10.3% on fastMRI and 83.9% / 12.5% / 0.6% on NingXia.
- Decision: promote latent examination difficulty branch.

## E017 — Pre-reconstruction acquired-context signals

- Type: EXPLORATORY on fastMRI/NingXia; CONFIRMATORY fixed-feature replication on IXI.
- Result: adjacent-anchor RMSE predicts raw error across all three cohorts and six IXI methods; scale-controlled effects remain but vary strongly by cohort.
- Decision: KEEP as domain-dependent proxy; reject universal replacement of PC.

## E018 — Multi-context triangle attribution

- Type: EXPLORATORY falsification.
- Result: triangle outlier loses to constant x6 because x6 is worst in all 138 evaluated units.
- Decision: REJECT attribution.

## E019 — Intervention error-diversity test

- Type: MECHANISTIC / RETROSPECTIVE.
- Result: profile-level error decorrelation does not predict witness quality in either cohort.
- Decision: REJECT monotonic diversity principle; require target preservation, scale, and shared-bias terms.

## E020 — Spectral decomposition

- Type: MECHANISTIC.
- Result: low-frequency PC-error association is at least as strong as raw and stronger than high-frequency association; high-frequency-only explanation fails.
- Decision: REJECT P3-H05.

## E021 — Context geometry and anchor curvature

- Type: MECHANISTIC / RETROSPECTIVE.
- Result: shared-anchor x4–x6 outputs have lower disagreement despite higher NingXia error. Target anchor-path curvature correlates with error at rho 0.936 and is 260 versus 168 median in stable-wrong versus other planes.
- Decision: KEEP shared-anchor/nonlinear-trajectory mechanism.

## E022 — Exact bias–diversity decomposition

- Type: THEORETICAL + RETROSPECTIVE.
- Result: context diversity explains median 19.1%/13.5% of squared error; shared consensus error 80.9%/86.5% on fastMRI/NingXia. Numerical identity residual is negligible relative to squared-error scale.
- Decision: KEEP as central explanation of the witness ceiling.

## E023 — Full model-family analysis

- Type: RETROSPECTIVE REPLICATION.
- Result: 11 fastMRI neural models have median pairwise error rho 0.961; six IXI methods 0.991.
- Decision: KEEP architecture-invariant latent difficulty claim.

## E024 — Asymmetric context deletion

- Type: MECHANISTIC / SYNTHETIC, four frozen fastMRI HAT cases.
- Result: deleting/replacing the first left anchor raises first-interval error by 42.8, interior error by -0.21; output change 93.4 versus 2.17.
- Decision: supports local boundary-context sensitivity, not clinical prevalence.

## E025 — Three-architecture flip-TTA comparison

- Type: CONFIRMATORY-compatible on frozen fastMRI x4 outputs/checkpoints.
- Result: expanded to both cohorts and all x2/x4/x6 factors. PC beats flip-TTA in 18/18 profiles; mean delta nAURC fastMRI -0.0340 (`p=0.0035`), NingXia -0.1143 (`p=0.0015`), pooled -0.0741 (`p<0.0005`).
- Decision: KEEP for physical sampling context versus flip-TTA in this scope; do not generalize to arbitrary perturbations.
