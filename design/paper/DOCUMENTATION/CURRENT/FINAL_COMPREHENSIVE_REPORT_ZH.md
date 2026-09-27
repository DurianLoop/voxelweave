# MRI 层间插值研究项目最终综合报告

**整理日期：** 2026-08-14  
**项目根目录：** `D:\MRI\design\paper`  
**研究范围：** MRI inter-slice / through-plane interpolation、确定性重建分歧、物理测量依赖、共识错误与重建质量保证  
**当前状态注记（2026-09-07）：** 本文主体记录 Plan 1--10 时点；最新科学状态已推进至 Plan 12，目录布局和正式结果请以项目根目录 [`README.md`](../../README.md) 与 Plan 12 严格审稿报告为准；未自动投稿。

---

## 1. 报告目的

本报告不是单一阶段的实验摘要，而是整个 `paper` 目录的项目级说明，统一回答以下问题：

1. 这个项目最终研究了什么问题；
2. Plan 1–9 如何逐步改变了科学主张；
3. 哪些结论被多数据集、多架构和受控干预支持；
4. 哪些原假设被否定或必须收缩；
5. TMI 与 CVPR 两篇论文各自拥有哪部分科学内容；
6. 当前目录如何使用、哪些文件是最终候选、哪些只是历史快照；
7. 投稿前还有哪些必须由作者完成的工作。

项目中所有重要负结果都保留在报告、机器可读输出或补充材料中。本文不会把阶段性最优数字重新解释成普适规律。

## 2. 一句话结论

> 在已评估的 MRI 层间插值范式中，两个确定性预测若复用相同或高度相似的物理测量，它们的误差更容易对齐并在预测差中相互抵消，从而形成“模型一致但共同出错”的质量保证盲区；改变物理测量依赖能稳定提高局部误差可观测性，但检查级排序收益和有限差分影响相对共享计数的优势具有显著的数据集与架构依赖性。

这句话包含三个层次：

- **稳健现象：** consensus blindness / shared error 是真实且可复现的；
- **稳健机制边界：** 物理测量依赖会改变误差几何与可观测性；
- **不允许扩大的部分：** 低分歧不能证明正确，disjoint 不保证总能改善全局排序，局部影响也不是所有架构上的稳定全局属性。

## 3. 本次目录整理结果

2026-09-07 已进行第二次目录整理：当前稿件留在 `CVPR/CVPR_ARCH_GENERALIZED` 和 `TMI/TMI_ARCH_GENERALIZED`，旧稿进入各自 `archive/`，Plan 2--8、早期脚本与输出进入 `ARCHIVE/`。没有删除文件。

完成的调整：

- 重写根目录 [README.md](../../README.md)，作为全项目导航；
- 更新 [TMI/README.md](../../TMI/README.md) 和 [CVPR/README.md](../../CVPR/README.md)，说明当前稿与历史稿边界；
- 将历史 ZIP 和 manifest 集中到 [`ARCHIVE/PACKAGES/`](../../ARCHIVE/PACKAGES/)；
- 为全部历史 ZIP 记录大小与 SHA-256；
- Plan 2--4 的脚本与输出作为一个相互依赖的历史工作区保存在 `ARCHIVE/PLANS/PLAN02_TO_PLAN04/`；
- Plan 9--12 仍是活跃证据链，保留在项目入口层。

当前顶层职责如下：

| 路径 | 主要内容 | 是否为当前入口 |
|---|---|---|
| `PLAN9_ARCH_GENERALIZATION/` -- `PLAN12_STRICT_REVIEW_ITERATION/` | 当前架构、全模型库、claim 加固与严格审稿证据链 | 是 |
| `TMI/TMI_ARCH_GENERALIZED/` | 当前 TMI 候选；旧稿位于 `TMI/archive/` | 是 |
| `CVPR/CVPR_ARCH_GENERALIZED/` | 当前 CVPR 候选；旧稿位于 `CVPR/archive/` | 是 |
| `DOCUMENTATION/` | 当前综合报告和历史决策路径 | 是 |
| `ARCHIVE/PLANS/` | Plan 2--8、早期脚本与机器可读输出 | 历史证据层 |
| `ARCHIVE/RESEARCH_RECORDS/` | 初始审计、理论、笔记和报告 | 历史审计层 |
| `ARCHIVE/PACKAGES/` | Plan 6/7 历史交付 ZIP | 仅归档 |

