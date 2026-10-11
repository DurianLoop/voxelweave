# Plan 9 最终结果汇总报告

**项目：** MRI 层间/层厚方向插值的架构族泛化与双论文升级  
**完成日期：** 2026-08-14  
**工作目录：** `D:\MRI\design\paper`  
**状态：** 实验、统计、文献审计、论文重构、PDF 编译与内部审稿模拟均已完成；**未执行投稿**。

## 1. 执行结论

Plan 9 得到了一个比“所有新架构都复制原结论”更有信息量的结果。

1. **TMI 方向成功。** 在 Transformer、专用层间 CNN、空间感知网络和隐式表示模型上，只要两个预测复用更多相同物理测量，它们的局部误差就更容易形成共同不可见部分。五个神经架构在 fastMRI x4 上的“可观测误差增益”95% 病例簇置信区间均排除零。因此，原先“仅在 HAT/SwinIR 两个相近架构中成立”的主要风险已在现象层面解决。
2. **CVPR 方向得到有边界的加强，而非无条件成功。** 物理依赖—误差对齐—分歧可观测性这一局部链条跨架构存在；但新架构的有限差分影响探针只有 SAINT 通过全部稳定性门槛，且 SAINT 在固定共享计数后的影响效应区间跨零。I3Net 与 CycleINR 未通过预注册稳定性门槛。因此不能声称“影响度在所有架构上都稳定且优于共享计数”。
3. **排名改善不是普适结果。** CycleINR 的 disjoint-versus-shared 排名改善很强，I3Net 接近零，SAINT 略为负且不确定。架构异质性是真实结果，不应平均掉。
4. **架构多样性不等于病例级误差独立。** 不同模型仍倾向于在同一检查上失败；但像 CycleINR–I3Net 这样的异构组合可以带来更大的像素级误差多样性。
5. **双稿不能直接并行投稿。** 文字重合诊断很低，但科学实验存在实质交叉，最终治理结论是 `MERGE_OR_SEQUENCE_REQUIRED`。

## 2. 基线恢复与资格审计

共恢复 **13 个方法**：

| 类型 | 方法 |
|---|---|
| 解析插值 | Linear、Cubic |
| Transformer / SR | HAT、SwinIR |
| 专用医学层间插值 | I3Net |
| 空间感知层合成 | SAINT |
| 隐式/连续体插值 | CycleINR、ArSSR |
| 其他历史神经基线 | SMamba-UNet、Pix2PixGAN、ResUNet、Res-SRDiff、ACVTT |

关键谱系结论：

- **I3Net：** 官方架构谱系、本地训练，无官方预训练权重。
- **SAINT：** 本地适配的 SAINT-style 实现，不是官方仓库/权重的逐项复现。
- **CycleINR：** 基于本地 ArSSRNet 路径的 CycleINR-style 训练，不是官方实现的精确复现。
- 文件名中预期的 **ACVIT** 未能恢复；历史可确认方法是 **ACVTT**，未做名称替换或结果拼接。
- SAINT x2/x6 的 manifest 被后续 ResUNet 元数据覆盖；真实 SAINT 来源由 checkpoint payload 的 stride 信息确认，并在审计中保留该异常。

数据拆分：fastMRI 为 112/24/24，IXI 为 404/58/115，NingXia 为 8 个患者折、22 个 OOF 序列。所有纳入比较均按检查/患者作为独立单位；不把像素当作独立样本。

详细证据：

- [BASELINE_RECOVERY_AUDIT.md](BASELINE_RECOVERY_AUDIT.md)
- [PROTOCOL_FAIRNESS_AUDIT.md](PROTOCOL_FAIRNESS_AUDIT.md)
- [RECONSTRUCTION_BENCHMARK_REPORT.md](RECONSTRUCTION_BENCHMARK_REPORT.md)

## 3. 冻结协议与修订

主假设 H-ARCH-01 在观察新结果前注册：复用高影响物理测量所导致的 consensus blindness 不应只存在于 HAT/SwinIR。

