# MRI 插值实验统一口径

更新时间：2026-05-29

本文档用于我和同学并行复现不同模型时统一数据、划分、指标、表格和命名口径。后续任何新模型都必须先对齐这里的规则，再进入大表。

## 1. 当前主线

老师最新要求是先只做 `T2` 相关实验，暂时不把 `T1`、`PD` 当作主线推进。

因此后续默认口径是：

| 项目 | 统一口径 |
|---|---|
| 主任务 | 3D MRI through-plane slice interpolation / z 向层间插值 |
| 主模态 | T2 优先 |
| 默认 scale | x4；如果论文或数据需要，可补 x2/x6 |
| 划分方式 | 病例级划分，不能按切片随机划分 |
| 对比方式 | 同一数据集、同一模态、同一 scale、同一 split 下比较 |
| 外部验证 | NingXiaData 作为外部临床验证候选，不应和 IXI/OAI 训练集混用 |

已有的 `IXI-T1/PD` 结果可以保留为探索记录，但以后论文主表优先放 `IXI-T2`、`OAI / NingXia T2`、`fastMRI brain` 等更贴近当前主线的数据。

## 2. 现有数据集定位

| Dataset | 路径 | 当前状态 | 实验定位 |
|---|---|---|---|
| IXI | `D:\MRI\dataset\IXI` | 已整理，已有 T1/T2/PD，已有病例级 split | 主开发数据集；先用 IXI-T2 训练和筛模型 |
| TopCaw2024 | `D:\MRI\dataset\TopCaw2024` | 已用于 GAN / diffusion 早期可行性实验 | 血管结构保持验证；适合 Dice/HD95/centerline，不作为当前 T2 主线 |
| CAS2023 | `D:\MRI\dataset\CAS2023` | 已有原始目录 | 血管/结构泛化候选；后续可用于结构保持验证 |
| OAI-ZIB | `D:\MRI\dataset\OAI-ZIB` | 已有 `V00/V01/...` | 公开膝关节结构数据；适合 T2/PD-like 膝关节外部验证和 segmentation downstream |
| fastMRI brain DICOM | `D:\MRI\dataset\fastMRI_brain_DICOM` | 已下载，已有部分 metadata 处理 | 大规模 brain MRI 泛化候选；更偏 reconstruction 数据生态 |
| fastMRI brain prepared | `D:\MRI\dataset\fastMRI_brain_prepared` | 已生成 case metadata/split 和少量 NIfTI sanity samples | 后续接入模型前需要统一序列筛选与图像转换 |
| NingXiaData | `D:\MRI\dataset\NingXiaData` | 已索引、分类、划分；部分 T2 DICOM 已转 NIfTI | 本地外部临床验证候选，当前最需要统一口径 |

## 3. NingXiaData 当前整理结果

原始路径：

```text
D:\MRI\dataset\NingXiaData\Data
```

处理输出：

```text
D:\MRI\dataset\NingXiaData\processed
```

处理脚本：

```text
D:\MRI\processing\ningxia_prepare.py
```

已生成的关键文件：

| 文件 | 作用 |
|---|---|
| `metadata/dataset_overview.csv` | NingXiaData 包内 MRNet/OAI/SKI10/NingXia_Data 的文件数和体积概览 |
| `metadata/archive_manifest.csv` | 压缩包清单与解压状态 |
| `metadata/ningxia_local_series_manifest.csv` | 宁夏本地 DICOM 全部 MR 序列清单 |
| `metadata/ningxia_local_t2_series_manifest.csv` | 严格 T2 序列清单 |
| `metadata/ningxia_local_t2_candidate_series_manifest.csv` | T2 序列清单；文件名保留 candidate 是脚本历史命名 |
| `metadata/ningxia_local_t2_nifti_manifest.csv` | 已转换 NIfTI 的 T2 序列清单 |
| `t2_nifti/*.nii.gz` | 已成功转换的 T2 NIfTI 体数据 |
| `splits/t2_candidate_seed3407` | T2 病例级划分；文件夹名保留 candidate 是脚本历史命名 |
| `splits/t2_nifti_ok_seed3407` | 已成功转 NIfTI 的病例级划分 |

### 3.1 数据包概览