## 4. 核心科学问题

项目最初希望回答：能否在没有稠密真实目标的情况下，用同一重建器在不同采样上下文中的输出分歧判断 MRI 插值误差？

研究最终发现，这个问题必须拆成两个方向：

1. **单向证据：** 若两个预测相差很大，则至少一个预测有明显误差；
2. **一致性盲区：** 若两个预测非常接近，不能推出它们都正确，因为共享的错误方向会在预测差中抵消。

对任意满足三角不等式的距离 `d`，目标 `y` 与两个重建 `f_a`、`f_b` 满足：

`d(f_a, f_b) <= d(f_a, y) + d(f_b, y)`，因此  
`max(d(f_a,y), d(f_b,y)) >= d(f_a,f_b)/2`。

所以大分歧是一个 one-sided witness；小分歧不是 correctness certificate。后续所有实验都围绕“什么条件决定分歧能看到多少真实误差”展开。

## 5. 数据、独立单位与评估规则

主要数据资源：

| 数据集 | 使用方式 | 独立单位 | 角色 |
|---|---|---:|---|
| fastMRI brain | 112/24/24 训练/验证/测试 | 24 个最终测试检查 | 主要机制与架构泛化 |
| IXI | 404/58/115 训练/验证/测试 | 115 个测试检查 | 大样本独立复现与难度排序 |
| NingXia | 8 个患者折、22 个 OOF 序列 | 8 个患者簇 | 临床来源异质性与边界 |

统计原则：

- 检查或患者是独立单位，而不是像素；
- 置信区间采用检查/患者簇 bootstrap 或相应簇级置换；
- 同目标干预固定目标、检查、模型、因子、平面、预处理、mask 和 endpoint；
- 不用目标真值选择最有利的 qualitative case；
- 探索性结果不能替换预注册主结果；
- 不兼容历史输出只能进入 benchmark-only 或 supplement，不做静默拼表。

## 6. Plan 1–9 研究演进

### 6.1 初始审计与治理（goal / Plan 1）

首先建立 `RESEARCH_STATE.md`、`HYPOTHESES.md`、`EXPERIMENTS.md`、`CLAIMS.md`、`CLAIM_EVIDENCE_MATRIX.md`、`LITERATURE.md` 和审稿红队材料。独立审计把已有数据、模型、评估代码、几何关系和缺失证据分开登记，避免把文件名或历史表格直接当成可信事实。

### 6.2 Plan 2：冻结 Physical Consistency，并证明它只能单向作证

`PC-v1-FROZEN` 比较同一物理世界平面在不同插值因子下的重建差异。主要结果：

| 队列 | 像素 Spearman | 平面 Spearman | 检查/组合 Spearman | Top-10% 错误富集 |
|---|---:|---:|---:|---:|
| fastMRI held-out 16 例 | 0.693 | 0.799 | 0.915 | 2.49× |
| NingXia OOF 22 序列 | 0.489 | 0.727 | 0.883 | 2.06× |

检查级比较中，PC 相对 committee 的 nAURC 差在 fastMRI 为 -0.0698，病例簇 CI `[-0.1597,-0.0183]`；NingXia 为 -0.0256，CI `[-0.0957,0.0092]`，方向一致但统计不确定。

共享 blur 反证非常关键：错误增加时，模型分歧和 PC 反而下降。这直接否定“任何共同错误都会被一致性分数发现”。Plan 2 的最终贡献不是更高分数，而是“一致性只能单向作证”的严格边界。

### 6.3 Plan 3：从单一分数转向共识误差结构

Plan 3 发现，MRI 插值误差主要由病例与采样难度决定，而不是架构差异：

