# 模型对家族稳健性（事后描述）

20对共享检查和架构，不是20个独立重复。所有pair列共同重采样检查；bootstrap内部先算各pair检查均值，再做家族mean/median。逐架构排除全部涉及该架构的方向对，剩余12对。区间为描述性95% percentile，不替代完整矩阵。

| Cohort | Excluded | Pairs | Statistic | ΔO [95% CI] (pp) |
|---|---|---:|---|---|
| fastmri | none | 20 | mean | 10.478 [9.625,11.354] |
| fastmri | none | 20 | median | 10.849 [9.863,11.736] |
| fastmri | hat | 12 | mean | 9.237 [8.366,10.139] |
| fastmri | hat | 12 | median | 9.675 [8.750,10.387] |
| fastmri | swinir | 12 | mean | 9.768 [9.008,10.567] |
| fastmri | swinir | 12 | median | 10.228 [9.517,10.874] |
| fastmri | i3net | 12 | mean | 11.639 [10.670,12.650] |
| fastmri | i3net | 12 | median | 11.347 [10.190,12.449] |
| fastmri | saint | 12 | mean | 10.423 [9.592,11.289] |
| fastmri | saint | 12 | median | 10.409 [9.496,11.214] |
| fastmri | cycleinr | 12 | mean | 11.323 [10.497,12.176] |
| fastmri | cycleinr | 12 | median | 10.849 [9.973,11.816] |
| ixi | none | 20 | mean | 21.775 [21.257,22.332] |
| ixi | none | 20 | median | 21.765 [21.326,22.208] |
| ixi | hat | 12 | mean | 20.400 [19.858,20.991] |
| ixi | hat | 12 | median | 20.300 [19.767,20.878] |
| ixi | swinir | 12 | mean | 20.107 [19.565,20.700] |
| ixi | swinir | 12 | median | 19.727 [19.195,20.311] |
| ixi | i3net | 12 | mean | 25.040 [24.586,25.510] |
| ixi | i3net | 12 | median | 25.039 [24.586,25.530] |
| ixi | saint | 12 | mean | 20.241 [19.706,20.827] |
| ixi | saint | 12 | median | 19.727 [19.195,20.311] |
| ixi | cycleinr | 12 | mean | 23.086 [22.501,23.727] |
| ixi | cycleinr | 12 | median | 22.908 [22.329,23.542] |