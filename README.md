# MRI 超分辨率实验仓库

本仓库用于 MRI 体数据切片间超分辨率实验，涵盖数据准备、基线模型复现、方法设计、交叉验证、评估与论文材料。实验以病例级数据划分为基本单位，统一保存可复现的运行配置、训练记录、预测结果和指标。

## 研究交接与模型筛选

| 文档 | 用途 |
| --- | --- |
| [自研模型与 baseline 梯队](docx/experiment/self_model_baseline_tiers.md) | 同协议五指标对比、效果梯队与优先保留模型。 |
| [完整研究交接](docx/experiment/research_handoff_20261023.md) | 后续模型研究、复现资产、运行入口、论文路线和证据缺口。 |
| [方法与结果总汇](docx/experiment/self_innovation_methods_and_results.md) | 各代自研方法、消融、负结果与原始来源。 |
| [统一 baseline 主表](docx/experiment/experiment_master_table.md) | T2/x4 三数据集及 x2/x6、训练预算敏感性。 |
| [交接证据快照](docx/experiment/handoff_evidence_20261023/README.md) | 轻量汇总结果、源路径/SHA 和本地权重库存；影像和权重另行交接。 |

优先候选为 PAST 成熟 G 系列和轻量 ACSI v1；性能信号、研究优先级与独立验证完整度分别说明。文档核验：`python processing/verify_research_handoff.py`。

## 目录结构

| 路径 | 用途 |
| --- | --- |
| `dataset/` | 原始数据、处理后数据、病例级划分与元数据。 |
| `processing/` | 数据解压、格式转换、索引、划分和汇总脚本。见 [processing/README.md](processing/README.md)。 |
| `baseline/` | 已复现的基线模型实验工程及其运行记录。 |
| `design/` | 本项目设计和改进模型的实验工程。 |
| `fastmri_brain/` | fastMRI brain DICOM 数据处理相关代码。 |
| `pre/` | 共用的预处理或辅助代码。 |
| `docx/` | 实验笔记、结果汇总、论文和演示材料。 |
| `tests/` | 自动化测试。 |
| `temp/` | 一次性脚本和临时文件；不存放正式实验结果。 |
| `logs/` | 运行日志。 |
| `external/` | 外部依赖、下载资源或第三方材料。 |

## 数据集

仓库当前包含以下主要数据集目录：

| 数据集 | 路径 | 说明 |
| --- | --- | --- |
| IXI | `dataset/IXI/` | MRI 数据及病例级 split。 |
| NingXiaData | `dataset/NingXiaData/` | 宁夏数据的原始文件、处理结果和 T2 相关数据划分。 |
| fastMRI brain | `dataset/fastMRI_brain_DICOM/`、`dataset/fastMRI_brain_T2/` | 原始多序列 DICOM 与筛选后的 T2 数据。 |
| OAI-ZIB | `dataset/OAI-ZIB/`、`dataset/OAI-ZIB-prepared/` | OAI-ZIB 原始与准备后的数据。 |
| TopCaw | `dataset/TopCaw2024/` | TopCaw 数据。 |

处理后的数据应写入对应数据集下的 `processed/`（或已有的准备数据目录），不要复制到模型工程内。

## 实验工程

实验工程通常按“数据集 + 方法”命名。例如：

```text
baseline/fastmri_brain_acvtt_2p5d/
baseline/ningxia_t2_saint_cv/
design/fastmri_brain_pastnet_2p5d/
design/ixi_pastnet_2p5d/
```

`baseline/` 保存对比方法，包括 ACVTT、ARSSR、CycleINR、GAN、HAT、I3Net、ResSRDiff、SAINT、SMamba-UNet 和 SwinIR 等；`design/` 保存自主设计的方法与消融实验。

新训练输出必须写入所属工程的 `runs/<profile>/`，不要直接写在仓库根目录。

### 运行结果约定

一个正式 profile 应尽量包含以下内容：

```text
runs/<profile>/
  run_manifest.json          # 数据、split、参数和运行口径
  training_history.csv/json  # 训练和验证过程
  checkpoints/               # best 与 final checkpoint
  eval_inputs/               # 评估使用的 GT 与稀疏输入（如适用）
  baseline_outputs/          # Linear / Cubic 插值结果
  model_outputs/             # 或具体模型的预测输出目录
  metrics/                   # 病例级、汇总和论文表格指标
```

默认报告基于验证集选择的 best checkpoint；若使用 final checkpoint，必须在结果和文档中明确说明。所有可比较实验应同时输出 `Linear`、`Cubic` 和当前模型结果。

### 保留的根目录结果副本

为避免覆盖历史结果，2026 年 7 月在根目录生成的实验结果已迁入 `baseline/`，并以 `_root_results_202607` 结尾。例如：

```text
baseline/fastmri_brain_acvtt_2p5d_root_results_202607/
baseline/ningxia_t2_acvtt_2p5d_cv_root_results_202607/
```

这些目录是完整保留的历史结果副本，不替代对应的同名实验代码工程；后续运行请使用不带该后缀的工程目录。

## 数据处理

所有数据准备脚本位于 `processing/`。常见任务包括：

```powershell
# 建立 fastMRI brain NIfTI 索引
D:\conda\envs\MRI\python.exe -B -m processing.fastmri_brain_nifti_index

# 准备或筛选 fastMRI brain T2 数据
D:\conda\envs\MRI\python.exe -B .\processing\fastmri_brain_t2_prepare.py

# NingXiaData 准备、索引和 T2 转换
D:\conda\envs\MRI\python.exe -B .\processing\ningxia_prepare.py
```

运行前请查看脚本的 `--help` 以及 [processing/README.md](processing/README.md) 中的参数说明。fastMRI brain 原始 DICOM 是多序列集合，只有经过明确序列筛选的 T2 数据才可进入 T2 主结果表。

## 环境

推荐使用仓库提供的 Conda 环境定义：

```powershell
conda env create -f environment.yml
conda activate MRI
```

也可按 `requirements.txt` 安装 Python 依赖。该环境使用 CUDA 12.8 对应的 PyTorch 软件源；请根据本机 CUDA 驱动和硬件情况调整。

## 实验与结果规范

- 数据划分必须以病例为单位；同一比较表中不得混用不同模态、比例或 split。
- 每次正式运行应保存 `run_manifest.json`，记录数据源、划分、训练参数与 checkpoint 选择方式。
- 指标至少保存病例级指标、汇总指标和论文表格；常用主指标为 PSNR、SSIM、MAE、MSE 和 NCC。
- `ResUNet residual` 属于内部 baseline，不能表述为特定论文的复现；未严格复现原论文细节的 SAINT 类实现需清楚说明为 style/reproduction。
- 临时 PowerShell 脚本放入 `temp/`，正式文档和实验汇总放入 `docx/`。
- 不要将原始数据或新的训练输出直接写入仓库根目录。

## 测试

在仓库根目录执行：

```powershell
pytest -q
```

可根据正在修改的工程选择对应测试文件，以缩短验证时间。

