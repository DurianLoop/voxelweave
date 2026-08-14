# 两篇论文研究进展报告

更新时间：2026-08-13  
工作根目录：`D:\MRI\design\paper`  
覆盖论文：TMI（医学影像完整机制表征）与 CVPR（共享影响机制 + Anchor-CV）

## 1. 总体状态

两篇论文已经从原始约 6 页压缩稿进入“科学扩展优先”的 Plan6 阶段。内容缺口审计、假设注册、三数据集覆盖规则和 Anchor-CV 冻结定义均已完成。当前新增研究默认同时覆盖 fastMRI、IXI、NingXia；若只能使用两个数据集，严格限定为 IXI + fastMRI。本轮没有用 fastMRI + NingXia 冒充两数据集确认。

截至本报告：

| 方向 | 当前状态 | 已有可编译稿 | Plan6 新科学 | 尚未完成 |
|---|---|---|---|---|
| TMI | 原始压缩稿完成；研究 master 的实验资产正在扩充 | `TMI/TMI_MANUSCRIPT/main.pdf` | 多指标、完整共识分布、三因子解析稳健性已完成 | 18–20 页 master、10 页 submission、风险覆盖、效率、正式写作与编译 |
| CVPR | 原始升级稿与短补充材料已完成；P0/P1 机制实验大部分完成 | `CVPR/CVPR_UPGRADE/PAPER/main.pdf`、`supplement.pdf` | 神经共享影响、机制链、强基线、难度分解、失败分类、冻结风险覆盖已完成 | 约 8 页主文重写、完整补充、效率、IXI x2 后果、最终文献与红队审查 |

共享研究基础为 3 个 MRI 队列：fastMRI 24 个检查，IXI 115 个检查，NingXia 22 个序列、8 位独立患者。NingXia 的所有推断均以 8 位患者为聚类单位，不把 22 个序列写成 22 位患者。

## 2. 已完成的公共研究治理

- 已完成逐页/逐节/逐主张的扩展缺口审计：`PAPER_EXPANSION_GAP_AUDIT.md`。
- 已建立 Plan6 假设与实验注册表：`PLAN6_HYPOTHESES_AND_EXPERIMENTS.md`，含 P6-E01 至 P6-E11 的检验、竞争解释和证伪规则。
- 已冻结 `ANCHOR_CV_V1`：`CVPR/CVPR_UPGRADE/ANCHOR_CV_FROZEN.md`。
- 已固定数据集覆盖规则：默认 3 数据集；只做 2 数据集时仅允许 IXI + fastMRI。
- 已保留负结果，未因叙事便利删除：Anchor-CV 独立信息主张被否定、固定重叠阶梯在 NingXia 未复现、最终排序箭头只部分支持、朴素融合不成立。

## 3. TMI 论文进展

### 3.1 论文定位与已有稿件

TMI 论文的科学中心保持为：确定性 MRI 层间插值中的共识盲点，以及测量重叠如何降低分歧的可靠性。它不被改写成 Anchor-CV 方法论文。

当前压缩稿位于：

- `TMI/TMI_MANUSCRIPT/main.tex`
- `TMI/TMI_MANUSCRIPT/main.pdf`

现稿已经包含理论、测量重叠假设、材料方法、共识误差、受控重叠、架构/解析推广、回顾性后果和失败边界，但仍是约 6 页级别的压缩总结。新的 18–20 页研究 master 目录已建立：`TMI/TMI_MANUSCRIPT_MASTER/`，目前主要存放新增实验、脚本和图，还没有完成 `main.tex` 与 `main_20page.pdf`。

### 3.2 已完成的新增科学

#### P6-E01：多重重建端点稳健性

在三个队列、HAT/SwinIR、每病例 3 个物理平面、分离/最大共享两种上下文上，重新获得配对图像并评估 7 个端点：MAE、RMSE、MSE、SSIM error、梯度 MAE、低频 MAE、高频 MAE。