- fastMRI 的病例方差占比 0.583、因子占比 0.258、架构占比 0.103；
- NingXia 相应为 0.839、0.125、0.006；
- 138 个病例–架构单元全部满足 x2 < x4 < x6 error；
- 11 个 fastMRI 神经家族的病例误差中位两两 rho 为 0.961；
- 6 个 IXI 方法的中位 rho 为 0.991；
- 精确 MSE 分解显示 shared consensus error 占 80.9%/86.5%，observable diversity 仅占 19.1%/13.5%。

这一步把研究问题从“哪个 score 更好”提升为“为什么分歧只看到少数错误”。同时，flip-TTA 在两个队列、三个因子、三个主架构形成的 18 个 profile 上都不如物理采样上下文，说明有效干预必须改变与目标有关的信息来源，而不只是制造输出变化。

### 6.4 Plan 4：同目标、不同物理测量的受控干预

Plan 4 构造 x4 phase-0 与 phase-2 上下文：目标相同，但 acquired anchors 不相交；并用最大共享上下文作为对照。主要结果：

| 队列 | Disjoint 排名 rho | 最大共享 rho | 差值 | 病例簇 95% CI |
|---|---:|---:|---:|---:|
| fastMRI | 0.960 | 0.605 | 0.355 | [0.225, 0.557] |
| NingXia OOF | 0.891 | 0.699 | 0.193 | [0.111, 0.306] |

HAT 与 SwinIR 分别复现；Linear 与 Cubic 也支持该现象。因此 measurement overlap 是决定分歧能否暴露共享错误的实验因素，不是 Transformer 特有现象。

但 Plan 4 同样否定了数个更强故事：重合数量不是严格单调剂量律，disjoint 不是普适最优估计器，回顾性 phase-grid 不能包装成无额外成本的前瞻采集优化。

### 6.5 Plan 5：形成 TMI / CVPR 双轨写作

Plan 5 将共同证据拆成两个科学所有权：

- TMI 负责医学影像 QA：一致性何时失效、不同指标/因子/操作条件下如何表现、有哪些 stable-wrong 和临床解释边界；
- CVPR 负责机制：共享测量、共享影响、误差对齐、抵消和同目标物理干预。

这一阶段形成早期完整 TMI 稿和 CVPR 机制稿，并开始严格区分“论文内容相邻”与“允许并行投稿”。

### 6.6 Plan 6：扩充实验而不是填页

Plan 6 系统加入共识误差分解、重合响应、metric robustness、granularity、x2/x4/x6、架构与估计器、几何与强度、risk–coverage、回顾性 densification、错误分类和效率分析。

保留的主要负结果包括：

- 整数 overlap 不构成单调规律；
- NingXia fixed-count neural influence 为 null/mixed；
- 局部 cancellation 链强于全局 context-ranking 链，不能声称因果中介；
- Anchor-CV 与 adjacent MAE/RMSE 统计上接近，不具唯一性；
- scale normalization 和朴素特征拼接可能损害表现；
- 检查级风险分数不能定位最差平面；
- densification 只是回顾性分析，不是前瞻采集优化。

Plan 6 产出了 TMI research master、独立提交版和 CVPR 8 页主文/补充材料。

### 6.7 Plan 7：接收风险优化与失败方法门控

Plan 7 先模拟审稿人，再决定是否运行新实验。对影响探针、操作用途和跨稿重合进行压力测试后，结论是：机制论文可以成立，但不应伪装成普适优越的新可靠性方法。影响在局部 target/plane/context 内数值稳定，却不是物理平面不变属性；进一步训练或调参无法解决核心 venue/sequence 风险。

当时的治理决定为：TMI 可在人工元数据补齐后准备，CVPR 应合并或改变投稿顺序。

### 6.8 Plan 8：恢复 CVPR 的机制论文叙事

Plan 8 删除“必须提出优越方法”的错误目标，重新围绕以下链条组织 CVPR：

`共享物理测量 → 共享局部影响 → 误差对齐 → 分歧抵消 → 降低错误可观测性`

主要结果包括：