| 子数据集 | 文件数 | 大小 | 定位 |
|---|---:|---:|---|
| MRNet-v1.0 | 2533 | 4.9732 GB | 公开膝关节 MRI 分类数据，不是当前插值主目标 |
| OAI | 2165 | 20.4483 GB | 公开膝关节结构数据，可作为外部泛化候选 |
| SKI10Data | 493 | 4.7589 GB | 膝关节分割/结构 benchmark 候选 |
| NingXia_Data | 18473 | 4.8098 GB | 本地临床膝关节数据，当前外部验证重点 |

### 3.2 NingXia 本地数据的重要发现

严格按 DICOM `SeriesDescription / ProtocolName / EchoTime` 自动识别：

| 类别 | 数量 |
|---|---:|
| 本地 MR 序列总数 | 81 |
| 老师确认按 T2 使用的序列 | 22 |
| 原始 DICOM 字段中写作 PD / PDW 的序列 | 46 |
| T1 序列 | 16 |
| survey/localizer | 19 |
| 当前纳入 T2 口径的候选序列 | 22 |

老师已确认 NingXiaData 这批数据按 T2 口径使用。DICOM 中部分序列名写作 `PDW_SPAIR / ePDW_aTSE / PD FSE FS / PD PROP fs`，但后续实验和表格统一记为 `NingXia T2 knee MRI`。

统一叫法建议：

```text
NingXia T2 knee MRI
```

### 3.3 NingXia 划分

原始 DICOM 字段严格写成 T2 的序列：

| Split | 病例数 |
|---|---:|
| train | 0 |
| val | 0 |
| test | 0 |
| holdout | 0 |

老师确认按 T2 使用的序列，覆盖 8 个病例：

| Split | 病例 |
|---|---|
| train | NX003, NX005, NX006, NX007, NX008 |
| val | NX002, NX004 |
| test | NX001 |
| holdout | NX001-NX008 全部 |

安装 `pydicom + pylibjpeg-openjpeg` 后，压缩 DICOM 已可解码。当前已成功转成 NIfTI 的 T2 数据覆盖 8 个病例：

| Split | 病例 |
|---|---|
| train | NX003, NX005, NX006, NX007, NX008 |
| val | NX002, NX004 |
| test | NX001 |
| holdout | NX001-NX008 全部 |

目前 NIfTI 转换结果：

| 状态 | 序列数 |
|---|---:|
| 成功 | 22 |
| 失败 | 0 |

已额外生成 SAINT 兼容索引：

```text
D:\MRI\dataset\NingXiaData\processed_saint
```

该索引用同一病例级 split；同一病例下的多条 T2 series 会进入同一 split，不会跨 train/val/test 泄漏。

## 4. 数据处理统一流程

### 4.1 IXI

当前默认 split：

```text
D:\MRI\dataset\IXI\splits\seed3407
```

病例数：

| Split | 病例数 |
|---|---:|
| train | 404 |
| val | 58 |
| test | 115 |

后续 IXI 主线只看 T2：

```text
profile: resunet_full_t2 / future ixi_*_t2
modality: T2
scale: x4
direction: z / through-plane
split seed: 3407
```

### 4.2 NingXiaData

处理命令：

```powershell
D:\conda\envs\MRI\python.exe -B .\processing\ningxia_prepare.py --data-root .\dataset\NingXiaData\Data --processed-root .\dataset\NingXiaData\processed --seed 3407 --extract-small-archives --convert-t2
```

当前可直接用于模型输入的是：

```text
D:\MRI\dataset\NingXiaData\processed\t2_nifti
```

但论文中要注明：

```text
NingXia T2 knee MRI, confirmed by supervisor.
```

### 4.3 外部验证原则

如果 NingXiaData 被定义为 external validation：

```text
不能参与 IXI/OAI/fastMRI 训练；
只能在最终模型确定后做 holdout evaluation。
```

如果只是前期工程调试：

```text
可以使用 t2_nifti_ok_seed3407 的 train/val/test；
但这不能再叫 external validation。
```

## 5. 指标统一口径

以后每个模型都至少输出以下指标。

### 5.1 直观主表指标

| Metric | 趋势 | 说明 |
|---|---|---|
| PSNR | 越高越好 | 像素级重建质量 |
| SSIM | 越高越好 | 结构相似性 |
| MAE | 越低越好 | 平均绝对误差 |
| MSE | 越低越好 | 平方误差 |
| NCC | 越高越好 | 强度相关性 |

