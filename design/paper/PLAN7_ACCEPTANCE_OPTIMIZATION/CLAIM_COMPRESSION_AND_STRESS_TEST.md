# Claim compression, Fig. 1, abstract and memory tests

Audit date: 2026-08-14. This audit uses the compiled Plan7 TMI candidate and the current CVPR findings candidate; CVPR remains provisional until P7-CV-E02 is complete.

## TMI

### One sentence

Reusing the same physical slice measurements can align deterministic MRI interpolation errors and make agreement-based reconstruction QA blind, whereas deliberately disjoint contexts expose more of that error under defined operating conditions.

### Three contributions

1. A target-preserving physical measurement-overlap intervention across fastMRI, IXI and patient-clustered NingXia, not a claim that the elementary error-difference identity is new.
2. Multi-endpoint, two-architecture and analytical-factor characterization of when shared error suppresses disagreement observability, including metric/intensity/failure boundaries.
3. MRI reconstruction-QA consequences at fixed coverage and an explicit reliability/compute/storage/acquisition operating-regime audit.

### One central figure

`TMI/TMI_MANUSCRIPT_SUBMISSION_FINAL/figures/fig1_concept.pdf`: two distinct rows show `same anchors → aligned errors → small disagreement / hidden shared error` and `different anchors → context-sensitive errors → visible disagreement`. Visual inspection found no text/arrow collision after redesign. **30-second test: PASS.**

### One central quantitative result

All 42 architecture–cohort–endpoint disjoint-minus-shared error-ranking contrasts were positive. This is the breadth result; it does not imply equal effect size across metrics or cohorts.

### Abstract seven-question stress test

| Question | Current answer | Result |
|---|---|---|
| What problem? | Deterministic interpolation lacks a trustworthy error indication. | PASS |
| What assumption fails? | Agreement need not mean correctness. | PASS |
| Why? | Shared anchors generate aligned/shared error canceled by disagreement. | PASS |
| What was proposed/discovered? | Controlled physical-overlap characterization and QA operating boundary. | PASS |
| Strongest evidence? | 42/42 positive contrasts; partial ranks; three cohorts; fixed-coverage IXI counts. | PASS |
| Why matter? | Technical MRI reconstruction QA can retain high-error cases under shared agreement. | PASS |
| What is not claimed? | No calibrated uncertainty, clinical safety or universal deployment prescription. | PASS |

### Reviewer memory target

**Shared physical measurement reuse can make deterministic MRI interpolators agree while being wrong.** The title, Fig. 1, abstract and conclusion reinforce this one message. PASS.

## CVPR

### One sentence

Shared-anchor count is not neural estimator influence: finite-difference response similarity explains local error alignment and disagreement cancellation more precisely, but three locked attempts show that mechanism insight does not automatically yield a better reliability score.

### Three contributions

1. A neural shared-influence response statistic evaluated on three MRI cohorts and two frozen architectures, with a prespecified perturbation/plane audit.
2. Fixed-count and arrow-wise tests separating influence, error alignment, cancellation and observability, including the mixed/null NingXia boundary.
3. Three locked falsifications—context selection, multi-anchor jackknife and covariance residualization—that delimit the gap between explanation and operational capability.

### One central figure

`CVPR/CVPR_UPGRADE/PAPER_FINAL/figures/p7_fig1_mechanism_findings.pdf`: count-matched contexts lead to a finite-difference response cosine and then to supported local evidence, a NingXia boundary and failed method gates. It does not reuse TMI iconography or present Anchor-CV as the solution. Visual inspection found no text collision after redesign. E02 parameter robustness and plane dependence are now integrated. **30-second test: PASS.**

### One central quantitative result

Across the broad grid, all 18 primary absolute-correlation advantages of neural influence over count were positive (0.036–0.089) with clustered intervals above zero. Fixed-count confirmation is limited to fastMRI/IXI; this number cannot be presented as a universal law.

### Abstract seven-question stress test

| Question | Current answer | Result |
|---|---|---|
| What problem? | Dependence makes output disagreement hide reconstruction error. | PASS |
| What assumption fails? | Integer measurement overlap is an adequate dependence descriptor. | PASS |
| Why? | Reused anchors have unequal network response/influence. | PASS |
| What was proposed/discovered? | Neural shared-influence probe plus scoped mechanism chain. | PASS |
| Strongest evidence? | 18/18 broad-grid advantages; fixed-count support on two larger cohorts; three failed method gates. | PASS |
| Why matter? | It prevents count-only reasoning and exposes why mechanistic explanation is not a reliability solution. | PASS for findings positioning; venue-fit remains disputed. |
| What is not claimed? | No superior estimator; NingXia and final ranking arrow are heterogeneous. | PASS |

### Reviewer memory target

**Measurement count is not estimator influence, and explaining disagreement blindness does not automatically solve reliability ranking.** Title, redesigned Fig. 1, E02 boundary and conclusion are aligned. PASS.

## Separation verdict

The summaries are substantially different. TMI is an imaging-methodology/QA characterization centered on a physical intervention and operational consequence. CVPR is a nonlinear estimator-response findings paper centered on continuous influence and failed method derivations. Textual separation passes the internal diagnostic, while scientific overlap still requires merge/sequencing and disclosure review.
