# 支持区域敏感性（事后）

同一冻结A0/B0/B2与目标；先目标均值、再检查均值；5000次联合检查bootstrap；每支持区域/数据集内20对 simultaneous 95% CI。家族行是描述性percentile CI，未对所有敏感性联合校正。排序比较的是20对效应量顺序，不是患者错误排序。

| Cohort | Support | ΔO range (pp) | Positive effects / CI | Family ΔO [CI] (pp) | Pair-rank rho | Max rank movement | Material ordering change |
|---|---|---:|---|---|---:|---:|---|
| fastmri | acquired_union | 6.165–15.878 | 20/20; 20/20 | 10.391 [9.541,11.268] | 0.9985 | 1 | False |
| fastmri | full_common_valid | 6.153–15.870 | 20/20; 20/20 | 10.381 [9.529,11.258] | 0.9970 | 1 | False |
| fastmri | target_1pct | 6.236–16.022 | 20/20; 20/20 | 10.478 [9.625,11.354] | 1.0000 | 0 | False |
| ixi | acquired_union | 13.009–28.420 | 20/20; 20/20 | 21.661 [21.139,22.225] | 1.0000 | 0 | False |
| ixi | full_common_valid | 12.995–28.356 | 20/20; 20/20 | 21.612 [21.094,22.169] | 1.0000 | 0 | False |
| ixi | target_1pct | 13.113–28.531 | 20/20; 20/20 | 21.775 [21.257,22.332] | 1.0000 | 0 | False |

Acquired support uses only the two bracketing phase-0 anchors, each absolute intensity >1% its own maximum; unchanged historical union contract. It is intentionally held fixed across both conditions and all architectures. The full support uses the common finite pixel set, including background. All masks and eligibility counts are in outputs/geometry_registry.csv and sensitivity_per_plane.csv. No independence of model pairs is assumed.