主试验固定 fastMRI 24 个测试检查、x4、同一目标平面与同一模型，仅改变物理上下文依赖：

- shared 上下文：`{0,4,8,12}`；
- disjoint 上下文：`{2,6,10,14}`；
- 固定目标：`{3,5,7,9,11}`；
- 洁净共享对照：in-plane axis-0 flip 后映射回原坐标；
- 病例级配对及病例簇 bootstrap。

早期 smoke test 使用 through-plane reversal，但会混入顺序效应，已在查看整队列结果前废止；其输出没有进入任何结论。该决定记录于 [PROTOCOL_AMENDMENT_001.md](PROTOCOL_AMENDMENT_001.md)。

有限差分影响协议统一使用四个中心化 Rademacher seed（6101--6104），主幅度 `+0.01`，稳定性幅度 `+0.005`、`+0.02`、`-0.01`；所有替代幅度与主幅度的秩相关必须达到 0.90。采样、上下文几何和 qualitative case 选择均在结果分析前冻结。

协议文件：

- [HYPOTHESIS_REGISTRATION.md](HYPOTHESIS_REGISTRATION.md)
- [UNIFIED_INFLUENCE_PROTOCOL.md](UNIFIED_INFLUENCE_PROTOCOL.md)
- [INFLUENCE_SAMPLING_ADDENDUM.md](INFLUENCE_SAMPLING_ADDENDUM.md)
- [QUALITATIVE_SELECTION_RULE.md](QUALITATIVE_SELECTION_RULE.md)

## 4. 重建基准与 broken-model gate

fastMRI x4 同一支持集上的 MAE：

| 方法 | MAE | 相对 Linear |
|---|---:|---|
| Linear | 134.54 | 参考 |
| Cubic | 153.24 | 更差 |
| I3Net | **70.87** | 通过 |
| SAINT | **80.14** | 通过 |
| HAT | 86.09 | 通过 |
| SwinIR | 90.37 | 通过 |
| CycleINR | **114.39** | 通过 |

三个 P0 模型在全部 24 个检查上均输出有限值，且都优于 Linear，故通过 broken-model gate。CycleINR 较弱，但没有灾难性欠训练，不能因其结果不利而删除。

随着 fastMRI 因子从 x2 增至 x6，五个代表神经模型的 MAE 均升高；x6/x2 比值为 HAT 1.42、SwinIR 1.49、I3Net 1.79、SAINT 1.26、CycleINR 1.60。NingXia 的 22 个 out-of-fold 序列也已按患者分组实验恢复为 x2/x4/x6 语境。IXI 的完整可审计历史输出仅覆盖 x4 下的 Linear、Cubic、ACSI-Net、HAT、SwinIR、I3Net；未用不兼容或零散结果补齐其它方法与倍率。

机器可读结果：

- `outputs/p9_reconstruction_benchmark.csv`
- `outputs/p9_reconstruction_benchmark_compact.csv`
- `outputs/p9_factor_architecture_interaction.csv`

## 5. 同目标 shared / disjoint 主实验

“可观测误差增益”定义为 disjoint 相对 shared 的增益。数值为比例值，括号内给出病例簇 95% CI。

| 架构 | 家族 | 可观测误差增益 | 排名 Spearman：shared → disjoint | 排名差及 95% CI |
|---|---|---:|---:|---:|
| HAT | Transformer SR | 17.8 pp [17.0, 18.7] | 参考分析 | +0.0565 [-0.0298, 0.1857] |
| SwinIR | Transformer SR | 17.6 pp [16.4, 18.8] | 参考分析 | +0.0617 [-0.0509, 0.2344] |
| I3Net | 专用 inter/intra CNN | 8.0 pp [7.2, 8.8] | 0.9426 → 0.9609 | +0.0183 [-0.0613, 0.1075] |
| SAINT | 空间感知 CNN | 13.7 pp [12.5, 14.9] | 0.9339 → 0.9243 | -0.0096 [-0.1425, 0.1139] |
| CycleINR | 隐式坐标/循环 | 22.6 pp [21.9, 23.3] | 0.6339 → 0.9757 | +0.3417 [0.1129, 0.7108] |

