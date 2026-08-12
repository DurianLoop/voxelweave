# RASI 论文级补强实验总结

本页汇总 bootstrap CI、calibration/monotonicity、failure definition ablation 和 domain-shift 分析。所有实验基于已有 post-hoc 输出表，不引入新模型训练。

## 1. Calibration / monotonicity 摘要

| Dataset | Method | Proxy | Metric | Mean | Std |
|---|---|---|---|---:|---:|
| full_test115 | ACSI | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| full_test115 | ACSI | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| full_test115 | ACSI | baseline_disagreement | high_low_error_ratio | 40091.6290 | 188886.5552 |
| full_test115 | ACSI | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |
| full_test115 | HAT | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| full_test115 | HAT | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| full_test115 | HAT | baseline_disagreement | high_low_error_ratio | 25950.9768 | 166428.7361 |
| full_test115 | HAT | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |
| full_test115 | I3Net | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| full_test115 | I3Net | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| full_test115 | I3Net | baseline_disagreement | high_low_error_ratio | 34833.5551 | 159065.7796 |
| full_test115 | I3Net | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |
| full_test115 | SwinIR | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| full_test115 | SwinIR | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| full_test115 | SwinIR | baseline_disagreement | high_low_error_ratio | 34415.8186 | 185202.2007 |
| full_test115 | SwinIR | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |
| fastmri_full | HAT | baseline_disagreement | spearman_bin_error | 0.9960 | 0.0083 |
| fastmri_full | HAT | baseline_disagreement | spearman_uncertainty_error | 0.9960 | 0.0083 |
| fastmri_full | HAT | baseline_disagreement | high_low_error_ratio | 49.8903 | 17.8571 |
| fastmri_full | HAT | baseline_disagreement | monotonic_case_fraction | 0.7500 | 0.0000 |
| fastmri_full | I3Net | baseline_disagreement | spearman_bin_error | 0.9919 | 0.0120 |
| fastmri_full | I3Net | baseline_disagreement | spearman_uncertainty_error | 0.9919 | 0.0120 |
| fastmri_full | I3Net | baseline_disagreement | high_low_error_ratio | 40.2936 | 15.2944 |
| fastmri_full | I3Net | baseline_disagreement | monotonic_case_fraction | 0.5833 | 0.0000 |
| fastmri_full | SwinIR | baseline_disagreement | spearman_bin_error | 0.9965 | 0.0082 |
| fastmri_full | SwinIR | baseline_disagreement | spearman_uncertainty_error | 0.9965 | 0.0082 |
| fastmri_full | SwinIR | baseline_disagreement | high_low_error_ratio | 58.4128 | 22.0731 |
| fastmri_full | SwinIR | baseline_disagreement | monotonic_case_fraction | 0.7917 | 0.0000 |
| ningxia_cv | HAT | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| ningxia_cv | HAT | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| ningxia_cv | HAT | baseline_disagreement | high_low_error_ratio | 2431.6715 | 3293.7779 |
| ningxia_cv | HAT | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |
| ningxia_cv | I3Net | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| ningxia_cv | I3Net | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| ningxia_cv | I3Net | baseline_disagreement | high_low_error_ratio | 3257.9170 | 4467.3665 |
| ningxia_cv | I3Net | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |
| ningxia_cv | SwinIR | baseline_disagreement | spearman_bin_error | 1.0000 | 0.0000 |
| ningxia_cv | SwinIR | baseline_disagreement | spearman_uncertainty_error | 1.0000 | 0.0000 |
| ningxia_cv | SwinIR | baseline_disagreement | high_low_error_ratio | 2662.8256 | 3590.8580 |
| ningxia_cv | SwinIR | baseline_disagreement | monotonic_case_fraction | 1.0000 | 0.0000 |

## 2. Failure definition ablation 摘要

