# I3Net IXI-T2/x4 run notes

更新日期：2026-06-16

## 方法口径

本轮接入 `I3Net: Inter-Intra-slice Interpolation Network for Medical Slice Synthesis`，论文为 TMI 2024。公开论文页和代码入口：

- Paper: https://doi.org/10.1109/TMI.2024.3394033
- arXiv: https://arxiv.org/abs/2405.02857
- Code: https://github.com/DeepMed-Lab-ECNU/Medical-Image-Reconstruction

本地已存在源码副本：

```text
external/I3Net/
external/Medical-Image-Reconstruction/
```

I3Net 的接口与本项目 `x4 through-plane interpolation` 很贴近：输入 4 个 sparse through-plane slices，输出 `(4 - 1) * 4 + 1 = 13` 个 HR slices，并把原 sparse anchor slice 直接复制回输出。当前接入保持这个 window-level 设定，而不是改写成单 slice residual 模型。

新增代码：

- `ixi_i3net/settings.py`
- `ixi_i3net/data.py`
- `ixi_i3net/train.py`
- `ixi_i3net/run_all.py`
- `ixi_i3net/paper_table.py`

依赖补齐：

```powershell
D:\conda\envs\MRI\python.exe -m pip install einops
```

## Profile 说明

| profile | 用途 | train / val / test | epochs | model width | 是否进主表 |
|---|---|---:|---:|---:|---|
| smoke | 管线验证 | 2 / 1 / 1 | 1 | n_feats=16 | 否 |
| mini | IXI 小规模筛选 | 8 / 2 / 2 | 3 | n_feats=32 | 否 |
| full | 主表候选 | all / all / 25 | 30 | n_feats=64 official | 是 |

注意：I3Net 原始 cross-view alignment 依赖固定的 body depth 位置，因此所有 profile 都保留 `num_blocks=16`。smoke/mini 只缩小 `n_feats` 和训练数据量。

## Smoke 结果

运行命令：

```powershell
D:\conda\envs\MRI\python.exe -m ixi_i3net.run_all --profile smoke
```

输出目录：

```text
ixi_i3net/runs/smoke/
```

| method | cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| linear | 1 | 27.4291 | 0.8772 | 26.3205 | 3283.3493 | 0.9566 |
| cubic | 1 | 27.1568 | 0.8682 | 27.6104 | 3523.0295 | 0.9507 |
| i3net | 1 | 18.0946 | 0.5057 | 88.1267 | 29774.0637 | 0.7251 |

结论：smoke 只证明训练、推理、NIfTI 输出和统一指标链路可跑通。该配置太小且只训练 1 epoch，结果不作为模型判断。

## Mini 结果

运行命令：

```powershell
D:\conda\envs\MRI\python.exe -m ixi_i3net.run_all --profile mini
D:\conda\envs\MRI\python.exe -m ixi_i3net.paper_table --profile mini
```

输出目录：

```text
ixi_i3net/runs/mini/
```

训练曲线：

| epoch | train_loss | val_loss | improved |
|---:|---:|---:|---|
| 1 | 0.025160 | 0.014412 | True |
| 2 | 0.013117 | 0.012311 | True |
| 3 | 0.011661 | 0.011550 | True |

主指标：

| method | cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| linear | 2 | 23.8926 | 0.7638 | 54.6535 | 16518.7019 | 0.8756 |
| cubic | 2 | 23.3145 | 0.7435 | 60.9144 | 20319.2395 | 0.8548 |
| i3net | 2 | 24.2161 | 0.7417 | 53.3115 | 15740.6671 | 0.8826 |

相对 Linear：

| metric | delta |
|---|---:|
| PSNR | +0.3235 |
| SSIM | -0.0220 |
| MAE | -1.3420 |
| MSE | -778.0348 |
| NCC | +0.0070 |

## 当前判断

1. I3Net 官方架构已完成本地接入，IXI-T2 smoke/mini 链路正常。
2. mini 已经在 PSNR / MAE / MSE / NCC 上略优于 Linear，但 SSIM 暂低于 Linear；这说明 full 值得跑，但不应直接预设一定超过 SwinIR-style 2.5D 或 SAINT-style。
3. mini 使用 `n_feats=32`，不是官方宽度；只有 `full` profile 的结果可以进入 `docx/experiment/experiment_master_table.md`。
4. `intensity_sanity.csv` 里模型输出行名沿用了旧 helper 的 `diffusion` 字段名，实际对应 `i3net` 输出，不影响 metrics 计算，但后续可统一改名。