- 42 个数据集–网络–端点层的“分离减共享”排序相关点差全部为正。
- MAE/RMSE/MSE/低频结果在全部 6 个数据集–网络层最稳定。
- IXI 的 7 个端点全部得到不跨零的聚类区间。
- SSIM error 在 fastMRI/NingXia 的绝对相关很弱或为负，部分梯度/高频区间也跨零。

结论：测量分离揭示的是较广泛的重建困难，不只依赖 MAE；但像素分歧不是所有结构指标的通用代理，论文必须写成“广泛但非度量无关”。

主要产物：`TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e01_metric_robustness_*`。

#### P6-E02：完整共识误差分布与 stable-wrong

覆盖三个队列、HAT/SwinIR、分离与最大共享条件，计算逐物理平面的总误差、共享分量、上下文敏感分量、共享比例、可观测比例、误差余弦和分歧。

- 控制总误差和病例后，共享比例与 RMSE 归一化分歧的偏秩相关为 `-0.746` 至 `-0.975`。
- 严格定义的 stable-wrong（同一数据集/模型内，高于误差 75% 分位且低于分歧 25% 分位）在分离上下文中为 0。
- 最大共享上下文中的 prevalence：fastMRI/IXI 为 `0–0.32%`，NingXia 为 `2.42–3.23%`；NingXia 仅 8 位患者，区间较宽。

结论：低分歧不能认证正确这一结构性风险得到强机制支持，但不能把 stable-wrong 写成高发生率临床事件。

主要产物：

- `TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e02_consensus_*`
- `TMI/TMI_MANUSCRIPT_MASTER/figures/p6_e02_consensus_distributions.pdf`

#### P6-E11：三个队列的 ×2/×4/×6 解析因子稳健性

为保证 shallow-volume 的 fastMRI/NingXia 在 ×6 仍有统一定义，使用两锚线性插值与最近锚复制构成解析估计器对；这项实验是解析机制泛化，不替代缺失的 IXI 神经 ×2/×6 输出。

| 数据集 | 共享比例 ×2→×4→×6 | 分歧–误差 rho ×2→×4→×6 |
|---|---:|---:|
| fastMRI | 0.843 → 0.940 → 0.953 | 0.955 → 0.833 → 0.798 |
| IXI | 0.750 → 0.886 → 0.923 | 0.961 → 0.947 → 0.947 |
| NingXia | 0.860 → 0.933 → 0.953 | 0.937 → 0.830 → 0.818 |

三个队列中，因子升高都伴随配对误差和共享比例上升、可观测比例和可靠性下降。绝对分歧多数反而下降；IXI 在 ×6 略回升，但可靠性未恢复。这个结果直接支持“问题更难、估计器却更一致”的共识盲点。

主要产物：`TMI/TMI_MANUSCRIPT_MASTER/experiments/p6_e11_analytic_factor_*`。

### 3.3 已有但待正式整合的证据

- 几何审计已验证已有配对的 in-plane shape、orientation、spacing、FOV 等一致；最大法向角误差约 `1.48e-6` 度。现有正式数据主要覆盖 fastMRI/NingXia，需决定是否补 IXI 或按 IXI+fastMRI 两队列规则重做。
- 强度处理已证实会改变排序：原始公共强度、pooled normalization 和 independent per-factor normalization 不等价；独立归一化可能破坏跨上下文分歧的科学含义。
- 既有 Plan1–4 已包含模型/因子相关、TTA、风险覆盖、边界位置、频率分解、病例尺度效应、回顾性 densification 等大量资产，待按 Plan6 的主张层级重整，而不是机械复制。

### 3.4 TMI 当前主要缺口

1. P6-E03 几何/归一化 operating range 尚未整理为 Plan6 三队列或合规两队列正式结果。
2. TMI 完整 risk–coverage、预算后果和部署效率仍需统一重算/汇总。
3. `TMI_ERROR_TAXONOMY.md`、计算成本表、完整森林图和 leave-one-patient influence 尚未完成。
4. `TMI/TMI_MANUSCRIPT_MASTER/main.tex`、`main_20page.pdf`、`PAGE_GROWTH_LEDGER.md`、`NEW_EXPERIMENTS.md`、`CLAIM_TRACEABILITY.md` 尚未完成。
5. 只有 master 完成后，才能独立蒸馏 10 页 TMI submission；当前还未建立最终 submission 版本。