日报/周报可以用这个短表：

| Dataset | Modality | Scale | Method | PSNR mean | SSIM mean | MAE mean | MSE mean | NCC mean |
|---|---|---|---|---:|---:|---:|---:|---:|
| IXI | T2 | x4 | Linear | 待填 | 待填 | 待填 | 待填 | 待填 |
| IXI | T2 | x4 | Ours / Baseline | 待填 | 待填 | 待填 | 待填 | 待填 |

### 5.2 论文最终补算指标

中间训练、mini、sanity check 阶段不要每一步都打印全部指标。默认只打印 5.1 的主表指标，减少评估和日志负担。等某个模型在主指标上整体表现稳定后，再补算下面这些扩展指标。

| Metric | 趋势 | 是否默认展示 | 说明 |
|---|---|---|---|
| SSIMa / SSIMc / SSIMs | 高 | 最终补算 | axial/coronal/sagittal 三视图结构一致性 |
| RMSE | 低 | 不默认展示 | 可由 MSE 开方得到，最终需要时再显示 |
| NMSE | 低 | 最终补算 | 归一化平方误差，便于跨数据集比较 |
| NRMSE | 低 | 不默认展示 | 可由 RMSE 和归一化范围得到，最终需要时再显示 |
| SNLI | 低 | 最终补算 | 层间连续性代理指标 |
| Gradient-MAE | 低 | 最终补算 | 边缘/纹理误差 |
| LPIPS | 低 | 最终补算 | 感知指标；当前已预留入口，需安装 `lpips` 后填 |
| Params(M) | 低 | 模型定稿后补 | 模型参数量 |
| FLOPs(G) | 低 | 模型定稿后补 | 每个 256x256 生成切片的计算量 |

论文主表模板采用 Method 在最左、数据集横向展开的格式：

| Method | Scale | IXI-T2 | OAI-T2 | NingXia-T2 |
|---|---|---|---|---|
| Linear | x4 | PSNR / SSIM / MAE / MSE / NCC | 待填 | 待填 |
| Cubic | x4 | PSNR / SSIM / MAE / MSE / NCC | 待填 | 待填 |
| SAINT | x4 | PSNR / SSIM / MAE / MSE / NCC | 待填 | 待填 |
| I3Net | x4 | PSNR / SSIM / MAE / MSE / NCC | 待填 | 待填 |

### 5.3 结构数据额外指标

TopCaw / CAS / OAI 如果有标签或可生成结构 mask，再补：

| Metric | 趋势 | 用途 |
|---|---|---|
| Mask-PSNR | 高 | 结构区域重建质量 |
| Mask-SSIM | 高 | 结构区域结构相似性 |
| Auto-Dice | 高 | 自动阈值结构重合 |
| Auto-HD95 | 低 | 自动结构边界距离 |
| downstream segmentation Dice | 高 | 插值是否帮助下游分割 |
| centerline / topology metrics | 高/低按定义 | 血管/管状结构连通性 |

## 6. 需要对比或复现的模型

### 6.1 必须有的基础 baseline

| Method | 类型 | 是否需要训练 | 用途 |
|---|---|---|---|
| Linear | 插值基线 | 否 | 最基础下限 |
| Cubic | 插值基线 | 否 | 传统强一点的插值基线 |

### 6.2 我们已经实现或尝试过的内部 baseline

| Method | 当前状态 | 能否当论文强 baseline |
|---|---|---|
| TopCaw GAN / pix2pix | 已在 TopCaw 做完整流程 | 可作为早期项目继承，不适合当前 T2 主表核心 |
| HiFiDiff residual low/strict | 已尝试，严格版有偏亮/不稳定问题 | 暂时作为探索记录 |
| ResUNet residual | 已在 IXI T1/T2/PD 跑过 | 可作为 internal sanity baseline，但不要说成复现某篇论文 |
| SAINT-style | 已实现 mini，待 full | 可以作为医学切片插值方向的重要 baseline，但要标明是 ours reproduction / style reproduction |

### 6.3 建议正式对比的公开模型

