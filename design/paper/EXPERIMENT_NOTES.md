# Experiment Notes

## 2026-08-12

- Inventory found nine top-level project directories and thousands of artifacts. Three `rasinet` copies are largely snapshots; the non-copy directory contains the latest nested/physical correction and was treated as canonical.
- Existing audit documents expose earlier defects rather than hiding them: target-derived support mismatch, an unimplemented one-SE/cost rule, invalid flattened aggregate bootstrap, and mistaken rejection of cross-scale matching from array-shape mismatch. Later artifacts correct these issues.
- The first unconstrained nested selector often chose only Linear+Cubic. Its outer failure is preserved. The neural-peer amendment was made only after observing that failure and is labeled exploratory; it also fails.
- The main positive signal is not the large candidate search. It is the simple fixed physical consistency score.
- `audit_evidence.py` produced 18 passing checks. Important values: baseline nAURC 0.077209; physical 0.051571; hybrid 0.050427; physical paired delta -0.025639 [-0.063291, -0.000595].
- Initial test command failed because `pytest` is not installed. This was an environment issue, not a code failure. Re-running with the standard-library `unittest` runner and the documented project paths yielded 32/32 selected tests, then 64/64 complete RASINet tests.
- Literature search found close work on learned error prediction, probabilistic/SURE reconstruction, deep ensembles, heteroscedastic IQA, training-free reconstruction uncertainty, and AURC. No verified paper was found that duplicates the exact world-coordinate cross-factor case-ranking mechanism. This is evidence against a known fatal collision, not proof of global novelty.

## 2026-08-12 — Plan 2 continuation

- Froze `PC-v1-FROZEN` before new analyses.
- Replaced profile-aligned inference with examination-clustered bootstrap/permutation. NingXia interval now includes zero; this unfavorable correction is preserved.
- Aligned fastMRI baseline score to the later common-support error labels. The old baseline table used a slightly different error support; mixing them caused missing pair rows in the first permutation implementation.
- Corrected the permutation test to operate on within-profile ranks because raw PC and committee scores have different units.
- Extended geometry audit initially failed because NingXia x2/x6 paths in `optimization_protocol.py` are stale. Resolved the read-only archive roots explicitly inside the new paper script; did not modify source data or original code.
- Common-mode blur falsified the idea that PC generally detects errors shared by models.
- Independent per-factor robust normalization destroyed PC; shared per-case range normalization retained a weaker signal. This exposed intensity scale as a material component rather than a harmless preprocessing detail.
- Local PC maps showed strong error association on eight outcome-blind fastMRI derivation cases. The exact protocol was then run on the remaining 16 cases and replicated without changes on all 22 NingXia OOF cases.
- Real consistent-but-wrong planes cluster at the first generated x4-x6 plane, suggesting a boundary-context failure rather than random anomalies.
- Closeout verification: all 10 `plan2_*.py` files parsed successfully; `audit_evidence.py` passed 21/21 checks; the full canonical RASINet suite passed 64/64 tests in 0.424 s.

## 2026-08-13 — Plan 3

- Reopened the project beyond the local PC claim and executed multiple independent branches: boundary mechanics, hierarchical variance, pre-inference signals, spectral mechanisms, continuous geometry, multi-context attribution, model-family behavior, error decomposition, motion, and generic flip-TTA.
- Preserved major negative results: diversity alone, high-frequency-only PC, triangle attribution, motion as a shared driver, and naive score fusion all fail.
- Ran frozen four-view TTA over both cohorts, all factors, and all three primary architectures. PC favors 18/18 profiles with examination-clustered significance in each cohort.
- Completed the Plan-3 formal exhaustion audit only after checking checkpoint availability and executing previously mislabeled TTA work.
- Closeout: 19 Plan-3 scripts and 35 JSON outputs validated; 21/21 evidence checks and 64/64 canonical tests pass.