| Dataset | Method | Proxy | Definition | AUROC | AUPRC | Top-k recall |
|---|---|---|---|---:|---:|---:|
| full_test115 | ACSI | baseline_disagreement | top_mae | 0.9871 | 0.8849 | 0.8333 |
| full_test115 | ACSI | baseline_disagreement | top_risk_aurc | 0.9741 | 0.8223 | 0.7500 |
| full_test115 | ACSI | baseline_disagreement | top_mae_50pct_low_u | 0.9328 | 0.7418 | 0.7500 |
| full_test115 | ACSI | baseline_disagreement | bottom_ssim | 0.7176 | 0.2818 | 0.3333 |
| full_test115 | ACSI | baseline_disagreement | bottom_mask_ssim | 0.8374 | 0.4266 | 0.4167 |
| full_test115 | ACSI | baseline_disagreement | top_zge | 0.4450 | 0.1708 | 0.0833 |
| full_test115 | ACSI | baseline_disagreement | top_zle | 0.4450 | 0.1708 | 0.0833 |
| full_test115 | ACSI | baseline_disagreement | top_interslice_ncc_mae | 0.7152 | 0.2932 | 0.3333 |
| full_test115 | HAT | baseline_disagreement | top_mae | 0.9871 | 0.8849 | 0.8333 |
| full_test115 | HAT | baseline_disagreement | top_risk_aurc | 0.9741 | 0.8223 | 0.7500 |
| full_test115 | HAT | baseline_disagreement | top_mae_50pct_low_u | 0.9328 | 0.7418 | 0.7500 |
| full_test115 | HAT | baseline_disagreement | bottom_ssim | 0.7176 | 0.2818 | 0.3333 |
| full_test115 | HAT | baseline_disagreement | bottom_mask_ssim | 0.8374 | 0.4266 | 0.4167 |
| full_test115 | I3Net | baseline_disagreement | top_mae | 0.9822 | 0.8473 | 0.7500 |
| full_test115 | I3Net | baseline_disagreement | top_risk_aurc | 0.9741 | 0.8223 | 0.7500 |
| full_test115 | I3Net | baseline_disagreement | top_mae_50pct_low_u | 0.9328 | 0.7418 | 0.7500 |
| full_test115 | I3Net | baseline_disagreement | bottom_ssim | 0.7176 | 0.2818 | 0.3333 |
| full_test115 | I3Net | baseline_disagreement | bottom_mask_ssim | 0.8374 | 0.4266 | 0.4167 |
| full_test115 | SwinIR | baseline_disagreement | top_mae | 0.9871 | 0.8849 | 0.8333 |
| full_test115 | SwinIR | baseline_disagreement | top_risk_aurc | 0.9741 | 0.8223 | 0.7500 |
| full_test115 | SwinIR | baseline_disagreement | top_mae_50pct_low_u | 0.9328 | 0.7418 | 0.7500 |
| full_test115 | SwinIR | baseline_disagreement | bottom_ssim | 0.7176 | 0.2818 | 0.3333 |
| full_test115 | SwinIR | baseline_disagreement | bottom_mask_ssim | 0.8374 | 0.4266 | 0.4167 |
| fastmri_full | HAT | baseline_disagreement | top_mae | 1.0000 | 1.0000 | 1.0000 |
| fastmri_full | HAT | baseline_disagreement | top_risk_aurc | 0.8254 | 0.4722 | 0.6667 |
| fastmri_full | HAT | baseline_disagreement | top_mae_50pct_low_u | 0.7937 | 0.3611 | 0.3333 |
| fastmri_full | HAT | baseline_disagreement | bottom_ssim | 0.7937 | 0.3611 | 0.3333 |
| fastmri_full | HAT | baseline_disagreement | bottom_mask_ssim | 0.6190 | 0.1987 | 0.0000 |
| fastmri_full | I3Net | baseline_disagreement | top_mae | 1.0000 | 1.0000 | 1.0000 |
| fastmri_full | I3Net | baseline_disagreement | top_risk_aurc | 0.8254 | 0.4722 | 0.6667 |
| fastmri_full | I3Net | baseline_disagreement | top_mae_50pct_low_u | 0.7937 | 0.3611 | 0.3333 |
| fastmri_full | I3Net | baseline_disagreement | bottom_ssim | 0.7937 | 0.3611 | 0.3333 |
| fastmri_full | I3Net | baseline_disagreement | bottom_mask_ssim | 0.6190 | 0.1987 | 0.0000 |
| fastmri_full | SwinIR | baseline_disagreement | top_mae | 1.0000 | 1.0000 | 1.0000 |
| fastmri_full | SwinIR | baseline_disagreement | top_risk_aurc | 0.8254 | 0.4722 | 0.6667 |
| fastmri_full | SwinIR | baseline_disagreement | top_mae_50pct_low_u | 0.7937 | 0.3611 | 0.3333 |
| fastmri_full | SwinIR | baseline_disagreement | bottom_ssim | 0.7937 | 0.3611 | 0.3333 |
| fastmri_full | SwinIR | baseline_disagreement | bottom_mask_ssim | 0.6190 | 0.1987 | 0.0000 |
| ningxia_cv | HAT | baseline_disagreement | top_mae | 0.9474 | 0.8333 | 0.6667 |
| ningxia_cv | HAT | baseline_disagreement | top_risk_aurc | 0.8947 | 0.6333 | 0.3333 |
| ningxia_cv | HAT | baseline_disagreement | top_mae_50pct_low_u | 0.8947 | 0.4778 | 0.3333 |
| ningxia_cv | HAT | baseline_disagreement | bottom_ssim | 0.8596 | 0.4111 | 0.3333 |
| ningxia_cv | HAT | baseline_disagreement | bottom_mask_ssim | 0.3333 | 0.1313 | 0.0000 |
| ningxia_cv | I3Net | baseline_disagreement | top_mae | 0.9474 | 0.8333 | 0.6667 |
| ningxia_cv | I3Net | baseline_disagreement | top_risk_aurc | 0.8947 | 0.6333 | 0.3333 |
| ningxia_cv | I3Net | baseline_disagreement | top_mae_50pct_low_u | 0.8947 | 0.4778 | 0.3333 |
| ningxia_cv | I3Net | baseline_disagreement | bottom_ssim | 0.8596 | 0.4111 | 0.3333 |
| ningxia_cv | I3Net | baseline_disagreement | bottom_mask_ssim | 0.3333 | 0.1313 | 0.0000 |
| ningxia_cv | SwinIR | baseline_disagreement | top_mae | 0.9474 | 0.8333 | 0.6667 |
| ningxia_cv | SwinIR | baseline_disagreement | top_risk_aurc | 0.8947 | 0.6333 | 0.3333 |
| ningxia_cv | SwinIR | baseline_disagreement | top_mae_50pct_low_u | 0.8947 | 0.4778 | 0.3333 |
| ningxia_cv | SwinIR | baseline_disagreement | bottom_ssim | 0.8596 | 0.4111 | 0.3333 |
| ningxia_cv | SwinIR | baseline_disagreement | bottom_mask_ssim | 0.3333 | 0.1313 | 0.0000 |

