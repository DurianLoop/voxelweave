# Clean-room reproduction check

All historical and new headline checks below PASS. No manuscript summary CSV is used as a numerical input. The three new experiments and the principal historical control/influence/architecture results are independently recomputed from saved target/prediction/response arrays. The old guard negative statement is independently recomputed from the lowest preserved per-examination score records and frozen CDF/threshold parameters; this is explicitly not a full image-level guard replay. Old supplemental benchmark results are retained, not mislabeled as newly array-reproduced.

The array audit has 71 per-table/column checks. Historical maximum numerical difference is 8.53e-14; new maximum is 5.51e-10. Absolute and relative tolerances, observation counts and source bindings are in the CSV/JSON audit. A field-name adaptation (historical target_z to z) was needed by the independent reproducer; it changed no experiment. The original failed run and completed rerun remain in this iteration history.

The exact original/current protocol hashes remain immutable. The SAINT coordinate amendment was made before inference; the IXI fixed-ranking endpoint label was corrected after source audit without changing its numbers.

## Every headline assertion

| Headline | Reported | Recomputed | Difference | Tolerance | Result | Source SHA-256 |
|---|---:|---:|---:|---:|---|---|
| Figure1 shared MAE_A | 73.8 | 73.7978437 | 0.00216 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 shared MAE_B | 77.7 | 77.7475646 | 0.0476 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 shared D | 22.8 | 22.7534447 | 0.0466 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 shared O_percent | 2 | 1.98439789 | 0.0156 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 disjoint MAE_A | 73.8 | 73.7978437 | 0.00216 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 disjoint MAE_B | 74.4 | 74.426407 | 0.0264 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 disjoint D | 69.3 | 69.2591059 | 0.0409 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Figure1 disjoint O_percent | 19.8 | 19.7682584 | 0.0317 | 0.051 | PASS | `af96ad63fb6eb4e885d86f50cf92e298fc3d3f91233161b0c259c513ae74dd3e` |
| Table1/Figure2 fastmri rho_disjoint | 0.959 | 0.959198587 | 0.000199 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 fastmri rho_shared | 0.867 | 0.866914318 | 8.57e-05 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 fastmri delta_rho | 0.092 | 0.0922842688 | 0.000284 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 fastmri CI_low | 0.043 | 0.0430249773 | 2.5e-05 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 fastmri CI_high | 0.176 | 0.176444209 | 0.000444 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 fastmri observable_percent | 2.61 | 2.61257045 | 0.00257 | 0.0051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ningxia rho_disjoint | 0.892 | 0.891712599 | 0.000287 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ningxia rho_shared | 0.698 | 0.698289305 | 0.000289 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ningxia delta_rho | 0.193 | 0.193423295 | 0.000423 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ningxia CI_low | 0.111 | 0.111421189 | 0.000421 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ningxia CI_high | 0.371 | 0.371198298 | 0.000198 | 0.00051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ningxia observable_percent | 0.25 | 0.253917124 | 0.00392 | 0.0051 | PASS | `6cf9485100dd462a0f723ce512619c7efbb6ad356afbfd99bd4beec3016d09d9` |
| Table1/Figure2 ixi rho_disjoint | 0.981 | 0.981352452 | 0.000352 | 0.00051 | PASS | `e53b45c5311f40f6c35a1b40da34babb831bd208cf62c627206318454dc43a5f` |
| Table1/Figure2 ixi rho_shared | 0.886 | 0.886498928 | 0.000499 | 0.00051 | PASS | `e53b45c5311f40f6c35a1b40da34babb831bd208cf62c627206318454dc43a5f` |
| Table1/Figure2 ixi delta_rho | 0.095 | 0.0948535243 | 0.000146 | 0.00051 | PASS | `e53b45c5311f40f6c35a1b40da34babb831bd208cf62c627206318454dc43a5f` |
| Table1/Figure2 ixi CI_low | 0.078 | 0.078311257 | 0.000311 | 0.00051 | PASS | `e53b45c5311f40f6c35a1b40da34babb831bd208cf62c627206318454dc43a5f` |
| Table1/Figure2 ixi CI_high | 0.126 | 0.125572744 | 0.000427 | 0.00051 | PASS | `e53b45c5311f40f6c35a1b40da34babb831bd208cf62c627206318454dc43a5f` |
| Table1/Figure2 ixi observable_percent | 1.58 | 1.5812154 | 0.00122 | 0.0051 | PASS | `e53b45c5311f40f6c35a1b40da34babb831bd208cf62c627206318454dc43a5f` |
| Table1 fastmri stable_wrong_pp | 27.1 | 27.0833333 | 0.0167 | 0.051 | PASS | `6304e25e105a5dd3da2d663a553d0ff07bfa188732964b7ce5da5c2c0205b220` |
| Table1 ixi stable_wrong_pp | 20.9 | 20.8685248 | 0.0315 | 0.051 | PASS | `6304e25e105a5dd3da2d663a553d0ff07bfa188732964b7ce5da5c2c0205b220` |
| Table1 ningxia stable_wrong_pp | 28.2 | 28.2258065 | 0.0258 | 0.051 | PASS | `6304e25e105a5dd3da2d663a553d0ff07bfa188732964b7ce5da5c2c0205b220` |
| Table2/Figure3 fastmri/hat count | 0.704 | 0.70421052 | 0.000211 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat influence | 0.766 | 0.76564483 | 0.000355 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat advantage | 0.061 | 0.0614343093 | 0.000434 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat sim_low | 0.042 | 0.0424327055 | 0.000433 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat sim_high | 0.08 | 0.080435913 | 0.000436 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat fixed | 0.169 | 0.168718648 | 0.000281 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat fixed_low | 0.053 | 0.0526900259 | 0.00031 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/hat fixed_high | 0.283 | 0.282865118 | 0.000135 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir count | 0.699 | 0.698634972 | 0.000365 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir influence | 0.784 | 0.784132552 | 0.000133 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir advantage | 0.085 | 0.0854975796 | 0.000498 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir sim_low | 0.073 | 0.0727046594 | 0.000295 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir sim_high | 0.098 | 0.0982904998 | 0.00029 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir fixed | 0.35 | 0.350283431 | 0.000283 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir fixed_low | 0.212 | 0.211631309 | 0.000369 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 fastmri/swinir fixed_high | 0.464 | 0.463597247 | 0.000403 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat count | 0.577 | 0.577478547 | 0.000479 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat influence | 0.705 | 0.705380071 | 0.00038 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat advantage | 0.128 | 0.127901524 | 9.85e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat sim_low | 0.117 | 0.116894312 | 0.000106 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat sim_high | 0.139 | 0.138908737 | 9.13e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat fixed | 0.346 | 0.345514261 | 0.000486 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat fixed_low | 0.259 | 0.258985106 | 1.49e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/hat fixed_high | 0.424 | 0.424417161 | 0.000417 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir count | 0.573 | 0.573405808 | 0.000406 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir influence | 0.691 | 0.691145572 | 0.000146 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir advantage | 0.118 | 0.117739764 | 0.00026 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir sim_low | 0.107 | 0.107100631 | 0.000101 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir sim_high | 0.128 | 0.128378897 | 0.000379 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir fixed | 0.258 | 0.258220704 | 0.000221 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir fixed_low | 0.181 | 0.180893666 | 0.000106 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ixi/swinir fixed_high | 0.335 | 0.335242689 | 0.000243 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat count | 0.62 | 0.620394196 | 0.000394 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat influence | 0.69 | 0.690467521 | 0.000468 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat advantage | 0.07 | 0.0700733244 | 7.33e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat sim_low | 0.042 | 0.04190363 | 9.64e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat sim_high | 0.098 | 0.0982430188 | 0.000243 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat fixed | 0.014 | 0.0135385507 | 0.000461 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat fixed_low | -0.232 | -0.231945247 | 5.48e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/hat fixed_high | 0.223 | 0.223261989 | 0.000262 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir count | 0.609 | 0.608987333 | 1.27e-05 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir influence | 0.669 | 0.669287134 | 0.000287 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir advantage | 0.06 | 0.0602998011 | 0.0003 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir sim_low | 0.019 | 0.018768656 | 0.000231 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir sim_high | 0.102 | 0.101830946 | 0.000169 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir fixed | -0.039 | -0.039321778 | 0.000322 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir fixed_low | -0.175 | -0.174839642 | 0.00016 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Table2/Figure3 ningxia/swinir fixed_high | 0.144 | 0.144329862 | 0.00033 | 0.00051 | PASS | `2bc8e10606b281cde50930efccd420c171b1810078f3f74d8f572c856c4260d0` |
| Figure4 fastmri/hat local_gap | 0.178 | 0.178454091 | 0.000454 | 0.00051 | PASS | `8f64035da08d744e9c3171f20bf7e620b32c473d8488605cc228f94065206263` |
| Figure4 fastmri/swinir local_gap | 0.176 | 0.175854204 | 0.000146 | 0.00051 | PASS | `8f64035da08d744e9c3171f20bf7e620b32c473d8488605cc228f94065206263` |
| Figure4 fastmri/i3net local_gap | 0.08 | 0.0799580431 | 4.2e-05 | 0.00051 | PASS | `8f64035da08d744e9c3171f20bf7e620b32c473d8488605cc228f94065206263` |
| Figure4 fastmri/saint local_gap | 0.137 | 0.136566054 | 0.000434 | 0.00051 | PASS | `8f64035da08d744e9c3171f20bf7e620b32c473d8488605cc228f94065206263` |
| Figure4 fastmri/cycleinr local_gap | 0.226 | 0.225950889 | 4.91e-05 | 0.00051 | PASS | `8f64035da08d744e9c3171f20bf7e620b32c473d8488605cc228f94065206263` |
| Figure4 ixi/hat local_gap | 0.29 | 0.290288227 | 0.000288 | 0.00051 | PASS | `a056c7f455e2c6f0b10913d03f52d25cdc8065265f1cc948e51442bc6520a59e` |
| Figure4 ixi/swinir local_gap | 0.302 | 0.302102862 | 0.000103 | 0.00051 | PASS | `a056c7f455e2c6f0b10913d03f52d25cdc8065265f1cc948e51442bc6520a59e` |
| Figure4 ixi/i3net local_gap | 0.252 | 0.252021246 | 2.12e-05 | 0.00051 | PASS | `a056c7f455e2c6f0b10913d03f52d25cdc8065265f1cc948e51442bc6520a59e` |
| Figure4 ixi/saint local_gap | 0.298 | 0.298071419 | 7.14e-05 | 0.00051 | PASS | `a056c7f455e2c6f0b10913d03f52d25cdc8065265f1cc948e51442bc6520a59e` |
| Figure4 ixi/cycleinr local_gap | 0.296 | 0.296078709 | 7.87e-05 | 0.00051 | PASS | `a056c7f455e2c6f0b10913d03f52d25cdc8065265f1cc948e51442bc6520a59e` |
| Final cross fastmri minimum pp | 6.2 | 6.23596256 | 0.036 | 0.051 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final cross fastmri maximum pp | 16 | 16.0224098 | 0.0224 | 0.051 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| All ordered local intervals positive fastmri | 20 | 20 | 0 | 0 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final fastmri fixed_reference_ranking positive count | 0 | 0 | 0 | 0 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final fastmri paired_error_ranking positive count | 0 | 0 | 0 | 0 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final cross ixi minimum pp | 13.1 | 13.1126339 | 0.0126 | 0.051 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final cross ixi maximum pp | 28.5 | 28.5312968 | 0.0313 | 0.051 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| All ordered local intervals positive ixi | 20 | 20 | 0 | 0 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final ixi fixed_reference_ranking positive count | 16 | 16 | 0 | 0 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final ixi paired_error_ranking positive count | 20 | 20 | 0 | 0 | PASS | `b2e2444ee525178a2b447b6b2a132177e27e2addfcf8a78a1f30e2ee860c4070` |
| Final Table2 ixi/hat field1 | 0.098 | 0.0978215124 | 0.000178 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/hat field2 | 0.09 | 0.0895051091 | 0.000495 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/hat field3 | 0.106 | 0.106137916 | 0.000138 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/hat field4 | 0.27 | 0.269525532 | 0.000474 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/hat field5 | 0.194 | 0.193923393 | 7.66e-05 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/hat field6 | 0.345 | 0.34512767 | 0.000128 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/hat field7 | 0.93 | 0.929824356 | 0.000176 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field1 | 0.093 | 0.0932506125 | 0.000251 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field2 | 0.084 | 0.0836251892 | 0.000375 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field3 | 0.103 | 0.102876036 | 0.000124 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field4 | 0.265 | 0.264861473 | 0.000139 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field5 | 0.195 | 0.195425504 | 0.000426 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field6 | 0.334 | 0.334297443 | 0.000297 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 ixi/swinir field7 | 0.88 | 0.880314088 | 0.000314 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field1 | 0.103 | 0.103319534 | 0.00032 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field2 | 0.089 | 0.0886091327 | 0.000391 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field3 | 0.118 | 0.118029935 | 2.99e-05 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field4 | 0.474 | 0.474105618 | 0.000106 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field5 | 0.321 | 0.320854992 | 0.000145 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field6 | 0.627 | 0.627356243 | 0.000356 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/hat field7 | 0.964 | 0.964290235 | 0.00029 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field1 | 0.093 | 0.0933222458 | 0.000322 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field2 | 0.08 | 0.080495597 | 0.000496 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field3 | 0.106 | 0.106148895 | 0.000149 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field4 | 0.365 | 0.365011516 | 1.15e-05 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field5 | 0.216 | 0.215607858 | 0.000392 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field6 | 0.514 | 0.514415173 | 0.000415 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| Final Table2 fastmri/swinir field7 | 0.942 | 0.942054081 | 5.41e-05 | 0.00051 | PASS | `8d6b84da99292976c1e3916251ad1eaa32c6eca294142a99ae38ff5e1c154af2` |
| All twelve acquired stability checks pass | 12 | 12 | 0 | 0 | PASS | `3b3f6f7eaef092e0f6ccb931370866d2fb57276ce16d6c21cecd09986fc75d0c` |
| Minimum acquired stability | 0.88 | 0.880314088 | 0.000314 | 0.00051 | PASS | `3b3f6f7eaef092e0f6ccb931370866d2fb57276ce16d6c21cecd09986fc75d0c` |
| Eight neural mean intervals negative | 8 | 8 | 0 | 0 | PASS | `93ddaef2240e7ff57cb99a5bd1a2c4bab3766e1084fb58afe727208452a31093` |
| Minimum median approximation percent | 1.9 | 1.8984766 | 0.00152 | 0.051 | PASS | `93ddaef2240e7ff57cb99a5bd1a2c4bab3766e1084fb58afe727208452a31093` |
| Maximum median approximation percent | 10.6 | 10.6124027 | 0.0124 | 0.051 | PASS | `93ddaef2240e7ff57cb99a5bd1a2c4bab3766e1084fb58afe727208452a31093` |
| Maximum individual approximation percent | 126.4 | 126.409141 | 0.00914 | 0.051 | PASS | `7b22a76dac087bb1ae5383274815ddb240172f242cd5ff0ec99f6dfe905511f8` |
| Final neural reference sensitivity aligned | 86 | 86 | 0 | 0 | PASS | `cf6c89337f8add9c6fdad441ac1cb235dc619f7a8bccd1b8b6098b07e33a5585` |
| Final neural reference sensitivity near | 10 | 10 | 0 | 0 | PASS | `cf6c89337f8add9c6fdad441ac1cb235dc619f7a8bccd1b8b6098b07e33a5585` |
| Final neural reference sensitivity opposing | 0 | 0 | 0 | 0 | PASS | `cf6c89337f8add9c6fdad441ac1cb235dc619f7a8bccd1b8b6098b07e33a5585` |
| Final guard positives fastmri/hat_swinir | 0 | 0 | 0 | 0 | PASS | `0475dd0fcf391bdb2337bf0c0249d6e6d1c04e52492417e01de0c40eaecde5a8` |
| Final guard positives fastmri/i3net_cycleinr | 0 | 0 | 0 | 0 | PASS | `0475dd0fcf391bdb2337bf0c0249d6e6d1c04e52492417e01de0c40eaecde5a8` |
| Final guard positives ixi/hat_swinir | 2 | 2 | 0 | 0 | PASS | `0475dd0fcf391bdb2337bf0c0249d6e6d1c04e52492417e01de0c40eaecde5a8` |
| Final guard positives ixi/i3net_cycleinr | 2 | 2 | 0 | 0 | PASS | `0475dd0fcf391bdb2337bf0c0249d6e6d1c04e52492417e01de0c40eaecde5a8` |
| Final guard positive simultaneous AP comparisons | 0 | 0 | 0 | 0 | PASS | `0475dd0fcf391bdb2337bf0c0249d6e6d1c04e52492417e01de0c40eaecde5a8` |
| Final guard all twelve AP intervals cross zero | 12 | 12 | 0 | 0 | PASS | `0475dd0fcf391bdb2337bf0c0249d6e6d1c04e52492417e01de0c40eaecde5a8` |

