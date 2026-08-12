# CycleINR-style fastMRI/NingXia 补全记录

更新时间：2026-06-16

## 任务

在已有 `IXI-T2 / x4 / CycleINR-style` full 结果基础上，补全剩余两个主表数据集：

- `fastMRI-brain-T2 expanded`，test n=24
- `NingXia-T2 case-level CV`，8 folds

## 本地实现口径

`CycleINR-style` 作为 published INR baseline 的本地 style reproduction。当前实现复用 `ArSSRInterpolator` 推理接口，训练目标为：

- sparse input 线性 densify 后进入 coordinate INR
- dense target reconstruction loss
- observed sparse planes 上的 cycle consistency loss

因此该行表示 CycleINR-style baseline 对齐实验，不写成官方逐细节复现。

## 运行命令

```powershell
D:\conda\envs\MRI\python.exe -u -B -m fastmri_brain_cycleinr.run_all --profile full
D:\conda\envs\MRI\python.exe -u -B -m fastmri_brain_cycleinr.paper_table --profile full

D:\conda\envs\MRI\python.exe -u -B -m processing.run_ningxia_cycleinr_cv --profile full
D:\conda\envs\MRI\python.exe -B -m processing.summarize_case_cv --title "NingXia-T2 Case-Level CV Full" --include-arssr --include-cycleinr --include-swinir
```

## 输出位置

```text
fastmri_brain_cycleinr/runs/full/metrics/summary_metrics.csv
fastmri_brain_cycleinr/runs/full/metrics/paper_table.md
ningxia_t2_cycleinr_cv/runs/fold_*/full/metrics/summary_metrics.csv
docx/experiment_notes/ningxia_case_cv_summary.csv
docx/experiment_notes/ningxia_case_cv_summary.md
```

## 主表结果

| Dataset | Cases | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|---:|
| IXI-T2 | 25 | 26.1120 | 0.8587 | 34.6777 | 7643.8680 | 0.9318 |
| fastMRI-brain-T2 expanded | 24 | 20.3156 | 0.6577 | 66.0985 | 17743.2358 | 0.8302 |
| NingXia-T2 case-level CV | 8 folds | 22.9009 | 0.6935 | 101.0990 | 40735.3568 | 0.8625 |

## 当前判断

CycleINR-style 三数据集横向已经补全，但结果不构成强 baseline：

- IXI-T2：基本贴近 Linear，不稳定超过 Linear。
- fastMRI-brain-T2 expanded：几乎与 ArSSR-style 持平，明显弱于 ResUNet residual / SwinIR-style 2.5D / SAINT-style。
- NingXia-T2：优于 Linear/Cubic，但弱于 ArSSR-style、ResUNet residual、SwinIR-style 2.5D、SAINT-style。

当前建议：保留 CycleINR-style 作为完整 published INR 对照，但后续不再优先投入调参，除非要专门做 INR 类方法的消融或需要从论文机制上解释任意尺度体数据 SR 在本项目协议中的边界。