## Full 结果

完成日期：2026-06-17

运行命令：

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -m ixi_i3net.run_all --profile full
D:\conda\envs\MRI\python.exe -m ixi_i3net.paper_table --profile full
```

输出目录：

```text
ixi_i3net/runs/full/
```

主指标：

| method | cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| linear | 25 | 26.1113 | 0.8588 | 34.6798 | 7643.7916 | 0.9318 |
| cubic | 25 | 25.6655 | 0.8486 | 36.9456 | 8472.9004 | 0.9215 |
| i3net | 25 | 31.0386 | 0.9278 | 20.5964 | 2994.9736 | 0.9736 |

相对 Linear：

| metric | per-case wins | mean delta |
|---|---:|---:|
| PSNR | 25/25 | +4.9272 |
| SSIM | 25/25 | +0.0690 |
| MAE | 25/25 | -14.0834 |
| MSE | 25/25 | -4648.8180 |
| NCC | 25/25 | +0.0418 |

相对已有第一梯队：

| method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| SwinIR-style 2.5D | 28.7582 | 0.9060 | 25.6723 | 4585.3369 | 0.9618 |
| SAINT-style | 28.7980 | 0.9027 | 26.1536 | 4552.2339 | 0.9622 |
| I3Net | 31.0386 | 0.9278 | 20.5964 | 2994.9736 | 0.9736 |

训练稳定性 caveat：

| epoch range | 观察 |
|---|---|
| 0-5 | train / val loss 正常下降，best val loss 到 0.007014 |
| 6-13 | train / val loss 变为 `nan` |
| final eval checkpoint | 使用的是 epoch 5 的 best checkpoint，不是 NaN 后的 final 权重 |

当前判断更新：

1. I3Net 在 IXI-T2 full test n=25 上显著超过 Linear/Cubic、SwinIR-style 2.5D 和 SAINT-style，是当前 IXI 最强 published medical slice synthesis baseline。
2. 结果已经写入 `docx/experiment/experiment_master_table.md`，但 fastMRI / NingXia 仍为 pending。
3. 训练过程出现 NaN，虽然 best checkpoint 可用，但扩展到 fastMRI / NingXia 前应先修稳定性：关闭 AMP 或降低 LR，并加入 NaN guard。

## Full test n=115 结果

完成日期：2026-06-17

本轮不重新训练，只使用 `ixi_i3net/runs/full/checkpoints/i3net_epoch_best.pth` 在完整 IXI test split 上评估。

运行命令：

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m ixi_i3net.run_all --profile full_test115 --eval-only-checkpoint ixi_i3net\runs\full\checkpoints\i3net_epoch_best.pth
D:\conda\envs\MRI\python.exe -B -m ixi_i3net.paper_table --profile full_test115
```

输出目录：

```text
ixi_i3net/runs/full_test115/
```

主指标：

| method | cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| linear | 115 | 26.1722 | 0.8529 | 29.2781 | 6553.8673 | 0.9390 |
| cubic | 115 | 25.7138 | 0.8422 | 31.1269 | 7217.2979 | 0.9303 |
| i3net | 115 | 30.7526 | 0.9231 | 18.5089 | 2858.7057 | 0.9771 |

相对 Linear：

| metric | per-case wins | mean delta |
|---|---:|---:|
| PSNR | 115/115 | +4.5805 |
| SSIM | 115/115 | +0.0702 |
| MAE | 115/115 | -10.7691 |
| MSE | 115/115 | -3695.1616 |
| NCC | 115/115 | +0.0381 |

相对 Cubic：

| metric | per-case wins | worst delta |
|---|---:|---:|
| PSNR | 115/115 | +1.7489 |
| SSIM | 115/115 | +0.0394 |
| MAE | 115/115 | -3.3715 |
| MSE | 115/115 | -290.9159 |
| NCC | 115/115 | +0.0215 |

判断：

1. I3Net 在完整 IXI test n=115 上仍然稳定显著优于 Linear/Cubic，前 25 例结果不是偶然。
2. 后续 IXI 方向的新实验建议优先使用 `test n=115` 作为完整公开 benchmark 口径。
3. 旧主表中的 IXI n=25 横向结果暂不混改；等 I3Net / HAT / Mamba 等整体跑完后，再统一补齐所有关键方法的 IXI n=115 横向表。