## Array comparison details

| Table | Field | Observations | Max absolute difference | Failed observations | Result |
|---|---|---:|---:|---:|---|
| clean_max_overlap_per_plane.csv | score | 624 | 7.11e-15 | 0 | PASS |
| clean_max_overlap_per_plane.csv | error | 624 | 5.68e-14 | 0 | PASS |
| clean_max_overlap_per_plane.csv | cosine | 624 | 3.2e-14 | 0 | PASS |
| clean_max_overlap_per_plane.csv | shared_fraction | 624 | 1.78e-15 | 0 | PASS |
| clean_max_overlap_per_plane.csv | observable_fraction | 624 | 6.21e-16 | 0 | PASS |
| clean_max_overlap_ixi_per_plane.csv | score | 14668 | 3.55e-15 | 0 | PASS |
| clean_max_overlap_ixi_per_plane.csv | error | 14668 | 2.84e-14 | 0 | PASS |
| clean_max_overlap_ixi_per_plane.csv | cosine | 14668 | 4.66e-15 | 0 | PASS |
| clean_max_overlap_ixi_per_plane.csv | shared_fraction | 14668 | 7.77e-16 | 0 | PASS |
| clean_max_overlap_ixi_per_plane.csv | observable_fraction | 14668 | 1.73e-16 | 0 | PASS |
| overlap_covariance_per_plane.csv | disagreement_mae | 440 | 2.84e-14 | 0 | PASS |
| overlap_covariance_per_plane.csv | mae | 440 | 5.68e-14 | 0 | PASS |
| overlap_covariance_per_plane.csv | error_cosine | 440 | 2.22e-14 | 0 | PASS |
| overlap_covariance_per_plane.csv | shared_fraction | 440 | 7.88e-15 | 0 | PASS |
| overlap_covariance_per_plane.csv | observable_fraction | 440 | 6.72e-15 | 0 | PASS |
| overlap_covariance_ixi_per_plane.csv | disagreement_mae | 14208 | 2.84e-14 | 0 | PASS |
| overlap_covariance_ixi_per_plane.csv | mae | 14208 | 2.84e-14 | 0 | PASS |
| overlap_covariance_ixi_per_plane.csv | error_cosine | 14208 | 2.55e-15 | 0 | PASS |
| overlap_covariance_ixi_per_plane.csv | shared_fraction | 14208 | 1.28e-15 | 0 | PASS |
| overlap_covariance_ixi_per_plane.csv | observable_fraction | 14208 | 1.05e-15 | 0 | PASS |
| disjoint_anchor_per_plane.csv | disjoint_inconsistency | 192 | 1.42e-14 | 0 | PASS |
| disjoint_anchor_per_plane.csv | phase0_error | 192 | 1.42e-14 | 0 | PASS |
| ningxia_disjoint_per_plane.csv | disjoint_inconsistency | 248 | 5.68e-14 | 0 | PASS |
| ningxia_disjoint_per_plane.csv | phase0_error | 248 | 5.68e-14 | 0 | PASS |
| plan6_neural_shared_influence_confirm3_per_case_config.csv | neural_influence_cosine | 8694 | 9.71e-17 | 0 | PASS |
| plan6_neural_shared_influence_confirm3_per_case_config.csv | error_cosine | 8694 | 2.14e-14 | 0 | PASS |
| plan6_neural_shared_influence_confirm3_per_case_config.csv | observable_fraction | 8694 | 2.76e-15 | 0 | PASS |
| plan6_neural_shared_influence_confirm3_per_case_config.csv | shared_fraction | 8694 | 2.22e-15 | 0 | PASS |
| plan6_neural_shared_influence_confirm3_per_case_config.csv | paired_error_mae | 8694 | 8.53e-14 | 0 | PASS |
| plan6_neural_shared_influence_confirm3_per_case_config.csv | disagreement_mae | 8694 | 5.68e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane.csv | paired_error_mae | 720 | 2.84e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane.csv | prediction_disagreement_mae | 720 | 1.42e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane.csv | error_cosine | 720 | 1.93e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane.csv | shared_error_fraction | 720 | 4.66e-15 | 0 | PASS |
| p9_disjoint_shared_per_plane.csv | observable_error_fraction | 720 | 2.83e-15 | 0 | PASS |
| p9_disjoint_shared_per_plane_transformer_reference.csv | paired_error_mae | 480 | 1.42e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane_transformer_reference.csv | prediction_disagreement_mae | 480 | 1.42e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane_transformer_reference.csv | error_cosine | 480 | 2.31e-14 | 0 | PASS |
| p9_disjoint_shared_per_plane_transformer_reference.csv | shared_error_fraction | 480 | 7.66e-15 | 0 | PASS |
| p9_disjoint_shared_per_plane_transformer_reference.csv | observable_error_fraction | 480 | 6.66e-15 | 0 | PASS |
| p11_ixi_clean_per_plane_full.csv | paired_error_mae | 5750 | 2.84e-14 | 0 | PASS |
| p11_ixi_clean_per_plane_full.csv | prediction_disagreement_mae | 5750 | 2.84e-14 | 0 | PASS |
| p11_ixi_clean_per_plane_full.csv | error_cosine | 5750 | 4.44e-15 | 0 | PASS |
| p11_ixi_clean_per_plane_full.csv | shared_error_fraction | 5750 | 1.17e-15 | 0 | PASS |
| p11_ixi_clean_per_plane_full.csv | observable_error_fraction | 5750 | 9.99e-16 | 0 | PASS |
| cross_arch_shared_disjoint.csv | observable | 27800 | 5.83e-15 | 0 | PASS |
| cross_arch_shared_disjoint.csv | alignment | 27800 | 2.24e-14 | 0 | PASS |
| cross_arch_shared_disjoint.csv | disagreement | 27800 | 2.84e-14 | 0 | PASS |
| cross_arch_shared_disjoint.csv | reference_error | 27800 | 2.84e-14 | 0 | PASS |
| cross_arch_shared_disjoint.csv | paired_error | 27800 | 2.84e-14 | 0 | PASS |
| cross_arch_shared_disjoint_intervals.csv | delta | 200 | 3.55e-15 | 0 | PASS |
| cross_arch_shared_disjoint_intervals.csv | simultaneous_low | 200 | 3.55e-15 | 0 | PASS |
| cross_arch_shared_disjoint_intervals.csv | simultaneous_high | 200 | 7.11e-15 | 0 | PASS |
| acquired_only_influence.csv | influence | 26688 | 9.84e-17 | 0 | PASS |
| acquired_only_influence.csv | observable | 26688 | 2.75e-15 | 0 | PASS |
| acquired_only_influence.csv | alignment | 26688 | 2.01e-14 | 0 | PASS |
| acquired_only_influence.csv | disagreement | 26688 | 1.42e-14 | 0 | PASS |
| acquired_only_influence.csv | reference_error | 26688 | 2.84e-14 | 0 | PASS |
| acquired_only_influence.csv | paired_error | 26688 | 2.84e-14 | 0 | PASS |
| acquired_only_summary.csv | estimate | 8 | 5.55e-17 | 0 | PASS |
| acquired_only_summary.csv | simultaneous_low | 8 | 1.67e-16 | 0 | PASS |
| acquired_only_summary.csv | simultaneous_high | 8 | 1.11e-16 | 0 | PASS |
| acquired_only_stability.csv | rank_stability | 12 | 1.11e-16 | 0 | PASS |
| proposition1_neural_validation.csv | observed_delta | 384 | 5.51e-10 | 0 | PASS |
| proposition1_neural_validation.csv | linear_prediction | 384 | 5.68e-14 | 0 | PASS |
| proposition1_neural_validation.csv | approx_relative_error | 384 | 2.41e-10 | 0 | PASS |
| proposition_summary.csv | observed_delta_mean | 8 | 2.6e-11 | 0 | PASS |
| proposition_summary.csv | linear_prediction_mean | 8 | 1.42e-14 | 0 | PASS |
| proposition_summary.csv | median_relative_error | 8 | 2.55e-11 | 0 | PASS |
| proposition_summary.csv | simultaneous_low | 8 | 2.3e-10 | 0 | PASS |
| proposition_summary.csv | simultaneous_high | 8 | 2.38e-10 | 0 | PASS |
