# HAT / SMamba 当前运行状态记录 2026-06-29

本文档记录本轮命令的完成情况，避免把未完成的 cross-validation 结果误填入主表。

## 已完成

### IXI-T2 SMamba-UNet-style 2.5D

命令：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI;D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m ixi_smamba_unet_2p5d.paper_table --profile full_test115
```

输出：

- `D:\MRI\ixi_smamba_unet_2p5d\runs\full_test115\metrics\summary_metrics.csv`
- `D:\MRI\ixi_smamba_unet_2p5d\runs\full_test115\metrics\paper_table.csv`
- `D:\MRI\ixi_smamba_unet_2p5d\runs\full_test115\metrics\paper_table.md`

主表指标：

| Dataset | Profile | Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| IXI-T2 | full_test115 | SMamba-UNet-style 2.5D | 115 | 29.3536 | 0.9077 | 21.1352 | 3691.2381 | 0.9699 |

说明：该行已写入 `docx/experiment/experiment_master_table.md`，但由于早期 IXI 行多为 test n=25，暂不参与同列加粗最优标记。等前序方法补齐 n=115 后再统一重排。

### IXI-T2 HAT-style 2.5D

| Dataset | Profile | Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| IXI-T2 | full_test115 | HAT-style 2.5D | 115 | 28.7249 | 0.9016 | 22.2500 | 4088.7422 | 0.9663 |

### fastMRI-brain-T2 expanded HAT / SMamba

| Dataset | Profile | Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| fastMRI-brain-T2 expanded | full | HAT-style 2.5D | 24 | 22.7858 | 0.7536 | 49.6702 | 10454.4878 | 0.9079 |
| fastMRI-brain-T2 expanded | full | SMamba-UNet-style 2.5D | 24 | 22.7322 | 0.7618 | 49.4487 | 10826.4468 | 0.9051 |

## 尚未完成

### NingXia-T2 HAT 2.5D full case-level CV

当前已存在 full summary 的 folds：

- `fold_00`
- `fold_01`
- `fold_02`
- `fold_03`
- `fold_04`
- `fold_05`
- `fold_06`

缺失：

- `fold_07`

当前状态：7/8 folds completed。不能进入主表。

### NingXia-T2 SMamba-UNet-style 2.5D full case-level CV

当前已存在 full summary 的 folds：

- `fold_00`
- `fold_01`
- `fold_02`
- `fold_03`
- `fold_04`
- `fold_05`

缺失：

- `fold_06`
- `fold_07`

当前状态：6/8 folds completed。不能进入主表。

## 当前观察

`fold_00` 的局部结果显示 HAT 和 SMamba 均明显优于 Linear / Cubic：

| Fold | Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---|---:|---:|---:|---:|---:|
| fold_00 | Linear | 23.0590 | 0.6681 | 92.4671 | 28483.7821 | 0.8721 |
| fold_00 | Cubic | 21.8955 | 0.6138 | 107.2163 | 37366.5693 | 0.8409 |
| fold_00 | HAT 2.5D | 24.4209 | 0.7495 | 76.3000 | 20912.5193 | 0.9075 |
| fold_00 | SMamba-UNet-style 2.5D | 24.2911 | 0.7453 | 78.2230 | 21682.3790 | 0.9043 |

但该观察只来自单 fold，不能替代 8-fold case-level CV 均值。NingXia 结果必须等待 8 folds 全部完成并由 `processing.summarize_case_cv` 汇总后，才可以进入统一主表。

## 后续命令

如果当前 Python 进程仍在运行，不要重复启动。等它结束后可以只补缺失 folds：

```powershell
Set-Location D:\MRI
$env:PYTHONPATH = "D:\MRI;D:\MRI\pre"
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile full --models hat --folds fold_07
D:\conda\envs\MRI\python.exe -B -m processing.run_ningxia_case_cv --profile full --models smamba --folds fold_06 fold_07
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --profile full --include-hat --include-smamba
```

若汇总后出现 HAT / SMamba 的 8-fold mean，再补入 `docx/experiment/experiment_master_table.md`。
