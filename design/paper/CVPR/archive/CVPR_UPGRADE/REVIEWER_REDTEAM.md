# CVPR Upgrade Reviewer Red Team

## Likely objections and current answers

**“Independent contexts trivially differ.”** The claim is not raw diversity. Exact error-energy decomposition, a clean same-anchor control, and five-level ladders test alignment, observable fraction, disagreement, and ranking. Clean-max contexts retain only `0.25–2.61%` observable paired-error energy.

**“Overlap count is an arbitrary causal variable.”** Agreed and experimentally exposed: the repeated `0→1` ladder exception rejects strict count monotonicity. C5-E014 replaces it with estimator coefficient influence, which improves absolute endpoint association over count by `0.189–0.283` with every clustered interval positive.

**“The method evaluates an x4 network at stride 8.”** Anchor-CV eliminates that dependency. Its pseudo-target is an already acquired anchor, its predictor is local linear interpolation, and it requires no x8-trained model. Neural bipartition is retained only as historical triangulation.

**“The acquisition experiment is circular or needs unavailable targets.”** Dense slices are evaluation-only. At decision time Anchor-CV uses the acquired x4 lattice; the withheld anchor supplies an observed cross-validation residual. It ranks x4 error in all cohorts and retrospective x4-to-x2 benefit in both eligible cohorts.

**“This is a slice uncertainty map.”** It is not. FastMRI within-case localization is negative (median rho `-0.264`). The manuscript limits the method to examination-level triage.

**“The policy is universally superior.”** No such claim is made. It beats random at all fastMRI budgets and NingXia 20/30/50%, but NingXia 10% crosses zero and adjacent-anchor RMSE is best there.

**“The mechanism is only linear.”** The exact coefficient analysis is analytical and estimator-specific. Clean neural controls and two frozen architectures show compatible phenomena, but influence approximations for nonlinear networks remain future work.

## Remaining submission risks

- only eight independent NingXia patients;
- no IXI x2 benefit endpoint and no prospective acquisition;
- no clinical safety or calibrated-uncertainty evidence;
- authors must resolve ethics/data statements and avoid concurrent TMI/CVPR review with substantially overlapping content;
- the 2026 official kit is a temporary formatting basis until the target-year kit is published.
