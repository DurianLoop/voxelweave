# Nested Selection Protocol Amendment

## Frozen first pass

The first nested outer-fold run is permanently retained in files ending in
`_unconstrained.csv`. It selected an analytical-only two-member committee in
254 of 264 main decisions. Its primary-target aggregate nAURC was 0.270 versus
0.077 for the frozen baseline. These results were inspected before the
amendment below and therefore cannot be presented as untouched evidence.

## Defect and prospective correction

The declared deployment motivation requires heterogeneous learned peers, but
the first implementation allowed Linear+Cubic to satisfy the one-standard-
error simplicity rule. With only 2--4 cases in an individual fold, fold-only
nAURC also gives a very noisy standard error. Before running the amended outer
analysis, the following rule is frozen:

1. Main committees contain at least two neural peers.
2. Low-cost committees contain at least one neural peer, at most two neural
   peers, and at most three total members.
3. Public fastMRI development nAURC and pooled NingXia inner-fold nAURC are
   both ranked; the objective also includes worst inner-fold nAURC,
   instability, and the declared cost rank.
4. The one-standard-error threshold uses a delete-one-case jackknife standard
   error of pooled inner nAURC, avoiding a standard error estimated mainly
   from two-case folds.
5. The held-out outer fold remains unavailable to every calculation above.
6. The original failed finalist is not deleted or relabeled.

Because the first outer results were already observed, the amended run is an
exploratory nested sensitivity analysis. It may support a robustness or cost
finding, but it is not an untouched replacement for the pre-specified frozen
baseline.