## 4. CVPR 论文进展

### 4.1 论文定位与已有稿件

CVPR 论文的主线为：

`measurement overlap → neural shared influence → error alignment → disagreement cancellation → Anchor-CV acquired-data difficulty`

当前可编译稿位于：

- `CVPR/CVPR_UPGRADE/PAPER/main.tex`
- `CVPR/CVPR_UPGRADE/PAPER/main.pdf`
- `CVPR/CVPR_UPGRADE/PAPER/supplement.tex`
- `CVPR/CVPR_UPGRADE/PAPER/supplement.pdf`

现稿仍是 Plan6 前的约 5 页真实主内容/约 6 页总页数级别，尚未写入本轮大部分新实验。Plan6 的实验资产已经大幅超过现稿，需要整体重写，而不是局部添段。

### 4.2 已完成的新增科学

#### P6-E04：神经共享影响

已建立固定有限差分神经影响定义：对共享物理锚点施加 4 个固定 Rademacher 扰动（种子 6101–6104，病例归一化范围的 1%），计算 HAT/SwinIR 输出响应向量的共同余弦/质量。

三切片确认规模：

- fastMRI：24 检查、72 平面；
- IXI：115 检查、345 平面；
- NingXia：22 序列、66 平面、8 位患者聚类；
- 两种网络：HAT、SwinIR。

主要结果：

- 在全部 6 个数据集–网络层，神经影响对误差余弦、共享比例、可观测比例的绝对关联均优于整数重叠计数。
- 18 个主要比较的 cluster-bootstrap 95% CI 均不跨零，改进幅度为 `0.036–0.089`。
- 控制重叠计数、跨度、不对称性和病例后，神经影响仍保留 `|rho|=0.185–0.395`。
- 分歧 MAE 的点差全部为正，但 fastMRI 两层区间跨零，因此只作为支持性终点。

更干净的固定计数检验把 overlap count 固定为 1：fastMRI/IXI 的全部网络/终点仍支持连续神经影响，`|rho|=0.135–0.587` 且区间不跨零；NingXia 点估计接近零或方向混合，全部区间跨零。因此“影响优于计数”在两个较大队列成立，但不宣称在 8 患者外部队列普适。

主要产物：

- `CVPR/CVPR_UPGRADE/outputs/plan6_neural_shared_influence_confirm3_*`
- `CVPR/CVPR_UPGRADE/outputs/plan6_fixed_overlap_ladder.*`
- `CVPR/CVPR_UPGRADE/PAPER/figures/plan6_neural_influence_forest.pdf`

#### P6-E05：完整机制链

三个局部箭头在所有 6 个数据集–网络层成立：

- 共享影响 → 误差对齐：控制病例与几何后 `rho=0.219–0.410`；
- 误差对齐 → 归一化分歧受抑：`rho=-0.933` 至 `-0.889`；
- 共享影响 → 可观测误差比例下降：`rho=-0.412` 至 `-0.211`。

以上区间均不跨零。最后的“更高对齐/影响 → 更差排序”只在部分上下文层显著：IXI 两网络与 NingXia HAT 较稳定，fastMRI 及其他层不稳定。论文应写成“强局部抵消机制 + 部分支持的上下文级排序后果”，不能写成已识别的完整因果中介。

主要产物：`CVPR/CVPR_UPGRADE/outputs/plan6_mechanism_chain_*`。

#### P6-E06：Anchor-CV 强基线与解释审计

Anchor-CV 的冻结实现已得到数值级复现。审计中曾发现 NingXia 一个病例有 0.91 强度单位差异，定位为 float64 审计掩膜改变了 751 个阈值边缘像素；恢复冻结 float32 运算后，322 个模型–病例记录的最大绝对差为 `5.68e-14`。

核心结果：