- disjoint − shared 的错误排序 rho：fastMRI 0.092、IXI 0.095、NingXia 0.193，病例簇区间均排除零；
- shared 条件下 observable paired-error energy 仅为 fastMRI 2.61%、IXI 1.58%、NingXia 0.25%；
- 解析插值器中，共享影响与误差对齐的 rho 为 0.789–0.855，而 anchor count 为 0.466–0.630；
- HAT/SwinIR 的 18 个主要误差对齐/分解终点中，影响相对计数优势为 0.036–0.089，区间均高于零；
- fixed-count 结果在 fastMRI/IXI 支持附加解释，在 NingXia 为 null/mixed；
- Anchor-CV 能排序检查难度并预测回顾性 x4→x2 收益，但不显著优于简单相邻锚点差异或输出 PC。

CVPR 模拟评分达到 4/4/3/4/4，中位数 Weak Accept。剩余主要质疑转为范围较窄以及与 TMI 的治理，而非内部机制矛盾。

### 6.9 Plan 9：I3Net、SAINT、CycleINR 架构族证伪

Plan 9 不再追求“多几行 baseline”，而是直接问：当插值范式改变时，consensus blindness 是否仍存在？

恢复并审计了 13 个方法：Linear、Cubic、HAT、SwinIR、I3Net、SAINT、CycleINR、ArSSR、SMamba-UNet、Pix2PixGAN、ResUNet、Res-SRDiff、ACVTT。ACVIT 无法恢复，未用 ACVTT 冒名替代。

三个 P0 模型的 fastMRI x4 MAE 均优于 Linear：I3Net 70.87、SAINT 80.14、CycleINR 114.39，Linear 为 134.54。它们在 24 个检查上均为有限输出，因而通过 broken-model gate。

同目标 shared/disjoint 主结果：

| 模型 | 家族 | 局部可观测误差增益 | 检查级排名差及 95% CI |
|---|---|---:|---:|
| HAT | Transformer SR | 17.8 pp [17.0,18.7] | +0.0565 [-0.0298,0.1857] |
| SwinIR | Transformer SR | 17.6 pp [16.4,18.8] | +0.0617 [-0.0509,0.2344] |
| I3Net | 专用 inter/intra CNN | 8.0 pp [7.2,8.8] | +0.0183 [-0.0613,0.1075] |
| SAINT | 空间感知 CNN | 13.7 pp [12.5,14.9] | -0.0096 [-0.1425,0.1139] |
| CycleINR | 隐式坐标/循环 | 22.6 pp [21.9,23.3] | +0.3417 [0.1129,0.7108] |

五个架构的局部可观测误差增益 CI 全部排除零；等权家族汇总为 15.49 pp `[14.78,16.23]`，leave-one-family-out 后仍全部为正。这解决了 TMI 的架构特异性质疑。

但影响探针产生了重要反证：

| 模型 | 三个稳定性 rho | 是否通过全部门槛 | 允许的结论 |
|---|---|---|---|
| SAINT | 0.940 / 0.964 / 0.995 | 是 | 可用于新架构影响主张 |
| I3Net | 0.859 / 0.737 / 0.939 | 否 | 仅现象层 |
| CycleINR | 0.779 / 0.857 / 0.876 | 否 | 仅现象层 |

SAINT 的 broad influence→error-cosine rho 为 0.706 `[0.680,0.734]`，但 influence-minus-count 只有 0.0138 `[-0.0024,0.0289]`；固定共享计数后的 error-cosine partial rho 为 0.0634 `[-0.0211,0.1488]`。所以“共享影响在所有架构上都稳定优于计数”被否定。

## 7. 当前证据的分层判定

### 7.1 高置信度、可进入主文的结论

- 大分歧是重建错误的 one-sided witness；小分歧不是正确性证书。
- MRI 层间插值误差含有很大的病例/采样共识成分，架构变化不能自动消除它。
- 在固定同一缺失目标时，改变物理测量依赖会改变局部误差对齐和可观测性。
- 该局部 QA 盲点在 HAT、SwinIR、I3Net、SAINT 和 CycleINR 五个已评估神经范式中均出现。
- 架构多样性不等于检查级错误独立，但可以增加某些模型对的像素级误差多样性。
- Anchor-CV/相邻锚点变化可以反映检查难度和回顾性加密收益，但不是唯一或普适最优的评分器。

