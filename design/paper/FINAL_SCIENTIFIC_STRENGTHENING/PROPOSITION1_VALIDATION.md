# Neural local validation of Proposition 1

Twelve IXI examinations were selected by the frozen hash order, not effect size. Both models, all four exactly-one-anchor contexts and all four amplitudes remain. Acquired-only preprocessing is fixed. Coupled noise uses eight identical field indices, while the independent condition uses the complete 8×8 Cartesian product. The empirical marginals are exactly equal; no noisy unmatched Monte Carlo comparator is used. Targets are not read in this experiment.

There are TWO distinct statements. First, computing centered finite-response covariance at the same amplitude gives ΔE||A−B||² = −2κ up to numerical precision (maximum absolute residual 5.59908e-12). This is an algebraic closure check, not scientific validation of a Jacobian model. Second, a single odd-response linearization fixed at ε0=.0025 predicts all amplitudes by ε² scaling. That prediction is compared to independently computed coupled-versus-independent disagreement from actual perturbed neural outputs. No amplitude is chosen after results.

All eight model/amplitude mean observed effects are negative with simultaneous eight-contrast intervals below zero. Median relative approximation errors range from 1.9% to 10.6%, but the worst individual relative error is 126.4% and the largest absolute error is 112.135 native intensity-squared units. Thus the approximation has a useful local average trend and material individual nonlinear boundaries. Relative error divides by |linear prediction|, not by observed effect.

The 96 fixed model/case/context combinations contain 86 aligned and 10 near-orthogonal reference sensitivities, and zero opposing examples. The near-orthogonal examples still have positive response covariance and retain negative observed effects. The neural experiment therefore does not validate the opposing-sensitivity sign reversal; the analytical counterexample remains separate. Lack of such examples is reported, not repaired by searching another subset.

The experiment perturbs fixed nominal contexts. It does not prove that a phase change preserves bias/Jacobians, that sharing creates deterministic common bias, or that every realized error cosine increases. No empirical global remainder bound or clinical noise model is claimed.

## All amplitude summaries

| model | epsilon | examples | cases | observed_delta_mean | linear_prediction_mean | median_relative_error | mean_abs_approx_error | simultaneous_low | simultaneous_high | family_size | maximum_closure_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hat | 0.0025 | 48 | 12 | -1.80322 | -1.79227 | 0.0189848 | 0.0374022 | -2.83538 | -0.771051 | 8 | 3.24452e-12 |
| hat | 0.005 | 48 | 12 | -7.34985 | -7.16908 | 0.0575006 | 0.79752 | -11.6303 | -3.06939 | 8 | 3.45324e-12 |
| hat | 0.01 | 48 | 12 | -28.7585 | -28.6763 | 0.0891951 | 3.43057 | -45.3446 | -12.1723 | 8 | 3.19034e-12 |
| hat | 0.02 | 48 | 12 | -110.005 | -114.705 | 0.106124 | 15.2753 | -173.455 | -46.5562 | 8 | 3.48876e-12 |
| swinir | 0.0025 | 48 | 12 | -1.50217 | -1.51497 | 0.028577 | 0.0414199 | -2.3657 | -0.63864 | 8 | 3.04889e-12 |
| swinir | 0.005 | 48 | 12 | -6.02788 | -6.05988 | 0.0965105 | 0.493168 | -9.45311 | -2.60264 | 8 | 5.22316e-12 |
| swinir | 0.01 | 48 | 12 | -24.1778 | -24.2395 | 0.10349 | 1.95905 | -37.9275 | -10.4282 | 8 | 2.06768e-12 |
| swinir | 0.02 | 48 | 12 | -94.6466 | -96.958 | 0.0982982 | 7.58381 | -148.847 | -40.446 | 8 | 5.59908e-12 |

## Largest individual approximation errors (all rows in CSV)

| model | case | context | epsilon | observed_delta | linear_prediction | approx_relative_error | reference_sensitivity_class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hat | IXI464 | (-1, 2) | 0.005 | -15.0481 | -6.6464 | 1.26409 | near_orthogonal |
| hat | IXI464 | (-1, 2) | 0.01 | -55.68 | -26.5856 | 1.09437 | near_orthogonal |
| hat | IXI464 | (-1, 2) | 0.02 | -218.478 | -106.342 | 1.05447 | near_orthogonal |
| hat | IXI014 | (-1, 2) | 0.01 | -9.91331 | -5.93175 | 0.671229 | near_orthogonal |
| hat | IXI014 | (-1, 2) | 0.005 | -2.31794 | -1.48294 | 0.563075 | near_orthogonal |
| swinir | IXI014 | (-2, 3) | 0.005 | -5.06809 | -3.30591 | 0.53304 | near_orthogonal |
| hat | IXI014 | (-1, 2) | 0.02 | -35.3791 | -23.727 | 0.49109 | near_orthogonal |
| swinir | IXI251 | (-1, 2) | 0.01 | -2.2307 | -1.54695 | 0.441997 | near_orthogonal |
| swinir | IXI251 | (-2, 1) | 0.01 | -2.00889 | -3.53959 | 0.432453 | aligned |
| swinir | IXI251 | (-1, 2) | 0.02 | -8.69889 | -6.1878 | 0.405813 | near_orthogonal |
| swinir | IXI251 | (-2, 1) | 0.02 | -8.65744 | -14.1584 | 0.388529 | aligned |
| swinir | IXI467 | (-3, 2) | 0.005 | -1.23071 | -0.893958 | 0.376694 | aligned |
