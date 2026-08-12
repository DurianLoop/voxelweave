# Final Reviewer Simulation

## Reviewer A: ICASSP Computational Imaging

**Strengths.** Physical-plane matching uses full NIfTI geometry and produces a factor-aware signal distinct from generic ensemble spread. The common-mode decomposition and fixed rank hybrid are clear. Broad negative adaptive results are not hidden.

**Weaknesses.** Core formulas remain simple and physical consistency requires multiple factor outputs. No learned refinement or formal optimality result is provided.

**Fatal concerns:** none after correcting shape matching and common-support fidelity.

Scores: novelty 4.0/5; technical quality 4.2/5; significance 3.9/5; clarity 4.3/5; reproducibility 4.6/5; overall 4.0/5.

## Reviewer B: Uncertainty and Selective Prediction

**Strengths.** The paper avoids calibrated-probability claims, separates triage/attribution/shared difficulty, uses nested outer predictions, and computes paired profile-aligned risk-coverage intervals.

**Weaknesses.** Attribution is weak and empirical-CDF calibration is limited by 18--20 inner cases. Adaptive selection has negative transfer.

**Fatal concerns:** none; negative attribution is correctly bounded.

Scores: novelty 3.8/5; technical quality 4.3/5; significance 3.8/5; clarity 4.4/5; reproducibility 4.6/5; overall 3.9/5.

## Reviewer C: Medical Imaging

**Strengths.** All cross-model errors use a common support; NingXia is correctly described as internal OOF rather than external validation; clinical safety and diagnostic harm are not claimed.

**Weaknesses.** NingXia and fastMRI-brain are small, evidence is T2 brain MRI, and there is no reader or downstream study.

**Fatal concerns:** none for a methods paper, provided claims stay at retrospective prioritization.

Scores: novelty 3.9/5; technical quality 4.1/5; significance 3.7/5; clarity 4.3/5; reproducibility 4.4/5; overall 3.8/5.

## Reviewer D: Skeptical Reproducibility

**Strengths.** Candidate failures remain machine-readable; cost/one-SE code matches the declaration; outer-label flags, target exclusion, physical matching, and 2,000 replicate counts are tested; the ZIP includes imported helpers.

**Weaknesses.** The full candidate registry is large and online neural cost uses an explicit proxy rather than common-hardware measurements.

**Fatal concerns:** none after package verification.

Scores: novelty 3.8/5; technical quality 4.4/5; significance 3.8/5; clarity 4.2/5; reproducibility 4.7/5; overall 4.0/5.

## Consensus

Mean technical quality: **4.25/5**. Mean overall: **3.93/5**. The remaining acceptance risk is scientific scope and cohort size, not an avoidable leakage, traceability, geometry, or packaging defect.
