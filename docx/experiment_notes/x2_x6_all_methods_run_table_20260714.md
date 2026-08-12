# T2 x2/x6 全方法运行指令总表

更新时间：2026-07-14

本文档是在目录整理之后重新校准的运行表。当前代码布局为：

- baseline 方法代码：`D:\MRI\baseline\`
- 自研 design 方法代码：`D:\MRI\design\`
- 历史 IXI ResUNet / SAINT 综合包：`D:\MRI\pre\ixi_diffusion\`
- NingXia 统一 runner：`D:\MRI\processing\run_ningxia_case_cv.py`

重要：因为 baseline/design 代码已经从根目录移动到子目录，后续运行必须先设置 `PYTHONPATH` 和 fastMRI/NingXia 的 root 参数，否则会找不到模块或把输出写回旧位置。

## 0. 每次开终端先复制这一段

```powershell
Set-Location D:\MRI
$py = "D:\conda\envs\MRI\python.exe"

# 代码搜索路径：pre 里有 ixi_diffusion；baseline 里有公开 baseline；design 里有自研方法；D:\MRI 里有 processing。
$env:PYTHONPATH = "D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI"

# IXI 数据路径，供 ixi_diffusion / IXI baseline / design 复用。
$env:IXI_DATA_ROOT = "D:\MRI\dataset\IXI"

# fastMRI 数据路径。
$fastmriData = "D:\MRI\dataset\fastMRI_brain_T2\processed"
$env:FASTMRI_BRAIN_SAINT_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_ARSSR_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_CYCLEINR_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_SWINIR_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_HAT_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_SMAMBA_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_GAN_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_ACVTT_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_RESSRDIFF_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_I3NET_DATA_ROOT = $fastmriData
$env:FASTMRI_BRAIN_PASTNET_DATA_ROOT = $fastmriData

# fastMRI 输出路径，保证目录整理后仍然写到 baseline/design 子目录。
$env:FASTMRI_BRAIN_SAINT_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_saint\runs"
$env:FASTMRI_BRAIN_ARSSR_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_arssr\runs"
$env:FASTMRI_BRAIN_CYCLEINR_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_cycleinr\runs"
$env:FASTMRI_BRAIN_SWINIR_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_swinir_2p5d\runs"
$env:FASTMRI_BRAIN_HAT_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_hat_2p5d\runs"
$env:FASTMRI_BRAIN_SMAMBA_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_smamba_unet_2p5d\runs"
$env:FASTMRI_BRAIN_GAN_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_gan_2p5d\runs"
$env:FASTMRI_BRAIN_ACVTT_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_acvtt_2p5d\runs"
$env:FASTMRI_BRAIN_RESSRDIFF_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_ressrdiff_2p5d\runs"
$env:FASTMRI_BRAIN_I3NET_RUN_ROOT = "D:\MRI\baseline\fastmri_brain_i3net\runs"
$env:FASTMRI_BRAIN_PASTNET_RUN_ROOT = "D:\MRI\design\fastmri_brain_pastnet_2p5d\runs"