所有五个架构的局部可观测误差增益区间均排除零。等权家族汇总为 15.49 pp [14.78, 16.23]。逐家族剔除后的估计仍全部为正：剔除 I3Net 17.99 pp、剔除 INR 13.12 pp、剔除 SAINT 16.10 pp、剔除 Transformer 14.75 pp。

这支持“物理测量依赖导致局部 QA 盲点在已评估范式中存在”，但排名差的明显异质性否定“disjoint 总能改善检查级排序”。

主图与数据：

- [架构族 forest plot（PDF）](figures/p9_architecture_forest.pdf)
- [架构族 forest plot（PNG）](figures/p9_architecture_forest.png)
- `outputs/p9_architecture_forest.csv`

## 6. 各 P0 架构结果

### 6.1 I3Net

- 重建性能最好：fastMRI x4 MAE 70.87。
- 局部可观测误差增益 8.0 pp，稳定为正。
- 检查级排序改善很小且 CI 跨零。
- 有限差分稳定性 rho 为 0.859、0.737、0.939；两个幅度门槛失败。
- 结论：支持物理依赖/误差几何现象，但影响度分析只能作为现象性、探索性证据。

### 6.2 SAINT

- fastMRI x4 MAE 80.14。
- 局部可观测误差增益 13.7 pp，稳定为正。
- 检查级排序差为 -0.0096，CI 跨零。
- 有限差分稳定性 rho 为 0.940、0.964、0.995，全部通过。
- broad 设计中，影响度与 error cosine 的 rho 为 0.706 [0.680, 0.734]，与 observable fraction 的 rho 为 -0.698 [-0.730, -0.666]。
- 但 influence-minus-count 对 error cosine 仅为 0.0138 [-0.0024, 0.0289]；固定非零共享计数后的 error-cosine partial rho 为 0.0634 [-0.0211, 0.1488]。
- 结论：是唯一可用于新架构影响度主张的稳定探针；支持总体方向，不支持“影响度明确优于计数”的强说法。

### 6.3 CycleINR

- fastMRI x4 MAE 114.39，仍显著优于 Linear。
- 局部可观测误差增益最大，为 22.6 pp。
- 检查级排序改善 +0.3417，CI 排除零，是新架构中唯一明确正向者。
- 有限差分稳定性 rho 为 0.779、0.857、0.876，三个替代设置均失败。
- 结论：强力支持现象层面的架构边界扩展，但不能支撑稳定影响函数或 influence-over-count 主张。

## 7. 稳定错误、跨模型相关与误差多样性

预注册 stable-wrong 规则下：HAT、SwinIR、I3Net、SAINT 均为 0；CycleINR 在 shared 条件为 4/120（3.33%），在 disjoint 条件为 0/120。这是一个稀少且带架构差异的结果，没有用 Plan 8 的旧定义替换它。

病例级误差秩相关中位数：fastMRI x2 为 0.9448，x4 和 x6 均为 0.9813；五模型共同 top-quartile 困难病例在 x2 为 4/24，在 x4/x6 为 6/24。IXI 的三个可用神经模型中位数为 0.9915。因此，架构变化没有自动产生检查级误差独立。

像素级则存在有意义差异：HAT–SwinIR 的 error cosine 为 0.918、observable fraction 为 0.041；CycleINR–I3Net 分别为 0.564 和 0.245。即“病例难度高度共享”和“局部误差方向可以更多样”可以同时成立。

定性图严格按冻结规则选取 `110856510804_ax_t2`、z=11，而不是事后挑选最醒目的图像：

- [定性面板 PDF](figures/p9_qualitative_generalization.pdf)
- [定性面板 PNG](figures/p9_qualitative_generalization.png)

## 8. 因子 × 架构边界

