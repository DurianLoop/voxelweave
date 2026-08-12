# Compact Conference Paper Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a compact conference manuscript whose method definition, experiments, tables, figures, and claims are mutually consistent and reproducible.

**Architecture:** Reliability primitives live in a focused analysis module and are tested independently. A paper-experiment runner reads existing NIfTI outputs and writes audit CSVs; table and figure builders consume only those CSVs; the LaTeX manuscript consumes the generated artifacts. Existing result directories are preserved.

**Tech Stack:** Python 3.12, NumPy, standard-library unittest, NIfTI I/O through existing project helpers, Matplotlib, LaTeX/BibTeX, Poppler.

## Global Constraints

- Work under `D:\MRI\design\rasinet` and preserve existing run outputs.
- Use `D:\conda\envs\MRI\python.exe` with `PYTHONPATH=D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI`.
- Use only full-profile cases for paper conclusions.
- Ground truth is evaluation-only and never enters an uncertainty proxy.
- Keep the main manuscript compact; detailed tables belong in the supplement.

---

### Task 1: Reliability Primitives

**Files:**
- Create: `design/rasinet/committee_reliability.py`
- Create: `tests/test_rasinet_committee_reliability.py`

**Interfaces:**
- Produces: `target_to_committee_disagreement(target, committee) -> np.ndarray`
- Produces: `committee_dispersion(committee) -> np.ndarray`
- Produces: `risk_coverage_summary(errors, scores, coverages) -> dict[str, float | np.ndarray]`

- [x] Write tests proving the target is excluded from committee construction, the median absolute disagreement matches a hand-computed array, shared dispersion is target-independent, and perfect uncertainty ranking matches oracle risk.
- [x] Run `D:\conda\envs\MRI\python.exe -B -m unittest tests.test_rasinet_committee_reliability -v` and confirm the tests fail because the module does not exist.
- [x] Implement the three functions with finite-value and shape validation.
- [x] Re-run the focused tests and confirm all pass.

### Task 2: Full Committee Experiment Runner

**Files:**
- Create: `design/rasinet/committee_experiments.py`
- Create: `tests/test_rasinet_committee_experiments.py`
- Read: `design/rasinet/posthoc_uncertainty.py`
- Read: `design/rasinet/posthoc_ningxia_cv.py`

**Interfaces:**
- Consumes: reliability primitives from Task 1.
- Produces: `design/rasinet/runs/committee_reliability/<profile>/metrics/per_case_committee.csv`
- Produces: `design/rasinet/runs/committee_reliability/<profile>/metrics/summary_committee.csv`
- Produces: `design/rasinet/runs/committee_reliability/<profile>/metrics/risk_coverage_committee.csv`

- [x] Write tests for source resolution after the baseline/design repository split and for committee membership under `all`, `neural`, `analytic`, and leave-one-member-out modes.
- [x] Run the focused tests and confirm expected failures.
- [x] Implement explicit roots for `baseline` and `design`, profile manifests for IXI/fastMRI/NingXia, and CSV generation without overwriting old post-hoc outputs.
- [x] Re-run the focused tests and existing RASInet tests.
- [x] Run all three full profiles and record completed case/method counts.
- [x] IXI full profile: 115 cases, four neural targets, 2,760 per-case/proxy rows.
- [x] fastMRI-brain full profile: 24 cases, three neural targets, 432 per-case/proxy rows.
- [x] NingXia held-out profile: 22 cases, three neural targets, 396 per-case/proxy rows.

### Task 3: Statistical Summaries

**Files:**
- Create: `design/rasinet/committee_statistics.py`
- Create: `tests/test_rasinet_committee_statistics.py`

**Interfaces:**
- Consumes: per-case CSVs from Task 2.
- Produces: `design/rasinet/reports/committee_reliability/committee_composition.csv`
- Produces: `design/rasinet/reports/committee_reliability/paired_proxy_bootstrap.csv`
- Produces: `design/rasinet/reports/committee_reliability/coverage_operating_points.csv`