### 7.2 有条件支持、必须带边界的结论

- 共享局部影响比共享数量提供更深机制解释：在解析估计器和 HAT/SwinIR 的主要层中强，在 SAINT 的新架构扩展中 beyond-count 证据不确定。
- disjoint 上下文改善检查级错误排序：在部分数据/架构上强，但不是普遍规律。
- curvature/spacing 与错误相关：有支持性，但绝对校准和跨队列普适律失败。
- 有限差分 influence 是局部统计，不是 plane-invariant、architecture-invariant 的模型属性。

### 7.3 已否定或明确禁止的主张

- “低分歧意味着重建正确”；
- “所有共同错误都能被一致性检测”；
- “越多输出多样性就越有用”；
- “每增加一个共享 anchor 都单调降低可观测性”；
- “disjoint 一定改善全局排序”；
- “影响度在所有架构上稳定优于计数”；
- “Anchor-CV 普遍优于 adjacent MAE/RMSE 或输出 PC”；
- “结果 architecture independent”；
- “已证明临床获益、前瞻采集优化或跨模态/跨器官泛化”。

## 8. 架构多样性与错误多样性

Plan 9 的跨架构分析显示，fastMRI 的病例级误差秩相关中位数在 x2 为 0.9448，在 x4/x6 为 0.9813；五模型共同 top-quartile 困难检查在 x2 为 4/24，在 x4/x6 为 6/24。IXI 三个可用神经模型的中位数为 0.9915。

然而像素级误差结构并不完全相同：HAT–SwinIR error cosine 为 0.918、observable fraction 为 0.041；CycleINR–I3Net 分别为 0.564 和 0.245。合理结论是：

> 不同架构仍会在相同困难检查上失败，但某些异构组合能增加局部错误方向的差异；仅以“架构不同”构建分歧集成并不能保证可靠性。

## 9. Stable-wrong 与定性证据

预注册 Plan 9 stable-wrong 规则下，HAT、SwinIR、I3Net、SAINT 的 shared 条件均未出现事件；CycleINR 为 4/120（3.33%），disjoint 后为 0/120。该结果与早期 Plan 8 定义下更高的发生率不同，两个定义没有被混用。

Plan 9 定性图使用冻结规则选择 `110856510804_ax_t2`、z=11，而不是选择最具视觉冲击力的病例。图件位于：

- [架构泛化定性面板](../../PLAN9_ARCH_GENERALIZATION/figures/p9_qualitative_generalization.pdf)
- [架构族 forest plot](../../PLAN9_ARCH_GENERALIZATION/figures/p9_architecture_forest.pdf)

## 10. Factor × architecture 的可识别边界

x2/x4/x6 的重建基准显示所有代表神经架构随插值难度增加而退化，但退化速度不同。五架构同目标机制交互只能在 x4 公平实现：互补 x2 phase grid 没有共同缺失整数目标，x6 缺少完整兼容上下文。若强行使用不等间距或 padding，会改变 estimand。

因此：

- reconstruction difficulty × architecture 可以跨 x2/x4/x6 报告；
- shared/disjoint mechanism × architecture 只报告 x4；
- 不建立跨架构、跨因子的普适神经机制定律。

## 11. TMI 论文最终状态

当前推荐分支：`TMI/TMI_ARCH_GENERALIZED/`。

- [主文源码](../../TMI/TMI_ARCH_GENERALIZED/main.tex)
- [主文 PDF](../../TMI/TMI_ARCH_GENERALIZED/main.pdf)
- [构建审计](../../TMI/TMI_ARCH_GENERALIZED/FINAL_BUILD_AUDIT.md)
- [审稿模拟](../../TMI/TMI_ARCH_GENERALIZED/FINAL_REVIEW_SIMULATION.md)

