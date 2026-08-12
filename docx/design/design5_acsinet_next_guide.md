# Design 5 下一步引导：ACSI-Net 解剖一致性路线

更新时间：2026-07-06

本文档是在 `design5_acsinet_anatomy_consistency.md` 和当前 `acsinet/` 第一阶段代码实现之后的下一步执行指南。当前 ACSI 路线已经有 smoke、mini、full_test115 输入缓存和 3D consistency 指标输出，因此它是 5/6/3 三条低算力方向里最适合优先推进成论文支撑结果的一条。

## 1. 当前状态

已看到的第一步产物：

```text
acsinet/
  model.py
  metrics.py
  train.py
  paper_table.py
  runs/
    smoke/
    mini/
    full_test115/
```

mini 已有输出：

```text
acsinet/runs/mini/metrics/
  summary_metrics.csv
  summary_3d_consistency.csv
  per_case_metrics.csv
  per_case_3d_consistency.csv
  paper_table.md
  paper_table.csv
```

mini 5 cases 当前结果显示：

| Method | PSNR | SSIM | MAE | MSE | NCC |
|---|---:|---:|---:|---:|---:|
| ACSI-Net | 25.7478 | 0.8438 | 43.0894 | 11134.6133 | 0.9229 |
| Linear | 25.0849 | 0.8268 | 47.0867 | 12633.8805 | 0.9121 |
| Cubic | 24.6061 | 0.8131 | 51.1790 | 14744.4780 | 0.8988 |

3D consistency mini 5 cases：

| Method | ZGE | ZLE | Edge-Z Error | Inter-slice NCC MAE |
|---|---:|---:|---:|---:|
| ACSI-Net | 0.01719 | 0.02554 | 0.01279 | 0.05552 |
| Linear | 0.01799 | 0.02600 | 0.01287 | 0.06406 |
| Cubic | 0.01887 | 0.02623 | 0.01349 | 0.06059 |

初步判断：

```text
ACSI-Net mini 已经同时超过 linear/cubic 的重建指标和大部分 3D consistency 指标。
这是一个好信号，下一步应该优先把它做成完整分析，而不是马上加复杂模型。
```

## 2. 下一阶段总目标

ACSI 路线接下来要证明：

1. ACSI 不只是单 slice 指标更高；
2. ACSI 的 z-axis consistency 也更好；
3. 这种 3D 连续性优势在 full_test115、fastMRI、NingXia 上稳定；
4. sagittal/coronal 视角能肉眼看到改善；
5. 这套 3D consistency 指标能作为论文新增评价维度。

## 3. P1：把 IXI full_test115 跑完整

当前 `acsinet/runs/full_test115/` 已经有大量 `eval_inputs/sparse` 和 `eval_inputs/gt`，说明数据准备已经完成或部分完成。

下一步优先补齐：

```text
acsinet/runs/full_test115/model_outputs/
acsinet/runs/full_test115/baseline_outputs/
acsinet/runs/full_test115/metrics/
```

### 3.1 P1 必须输出

```text
summary_metrics.csv
summary_3d_consistency.csv
per_case_metrics.csv
per_case_3d_consistency.csv
paper_table.md
paper_table.csv
```

### 3.2 P1 验收标准

IXI full_test115 上至少要证明：

| 对比 | 最低要求 |
|---|---|
| ACSI vs Linear | PSNR/SSIM/MAE/MSE/NCC 全面更好 |
| ACSI vs Cubic | 全面更好 |
| ACSI 3D consistency | 至少 3/4 个 3D 指标优于 Linear/Cubic |
| per-case | 大多数 case ACSI 优于 Linear |

如果 ACSI full_test115 指标只略强，但 3D consistency 明显强，也依然有价值。

## 4. P2：把 3D consistency 做成 baseline-level 分析

目前 ACSI 只和 linear/cubic 比还不够。论文里需要把已有强 baseline 也纳入 3D consistency。

优先顺序：

