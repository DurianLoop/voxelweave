# T2 x4 三数据集细节

更新日期：2026-06-17

本文档固定当前主线实验的数据集口径：只看 `T2` 模态、`x4 through-plane interpolation`。主表仍只维护：

```text
docx/experiment/experiment_master_table.md
```

## 统一实验协议

三个主表数据集都按同一 through-plane x4 方式构造评估输入：

1. 从原始 HR volume 沿 z 轴取 sparse volume：

```python
sparse = volume[:, :, ::4]
```

2. GT 截到与 sparse x4 重建一致的深度：

```python
full_depth = (sparse.shape[2] - 1) * 4 + 1
gt = volume[:, :, :full_depth]
```

3. 模型或插值方法输出与 `gt` 同 shape 的 dense volume。
4. 评估时只统计非锚点生成层，即 `z % 4 != 0` 的 slice。
5. 主表指标只保留：

```text
PSNR / SSIM / MAE / MSE / NCC
```

共同代码口径：

| 功能 | 代码 |
|---|---|
| IXI sparse/GT 构造 | `ixi_diffusion/stage_data.py` |
| fastMRI / NingXia 风格 sparse/GT 构造 | 各 baseline 的 `run_all.py` + dataset-specific settings |
| Linear / Cubic | `topcow_diffusion/baselines.py` |
| 主指标计算 | `topcow_diffusion/metrics.py` |

## 总览

| Dataset | 当前主表名称 | 定位 | 主表评估规模 | 本地数据规模 | Split / CV |
|---|---|---|---:|---:|---|
| IXI-T2 | `IXI-T2 test n=25` | 主开发 / 快速筛模型 | 25 test volumes | 578 T2 volumes available | seed3407 split；主表取 test 前 25 |
| fastMRI-brain-T2 expanded | `fastMRI-brain-T2 expanded test n=24` | 公开复杂 brain T2 验证 | 24 test volumes | 160 strict T2 NIfTI volumes | 112 / 24 / 24 |
| NingXia-T2 | `NingXia-T2 case-level CV 8 folds` | 本地外部临床验证 | 8 folds | 8 cases / 22 T2 series | case-level leave-one-case-out style CV |

## 1. IXI-T2

### 数据定位

IXI-T2 是当前主线的主开发 benchmark。它的图像相对规整、分辨率统一，Linear / Cubic 已经较强，因此适合快速筛掉弱模型，但不能单独证明临床泛化能力。

### 本地路径

| 项 | 路径 |
|---|---|
| root | `dataset/IXI/` |
| metadata | `dataset/IXI/metadata/ixi_cases.csv` |
| split | `dataset/IXI/splits/seed3407/` |
| T2 NIfTI path 字段 | `T2_path` |
| shape 字段 | `T2_shape` |

### 数据规模

| 项 | 数值 |
|---|---:|
| metadata 总 case 数 | 582 |
| 可用 T2 volume 数 | 578 |
| split train | 404 |
| split val | 58 |
| split test | 115 |
| 主表实际 test | 25 |

IXI split manifest：

```text
seed = 3407
ratios = train 0.7 / val 0.1 / test 0.2
require_all_modalities = true
modalities = T1 / T2 / PD
```

注意：主表的 `IXI-T2 test n=25` 不是完整 115 test cases，而是各 full profile 中设置 `test_cases=25` 后取 test split 的前 25 例。这是为了保持开发集评估成本可控，并与当前所有已完成 baseline 保持一致。

### 图像形状

| 项 | 范围 / 均值 |
|---|---|
| in-plane shape | 固定 `256 x 256` |
| z-depth min | 28 |
| z-depth max | 136 |
| z-depth mean | 130.39 |

### 当前使用方式

| 用途 | 口径 |
|---|---|
| smoke / mini | 快速确认模型是否值得扩 full |
| full | 训练用完整 train/val split，评估用 test 前 25 cases |
| 主表 | 只写 full 的 25-case 结果 |

### 2026-06-17 口径更新

I3Net 已单独完成完整 IXI test split 评估：

```text
ixi_i3net/runs/full_test115/
```

结果显示 I3Net 在 `test n=115` 上仍然 115/115 case 全胜 Linear/Cubic。因此后续新开的 IXI full 实验，优先采用完整 test n=115 作为公开 benchmark 口径；旧主表中已经完成的 n=25 横向结果暂不混改，等后续整体实验完成后再统一补齐。

## 2. fastMRI-brain-T2 expanded

### 数据定位

fastMRI-brain-T2 expanded 是当前最重要的公开复杂 brain T2 验证集。相比 IXI，它的 in-plane size 更不统一、slice depth 较短，传统插值指标明显下降，因此更能体现学习模型在复杂公开数据上的收益。

### 本地路径

| 项 | 路径 |
|---|---|
| raw DICOM root | `dataset/fastMRI_brain_DICOM/` |
| processed root | `dataset/fastMRI_brain_T2/processed/` |
| NIfTI dir | `dataset/fastMRI_brain_T2/processed/nifti/` |
| case metadata | `dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_nifti_cases.csv` |
| T2 NIfTI manifest | `dataset/fastMRI_brain_T2/processed/metadata/fastmri_brain_t2_nifti_manifest.csv` |
| split | `dataset/fastMRI_brain_T2/processed/splits/nifti_seed3407/` |
| prepare script | `processing/fastmri_brain_t2_prepare.py` |