## 3. Domain shift 摘要

| Dataset | Method | All-pixel corr | Nonzero corr | Background corr | Background fraction |
|---|---|---:|---:|---:|---:|
| full_test115 | ACSI | 0.5667 | 0.4037 | 0.5231 | 0.5894 |
| full_test115 | HAT | 0.6090 | 0.4628 | 0.5488 | 0.5894 |
| full_test115 | I3Net | 0.5018 | 0.3068 | 0.4941 | 0.5894 |
| full_test115 | SwinIR | 0.6153 | 0.4711 | 0.5660 | 0.5894 |
| fastmri_full | HAT | 0.4895 | 0.3176 | 0.4574 | 0.4324 |
| fastmri_full | I3Net | 0.4138 | 0.2347 | 0.3953 | 0.4324 |
| fastmri_full | SwinIR | 0.5122 | 0.3500 | 0.4609 | 0.4324 |
| ningxia_cv | HAT | 0.4581 | 0.2904 | 0.4116 | 0.4094 |
| ningxia_cv | I3Net | 0.4856 | 0.3137 | 0.5131 | 0.4094 |
| ningxia_cv | SwinIR | 0.4562 | 0.2886 | 0.3967 | 0.4094 |

## 4. 当前判断

- baseline disagreement 在三数据集上保持正相关，支持作为主 proxy。
- calibration 单调性和 failure definition ablation 可用于回应审稿人关于可靠性是否稳定的质疑。
- 后续若继续补实验，优先级为：TTA variance > learned uncertainty full training。前者是 proxy ablation，后者会改变论文资源和方法定位。