论文角色：回答“确定性 MRI 插值一致性在什么条件下会失去 QA 能力”。最新稿新增宽基准、`Generalization Across Interpolation Paradigms`、架构 forest、异质性和限制讨论，但没有转型成 shared-influence 方法论文。

最终编译 10 页，其中第 7 页为 fastMRI、IXI、NingXia 三数据集分组的 ×2/×4/×6 重建语境表。表中同时保留模型覆盖空档，不设置 “ours”，也不以粗体把 I3Net 塑造成本文方法；无未解析引用、未解析文献、LaTeX error 或 overfull box。模拟审稿中位数为 4/5。剩余主要问题是临床外部效度：回顾性、MRI-only、无读者研究、无前瞻性决策影响验证。

允许的升级措辞是 “observed across evaluated interpolation paradigms”，不允许 “architecture independent”。

## 12. CVPR 论文最终状态

当前推荐分支：`CVPR/CVPR_ARCH_GENERALIZED/PAPER/`。

- [主文源码](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex)
- [主文 PDF](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf)
- [补充材料源码](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.tex)
- [补充材料 PDF](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf)
- [构建审计](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/FINAL_BUILD_AUDIT.md)
- [审稿模拟](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/FINAL_REVIEW_SIMULATION.md)

论文角色：解释共享物理测量如何导致局部错误对齐、抵消和分歧盲区。主文技术内容在第 8 页结束，第 9 页为参考文献；补充材料 5 页。最终日志无 undefined reference/citation、LaTeX error 或 overfull box。

模拟审稿中位数为 4/5。Plan 9 已把原先“只有两个相关 Transformer”的主要质疑改写为“现象覆盖多个架构，但严格 influence-over-count 泛化只有部分支持”。这使稿件更像诚实的机制/证伪论文，而不是普适影响度方法。

## 13. 两篇论文的科学边界

| TMI 所有权 | CVPR 所有权 |
|---|---|
| MRI reconstruction QA 的失效条件 | 物理测量依赖与局部影响机制 |
| 指标、因子、操作区间和 risk–coverage | 同目标干预、误差对齐与抵消 |
| stable-wrong、病例困难度、临床解释 | influence vs count、有限响应稳定性 |
| 多插值范式的 QA 共识盲区 | 架构族机制边界与证伪结果 |

最终段落级 TF-IDF 诊断：TMI 66 段、CVPR 42 段；相似度至少 0.30 的配对为 3 个，至少 0.45 的为 1 个，高相似文字约占 1.59%。唯一高匹配段落是架构泛化数值结果。

该指标不是 CrossCheck，也不能清除重复发表风险。两稿共享 fastMRI 架构实验，科学重合仍然实质存在。最终治理决定是：

> **MERGE_OR_SEQUENCE_REQUIRED：不得在未核对双方 venue 政策、未披露共享实验且未作作者决策时并行投稿。**

## 14. 文献与新颖性边界

已核对 SAINT（CVPR 2020）、CycleINR（CVPR 2024）、I3Net（IEEE TMI 2024）、DeepResolve 和相关 MRI 不确定性文献的一手来源。现有重建论文主要研究插值质量、空间感知、连续表示或不确定性，没有执行本项目的“固定同一缺失目标、操纵物理测量依赖、测量确定性分歧中的错误抵消”这一完整设计。

最终可辩护的新颖性不是 consistency uncertainty 本身，也不是某个新 score，而是：

1. 同目标物理上下文干预；
2. shared error / observable error 的显式分解；
3. 测量依赖、局部影响、错误对齐和分歧抵消的证据链；
4. 跨插值范式的 falsification；
5. 对失败门槛、异质性和不可识别因素的公开报告。

详见 [Plan 9 文献与新颖性审计](../../PLAN9_ARCH_GENERALIZATION/LITERATURE_AND_NOVELTY_AUDIT.md)。

## 15. 可复现性与证据追踪

推荐按以下层次查证：