x2/x4/x6 支持重建难度随因子增加、且退化速率因架构而异。五架构的同目标机制交互不能在现有数据上公平识别：x2 的互补 phase grid 没有共同缺失整数目标，x6 缺少完整兼容上下文。使用不等间距或 padding 会改变 estimand。

因此最终只主张：

- 重建性能的 factor × architecture 结果覆盖 x2/x4/x6；
- 五架构的 shared/disjoint 机制结果严格限于 x4；
- 不宣称跨架构的神经机制因子定律。

详见 [FACTOR_ARCHITECTURE_ANALYSIS.md](FACTOR_ARCHITECTURE_ANALYSIS.md)。

## 9. 假设判定与修订后的主张

| 命题 | 判定 | 最终表述 |
|---|---|---|
| H-ARCH-01 的现象层：测量依赖造成 consensus blindness 跨范式存在 | 支持 | “在已评估的多种 MRI 插值范式中观察到。” |
| disjoint 在大多数新架构中改善检查级排序 | 否定 | 仅 CycleINR 明确改善；I3Net/SAINT 不确定。 |
| 新架构均产生稳定局部影响探针 | 否定 | 只有 SAINT 通过全部门槛。 |
| shared influence 跨架构稳定优于 raw overlap count | 否定/不支持 | SAINT beyond-count 和 fixed-count 区间跨零；I3Net/CycleINR 不具主张资格。 |
| 架构多样性等于误差独立 | 否定 | 检查级错误排序仍高度相关。 |
| 结果“architecture independent” | 不允许 | 只允许“across evaluated interpolation paradigms”。 |

完整追踪见 [CLAIM_TRACEABILITY.md](CLAIM_TRACEABILITY.md) 和 [CLAIM_REVISION_LEDGER.md](CLAIM_REVISION_LEDGER.md)。

## 10. 文献与新颖性审计

已核对 I3Net、SAINT、CycleINR 的一手论文，并检查 disagreement reliability、measurement overlap、shared measurement influence、common-mode interpolation error 和 same-target context intervention 等相邻概念。未发现这些基线论文已经执行本项目的同目标物理依赖干预和确定性分歧可靠性分析。

最终新颖性限定为：**在固定 MRI 缺失目标的条件下操纵物理测量依赖，并跨多种插值接口检验其与误差对齐、抵消和可观测性的关系，同时公开测量影响探针失效的架构边界。** 不使用 “first”、架构无关或影响度普适优越等措辞。

详见：

- [LITERATURE_AND_NOVELTY_AUDIT.md](LITERATURE_AND_NOVELTY_AUDIT.md)
- [NOVELTY_AUDIT.md](NOVELTY_AUDIT.md)
- [RELATED_WORK_MATRIX.md](RELATED_WORK_MATRIX.md)

## 11. 双论文重构结果

### TMI 架构泛化分支

- [main.tex](../TMI/TMI_ARCH_GENERALIZED/main.tex)
- [main.pdf](../TMI/TMI_ARCH_GENERALIZED/main.pdf)
- 新增宽基准表、“Generalization Across Interpolation Paradigms”章节、架构 forest 图、异质性与限制讨论。
- 保留 TMI 的核心所有权：MRI 重建 QA、指标失效条件、操作因素、stable-wrong、选择性风险和医学解释。
- 明确区分历史三队列 through-plane reversal（含顺序混杂）与 Plan 9 的洁净 in-plane flip 控制。
- 编译为 10 页；第 7 页为 fastMRI/IXI/NingXia 数据集分组、×2/×4/×6、四指标的重建语境表，缺失审计组合显式标为 “---”，不设置 “ours” 或指定胜者；无 undefined reference/citation、LaTeX error 或 overfull box。

### CVPR 架构泛化分支