# NingXia runner / summarizer root 参数。后面的 NingXia 命令都带 @ningxiaRoots。
$ningxiaRoots = @(
  "--saint-run-root", "D:\MRI\baseline\ningxia_t2_saint_cv\runs",
  "--resunet-run-root", "D:\MRI\baseline\ningxia_t2_resunet_cv\runs",
  "--arssr-run-root", "D:\MRI\baseline\ningxia_t2_arssr_cv\runs",
  "--cycleinr-run-root", "D:\MRI\baseline\ningxia_t2_cycleinr_cv\runs",
  "--swinir-run-root", "D:\MRI\baseline\ningxia_t2_swinir_2p5d_cv\runs",
  "--i3net-run-root", "D:\MRI\baseline\ningxia_t2_i3net_cv\runs",
  "--hat-run-root", "D:\MRI\baseline\ningxia_t2_hat_2p5d_cv\runs",
  "--smamba-run-root", "D:\MRI\baseline\ningxia_t2_smamba_unet_2p5d_cv\runs",
  "--gan-run-root", "D:\MRI\baseline\ningxia_t2_gan_2p5d_cv\runs",
  "--acvtt-run-root", "D:\MRI\baseline\ningxia_t2_acvtt_2p5d_cv\runs",
  "--ressrdiff-run-root", "D:\MRI\baseline\ningxia_t2_ressrdiff_2p5d_cv\runs"
)
```

说明：

- Linear / Cubic 不需要单独训练，通常由每个 run 的 `paper_table.py` 或 metrics 阶段自动生成。
- 建议一次只跑一个 row，跑完确认 `summary_metrics.csv` 和 `paper_table.csv` 后再跑下一行。
- 如果显存紧张，优先停其他 Python 进程，再跑 HAT / SMamba / diffusion 类方法。

## 1. IXI-T2 test n=115，x2/x6 baseline

| 顺序 | 方法 | x2 运行 | x2 表格 | x6 运行 | x6 表格 | 备注 |
|---:|---|---|---|---|---|---|
| I-01 | ResUNet residual | `& $py -B -m ixi_diffusion.run_all --profile resunet_full_t2_test115_x2` | `& $py -B -m ixi_diffusion.paper_table --profile resunet_full_t2_test115_x2` | `& $py -B -m ixi_diffusion.run_all --profile resunet_full_t2_test115_x6` | `& $py -B -m ixi_diffusion.paper_table --profile resunet_full_t2_test115_x6` | 来自 `D:\MRI\pre\ixi_diffusion` |
| I-02 | SAINT | `& $py -B -m ixi_diffusion.run_all --profile saint_full_t2_test115_x2` | `& $py -B -m ixi_diffusion.paper_table --profile saint_full_t2_test115_x2` | `& $py -B -m ixi_diffusion.run_all --profile saint_full_t2_test115_x6` | `& $py -B -m ixi_diffusion.paper_table --profile saint_full_t2_test115_x6` | 来自 `D:\MRI\pre\ixi_diffusion` |
| I-03 | ArSSR | `& $py -B -m ixi_arssr.run_all --profile full_test115_x2` | `& $py -B -m ixi_arssr.paper_table --profile full_test115_x2` | `& $py -B -m ixi_arssr.run_all --profile full_test115_x6` | `& $py -B -m ixi_arssr.paper_table --profile full_test115_x6` | baseline |
| I-04 | CycleINR | `& $py -B -m ixi_cycleinr.run_all --profile full_test115_x2` | `& $py -B -m ixi_cycleinr.paper_table --profile full_test115_x2` | `& $py -B -m ixi_cycleinr.run_all --profile full_test115_x6` | `& $py -B -m ixi_cycleinr.paper_table --profile full_test115_x6` | baseline |
| I-05 | SwinIR 2.5D | `& $py -B -m ixi_swinir_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_swinir_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_swinir_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_swinir_2p5d.paper_table --profile full_test115_x6` | baseline |
| I-06 | HAT 2.5D | `& $py -B -m ixi_hat_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_hat_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_hat_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_hat_2p5d.paper_table --profile full_test115_x6` | baseline |
| I-07 | SMamba-UNet 2.5D | `& $py -B -m ixi_smamba_unet_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_smamba_unet_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_smamba_unet_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_smamba_unet_2p5d.paper_table --profile full_test115_x6` | baseline |
| I-08 | Pix2Pix-GAN 2.5D | `& $py -B -m ixi_gan_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_gan_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_gan_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_gan_2p5d.paper_table --profile full_test115_x6` | baseline |
| I-09 | ACVTT | `& $py -B -m ixi_acvtt_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_acvtt_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_acvtt_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_acvtt_2p5d.paper_table --profile full_test115_x6` | baseline |
| I-10 | Res-SRDiff | `& $py -B -m ixi_ressrdiff_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_ressrdiff_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_ressrdiff_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_ressrdiff_2p5d.paper_table --profile full_test115_x6` | diffusion/refinement baseline |
| I-11 | I3Net | `& $py -B -m ixi_i3net.run_all --profile full_test115_x2_fast` | `& $py -B -m ixi_i3net.paper_table --profile full_test115_x2_fast` | `& $py -B -m ixi_i3net.run_all --profile full_test115_x6_fast` | `& $py -B -m ixi_i3net.paper_table --profile full_test115_x6_fast` | 推荐用 fast profile |

## 2. fastMRI-brain-T2 expanded，x2/x6 baseline

| 顺序 | 方法 | x2 运行 | x2 表格 | x6 运行 | x6 表格 | 备注 |
|---:|---|---|---|---|---|---|
| F-01 | ResUNet residual | `& $py -B -m fastmri_brain_saint.run_resunet --profile full_x2` | 只生成 `summary_metrics.csv` | `& $py -B -m fastmri_brain_saint.run_resunet --profile full_x6` | 只生成 `summary_metrics.csv` | 共用 SAINT 包里的 ResUNet runner |
| F-02 | SAINT | `& $py -B -m fastmri_brain_saint.run_all --profile full_x2` | 只生成 `summary_metrics.csv` | `& $py -B -m fastmri_brain_saint.run_all --profile full_x6` | 只生成 `summary_metrics.csv` | 无独立 `paper_table.py` |
| F-03 | ArSSR | `& $py -B -m fastmri_brain_arssr.run_all --profile full_x2` | `& $py -B -m fastmri_brain_arssr.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_arssr.run_all --profile full_x6` | `& $py -B -m fastmri_brain_arssr.paper_table --profile full_x6` | baseline |
| F-04 | CycleINR | `& $py -B -m fastmri_brain_cycleinr.run_all --profile full_x2` | `& $py -B -m fastmri_brain_cycleinr.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_cycleinr.run_all --profile full_x6` | `& $py -B -m fastmri_brain_cycleinr.paper_table --profile full_x6` | baseline |
| F-05 | SwinIR 2.5D | `& $py -B -m fastmri_brain_swinir_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_swinir_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_swinir_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_swinir_2p5d.paper_table --profile full_x6` | baseline |
| F-06 | HAT 2.5D | `& $py -B -m fastmri_brain_hat_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_hat_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_hat_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_hat_2p5d.paper_table --profile full_x6` | baseline |
| F-07 | SMamba-UNet 2.5D | `& $py -B -m fastmri_brain_smamba_unet_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_smamba_unet_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_smamba_unet_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_smamba_unet_2p5d.paper_table --profile full_x6` | baseline |
| F-08 | Pix2Pix-GAN 2.5D | `& $py -B -m fastmri_brain_gan_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_gan_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_gan_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_gan_2p5d.paper_table --profile full_x6` | baseline |
| F-09 | ACVTT | `& $py -B -m fastmri_brain_acvtt_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_acvtt_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_acvtt_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_acvtt_2p5d.paper_table --profile full_x6` | baseline |
| F-10 | Res-SRDiff | `& $py -B -m fastmri_brain_ressrdiff_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_ressrdiff_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_ressrdiff_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_ressrdiff_2p5d.paper_table --profile full_x6` | diffusion/refinement baseline |
| F-11 | I3Net | `& $py -B -m fastmri_brain_i3net.run_all --profile full_x2` | `& $py -B -m fastmri_brain_i3net.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_i3net.run_all --profile full_x6` | `& $py -B -m fastmri_brain_i3net.paper_table --profile full_x6` | baseline |

## 3. NingXia-T2 8-fold case-level CV，x2/x6 baseline

这些都走统一 runner。建议一次只跑一个方法的一个倍率。所有命令都必须带 `@ningxiaRoots`，保证输出写到 `D:\MRI\baseline\ningxia_t2_*`。

| 顺序 | 方法 | x2 运行 | x6 运行 |
|---:|---|---|---|
| N-01 | ResUNet residual | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models resunet @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models resunet @ningxiaRoots` |
| N-02 | SAINT | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models saint @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models saint @ningxiaRoots` |
| N-03 | ArSSR | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models arssr @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models arssr @ningxiaRoots` |
| N-04 | CycleINR | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models cycleinr @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models cycleinr @ningxiaRoots` |
| N-05 | SwinIR 2.5D | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models swinir @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models swinir @ningxiaRoots` |
| N-06 | HAT 2.5D | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models hat @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models hat @ningxiaRoots` |
| N-07 | SMamba-UNet 2.5D | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models smamba @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models smamba @ningxiaRoots` |
| N-08 | Pix2Pix-GAN 2.5D | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models gan @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models gan @ningxiaRoots` |
| N-09 | ACVTT | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models acvtt @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models acvtt @ningxiaRoots` |
| N-10 | Res-SRDiff | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models ressrdiff @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models ressrdiff @ningxiaRoots` |
| N-11 | I3Net | `& $py -B -m processing.run_ningxia_case_cv --profile full_x2 --models i3net @ningxiaRoots` | `& $py -B -m processing.run_ningxia_case_cv --profile full_x6 --models i3net @ningxiaRoots` |

### NingXia 每个倍率跑完后的汇总命令

```powershell
& $py -B -m processing.summarize_case_cv --profile full_x2 @ningxiaRoots --include-arssr --include-cycleinr --include-swinir --include-i3net --include-hat --include-smamba --include-gan --include-acvtt --include-ressrdiff --out-dir D:\MRI\docx\experiment_notes\ningxia_x2_summary --title "NingXia-T2 x2 Case-Level CV"