1. 先读 [Plan 9 最终报告](../../PLAN9_ARCH_GENERALIZATION/FINAL_REPORT.md)；
2. 用 [CLAIM_TRACEABILITY.md](../../PLAN9_ARCH_GENERALIZATION/CLAIM_TRACEABILITY.md) 从主张定位到输出；
3. 查看 `PLAN9_ARCH_GENERALIZATION/outputs/` 中的 CSV/JSON；
4. 查看 `PLAN9_ARCH_GENERALIZATION/scripts/` 中的分析代码；
5. 对历史论点，分别查看 `ARCHIVE/RESEARCH_RECORDS/REPORTS_AND_AUDITS/FINAL_RESEARCH_REPORT.md`、`ARCHIVE/PLANS/PLAN02_TO_PLAN04/PLAN3_RESEARCH_REPORT.md`、`ARCHIVE/PLANS/PLAN02_TO_PLAN04/PLAN_4_REPORT.md`、`ARCHIVE/PLANS/PLAN07/PLAN7_ACCEPTANCE_OPTIMIZATION/FINAL_ACCEPTANCE_OPTIMIZATION_REPORT.md` 和 `ARCHIVE/PLANS/PLAN08/CVPR_plan8_final_report.md`；
6. 论文构建状态以 TMI/CVPR 最新分支中的 `FINAL_BUILD_AUDIT.md` 为准。

Plan 9 关键机器可读文件：

- `outputs/p9_reconstruction_benchmark.csv`
- `outputs/p9_architecture_forest.csv`
- `outputs/p9_influence_clustered_inference.csv`
- `outputs/p9_new_arch_influence_stability.csv`
- `outputs/p9_cross_arch_error_rank_correlations.csv`
- `outputs/p9_error_correlation_pair_types.csv`
- `outputs/p9_consensus_error_intersection.csv`
- `outputs/p9_stable_wrong_cross_model_overlap.csv`
- `outputs/p9_submission_paragraph_overlap.csv`

## 16. 实现谱系与公平性限制

Plan 9 的架构广度应按本地可复现实验理解，而不是官方 benchmark 的完全复刻：

- I3Net：官方架构谱系，本地训练，无官方 checkpoint；
- SAINT：本地 SAINT-style 适配，不是官方仓库与权重的精确运行；
- CycleINR：内部 CycleINR-style 训练，使用本地 ArSSRNet 路径；
- HAT/SwinIR：作为 Plan 8 冻结参考架构；
- 发布论文中的 headline metric 与本项目数据、强度尺度、退化形成和实现不同，不做直接数值优劣比较。

这些模型只有在相同目标、mask、metric 和检查支持上才用于机制比较。缺失或不兼容输出不会用插值、跨实验复制或不匹配表格补齐。

## 17. 当前尚未解决的问题

下面的问题不是继续调当前模型就能可靠解决的：

- 外部器官、模态和站点泛化；
- 前瞻性 phase-grid 或 repeat acquisition 验证；
- 放射科医生读者研究和临床决策影响；
- 患者级安全阈值或校准不确定性；
- 自动识别“两个预测中究竟哪一个错”；
- 跨所有架构稳定、可比较的局部影响定义；
- TMI/CVPR 的最终 venue、作者列表、伦理措辞和投稿顺序。

任何后续工作若仍只在当前 fastMRI/IXI/NingXia 结果上调分数，信息增益会很低。更有价值的下一步是新前瞻性数据、外部解剖/站点、读者/下游标签，或预注册的新物理上下文设计。

## 18. 投稿前人工检查清单

- 确认 TMI 与 CVPR 的合并或错峰策略；
- 核对最新官方页面限制、双投/扩展稿政策与匿名要求；
- 补齐作者、单位、致谢、基金、伦理审批、知情同意和数据使用文本；
- 完成 CVPR compute-reporting 等 venue 表单；
- 再次检查共享数据、图表和实验的交叉披露；
- 由领域作者逐句审阅临床、安全、因果和泛化措辞；
- 在最终提交环境重新编译，并确认所有图字体、参考文献和匿名元数据；
- 不把本报告中的 simulated review score 当成真实录用概率。

## 19. 最终产物索引