| Method | 来源定位 | 是否建议复现 | 备注 |
|---|---|---|---|
| SAINT | 医学 slice interpolation baseline | 是 | 先在 IXI-T2 full 跑通 |
| I3Net | 你同学正在 IXI 上复现 | 跟进 | 如果 split/预处理一致，可直接纳入大表 |
| ArSSR | 3D MRI arbitrary-scale SR | 是 | 和 MRI 体数据最贴近 |
| CycleINR | CVPR 2024 volumetric SR / slice consistency | 是 | 对 SNLI/层间一致性叙事很重要 |
| EDSR2D | 2D SR baseline | 可选 | 用作图像 SR 传统深度 baseline |
| EDSR3D | 3D SR baseline | 可选 | 体数据版本，更公平 |
| RDN | CNN SR baseline | 可选 | 经典强 baseline |
| RCAN | CNN attention SR | 可选 | 经典强 baseline |
| SwinIR | Transformer SR | 建议 | 强图像复原 baseline |
| HAT | Transformer SR | 可选 | 更强但可能较重 |
| AdaCoF | video frame interpolation | 可选 | 从相邻切片视作 frame interpolation |
| RSTT | video/transformer interpolation | 可选 | 相邻切片辅助生成方向 |
| IFRNet | frame interpolation | 可选 | 和相邻切片插值任务形式接近 |
| TVSRN | slice/video SR baseline | 可选 | 可作为医学/视频插值桥接模型 |

并行工作分工建议：

```text
我：SAINT / ArSSR / CycleINR / Ours
同学：I3Net / SwinIR / EDSR/RDN/RCAN
共同：必须使用同一 IXI-T2 split seed3407，同一 x4，同一指标脚本。
```

## 7. 实验结果必须记录的信息

每个 profile 必须记录：

| 字段 | 示例 |
|---|---|
| Dataset | IXI / NingXia / OAI |
| Modality | T2 / PD / T1 |
| Scale | x2 / x4 / x6 |
| Direction | z / through-plane |
| Split seed | 3407 |
| Train cases | 数量 |
| Val cases | 数量 |
| Test cases | 数量 |
| Method | SAINT / I3Net / Linear / Cubic |
| Source | reported / ours rerun / ours reproduction / internal baseline |
| Checkpoint rule | best val loss / best PSNR / final |
| Early stopping | 是否使用 |
| LR schedule | 是否使用 |
| Metrics file | `summary_metrics.csv` / `paper_table.csv` |
| Visual QC path | `metrics/visual_qc` |

没有这些字段，结果不能进最终大表。

## 8. 当前建议的下一步

老师建议现阶段不要太急着固定某一个创新点。下一步重点应该是收集信息、统一实验、观察不同方法和数据之间的关联性。

### 8.1 第一阶段：统一信息

1. 把当前主线固定为 `IXI-T2 x4`。
2. 确认同学的 I3Net 预处理、split、scale、归一化方式是否与我们一致。
3. 整理每篇 baseline 论文使用的数据集、scale、输入输出方式、指标和最好结果。
4. 把 `SAINT / I3Net / ArSSR / CycleINR / SwinIR / EDSR / RDN / RCAN` 放到同一张方法信息表里。

### 8.2 第二阶段：统一实验

1. 用同一 split 跑 `Linear / Cubic / SAINT full / I3Net`。
2. 中间实验只打印 `PSNR / SSIM / MAE / MSE / NCC`。
3. 如果某个模型主指标明显优于 baseline，再补算 `SSIMa/c/s / NMSE / SNLI / Gradient-MAE / LPIPS / Params / FLOPs`。
4. NingXiaData 先作为 `T2 external holdout`，不要急着混进训练。
5. 当前可直接使用 `t2_nifti_ok` 里的 8 个病例做外部验证 sanity；但 test 只有 1 个病例，结论只能作为外部流程验证，不能单独支撑论文结论。

### 8.3 第三阶段：找关联性

优先观察这些关系：

| 观察点 | 目的 |
|---|---|
| CNN / Transformer / INR / diffusion 哪类方法在 IXI-T2 上更稳 | 判断技术路线 |
| PSNR 高的方法是否 SSIM/SNLI 也高 | 判断是否只是过平滑 |
| 在 IXI 上好的方法能否迁移到 NingXia/OAI | 判断泛化 |
| 层间连续性是否比单切片 PSNR 更能解释视觉质量 | 寻找论文叙事切入点 |
| 模型复杂度和收益是否成正比 | 判断是否值得用大模型 |