- [x] Write deterministic tests for paired bootstrap resampling and normalized/excess AURC.
- [x] Verify the tests fail before implementation.
- [x] Implement seeded case-level bootstrap summaries and operating-point tables.
- [x] Verify focused and aggregate tests pass.
- [x] Generate the report CSVs from all full-profile outputs with 2,000 bootstrap replicates.

### Task 4: Paper Tables and Figures

**Files:**
- Create: `design/rasinet/committee_paper_assets.py`
- Create: `tests/test_rasinet_committee_paper_assets.py`
- Modify: `design/rasinet/paper/figures/`
- Modify: `design/rasinet/paper/tables/`

**Interfaces:**
- Consumes: generated CSVs from Tasks 2 and 3.
- Produces: main table CSV/TeX files, supplementary table CSV/TeX files, and three main PDF figures.

- [x] Write tests that asset generation rejects missing columns and that every manuscript number is emitted from a source CSV.
- [x] Verify the tests fail before implementation.
- [x] Generate a compact main table, risk-coverage figure with random/oracle references, committee-robustness figure, and qualitative reliability panel.
- [x] Generate corrected supplementary CI/proxy assets and retain full-profile TTA, failure, calibration, and reconstruction-context assets with an explicit legacy-score boundary.
- [x] Run asset tests and inspect generated image dimensions and labels.

### Task 5: Manuscript Rewrite

**Files:**
- Modify: `design/rasinet/paper/main.tex`
- Modify: `design/rasinet/paper/references.bib`
- Modify: `design/rasinet/paper/README_overleaf.md`
- Modify: `design/rasinet/paper/outline.md`

**Interfaces:**
- Consumes: Task 4 TeX tables and PDF figures.
- Produces: compact two-column conference manuscript and supplement.

- [x] Replace the title, abstract, introduction, related work, method, experiments, results, discussion, limitations, and conclusion around the approved scientific positioning.
- [x] Make the target-to-committee formula identical to the tested implementation and describe committee dispersion separately.
- [x] Replace raw metric narration with operational risk-reduction statements and confidence intervals.
- [x] Add references for reconstruction uncertainty, risk-coverage evaluation, and medical abstention.
- [x] Keep reconstruction-quality context and secondary analyses in the supplement.

### Task 6: Consistency, Build, and Visual QA

**Files:**
- Create: `design/rasinet/check_paper_consistency.py`
- Create: `tests/test_rasinet_paper_consistency.py`
- Modify: `design/rasinet/reports/posthoc_uncertainty/checklist.md`
- Create: `design/rasinet/paper/overleaf_upload_rasinet_compact.zip`

**Interfaces:**
- Consumes: manuscript, generated tables, source CSVs, and figures.
- Produces: consistency report, compiled PDF, rendered page previews, updated checklist, and Overleaf archive.

- [x] Write a failing consistency test with an intentionally mismatched fixture.
- [x] Implement checks for required artifacts, numeric agreement, forbidden smoke/mini claims, and unresolved LaTeX references.
- [x] Run all RASInet tests: 23/23 passed on 2026-07-15.
- [x] Run `pdflatex`, `bibtex`, and two final `pdflatex` passes; require zero fatal errors and zero undefined citations/references.
- [x] Render every PDF page with Poppler and inspect typography, table width, figure legibility, and float placement.
- [x] Update checklist items only after their verification evidence exists.
- [x] Build the compact Overleaf ZIP and verify it by compiling from an independent extraction directory.

## Plan Self-Review

- Spec coverage: method correction, new experiments, manuscript rewrite, reproducibility, and PDF QA each have a dedicated task.
- Placeholder scan: no deferred implementation markers or unspecified file locations remain.
- Interface consistency: experiment CSVs feed statistics; statistics and experiment CSVs feed assets; assets feed LaTeX; consistency checks inspect the complete chain.
- Repository note: `D:\MRI\.git` is currently an empty directory, so this workspace cannot produce meaningful Git commits. Verification artifacts will be used as the execution record.
