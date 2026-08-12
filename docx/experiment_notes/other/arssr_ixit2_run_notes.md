# ArSSR-style IXI-T2/x4 复现记录

更新时间：2026-06-05

本文档记录 `ixi_arssr/` 的接入方式和当前 smoke/mini 结果。该实现是 ArSSR-style reproduction：保留 ArSSR 的 `3D feature encoder + coordinate MLP` 核心思想，但训练、split、x4 sparse/GT 生成、Linear/Cubic baseline、metrics 和输出目录全部对齐本项目已有 IXI-T2 主表口径。

## 1. 方法口径

| 项目 | 当前设置 |
|---|---|
| Dataset | IXI-T2 |
| Scale | x4 through-plane |
| Split | `dataset/IXI/splits/seed3407` |
| Input | sparse T2 volume, z 方向每 4 层保留 1 层 |
| Target | aligned full T2 volume |
| Model | ArSSR-style 3D encoder + coordinate MLP |
| Adaptation | linear densified sparse volume + coordinate residual correction |
| Metrics | PSNR / SSIM / MAE / MSE / NCC，使用现有 `topcow_diffusion.metrics` |
| Baselines | Linear / Cubic 同 profile 内重跑 |
| Source label | `ours ArSSR-style reproduction` |

说明：这里不是官方 ArSSR 的 HCP-1200 reported protocol，也不直接复用官方训练脚本；原因是官方数据、裁剪和任务口径与当前 IXI-T2/x4 through-plane 主表不一致。为了放进同一张大表，必须使用本项目统一 split 和评估脚本。

## 2. 文件结构

```text
ixi_arssr/
  settings.py
  data.py
  model.py
  train.py
  inference.py
  run_all.py
  paper_table.py
  runs/
    smoke/
    mini/
```

每个 profile 输出结构与现有实验保持一致：

```text
runs/{profile}/run_manifest.json
runs/{profile}/training_history.csv
runs/{profile}/checkpoints/arssr_epoch_best.pth
runs/{profile}/eval_inputs/gt
runs/{profile}/eval_inputs/sparse
runs/{profile}/baseline_outputs/linear
runs/{profile}/baseline_outputs/cubic
runs/{profile}/model_outputs
runs/{profile}/metrics/per_case_metrics.csv
runs/{profile}/metrics/summary_metrics.csv
runs/{profile}/metrics/paper_table.csv
runs/{profile}/metrics/paper_table.md
```

## 3. 已完成结果

### smoke

命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_arssr.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m ixi_arssr.paper_table --profile smoke
```

结果：链路已跑通，`arssr` 输出与 `linear` 基本一致，说明 sparse/GT、坐标轴、强度反归一化和评估口径已经对齐。

### mini

命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_arssr.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_arssr.paper_table --profile mini
```

当前 mini 结果：

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| ArSSR-style | 2 | 23.8926 | 0.7638 | 54.6524 | 16518.6681 | 0.8756 |
| Linear | 2 | 23.8926 | 0.7638 | 54.6535 | 16518.7019 | 0.8756 |
| Cubic | 2 | 23.3145 | 0.7435 | 60.9144 | 20319.2395 | 0.8548 |

解释：mini 只训练 3 epochs，当前主要证明接入链路和评估口径正确；它尚未证明 ArSSR-style 明显优于 Linear。full 需要用完整训练 split 和更长训练观察 residual 是否真正带来收益。

## 4. full 运行命令

一键脚本：

```powershell
.\temp\run_ixi_arssr_full.ps1
```

