# Compact Conference Paper Outline

## Working title

When MRI Slice Interpolators Disagree: Ground-Truth-Free Reliability Assessment Across Models and Datasets

## One-sentence story

When the missing MRI slice is unavailable, target-specific disagreement with a heterogeneous committee can rank reconstruction risk, but shared committee failures prevent it from serving as a correctness guarantee.

## Main claims

1. Median target-to-committee disagreement is positively associated with foreground reconstruction error across all evaluated model--dataset pairs.
2. Referring high-score examinations reduces retained MAE relative to random review; normalized risk--coverage makes this benefit comparable across datasets.
3. Committee composition and leave-one-member-out analyses identify dependence on analytical references and correlated neural failures.

## Main paper assets

- Figure 1: deployment/evaluation framework with ground-truth separation.
- Table 1: foreground pixel correlation, case Spearman, normalized AURC, and RRR at 50% coverage for every fixed target--dataset pair.
- Figure 2: normalized risk--coverage curves with random and oracle bounds.
- Table 2: all/neural/analytical committee composition.
- Figure 3: automatically selected useful referral, stable retention, and false-reassurance cases.

## Supplementary assets

- Case-bootstrap intervals for all primary metrics.
- Target-level committee-composition plot.
- Score-level leave-one-member-out CSV.
- Paired proxy comparison CSV.
- Complete operating points at 25%, 50%, and 75% coverage.
- Failure detection and TTA results as secondary analyses.

## Claim boundaries

- This is a reliability-ranking and quality-control study, not a new reconstruction architecture.
- The score is not a calibrated probability or Bayesian posterior.
- Ground truth is evaluation-only.
- Committee generation can be expensive if outputs do not already exist.
- Consensus cannot expose errors shared by all reconstructors.
- Reconstruction error does not establish diagnostic safety.
