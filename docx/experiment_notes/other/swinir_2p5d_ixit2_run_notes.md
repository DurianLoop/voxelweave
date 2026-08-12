# SwinIR-style 2.5D IXI-T2/x4 run notes

更新日期：2026-06-10

## 方法口径

本轮实现的是 `SwinIR-style 2.5D reproduction`，用于当前项目的 `IXI-T2 / x4 / through-plane interpolation` 协议。它不是官方 SwinIR 论文的原始 reported protocol，也不是把自然图像 SR 代码直接套到 MRI，而是把 Swin Transformer restoration block 接到本项目统一的数据、split、归一化、推理和指标脚本上。

输入为 4 通道 2.5D 条件：

| channel | 含义 |
|---|---|
| 1 | left slice |
| 2 | right slice |
| 3 | linear coarse slice |
| 4 | relative offset map |

模型预测 residual，并加回 linear coarse slice，输出中间目标层。输出文件前缀使用 `diff_`，保证能复用当前统一评估脚本并和 Linear / Cubic / ArSSR / CycleINR / ResUNet / SAINT-style 放到同一张大表。

代码目录：

- `ixi_swinir_2p5d/model.py`
- `ixi_swinir_2p5d/train.py`
- `ixi_swinir_2p5d/run_all.py`
- `ixi_swinir_2p5d/paper_table.py`
- `ixi_swinir_2p5d/settings.py`

## Smoke 结果

运行命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_swinir_2p5d.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m ixi_swinir_2p5d.paper_table --profile smoke
```

`smoke` 只用于检查代码链路，不进入主表。

| method | cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| linear | 1 | 27.4291 | 0.8772 | 26.3205 | 3283.3493 | 0.9566 |
| cubic | 1 | 27.1568 | 0.8682 | 27.6104 | 3523.0295 | 0.9507 |
| swinir | 1 | 27.4712 | 0.8762 | 26.3609 | 3258.6717 | 0.9570 |

结论：链路正常。SwinIR 在 PSNR / MSE / NCC 上略优于 Linear，在 SSIM / MAE 上略低于 Linear；单 case 只作为 sanity check。

## Mini 结果

运行命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_swinir_2p5d.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_swinir_2p5d.paper_table --profile mini
```

结果文件：

- `ixi_swinir_2p5d/runs/mini/metrics/summary_metrics.csv`
- `ixi_swinir_2p5d/runs/mini/metrics/paper_table.md`
- `ixi_swinir_2p5d/runs/mini/metrics/per_case_metrics.csv`
- `ixi_swinir_2p5d/runs/mini/training_history.csv`

| method | cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| linear | 5 | 25.0849 | 0.8268 | 47.0867 | 12633.8805 | 0.9121 | 0.0000 | 0.0000 |
| cubic | 5 | 24.6061 | 0.8131 | 51.1790 | 14744.4780 | 0.8988 | 0.0000 | 0.0000 |
| swinir | 5 | 26.1677 | 0.8547 | 41.4350 | 10526.4317 | 0.9303 | 0.0942 | 11.7634 |

相对 Linear 的均值变化：

| metric | per-case wins | delta |
|---|---:|---:|
| PSNR | 5/5 | +1.082799 |
| SSIM | 5/5 | +0.027929 |
| MAE | 5/5 | -5.651689 |
| MSE | 5/5 | -2107.448836 |
| NCC | 5/5 | +0.018189 |

相对 Cubic 的均值变化：

| metric | per-case wins | delta |
|---|---:|---:|
| PSNR | 5/5 | +1.561560 |
| SSIM | 5/5 | +0.041556 |
| MAE | 5/5 | -9.743941 |
| MSE | 5/5 | -4218.046255 |
| NCC | 5/5 | +0.031436 |

训练曲线：

| epoch | train_loss | val_loss | improved |
|---:|---:|---:|---|
| 1 | 0.118494 | 0.111637 | True |
| 2 | 0.104850 | 0.108857 | True |
| 3 | 0.099410 | 0.102923 | True |
| 4 | 0.095191 | 0.100814 | True |
| 5 | 0.091903 | 0.096685 | True |

## 当前判断

`mini` 结果显示 SwinIR-style 2.5D 在 5 个 IXI-T2 case 上稳定超过 Linear 和 Cubic，且五个主指标均为 5/5 per-case wins。因此它值得进入 `IXI-T2 full test n=25`。

mini 阶段不写入 `experiment_master_table.md` 的主表；主表只记录 full 或完整 CV 口径。该判断已由下面的 full 结果替代。

## Full 指令

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m ixi_swinir_2p5d.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m ixi_swinir_2p5d.paper_table --profile full
```

## Full 结果

完成日期：2026-06-12

| method | cases | PSNR | SSIM | MAE | MSE | NCC | Params(M) | FLOPs(G) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| linear | 25 | 26.1113 | 0.8588 | 34.6798 | 7643.7916 | 0.9318 | 0.0000 | 0.0000 |
| cubic | 25 | 25.6655 | 0.8486 | 36.9456 | 8472.9004 | 0.9215 | 0.0000 | 0.0000 |
| swinir | 25 | 28.7582 | 0.9060 | 25.6723 | 4585.3369 | 0.9618 | 0.2239 | 28.3682 |

相对 Linear/Cubic：SwinIR-style 2.5D 在 25 个 IXI-T2 test case 上五个主指标均为 25/25 per-case wins。

相对其他本地 full baseline：

| compared method | PSNR wins | SSIM wins | MAE wins | MSE wins | NCC wins | mean delta summary |
|---|---:|---:|---:|---:|---:|---|
| ResUNet residual | 25/25 | 25/25 | 25/25 | 25/25 | 25/25 | PSNR +1.2883, SSIM +0.0186, MAE -3.7131 |
| ArSSR-style | 25/25 | 25/25 | 25/25 | 24/25 | 25/25 | PSNR +1.5688, SSIM +0.0235, MAE -4.3711 |
| CycleINR-style | 25/25 | 25/25 | 25/25 | 25/25 | 25/25 | PSNR +2.6462, SSIM +0.0473, MAE -9.0054 |
| SAINT-style | 8/25 | 23/25 | 20/25 | 6/25 | 4/25 | PSNR -0.0398, SSIM +0.0033, MAE -0.4813 |

结论：SwinIR-style 2.5D 已经是 IXI-T2 上和 SAINT-style 同一级别的强 baseline。按均值看，SAINT-style 仍在 PSNR / MSE / NCC 上略优，SwinIR-style 2.5D 在 SSIM / MAE 上更优。因此当前不再能简单写“SAINT-style 是唯一最强 baseline”，更稳妥的表述是：SAINT-style 与 SwinIR-style 2.5D 构成当前 IXI-T2/x4 的第一梯队。

主表已更新：

- `docx/experiment/experiment_master_table.md`
