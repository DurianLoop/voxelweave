# RASI post-hoc 第三步 QC：full_test115

本 QC 只检查 post-hoc uncertainty 分析链路，不训练新模型。

## 已完成检查

- 对齐检查：115/115 个 case 的 GT、linear、cubic、I3Net、HAT、SwinIR、ACSI shape 一致。
- 生成切片检查：0 个 method/case 行与 x4 generated-slice 规则不一致。
- 背景影响检查：已输出全像素、非零脑区、背景区域三套 pixel correlation。
- pixel/slice 分歧检查：已输出相关性差距较大的 case。
- failure case 排名：已按 MAE 与 uncertainty 均值输出 top cases。

## 非零区域相关性摘要

| Method / proxy | all pixel corr | nonzero corr | nonzero-all | background fraction |
|---|---:|---:|---:|---:|
| acsinet__baseline_disagreement | 0.5667 | 0.4037 | -0.1630 | 0.5894 |
| acsinet__residual_cubic | 0.4271 | 0.2438 | -0.1834 | 0.5894 |
| acsinet__residual_linear | 0.4101 | 0.2335 | -0.1766 | 0.5894 |
| hat__baseline_disagreement | 0.6090 | 0.4628 | -0.1462 | 0.5894 |
| hat__residual_cubic | 0.4269 | 0.2464 | -0.1805 | 0.5894 |
| hat__residual_linear | 0.4096 | 0.2386 | -0.1711 | 0.5894 |
| i3net__baseline_disagreement | 0.5018 | 0.3068 | -0.1950 | 0.5894 |
| i3net__residual_cubic | 0.4406 | 0.2548 | -0.1858 | 0.5894 |
| i3net__residual_linear | 0.4363 | 0.2552 | -0.1811 | 0.5894 |
| swinir__baseline_disagreement | 0.6153 | 0.4711 | -0.1442 | 0.5894 |
| swinir__residual_cubic | 0.4217 | 0.2408 | -0.1809 | 0.5894 |
| swinir__residual_linear | 0.4031 | 0.2336 | -0.1695 | 0.5894 |

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