等这些关联性看清楚后，再决定创新点放在结构先验、层间一致性、跨数据泛化、轻量化，还是任意尺度插值上。

## 9. BraTS / TCGA 数据集口径

老师提到的 BraTS 和 TCGA 更适合先纳入“数据集信息整理表”，不建议现在立刻全部下载。原因是它们体量大、访问方式复杂，而且任务定位和我们当前 `T2 knee / IXI-T2 插值` 主线不完全一样。

### 9.1 BraTS

| 项目 | 口径 |
|---|---|
| 数据类型 | 多模态脑肿瘤 MRI，常见模态包括 T1、T1ce/T1c、T2、FLAIR |
| 主要任务 | 肿瘤分割、脑肿瘤相关泛化验证 |
| 对我们当前任务的作用 | 可作为 brain MRI 多模态泛化数据，不是膝关节 T2 主线的第一优先级 |
| 是否现在下载 | 暂不建议全量下载；先整理 accession、大小、模态、许可和已有论文结果 |
| 下载方式 | 官方 BraTS/Synapse challenge 页面申请；或 TCIA/HuggingFace 镜像用于调研，但正式论文应优先引用官方来源 |

### 9.2 TCGA

| 项目 | 口径 |
|---|---|
| 数据类型 | 癌症队列的基因组、临床、病理、部分影像数据 |
| 影像入口 | TCIA / IDC，如 TCGA-GBM、TCGA-LGG |
| 基因组/临床入口 | NCI GDC Data Portal |
| 对我们当前任务的作用 | 如果后续做 cancer MRI foundation / imaging-genomics，可作为强泛化和临床关联数据 |
| 是否现在下载 | 暂不建议全量下载；先选择 1-2 个脑肿瘤 MRI collection 做 metadata 调研 |

### 9.3 当前建议

当前不要让 BraTS/TCGA 打断 IXI-T2 / NingXia-T2 主线。短期只做三件事：

1. 建一个数据集信息表，记录 BraTS/TCGA 的模态、病例数、下载入口、许可、任务、是否有标签。
2. 选一个小 collection 做下载 sanity，例如 BraTS 2024 子集或 TCGA-GBM 的少量病例。
3. 等 SAINT/I3Net 在 IXI-T2 上有统一结果后，再决定是否把 BraTS/TCGA 纳入下一阶段泛化验证。
## fastMRI brain DICOM 统一口径补充

### 是否是 T2

不能把整个 `brain_fastMRI_DICOM` 直接视为 T2。当前本地抽查显示同一数据包中既有 `Axial T1 FSE / Axial T1 FSE POST`，也有 `AX T2 / AX T2 REPEAT`。因此统一口径如下：

| 数据 | 论文/实验口径 | 进入 T2 主表条件 |
|---|---|---|
| `dataset/fastMRI_brain_DICOM` | fastMRI brain 多序列 DICOM | 不直接进入 |
| `dataset/fastMRI_brain_prepared/nifti` | fastMRI brain NIfTI sanity 子集 | 只做代码链路验证 |
| 过滤后的 fastMRI brain T2 | fastMRI-brain-T2 external/generalization dataset | 可以进入 T2 主表 |

后续必须用 DICOM `SeriesDescription / ProtocolName` 做序列过滤：保留 T2，排除 T1、POST、T1ce、FLAIR。过滤后的 split 仍然必须是病例级 split，seed 继续使用 `3407`。

### SAINT 接入口

| 项目 | 路径 |
|---|---|
| NIfTI sanity 索引脚本 | `processing/fastmri_brain_nifti_index.py` |
| fastMRI brain SAINT 代码 | `fastmri_brain_saint/` |
| smoke 输出 | `fastmri_brain_saint/runs/smoke` |
| 一键脚本 | `temp/run_fastmri_brain_saint.ps1` |

当前 smoke 只证明代码能跑，不进入最终大表。正式对比顺序为：

1. 建立 fastMRI brain T2-only metadata。
2. 转换 T2-only NIfTI。
3. 建立病例级 split。
4. 跑 `fastmri_brain_saint.run_all --profile mini`。
5. mini 稳定后再跑 full，并与 IXI-T2 的 SAINT/I3Net/linear/cubic 结果分表或明确标注 dataset。