- [main.tex](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex)
- [main.pdf](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf)
- [supplement.tex](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.tex)
- [supplement.pdf](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf)
- 主文技术内容在第 8 页结束，第 9 页为参考文献；补充材料 5 页。
- 主文增加架构族 falsification、forest 图和影响稳定性边界；补充材料保留完整表格。
- 明确写入：新探针中仅 SAINT 稳定；I3Net/CycleINR 只能用于 phenomenon-level 结论。
- 最终日志无 undefined reference/citation、LaTeX error 或 overfull box。

构建审计：

- [TMI FINAL_BUILD_AUDIT.md](../TMI/TMI_ARCH_GENERALIZED/FINAL_BUILD_AUDIT.md)
- [CVPR FINAL_BUILD_AUDIT.md](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/FINAL_BUILD_AUDIT.md)

## 12. 审稿模拟

五角色独立式模拟的中位数均为 **4/5**：

- **TMI：** 架构族广度不再是中心缺陷；主要剩余问题转为回顾性、MRI-only、无读者研究或前瞻性临床验证。
- **CVPR：** “只有两个相关架构”的原始问题已显著缓解；剩余主要范围限制为 MRI-only，同时仍需承认影响度严格泛化只有部分支持。

详见 [REVIEW_SIMULATION.md](REVIEW_SIMULATION.md)。评分没有按目标倒推，也没有隐去 3/5 的影响函数与临床转化意见。

## 13. 投稿重合与治理

段落级 TF-IDF 审计比较最终两个 `main.tex`：TMI 66 段、CVPR 42 段；相似度至少 0.30 的配对为 3 个，至少 0.45 的为 1 个，高相似文字占比约 1.59%。唯一高匹配段落是架构泛化数值结果。

该数字不是 iThenticate/CrossCheck 分数。虽然文字分离较强，两稿仍共同使用 fastMRI 架构实验，科学重合是实质性的。最终决定：**`MERGE_OR_SEQUENCE_REQUIRED`**。作者需在投稿前核对 venue 政策、披露共享实验并决定合并或错峰。

详见 [SUBMISSION_OVERLAP_AUDIT.md](SUBMISSION_OVERLAP_AUDIT.md)。本次没有自动提交任何稿件。

## 14. 主要产物索引

| 产物 | 路径 |
|---|---|
| 最终总报告 | `PLAN9_ARCH_GENERALIZATION/FINAL_REPORT.md` |
| 架构 forest 数据/图 | `outputs/p9_architecture_forest.csv`; `figures/p9_architecture_forest.pdf` |
| 三数据集重建语境宽表 | `outputs/p9_three_cohort_reconstruction_benchmark.csv` |
| 原始 fastMRI/IXI 恢复基准 | `outputs/p9_reconstruction_benchmark.csv` |
| 影响稳定性与推断 | `outputs/p9_new_arch_influence_stability.csv`; `outputs/p9_influence_clustered_inference.csv` |
| 跨架构相关/多样性 | `outputs/p9_cross_arch_error_rank_correlations.csv`; `outputs/p9_error_correlation_pair_types.csv` |
| stable-wrong / 共识交集 | `outputs/p9_stable_wrong_cross_model_overlap.csv`; `outputs/p9_consensus_error_intersection.csv` |
| TMI 最终候选 | `TMI/TMI_ARCH_GENERALIZED/main.tex`, `main.pdf` |
| CVPR 最终候选 | `CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex`, `main.pdf`, `supplement.tex`, `supplement.pdf` |

## 15. 最终判断

Plan 9 已达到“用架构族做真正的证伪实验”这一目标，而不仅是扩充基线表。最稳健的新科学结论是：

> 在已评估的 MRI 层间插值范式中，复用相同物理测量会系统性地改变局部误差几何与分歧可观测性；但其对检查级排序的收益以及有限差分影响相对共享计数的优势具有显著架构依赖性。

因此，TMI 可把“两个冻结神经插值器”升级为“多个已评估插值范式”；CVPR 应把架构泛化写成对物理依赖/误差几何的支持，同时把影响探针稳定性和 influence-over-count 的失败作为机制边界，而不能写成普适定律。