& $py -B -m processing.summarize_case_cv --profile full_x6 @ningxiaRoots --include-arssr --include-cycleinr --include-swinir --include-i3net --include-hat --include-smamba --include-gan --include-acvtt --include-ressrdiff --out-dir D:\MRI\docx\experiment_notes\ningxia_x6_summary --title "NingXia-T2 x6 Case-Level CV"
```

注意：`summarize_case_cv` 默认包含 `saint` 和 `resunet`，其他方法通过 `--include-*` 加入。

## 4. 自研 design 方法已有 x2/x6 入口

这些不是 baseline，但已经有部分 x2/x6 profile。可以和 baseline 分开跑，避免混淆主表。

| 顺序 | 方法 | 数据集 | x2 运行 | x2 表格 | x6 运行 | x6 表格 | 备注 |
|---:|---|---|---|---|---|---|---|
| D-01 | PAST-Net | IXI-T2 | `& $py -B -m ixi_pastnet_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_pastnet_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_pastnet_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_pastnet_2p5d.paper_table --profile full_test115_x6` | design |
| D-02 | ECSI-Net | IXI-T2 | `& $py -B -m ixi_ecsinet_2p5d.run_all --profile full_test115_x2` | `& $py -B -m ixi_ecsinet_2p5d.paper_table --profile full_test115_x2` | `& $py -B -m ixi_ecsinet_2p5d.run_all --profile full_test115_x6` | `& $py -B -m ixi_ecsinet_2p5d.paper_table --profile full_test115_x6` | design |
| D-03 | ACSI-Net | IXI-T2 | `& $py -B -m acsinet.run_all --profile full_test115_x2` | `& $py -B -m acsinet.paper_table --profile full_test115_x2` | `& $py -B -m acsinet.run_all --profile full_test115_x6` | `& $py -B -m acsinet.paper_table --profile full_test115_x6` | design |
| D-04 | RASI-Net | IXI-T2 | `& $py -B -m rasinet.run_all --profile full_test115_x2` | `& $py -B -m rasinet.paper_table --profile full_test115_x2` | `& $py -B -m rasinet.run_all --profile full_test115_x6` | `& $py -B -m rasinet.paper_table --profile full_test115_x6` | design |
| D-05 | PAST-Net | fastMRI-brain-T2 | `& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_x2` | `& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_x2` | `& $py -B -m fastmri_brain_pastnet_2p5d.run_all --profile full_x6` | `& $py -B -m fastmri_brain_pastnet_2p5d.paper_table --profile full_x6` | design |

当前未发现这些自研方向的 NingXia 统一 runner：

- `pastnet`
- `ecsinet`
- `acsinet`
- `rasinet`

如果要让它们进入 NingXia x2/x6，需要先扩展 `processing.run_ningxia_case_cv --models` 的 choices 和 `model_to_module`。

## 5. I3Net-style x2/x4/x6 小表构建

当前 `processing.build_multiscale_table` 只收集 Linear / Cubic / I3Net。目录整理后需要显式传入 baseline 下的 run roots：

```powershell
& $py -B -m processing.build_multiscale_table `
  --ixi-root D:\MRI\baseline\ixi_i3net\runs `
  --fastmri-root D:\MRI\baseline\fastmri_brain_i3net\runs `
  --ningxia-root D:\MRI\baseline\ningxia_t2_i3net_cv\runs `
  --out D:\MRI\docx\experiment_notes\multiscale_x2_x4_x6_i3net_table.md
```

如果后续要生成“所有方法”的 x2/x4/x6 大表，需要另写或扩展 `processing.build_multiscale_table.py`，让 `METHOD_ORDER` 不只包含 `linear/cubic/i3net`。

## 6. 推荐实际运行顺序

为了避免显存和时间堆在一起，建议按这个顺序：

1. I3Net：IXI x2/x6 -> fastMRI x2/x6 -> NingXia x2/x6；
2. SwinIR/HAT/SMamba：先 IXI，再 fastMRI，再 NingXia；
3. ResUNet/SAINT：作为传统强 baseline 补齐；
4. ArSSR/CycleINR/GAN：作为 published/legacy 横向补齐；
5. ACVTT/Res-SRDiff：作为最近公开代码 baseline 补齐；
6. design 方法单独跑，不和 baseline 表混在一个执行批次里。

每跑完一个方法，确认：

```powershell
# IXI / fastMRI
Get-ChildItem <run_dir>\metrics

# NingXia
Get-ChildItem D:\MRI\baseline\<ningxia_method_dir>\runs\fold_*\full_x2\metrics\summary_metrics.csv
Get-ChildItem D:\MRI\baseline\<ningxia_method_dir>\runs\fold_*\full_x6\metrics\summary_metrics.csv
```

