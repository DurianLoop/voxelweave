# 几何敏感性（事后）

先在每检查每residue平均原先五个目标，再等权平衡residue。镜像差是两个反射类效应的差，不是重新执行镜像推理，不证明identity的纯因果效应。所有分析使用原target-1%支持。

| Cohort | Analysis | Units | ΔO range (pp) | Positive effects / positive CI / negative CI | Family estimate [CI] (pp) |
|---|---|---:|---:|---|---|
| fastmri | full_four_anchor_balanced | 0 | NA | NA | NA: no examination has both residue classes with two anchors on each side in both phases |
| fastmri | mirror_residue1_minus_residue3 | 24 | -5.409–2.420 | 5/20; 2/20; 6/20 | -0.937 [-1.555,-0.339] |
| fastmri | nearest_distance_matched_balanced | 24 | 6.293–15.655 | 20/20; 20/20; 0/20 | 10.384 [9.531,11.260] |
| fastmri | residue_1 | 24 | 5.872–15.470 | 20/20; 20/20; 0/20 | 9.916 [8.967,10.884] |
| fastmri | residue_3 | 24 | 6.007–17.492 | 20/20; 20/20; 0/20 | 10.853 [9.988,11.732] |
| fastmri | residue_balanced | 24 | 6.293–15.655 | 20/20; 20/20; 0/20 | 10.384 [9.531,11.260] |
| ixi | full_four_anchor_balanced | 115 | 13.055–28.550 | 20/20; 20/20; 0/20 | 21.768 [21.263,22.305] |
| ixi | mirror_residue1_minus_residue3 | 115 | -2.104–1.855 | 7/20; 2/20; 4/20 | -0.269 [-1.079,0.643] |
| ixi | nearest_distance_matched_balanced | 115 | 13.055–28.550 | 20/20; 20/20; 0/20 | 21.768 [21.263,22.305] |
| ixi | residue_1 | 115 | 12.343–29.067 | 20/20; 20/20; 0/20 | 21.633 [20.889,22.457] |
| ixi | residue_3 | 115 | 13.702–28.357 | 20/20; 20/20; 0/20 | 21.902 [21.345,22.439] |
| ixi | residue_balanced | 115 | 13.055–28.550 | 20/20; 20/20; 0/20 | 21.768 [21.263,22.305] |

Nearest-distance matching requires the actual bracketing distances {1,3} in both phases. Full-four-anchor eligibility additionally requires at least two actual acquired anchors on either side in both phases and both residue classes within an examination. fastMRI depth16 only admits target7 for the latter contract, hence cannot form the two-residue estimate. No boundary anchors are imputed. Significant mirror differences remain orientation warnings; intervals containing zero do not establish equivalence. Residual full-context geometry, preprocessing and anatomical changes are not eliminated.