### 数据筛选口径

处理脚本从 DICOM series label 中筛选 strict T2：

| 字段 | 说明 |
|---|---|
| `series_label` | 例如 `AX T2` |
| `contrast_status` | `strict_t2_from_series_label` |
| `case_id` | 处理后的 NIfTI case id，通常带 `ax_t2` / `t2_axial` 等后缀 |

当前 expanded 版本保留 160 个 T2 NIfTI volumes。

### 数据规模

| 项 | 数值 |
|---|---:|
| processed T2 NIfTI volumes | 160 |
| train | 112 |
| val | 24 |
| test | 24 |
| 主表 test | 24 |

### x4 训练样本数量怎么来

这里需要区分三个概念：

| 概念 | 含义 |
|---|---|
| 3D volume | 一个完整 NIfTI T2 series，例如 fastMRI 共有 160 个。 |
| single-slice residual sample | SAINT / ResUNet / SwinIR-style 2.5D 这类单张 slice 预测样本。 |
| I3Net window sample | I3Net 使用的 13-slice HR window，对应 4 个 sparse input slices -> 13 个 dense output slices。 |

当前 single-slice 数据集代码在 `fastmri_brain_swinir_2p5d/data.py` 与 `fastmri_brain_saint/data.py` 中采用滑动构造：

```python
for z in range(0, depth - stride):
    for offset in range(1, stride):
        items.append((path, z, offset, depth))
```

在 `stride=4` 时，每个起点 `z` 产生 3 个训练目标：`z+1`、`z+2`、`z+3`。因此单个 depth 为 `D` 的 volume 产生：

```text
(D - 4) * 3
```

当前 fastMRI split 的实际数量是：

| split | volumes | depth 分布 | 当前 sliding single-slice samples | 严格 phase-aligned samples |
|---|---:|---|---:|---:|
| train | 112 | 111 个 depth=16，1 个 depth=32 | 4080 | 1020 |
| val | 24 | 24 个 depth=16 | 864 | 216 |
| test | 24 | 24 个 depth=16 | 864 | 216 |
| total | 160 | - | 5808 | 1452 |

所以代码里看到的 `5808` 是 sliding single-slice 样本总数：

```text
5808 = 4080 + 864 + 864
```

它不是 160 个 3D volume 直接随机切片后再重新 8:1:1 划分得到的数量。当前项目先按 3D volume 做 split，然后只在各自 split 内生成 2D/2.5D 训练样本；因此没有 train/test volume 泄漏。

但需要注意：当前 sliding 构造会产生相位增强。例如按 1-based slice 编号，严格 x4 sparse grid 应该是：

```text
anchor: 1 和 5 -> predict 2 / 3 / 4
anchor: 5 和 9 -> predict 6 / 7 / 8
```

而当前 sliding 代码还会构造：

```text
anchor: 2 和 6 -> predict 3 / 4 / 5
anchor: 3 和 7 -> predict 4 / 5 / 6
anchor: 4 和 8 -> predict 5 / 6 / 7
```

这不会造成 train/test 数据泄漏，因为 volume split 已经在前面完成；但它确实不是最严格的 x4 acquisition-grid 训练口径，会让训练时看到“非全局 sparse anchor”的相位增强样本。若论文要强调 deterministic through-plane x4 acquisition setting，后续更严谨的版本应改成 phase-aligned 构造：

```python
for z in range(0, depth - stride, stride):
    for offset in range(1, stride):
        items.append((path, z, offset, depth))
```

在当前 fastMRI split 下，phase-aligned single-slice 样本数会从 `5808` 降到 `1452`。推荐做法不是把 `1452` 个 slice sample 再随机 8:1:1 划分，而是继续保持 3D volume-level split：train 1020、val 216、test 216。

I3Net 当前训练也使用滑动 13-slice window：

```python
hr_slice_patch = 4 * (4 - 1) + 1 = 13
for z in range(0, depth - 13 + 1, window_step):
    items.append((path, z))
```

fastMRI full 下对应数量为：

| split | 当前 I3Net sliding windows | 严格 phase-aligned I3Net windows |
|---|---:|---:|
| train | 464 | 116 |
| val | 96 | 24 |
| test | 96 | 24 |

### 图像形状

| 项 | 范围 / 均值 |
|---|---|
| in-plane H min / max | 256 / 768 |
| in-plane W min / max | 208 / 768 |
| z-depth min | 16 |
| z-depth max | 32 |
| z-depth mean | 16.10 |

### 当前使用方式

| 用途 | 口径 |
|---|---|
| full | 训练 112、验证 24、测试 24 |
| 主表 | 写完整 test n=24 结果 |
| 当前结论 | I3Net 当前最强；SAINT-style 是此前最强且仍属第一梯队 |

## 3. NingXia-T2 8-fold case-level CV

### 数据定位