- Anchor-CV 对 x4 误差的 Spearman 为 fastMRI/IXI/NingXia `0.943/0.955/0.958`；Kendall 为 `0.812/0.831/0.844`。
- 但 adjacent MAE/RMSE 与其统计上不可区分；IXI/NingXia 的 adjacent MAE 点估计略高。
- 控制 adjacent MAE、强度范围和 spacing 后，Anchor-CV 偏秩相关为 `0.333/-0.059/-0.100`。
- 强度尺度归一化显著降低或反转部分排名。

结论：已证伪“Anchor-CV 含有超越直接相邻变化的独立信息”这一主张。Anchor-CV 保留为简单、可解释、无需重建输出的 acquired-data difficulty score，而不是独立信息或精度冠军方法。

主要产物：`CVPR/CVPR_UPGRADE/outputs/plan6_anchor_cv_explanation_*`。

#### P6-E07A：冻结风险–覆盖重分析

三个队列、HAT/SwinIR 的完整前缀曲线及 10/20/30/50/70/90% 覆盖率均已完成。Anchor-CV 能稳定分层 x4 风险，但不是最佳 nAURC 方法：

- fastMRI/IXI：Output PC 更低；
- NingXia：Adjacent MAE 更低。

这些队列参与过早期方法发展，因此只能称“冻结重分析”，不是独立外部确认。该结果进一步收窄 Anchor-CV 的贡献边界。

主要产物：

- `CVPR/CVPR_UPGRADE/outputs/plan6_frozen_risk_coverage_*`
- `CVPR/CVPR_UPGRADE/PAPER/figures/plan6_frozen_risk_coverage.pdf`

#### P6-E08：架构无关的病例难度

- HAT–SwinIR 病例误差秩相关：`0.989/1.000/0.997`。
- 病例身份解释两网络误差平方和的 `99.1%/99.99%/99.78%`。
- 留一病例/患者聚类 ridge 中，Anchor-CV 单特征秩相关为 `0.939/0.954/0.953`，held-out R² 为 `0.789/0.900/0.837`。
- 堆叠相邻差分、梯度、频率、spacing 等共线特征没有改善秩相关，并在 IXI 严重破坏绝对校准。

结论：病例难度是跨架构稳定的潜在属性；朴素特征堆叠被否定。

主要产物：`CVPR/CVPR_UPGRADE/outputs/plan6_intrinsic_difficulty_*`。

#### P6-E09：失败分类与互补性

按冻结的 0.20 绝对秩误差优势阈值：

- PC 更准确：fastMRI 3 个、IXI 8 个模型–病例；
- Anchor-CV 更准确：fastMRI 1 个；
- NingXia：无大幅互补病例；
- 大多数层一致：44/48、222/230、44/44。

这不支持新融合方法。代表性真实 MRI/重建/误差图已经生成，并明确显示两种病例级分数都不能定位最差局部平面。

主要产物：

- `CVPR/CVPR_UPGRADE/outputs/plan6_failure_taxonomy_*`
- `CVPR/CVPR_UPGRADE/PAPER/figures/plan6_failure_exemplars.pdf`

### 4.3 IXI ×2 当前状态

IXI x2 checkpoint、SHA-256、端点与预算已在任何测试输出生成前冻结；随后成功生成 115 个 I3Net、ground-truth/sparse、linear/cubic 输出及 115 行 I3Net 病例指标。由此完成了合规的 IXI+fastMRI 两队列 x4→x2 后果确认。Anchor-CV 对收益的 Spearman 为 IXI/fastMRI `0.948/0.871`；所有 10/20/30/50% 预算均显著优于随机。IXI x4 使用已有 HAT/SwinIR 平均误差、x2 使用冻结 I3Net，因此该结果是跨估计器病例级可预测性，不是同一模型内因果收益。IXI 神经 x6 仍未生成。

### 4.4 CVPR 当前主要缺口

