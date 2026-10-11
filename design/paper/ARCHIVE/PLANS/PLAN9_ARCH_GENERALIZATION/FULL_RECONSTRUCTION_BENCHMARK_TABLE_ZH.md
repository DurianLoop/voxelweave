# 三数据集重建语境表说明

## 这张表在两篇论文中的作用

这张表不是为了证明 I3Net 最好，也不是把任何重建方法包装成本文的 “ours”。它把两篇论文中实际使用或恢复审计过的插值器放回同一实验语境，用来回答三个更贴合论文主线的问题：

1. 可靠性结论是否只来自两个较弱或过于相似的重建器；
2. fastMRI、IXI、NingXia 三个数据集上现有模型覆盖到什么程度；
3. 重建精度、架构差异和本文研究的错误可观测性为什么不能被混为一个排行榜。

因此，表中不设置 “ours”，不对最佳值或次佳值加粗，也不把 I3Net 放在最后形成视觉上的主方法行。方法按解析基线后接神经方法字母序排列。

## 表格结构

- 行按 ×2、×4、×6 三个倍率分块；
- 列按 fastMRI brain T2、IXI brain T2、NingXia knee T2 三个数据集分组；
- 每个数据集组展示 MAE、PSNR、SSIM、NCC 四项指标；
- “—” 表示该数据集—倍率—方法组合没有完整可审计结果，不代表零；
- MAE 仅在数据集内部解释，因为三个队列的强度范围不同，不进行跨数据集 MAE 排名或池化。

## 数据覆盖与统计单位

| 数据集 | 评测单位 | 当前可审计覆盖 | 说明 |
|---|---:|---|---|
| fastMRI brain T2 | 24 个检查 | 13 个方法，×2/×4/×6 | 固定测试集，共同 generated-plane support 与 1% 前景掩膜 |
| IXI brain T2 | 115 个检查 | ×4 下 Linear、Cubic、ACSI-Net、HAT、I3Net、SwinIR | 不用零散或不兼容结果补齐 ×2/×6 |
| NingXia knee T2 | 8 位患者、22 个序列 | 13 个方法，×2/×4/×6 | 患者分组的 out-of-fold 预测；表中为 22 个 OOF 序列均值 |

## 为什么这不是 I3Net 效果展示表

三数据集整合后，结果本身否定了“固定突出 I3Net”的表达方式。例如，I3Net 在 fastMRI 的若干组合上重建误差较低，但在 NingXia 上并非普遍占优：HAT、SwinIR 或其他模型可在不同倍率和指标上达到更好结果。论文真正研究的是共享物理测量如何使多个确定性重建共同犯错，并不是提出一个新的超分辨率骨干。

重建精度高也不等于可靠性评分一定更好。现有结果中，不同架构仍可能在同一批困难检查上共同失败，而局部像素误差的差异与检查级排序也可能给出不同结论。因此本表只提供实验背景，核心论证仍来自 same-target measurement-dependence intervention、shared/observable error decomposition、clustered inference 和 risk--coverage 分析。

## 已集成位置

- TMI 主文表格源：`TMI/TMI_ARCH_GENERALIZED/table_full_reconstruction_benchmark.tex`
- TMI 成稿：`TMI/TMI_ARCH_GENERALIZED/main.pdf`，第 7 页
- CVPR 补充材料表格源：`CVPR/CVPR_ARCH_GENERALIZED/PAPER/table_full_reconstruction_benchmark.tex`
- CVPR 补充成稿：`CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf`，第 2 页
- 独立预览：`p9_full_reconstruction_benchmark_table.pdf` 与 `p9_full_reconstruction_benchmark_table.png`
- 机器可读宽表：`outputs/p9_three_cohort_reconstruction_benchmark.csv`

## 数据来源

- fastMRI/IXI 汇总：`D:/MRI/design/rasinet/outputs/nested_optimization/corrected_reconstruction_fidelity.csv`
- NingXia OOF 逐序列指标：`D:/MRI/design/rasinet/outputs/nested_optimization/common_fidelity_per_case_ningxia.csv`
- 模型路径与审计状态：`D:/MRI/design/rasinet/outputs/optimization/model_bank_registry.csv`

所有论文表值均从上述本地共同协议结果恢复并按展示精度四舍五入，没有从各方法原论文的异构 headline protocol 抄数，也没有为填满表格而推算缺失结果。
