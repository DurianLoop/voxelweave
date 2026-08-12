# RASI post-hoc 第三步 QC：fastmri_full

本 QC 只检查 post-hoc uncertainty 分析链路，不训练新模型。

## 已完成检查

- 对齐检查：24/24 个 case 的 GT、linear、cubic、I3Net、HAT、SwinIR、ACSI shape 一致。
- 生成切片检查：0 个 method/case 行与 x4 generated-slice 规则不一致。
- 背景影响检查：已输出全像素、非零脑区、背景区域三套 pixel correlation。
- pixel/slice 分歧检查：已输出相关性差距较大的 case。
- failure case 排名：已按 MAE 与 uncertainty 均值输出 top cases。

## 非零区域相关性摘要

| Method / proxy | all pixel corr | nonzero corr | nonzero-all | background fraction |
|---|---:|---:|---:|---:|
| hat__baseline_disagreement | 0.4895 | 0.3176 | -0.1719 | 0.4324 |
| hat__residual_cubic | 0.3617 | 0.1813 | -0.1804 | 0.4324 |
| hat__residual_linear | 0.3728 | 0.1938 | -0.1790 | 0.4324 |
| i3net__baseline_disagreement | 0.4138 | 0.2347 | -0.1791 | 0.4324 |
| i3net__residual_cubic | 0.3568 | 0.1900 | -0.1668 | 0.4324 |
| i3net__residual_linear | 0.3778 | 0.2101 | -0.1677 | 0.4324 |
| swinir__baseline_disagreement | 0.5122 | 0.3500 | -0.1622 | 0.4324 |
| swinir__residual_cubic | 0.3487 | 0.1692 | -0.1795 | 0.4324 |
| swinir__residual_linear | 0.3574 | 0.1787 | -0.1787 | 0.4324 |

## 输出文件

- `qc_manifest.csv`
- `qc_alignment_summary.csv`
- `qc_generated_slice_check.csv`
- `qc_generated_slice_summary.csv`
- `qc_mask_background_per_case.csv`
- `qc_mask_background_summary.csv`
- `qc_pixel_slice_disagreement.csv`
- `qc_pixel_slice_disagreement_summary.csv`
- `qc_failure_case_review.csv`

## 后续判断

如果非零区域相关性仍保持正相关，则说明当前 reliability 结论不是单纯由背景区域支撑；如果某些 method/proxy 的 nonzero corr 大幅下降，后续主表要优先报告 masked 版本。