| 产物 | 路径 |
|---|---|
| 项目总导航 | [README.md](../../README.md) |
| 本综合报告 | `FINAL_COMPREHENSIVE_REPORT_ZH.md` |
| Plan 9 完整报告 | [PLAN9_ARCH_GENERALIZATION/FINAL_REPORT.md](../../PLAN9_ARCH_GENERALIZATION/FINAL_REPORT.md) |
| TMI 最新主文 | [TMI/TMI_ARCH_GENERALIZED/main.pdf](../../TMI/TMI_ARCH_GENERALIZED/main.pdf) |
| CVPR 最新主文 | [CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) |
| CVPR 最新补充 | [CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf](../../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) |
| Plan 9 forest 图 | [PLAN9_ARCH_GENERALIZATION/figures/p9_architecture_forest.pdf](../../PLAN9_ARCH_GENERALIZATION/figures/p9_architecture_forest.pdf) |
| Plan 9 qualitative 图 | [PLAN9_ARCH_GENERALIZATION/figures/p9_qualitative_generalization.pdf](../../PLAN9_ARCH_GENERALIZATION/figures/p9_qualitative_generalization.pdf) |
| 历史压缩包清单 | [ARCHIVE/PACKAGES/README.md](../../ARCHIVE/PACKAGES/README.md) |

## 20. 项目最终判断

这个项目最终没有得到“一个分数可以证明 MRI 重建正确”或“一个新影响函数适用于所有架构”的简单结论。相反，它建立了一条更可信的科学链：

1. 确定性分歧只能单向揭示错误；
2. MRI 插值中大量错误是跨上下文、跨架构共享的；
3. 共享物理测量是共识错误不可见的重要实验原因；
4. 改变物理测量依赖能提高局部错误可观测性；
5. 该现象跨多种已评估插值范式存在；
6. 但全局排序收益、影响稳定性和 influence-over-count 优势存在真实异质性。

因此，当前最合适的论文表达不是“我们发明了一个普适可靠性估计器”，而是：

> **我们识别、干预并跨架构检验了确定性 MRI 插值分歧的一个根本盲区，同时明确给出了它何时成立、何时失败以及为什么不能被过度解释。**

这也是当前目录中 TMI 与 CVPR 两个分支共同依赖、但必须分别组织和治理的最终研究资产。

## 21. Plan 10 接收率迭代（2026-08-27）

为回应“架构广度是否仅由精选五模型支持”的潜在审稿质疑，项目新增探索性全模型库审计。在 fastMRI ×2/×4/×6、IXI ×4 和 NingXia ×2/×4/×6 七层共同病例支持上，审计覆盖 6–13 个模型、483 个无向模型对和 807 个有向分歧对。

七层的模型间病例误差排名中位 Spearman ρ 为 .938–.991，聚类 bootstrap 区间下界均高于 .83，说明病例难度在更广的架构库中仍高度共享。NingXia ×2 的 12 个低相关模型对全部包含严重退化的 Res-SRDiff 运行；该边界说明“错误不同”不等于“可靠性有用”。在 38 个可匹配目标中，跨家族搭档相对同家族搭档 22 个为正、16 个为负，进一步拒绝“换架构家族即可保证独立且更有用错误”的普适规则。

本轮新增三联图并放入 CVPR 补充材料第 3 页；TMI 正文纳入完整数值但为维持 10 页未嵌入宽图。两篇稿件同时引用并区分 Savant 2026 关于 MRI 插值问题设定的新近研究。最终构建为 TMI 10 页、CVPR 主文 9 页（8 页内容 + 1 页参考文献）、CVPR 补充 6 页，日志无未定义引用、LaTeX 错误或 overfull box。

详细协议、数值、图表、论文改动和剩余风险见 [Plan 10 接收率迭代报告](../../PLAN10_ACCEPTANCE_ITERATION/FINAL_REPORT_ZH.md)。Plan 10 不改变双稿治理结论：共享队列与 Plan 9 实验仍要求 `MERGE_OR_SEQUENCE_REQUIRED`。