```text
Linear
Cubic
ResUNet
SwinIR
HAT
SMamba
I3Net
SAINT
ACSI-Net
```

如果强 baseline 没有保存 prediction，可以先只做已有输出；没有输出的只跑推理，不重训。

### 4.1 统一输出格式

建议统一为：

```text
docx/experiment_notes/acsinet_3d_consistency/
  ixi_full_test115_3d_consistency_summary.csv
  fastmri_full_3d_consistency_summary.csv
  ningxia_cv_3d_consistency_summary.csv
  per_case_3d_consistency_all_methods.csv
  visual_qc_index.csv
```

### 4.2 指标保留

建议至少保留：

- ZGE: z-gradient error；
- ZLE: z-Laplacian error；
- Edge-Z Error；
- Inter-slice NCC MAE；
- Inter-slice NCC pred mean；
- Inter-slice NCC GT mean。

其中最适合写论文的是：

```text
ZGE + Edge-Z Error + sagittal/coronal visual QC
```

## 5. P3：做 sagittal/coronal visual QC

ACSI 的论文价值不应该只靠 CSV。through-plane interpolation 的问题在 sagittal/coronal view 最直观。

每个数据集选：

```text
best case
median case
worst case
```

每个 case 输出：

```text
GT sagittal
Linear sagittal
I3Net/HAT sagittal
ACSI sagittal
error map sagittal
z-profile line plot
```

### 5.1 visual QC 文件结构

```text
docx/experiment_notes/visual_qc/acsinet_3d/
  ixi/
  fastmri/
  ningxia/
```

每张图命名：

```text
dataset_case_method_view.png
```

例如：

```text
ixi_IXI012_acsinet_sagittal.png
```

## 6. P4：扩 fastMRI 和 NingXia，但不急着训练新模型

ACSI 低算力路线可以先做评价框架扩展：

1. 收集已有 baseline prediction；
2. 计算 3D consistency；
3. 做 visual QC；
4. 再决定是否训练 ACSI-Net fastMRI/NingXia 版本。

NingXia 特别重要：

```text
如果 ACSI 的 3D consistency 在 NingXia 上比 SwinIR/HAT 更稳，
即使 PSNR 不是最高，也可以形成非常强的医学叙事。
```

## 7. 论文主张应该怎么写

ACSI 路线不要只写：

```text
我们提出一个新网络，PSNR 更高。
```

更好的主张：

```text
Existing slice interpolation benchmarks overemphasize per-slice fidelity.
We introduce anatomy-consistency evaluation and show that ACSI improves z-axis structural coherence.
```

中文：

```text
现有层间插值评估过度依赖单切片指标，而 ACSI 关注重建体数据的 z 轴解剖连续性。
```

## 8. 当前最具体的下一步

按顺序做：

1. 补齐 `acsinet/runs/full_test115/metrics/`；
2. 生成 IXI full_test115 的 3D consistency summary；
3. 按 per-case 排序找 best/median/worst；
4. 输出 sagittal/coronal visual QC；
5. 把 Linear/Cubic/ACSI 的 IXI full 结果整理成 `docx/experiment_notes/acsinet_3d_consistency/`；
6. 再纳入 I3Net/HAT/SwinIR 已有 prediction；
7. 最后扩 fastMRI 和 NingXia。

## 9. 不要做的事

暂时不要：

- 直接把 ACSI 当三数据集主表新 SOTA 宣称；
- 只跑 mini 5 cases 就写强结论；
- 只报 PSNR，不报 3D consistency；
- 先上复杂 3D CNN；
- 为了 3D consistency 大幅牺牲主表指标。

## 10. 阶段性结论

ACSI 当前是 5/6/3 三条低算力路线里最值得优先推进的。它已经在 mini 上显示出“重建指标 + 3D consistency”双重提升。下一步最重要的是把 IXI full_test115 和 visual QC 补完整，让它从代码 smoke 变成论文里能站住的一组分析。

