# CycleINR-style IXI-T2/x4 复现记录

本文档记录 `ixi_cycleinr/` 的本地接入与当前 smoke/mini 结果。该实现是 CycleINR-style reproduction：在本项目已有 ArSSR-style `3D encoder + coordinate MLP` 基础上加入 sparse-plane cycle consistency，使预测在原始稀疏采样平面上回到输入强度。训练、split、x4 sparse/GT 生成、Linear/Cubic baseline、metrics 和输出目录均对齐 IXI-T2 主表口径。

说明：当前不是官方 CycleINR 代码的严格复刻，不能直接写成官方复现；它适合作为本项目内部 CycleINR-style 可行性检查。

## 1. 代码位置

```text
ixi_cycleinr/
  settings.py
  data.py
  train.py
  run_all.py
  paper_table.py
```

输出目录：

```text
ixi_cycleinr/runs/{profile}
```

## 2. Smoke

命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_cycleinr.run_all --profile smoke
D:\conda\envs\MRI\python.exe -B -m ixi_cycleinr.paper_table --profile smoke
```

结果：

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Linear | 1 | 27.4291 | 0.8772 | 26.3205 | 3283.3493 | 0.9566 |
| Cubic | 1 | 27.1568 | 0.8682 | 27.6104 | 3523.0295 | 0.9507 |
| CycleINR-style | 1 | 27.4292 | 0.8773 | 26.3197 | 3283.2548 | 0.9566 |

## 3. Mini

命令：

```powershell
D:\conda\envs\MRI\python.exe -B -m ixi_cycleinr.run_all --profile mini
D:\conda\envs\MRI\python.exe -B -m ixi_cycleinr.paper_table --profile mini
```

结果：

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Linear | 5 | 25.0849 | 0.8268 | 47.0867 | 12633.8805 | 0.9121 |
| Cubic | 5 | 24.6061 | 0.8131 | 51.1790 | 14744.4780 | 0.8988 |
| CycleINR-style | 5 | 25.0849 | 0.8268 | 47.0865 | 12633.8784 | 0.9121 |

逐病例胜负：

| Comparison | PSNR | SSIM | MAE | MSE | NCC |
| --- | ---: | ---: | ---: | ---: | ---: |
| CycleINR-style vs Linear | 4/5 | 5/5 | 5/5 | 3/5 | 3/5 |
| CycleINR-style vs Cubic | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |

均值差异：

| Metric | Delta vs Linear | Delta vs Cubic |
| --- | ---: | ---: |
| PSNR | +0.00000182 | +0.47876223 |
| SSIM | +0.00000074 | +0.01362829 |
| MAE | -0.00018100 | -4.09243244 |
| MSE | -0.00213994 | -2110.59955920 |
| NCC | +0.00000007 | +0.01324704 |

结论：CycleINR-style mini 稳定优于 Cubic，但与 Linear 几乎完全持平，优势只在数值误差级别；按当前筛选标准，不应扩展到 fastMRI-brain-T2 expanded，也不建议立刻消耗资源跑 full。

## 4. Full 指令

如后续需要保留 IXI-T2 full 对照，可运行：

```powershell
cd D:\MRI
D:\conda\envs\MRI\python.exe -B -m ixi_cycleinr.run_all --profile full
D:\conda\envs\MRI\python.exe -B -m ixi_cycleinr.paper_table --profile full
```

## 5. Full updated on 2026-06-10

full run completed:

```text
ixi_cycleinr/runs/full
```

| Method | Cases | PSNR | SSIM | MAE | MSE | NCC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Linear | 25 | 26.1113 | 0.8588 | 34.6798 | 7643.7916 | 0.9318 |
| Cubic | 25 | 25.6655 | 0.8486 | 36.9456 | 8472.9004 | 0.9215 |
| CycleINR-style | 25 | 26.1120 | 0.8587 | 34.6777 | 7643.8680 | 0.9318 |

Per-case wins:

| Comparison | PSNR | SSIM | MAE | MSE | NCC |
| --- | ---: | ---: | ---: | ---: | ---: |
| CycleINR-style vs Linear | 11/25 | 5/25 | 24/25 | 11/25 | 18/25 |
| CycleINR-style vs Cubic | 25/25 | 25/25 | 25/25 | 25/25 | 25/25 |

Mean deltas:

| Metric | Delta vs Linear | Delta vs Cubic |
| --- | ---: | ---: |
| PSNR | +0.00062859 | +0.44651364 |
| SSIM | -0.00014552 | +0.01010031 |
| MAE | -0.00209405 | -2.26783033 |
| MSE | +0.07645284 | -829.03234527 |
| NCC | -0.00003861 | +0.01023262 |

Conclusion: CycleINR-style full is consistently better than Cubic, but it does not stably beat Linear. Its PSNR/MAE gains over Linear are tiny, while SSIM/MSE/NCC are slightly worse on average. Do not expand this baseline to fastMRI-brain-T2 expanded or NingXia-T2 unless the implementation/training objective is changed.

更新建议：full 已完成，但 CycleINR-style 仍接近 Linear；下一步优先分析实现和训练目标，不扩展 fastMRI/NingXia。
