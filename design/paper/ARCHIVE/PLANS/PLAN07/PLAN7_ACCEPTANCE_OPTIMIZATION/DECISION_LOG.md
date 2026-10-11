# Plan7 decision log

## 2026-08-13 — D001: Page count is frozen

- Decision: no experiment or text is justified by page growth.
- Reason: both Plan6 candidates already meet their working length constraints.
- Consequence: every Plan7 change must resolve a registered reviewer risk.

## 2026-08-13 — D002: ANCHOR_CV_V1 is evidence, not an optimization target

- Decision: prohibit cohort-specific retuning or fitted fusion around ANCHOR_CV_V1.
- Reason: adjacent MAE/RMSE are statistically indistinguishable and test-cohort reuse would invalidate a new superiority claim.
- Consequence: any new method receives a P7 ID and must pass the six CVPR method gates.

## 2026-08-13 — D003: First CVPR branch is context selection

- Decision: audit P7-CV-H01 before training or arbitrary score fusion.
- Reason: the branch follows directly from the demonstrated shared-influence failure and can be tested using frozen per-context outputs without target-based selection.
- Rejection condition: no out-of-sample advantage beyond count/random/trivial baselines.

## 2026-08-13 — D004: No causal-mediation language

- Decision: retain the mechanism as an arrow-wise conditional association unless a valid intervention/identification argument is established.
- Reason: Plan6 context-level ranking uses eight configurations and does not satisfy mediation assumptions.

## 2026-08-13 — D005: Reject influence-aware context selection as a main method

- Evidence: P7-CV-E01 passed only on 12 fastMRI confirmation cases and failed to improve random-context expectation/output PC on IXI; NingXia was heterogeneous.
- Decision: do not add the selector to the CVPR main contribution.
- Consequence: characterize neural shared influence as a mechanism probe with a documented zero-overlap identifiability boundary.

## 2026-08-13 — D006: Reject multi-anchor jackknife V2

- Evidence: development-selected IQR failed confirmation and both transfer cohorts; it was substantially worse than adjacent MAE.
- Decision: no jackknife V2, no test-cohort re-selection, and no arbitrary residual fusion.
- Consequence: adjacent difference remains the acquired-only default; ANCHOR_CV_V1 remains a cheap interpretable alternate but not a unique method.

## 2026-08-13 — D007: Reject influence residualization without retuning

- Evidence: the covariance-derived target-free correction did not consistently improve raw disagreement or simple comparators on locked fastMRI confirmation and transfer cohorts.
- Decision: preserve the negative result and prohibit exponent/clip tuning on these cohorts.
- Consequence: treat the CVPR contribution as a mechanism/findings candidate unless a remaining prespecified branch passes all gates.

## 2026-08-13 — D008: Narrow the TMI endpoint explanation

- Evidence: the endpoint-family contrast changed sign across cohorts.
- Decision: retain multi-endpoint robustness but remove the proposed universal low-frequency explanation.
- Consequence: metric heterogeneity is a boundary of the phenomenon, not a new general law.

## 2026-08-14 — D009: Require merge or submission sequencing

- Evidence: after the final findings rewrite, paragraph TF–IDF finds no audited TMI words in matches above 0.45 (two paragraphs exceed 0.30), but both papers depend on the same three-cohort interpolation phenomenon and inherited controls.
- Decision: textual separation is acceptable as a diagnostic, while scientific overlap remains moderate-to-high.
- Consequence: do not submit both concurrently without an author/policy decision and appropriate disclosure; current state is `MERGE_OR_SEQUENCE_REQUIRED`.

## 2026-08-14 — D010: TMI final candidate is impact-led

- Decision: retain the eight-page submission rather than expanding toward ten pages merely because policy permits it.
- Reason: Plan7 additions already cover operational false retention, endpoint heterogeneity and practical regimes without diluting the central physical-intervention message.
- Consequence: TMI is scientifically ready after exact human-data metadata and sequence review; generic filler is prohibited.

## 2026-08-14 — D011: Reposition CVPR as a mechanism/findings paper

- Evidence: P7-CV-E01, E03 and E04 all fail locked non-triviality/transfer gates.
- Decision: remove method-superiority framing; foreground “measurement count is not estimator influence,” arrow-wise evidence, fixed-count boundaries and falsified method branches.
- Consequence: the fatal method/capability risk remains visible. Submission is not recommended as a superior reliability-method paper.

## 2026-08-14 — D012: Do not launch mechanism-derived training

- Decision: enforce the registered stop rule instead of starting a large training branch.
- Reason: operational usefulness was required before training; both context selection and influence residualization had already failed, irrespective of the then-unresolved stability audit.
- Consequence: P7-CV-E02 is the last executable scientific gate; training would have low expected acceptance impact relative to cost and risk test-cohort story drift.

## 2026-08-14 — D013: Make P7-CV-E02 resumable and memory-bounded

- Decision: infer perturbations in bounded mini-batches, release models between checkpoints, atomically save each completed case and evaluate the stability gate per condition.
- Reason: the shared GPU remains occupied and a whole-cohort end-only write loses progress under interruption.
- Consequence: the experiment can safely resume when capacity becomes available without fabricating or silently truncating evidence.

## 2026-08-14 — D014: Accept perturbation robustness but reject plane invariance

- Evidence: all 42 amplitude/sign/field/direction strata pass the frozen stability gate (minimum .942), while plane-pair stability is .779–.954 and only one of three plane gates passes.
- Decision: call finite-difference influence a robust local probe at a declared plane, not a plane-invariant attribution.
- Consequence: replace all provisional E02 markers, integrate the positive parameter audit and negative plane boundary, and retain the CVPR paper as a scoped findings candidate.