NingXia-T2 是本地外部临床验证集。它的数据规模小，但更接近外部临床场景，因此当前不做固定 train/test 主表，而采用病例级 8-fold CV，优先报告 fold mean。

### 本地路径

| 项 | 路径 |
|---|---|
| original data root | `dataset/NingXiaData/Data/` |
| processed root | `dataset/NingXiaData/processed/` |
| T2 NIfTI dir | `dataset/NingXiaData/processed/t2_nifti/` |
| SAINT-compatible root | `dataset/NingXiaData/processed_saint/` |
| CV root | `dataset/NingXiaData/processed_saint_cv/` |
| case metadata | `dataset/NingXiaData/processed_saint/metadata/fastmri_brain_nifti_cases.csv` |
| CV summary | `dataset/NingXiaData/processed_saint_cv/case_cv_summary.csv` |
| prepare script | `processing/ningxia_prepare.py` |
| CV script | `processing/ningxia_case_cv.py` |

说明：`processed_saint/metadata/fastmri_brain_nifti_cases.csv` 沿用了既有 SAINT / fastMRI-style loader 的文件名，不表示 NingXia 是 fastMRI 数据。

### 数据规模

| 项 | 数值 |
|---|---:|
| patients / cases | 8 |
| T2 series | 22 |
| folds | 8 |
| each fold train cases | 6 |
| each fold val cases | 1 |
| each fold test cases | 1 |

每个 case 的 T2 series 数：

| case | series |
|---|---:|
| NX001 | 2 |
| NX002 | 4 |
| NX003 | 2 |
| NX004 | 4 |
| NX005 | 2 |
| NX006 | 3 |
| NX007 | 3 |
| NX008 | 2 |

### 图像形状

| 项 | 范围 / 均值 |
|---|---|
| in-plane H min / max | 256 / 640 |
| in-plane W min / max | 256 / 640 |
| z-depth min | 16 |
| z-depth max | 20 |
| z-depth mean | 17.77 |
| observed shapes | `256x256x20`, `512x512x16`, `512x512x18`, `512x512x19`, `528x528x18`, `640x640x18` |

### CV 划分

| fold | train cases | val | test |
|---|---|---|---|
| fold_00 | NX003, NX004, NX005, NX006, NX007, NX008 | NX002 | NX001 |
| fold_01 | NX001, NX004, NX005, NX006, NX007, NX008 | NX003 | NX002 |
| fold_02 | NX001, NX002, NX005, NX006, NX007, NX008 | NX004 | NX003 |
| fold_03 | NX001, NX002, NX003, NX006, NX007, NX008 | NX005 | NX004 |
| fold_04 | NX001, NX002, NX003, NX004, NX007, NX008 | NX006 | NX005 |
| fold_05 | NX001, NX002, NX003, NX004, NX005, NX008 | NX007 | NX006 |
| fold_06 | NX001, NX002, NX003, NX004, NX005, NX006 | NX008 | NX007 |
| fold_07 | NX002, NX003, NX004, NX005, NX006, NX007 | NX001 | NX008 |

八折的含义：NingXia 只有 8 个 patient / case，因此不适合再做一次固定 train/test 切分后只报一个小测试集。当前采用病例级 leave-one-case-out style CV：

1. 每一折固定 1 个 case 做 test。
2. 再固定 1 个不同 case 做 val。
3. 其余 6 个 case 做 train。
4. 8 折轮换后，NX001 到 NX008 每个 case 都恰好当过一次 test。
5. 主表报告 8 个 fold 的平均值，而不是把 22 个 series 随机拆开。

这个设计的核心目的是避免同一个 patient 的不同 T2 series 同时出现在 train 和 test 中。NingXia 有 22 个 T2 series，但它们属于 8 个 case；如果按 series 随机切分，会产生明显 patient-level leakage。

### 当前使用方式

| 用途 | 口径 |
|---|---|
| full CV | 8-fold case-level CV |
| 主表 | 报告 8 个 fold 的 mean |
| 当前结论 | SwinIR-style 2.5D 在平均主指标上最强，SAINT-style 非常接近 |

## 主表写入规则

| 数据集 | 可以写入主表的结果 |
|---|---|
| IXI-T2 | `profile=full` 且 `cases=25` |
| fastMRI-brain-T2 expanded | `profile=full` 且 `cases=24` |
| NingXia-T2 | 8-fold case-level CV 的 fold mean 汇总 |

smoke / mini / 单 fold / 单 case 结果只写入 `docx/experiment_notes/`，不写入 `docx/experiment/experiment_master_table.md`。

## 当前数据集层面的结论

1. IXI-T2 最适合快速筛模型，但由于传统插值已较强，不能作为唯一论据。
2. fastMRI-brain-T2 expanded 是公开复杂 T2 横向验证，当前最能体现 I3Net / SAINT-style 这类强学习基线相对传统插值的优势。
3. NingXia-T2 是小规模外部临床验证，必须保持 case-level CV，避免 series-level 泄漏。
4. 三个数据集共同支撑当前论文主线：公开干净 benchmark、公开复杂 benchmark、本地临床外部验证。