1. P6-E10 实测效率尚未完成；需要区分纯计分成本与生成预测的模型推理成本。
2. IXI ×2 definition-matched inference 未完成，故 x4→x2 预算后果仍缺一项关键确认。
3. 新结果尚未写入 `main.tex`；当前 PDF 仍是 Plan6 前版本。
4. `PAGE_GROWTH_LEDGER.md` 尚未建立，`CLAIM_TRACEABILITY.md` 需按新证据重写。
5. Supplement 目前很短，尚未纳入完整协议、所有负结果、聚类统计和大表。
6. 最新文献/新颖性审计、CVPR 七类 reviewer red team 和最终合规检查尚未完成。

## 5. 两篇论文之间的边界

| 科学内容 | TMI | CVPR |
|---|---|---|
| 共识误差分解 | 中心贡献，做完整医学影像表征 | 作为机制背景和必要证据 |
| 测量重叠 | 中心机制，强调可靠性边界 | 从 count 推进到 neural shared influence |
| 多指标/多因子/几何/强度 | 重点完整展开 | 只保留与方法机制直接相关部分 |
| Anchor-CV | 不作为论文中心 | 方法/获得数据难度分数，但已收窄主张 |
| 失败分析 | stable-wrong、粒度、临床解释边界 | Anchor-CV/PC 互补与局部定位失败 |
| 回顾性 densification | 医学应用后果，明确非 prospective policy | 资源分配后果；IXI ×2 仍待完成 |

## 6. 当前最重要的科学判断

1. 共识盲点主张比原稿更强：三个数据集、多指标、因子实验共同支持“误差更大但可观测分歧比例更小”。
2. 神经共享影响是有效扩展，但证据有异质性：完整网格在三队列成立；固定 overlap-count 的干净检验只在 fastMRI/IXI 稳健。
3. 完整因果链不能宣称已建立：局部抵消箭头稳定，最终排序后果仅部分支持。
4. Anchor-CV 的原始强相关真实，但独立信息与最佳方法主张均不成立；其合理定位是无需重建输出、简单可解释的 acquired-data difficulty score。
5. 病例难度高度跨架构稳定，支持从“某个网络失败”转向“检查本身的层间可插值性”解释。
6. 朴素融合与无机制特征堆叠均无充分依据，应保留为负结果。

## 7. 产物索引

重要根级文档：

- `PAPER_EXPANSION_GAP_AUDIT.md`
- `PLAN6_HYPOTHESES_AND_EXPERIMENTS.md`
- `CVPR/CVPR_UPGRADE/ANCHOR_CV_FROZEN.md`

当前 Plan6 资产规模：

- CVPR outputs：79 个文件，约 36.2 MB；
- CVPR figures：13 个文件；
- TMI master experiments：12 个文件，约 16.1 MB；
- TMI master figures：2 个文件。

新增实验的详细叙述已同步至：`CVPR/CVPR_UPGRADE/PAPER/NEW_EXPERIMENTS.md`。所有原始/汇总 CSV、JSON、脚本和图均位于 `D:\MRI\design\paper` 下。

## 8. 建议的后续执行顺序

1. 完成 P6-E03 几何/强度正式 operating-range 审计和 P6-E10 实测效率。
2. 继续检查 IXI ×2 推理条件；若能完成，立即运行 115 例冻结 x4→x2 收益和预算曲线；若不能，形成精确 blocker 记录。
3. 完成 TMI risk–coverage、densification、误差分类和统计森林图。
4. 更新新颖性审计和两套 reviewer red team。
5. 先写并编译 TMI 18–20 页研究 master，再独立蒸馏合规 submission。
6. 用本轮机制、负结果与方法边界整体重写 CVPR 主文和 supplement，使主文自然达到约 8 页，而不是在旧稿上填充。

## 9. 完成度判断

实验层面，CVPR 的 P0 神经机制问题已经得到实质回答，TMI 的多指标、共识分布和三因子扩展也已完成。论文层面，两篇都尚未达到 Plan6 的最终交付条件：新科学尚未完整写入和编译，TMI master/submission 未生成，CVPR 8 页主文/完整补充未生成，效率、文献、新颖性和红队审查仍有缺口。因此当前状态应标记为“研究证据显著扩展，正式稿重构前”，而非完成。