等价手动命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_arssr.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m ixi_arssr.paper_table --profile full
```

full profile 当前使用：

| Item | Value |
|---|---:|
| train cases | all IXI train T2 cases |
| val cases | all IXI val T2 cases |
| test cases | 25 |
| epochs | 30 |
| chunks per volume / epoch | 1 |
| samples per chunk | 2048 |
| feature channels | 24 |
| checkpoint rule | best validation loss |

full 跑完后，结果查看：

```text
ixi_arssr/runs/full/metrics/summary_metrics.csv
ixi_arssr/runs/full/metrics/paper_table.md
```

## 5. full 结果与分析

full 已完成，输出位于：

```text
ixi_arssr/runs/full
```

训练记录：

| Item | Value |
|---|---:|
| completed epochs | 30 |
| best val loss | 0.010294 |
| best epoch | 24 |
| final lr | 5e-05 |
| checkpoint used for inference | `checkpoints/arssr_epoch_best.pth` |

IXI-T2 full 结果：

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| ArSSR-style | 25 | 27.1894 | 0.8825 | 30.0435 | 6130.4423 | 0.9474 |
| Linear | 25 | 26.1113 | 0.8588 | 34.6798 | 7643.7916 | 0.9318 |
| Cubic | 25 | 25.6655 | 0.8486 | 36.9456 | 8472.9004 | 0.9215 |

相对 Linear：

| Metric | Delta |
|---|---:|
| PSNR | +1.0780 dB |
| SSIM | +0.0237 |
| MAE | -4.6364 |
| MSE | -1513.3493 |
| NCC | +0.0156 |

逐病例胜负：

| Comparison | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| ArSSR-style vs Linear | 25/25 | 25/25 | 25/25 | 25/25 | 25/25 |
| ArSSR-style vs Cubic | 25/25 | 25/25 | 25/25 | 25/25 | 25/25 |

结论：ArSSR-style 在 IXI-T2 full 上已经稳定优于 Linear/Cubic，说明 INR published baseline 接入成功，可以进入主表的 IXI-T2 列。但它仍低于 `ResUNet residual` 和 `SAINT-style`，因此当前定位应是 published INR baseline，而不是最强方法。

下一步需要补同口径 `fastMRI-brain-T2 expanded` 和 `NingXia-T2 case-level CV`，否则不能在三数据集横向主表中和 SAINT-style 做完整公平比较。

## 6. fastMRI-brain-T2 expanded full 结果

fastMRI-brain-T2 expanded 已完成同口径 ArSSR-style full：

```text
fastmri_brain_arssr/runs/full
```

训练与测试口径：

| Item | Value |
|---|---:|
| dataset | fastMRI-brain-T2 expanded |
| split | 160 NIfTI, train/val/test = 112/24/24 |
| scale | x4 through-plane |
| epochs | 30 |
| seconds / epoch | about 15 s |
| checkpoint used for inference | `checkpoints/arssr_epoch_best.pth` |

说明：这次 full 很快结束不是因为只跑了 smoke，而是因为该 ArSSR-style 配置是坐标点采样训练，每个 epoch 只对每个 volume 抽取有限点数，模型参数量也很小。

full 结果：

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| ArSSR-style | 24 | 20.3143 | 0.6575 | 65.9931 | 17745.8948 | 0.8301 |
| Linear | 24 | 19.1133 | 0.5970 | 78.8111 | 23092.0046 | 0.7733 |
| Cubic | 24 | 17.9736 | 0.5332 | 91.9330 | 29740.2642 | 0.7285 |

相对 Linear：

| Metric | Delta |
|---|---:|
| PSNR | +1.2010 dB |
| SSIM | +0.0605 |
| MAE | -12.8180 |
| MSE | -5346.1098 |
| NCC | +0.0568 |

逐病例胜负：

| Comparison | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| ArSSR-style vs Linear | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 |
| ArSSR-style vs Cubic | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 |

结论：ArSSR-style 在 fastMRI-brain-T2 expanded 上稳定优于 Linear/Cubic，可以进入主表；但仍低于 ResUNet residual 与 SAINT-style。因此当前定位保持为 published INR baseline，而不是最强 baseline。

## 7. NingXia-T2 case-level 8-fold CV 结果

NingXia-T2 已完成同口径 ArSSR-style 8-fold case-level CV：

```text
ningxia_t2_arssr_cv/runs/fold_00/full
...
ningxia_t2_arssr_cv/runs/fold_07/full
```

训练与测试口径：

| Item | Value |
|---|---:|
| dataset | NingXia-T2 |
| cases / series | 8 cases / 22 T2 series |
| split | case-level 8-fold CV |
| per fold | 6 train cases / 1 val case / 1 test case |
| scale | x4 through-plane |
| profile | full |
| source label | `ours ArSSR-style reproduction; case-level 8-fold CV` |

CV mean 结果：

| Method | Folds | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| ArSSR-style | 8 | 23.1634 | 0.7091 | 96.4890 | 38343.9409 | 0.8708 |
| Linear | 8 | 22.7335 | 0.6749 | 103.2052 | 42189.1127 | 0.8576 |
| Cubic | 8 | 21.6460 | 0.6184 | 119.4078 | 53313.5368 | 0.8252 |
| ResUNet residual | 8 | 23.3816 | 0.7209 | 97.0409 | 36316.2290 | 0.8785 |
| SAINT-style | 8 | 23.8350 | 0.7422 | 89.4140 | 32992.9496 | 0.8905 |

相对 Linear：

| Metric | Delta |
|---|---:|
| PSNR | +0.4299 dB |
| SSIM | +0.0342 |
| MAE | -6.7162 |
| MSE | -3845.1718 |
| NCC | +0.0132 |

逐 fold 胜负：

| Comparison | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| ArSSR-style vs Linear | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 |
| ArSSR-style vs Cubic | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 |

结论：ArSSR-style 在 NingXia-T2 8-fold CV 上稳定优于 Linear/Cubic，三数据集横向主表可以补齐。它在 NingXia 上低于 SAINT-style，和 ResUNet residual 接近；因此定位仍是稳定的 published INR baseline，而不是当前最强 baseline。
