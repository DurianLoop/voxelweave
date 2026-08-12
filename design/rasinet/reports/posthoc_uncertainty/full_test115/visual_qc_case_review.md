# full_test115 visual QC case review

主可视化对象：`SwinIR + baseline_disagreement`。每张图包含 prediction、absolute error、uncertainty proxy。所有 case 只用于 post-hoc reliability 检查，不代表新模型训练结果。

| Group | Case | Slice | Error rank | Uncertainty rank | Pixel corr | Slice corr | Panel |
|---|---|---:|---:|---:|---:|---:|---|
| high_risk_high_error | IXI014-HH-1236-T2.nii.gz | 6 | 1 | 1 | 0.5371 | 0.5541 | `high_risk_high_error_01_IXI014-HH-1236-T2.png` |
| high_risk_high_error | IXI395-IOP-0969-T2.nii.gz | 54 | 2 | 2 | 0.5797 | 0.0876 | `high_risk_high_error_02_IXI395-IOP-0969-T2.png` |
| high_risk_high_error | IXI476-IOP-1140-T2.nii.gz | 65 | 3 | 4 | 0.6008 | 0.5693 | `high_risk_high_error_03_IXI476-IOP-1140-T2.png` |
| high_risk_high_error | IXI442-IOP-1041-T2.nii.gz | 50 | 6 | 3 | 0.6047 | 0.3424 | `high_risk_high_error_04_IXI442-IOP-1041-T2.png` |
| high_risk_high_error | IXI464-IOP-1029-T2.nii.gz | 53 | 4 | 7 | 0.5793 | 0.6503 | `high_risk_high_error_05_IXI464-IOP-1029-T2.png` |
| low_risk_low_error | IXI260-HH-1805-T2.nii.gz | 125 | 115 | 115 | 0.6256 | 0.7935 | `low_risk_low_error_01_IXI260-HH-1805-T2.png` |
| low_risk_low_error | IXI225-Guys-0832-T2.nii.gz | 125 | 114 | 113 | 0.6204 | 0.2111 | `low_risk_low_error_02_IXI225-Guys-0832-T2.png` |
| low_risk_low_error | IXI648-Guys-1107-T2.nii.gz | 127 | 113 | 112 | 0.6063 | 0.6071 | `low_risk_low_error_03_IXI648-Guys-1107-T2.png` |
| low_risk_low_error | IXI605-HH-2598-T2.nii.gz | 125 | 110 | 114 | 0.6220 | 0.6219 | `low_risk_low_error_04_IXI605-HH-2598-T2.png` |
| low_risk_low_error | IXI189-Guys-0799-T2.nii.gz | 125 | 112 | 111 | 0.6289 | 0.4706 | `low_risk_low_error_05_IXI189-Guys-0799-T2.png` |
| high_uncertainty_low_error | IXI482-HH-2178-T2.nii.gz | 42 | 75 | 57 | 0.6154 | 0.5323 | `high_uncertainty_low_error_01_IXI482-HH-2178-T2.png` |
| high_uncertainty_low_error | IXI019-Guys-0702-T2.nii.gz | 106 | 28 | 15 | 0.6184 | 0.3960 | `high_uncertainty_low_error_02_IXI019-Guys-0702-T2.png` |
| high_uncertainty_low_error | IXI560-Guys-1070-T2.nii.gz | 98 | 79 | 68 | 0.6375 | 0.3016 | `high_uncertainty_low_error_03_IXI560-Guys-1070-T2.png` |
| low_uncertainty_high_error | IXI072-HH-2324-T2.nii.gz | 43 | 51 | 87 | 0.5103 | 0.5945 | `low_uncertainty_high_error_01_IXI072-HH-2324-T2.png` |
| low_uncertainty_high_error | IXI353-HH-1996-T2.nii.gz | 55 | 76 | 95 | 0.5758 | 0.5333 | `low_uncertainty_high_error_02_IXI353-HH-1996-T2.png` |
| low_uncertainty_high_error | IXI603-HH-2701-T2.nii.gz | 54 | 88 | 107 | 0.6568 | 0.8276 | `low_uncertainty_high_error_03_IXI603-HH-2701-T2.png` |
| pixel_slice_gap | IXI411-Guys-0959-T2.nii.gz | 54 | 91 | 83 | 0.5808 | -0.2869 | `pixel_slice_gap_01_IXI411-Guys-0959-T2.png` |
| pixel_slice_gap | IXI359-Guys-0918-T2.nii.gz | 42 | 101 | 97 | 0.5957 | -0.1195 | `pixel_slice_gap_02_IXI359-Guys-0918-T2.png` |
| pixel_slice_gap | IXI210-Guys-0856-T2.nii.gz | 58 | 60 | 58 | 0.6295 | -0.0102 | `pixel_slice_gap_03_IXI210-Guys-0856-T2.png` |

阅读建议：

- `high_risk_high_error` 应用于展示 uncertainty proxy 是否能覆盖真实失败区域。
- `low_risk_low_error` 用于展示低风险 case 的背景和结构区域是否稳定。
- `high_uncertainty_low_error` 与 `low_uncertainty_high_error` 是必须保留的反例类别，避免只展示成功样本。
- `pixel_slice_gap` 用于检查 pixel-level 与 slice-level 结论不一致的 case。
