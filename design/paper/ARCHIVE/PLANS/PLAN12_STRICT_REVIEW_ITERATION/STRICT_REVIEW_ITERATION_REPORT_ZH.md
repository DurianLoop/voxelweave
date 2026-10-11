# 两篇稿件严格审稿迭代报告

日期：2026-09-06  
范围：CVPR 机制稿与 TMI 医学 QA 稿  
原则：按预先定义的纳入规则保留所有合格结果；主文与补充材料按证据强度和叙事相关性分层，不按结果正负筛选。

## 1. 本轮结论

两篇稿件均完成了新一轮“拒稿优先”的重写、复编译和视觉检查。本轮新增两条互补证据：115 例 IXI 上五架构 clean shared/disjoint 独立复现，以及 matched-geometry identity-swap；此前完成的同模型 $\times4\!\rightarrow\!\times2$ 受益预测继续作为回顾性实用性证据。

当前版本比上一版更难被以下理由直接否定：

- 不再把 disagreement 写成校准不确定性；
- 不再把 anchor count 写成单调因果规律；
- 不再用跨模型比较替代同模型受益证据；
- 不把内部适配的 SAINT/CycleINR 写成官方精确复现；
- 不将小样本 NingXia 与大样本 fastMRI/IXI 粗暴合并以制造精度；
- 对不利的 Res-SRDiff、固定计数失败、结构端点异质性和架构排序异质性均保留并限制 claim。

两篇 PDF 均可稳定构建，但尚不能诚实地宣称“接收概率超过 80%”。接收率不是可由本地实验确定的量，而且仍存在伦理占位符、双稿重叠策略、目标年份模板/政策、临床端点缺失等硬风险。

## 2. 新增并写入稿件的核心证据

### 2.1 IXI 五架构 clean shared/disjoint 独立复现

正式队列覆盖 HAT、SwinIR、I3Net、SAINT-style 和 CycleINR-style，使用 115 例、每例 5 个冻结目标、5,000 次 examination-bootstrap。完整 clean 表有 5,750 行，无重复键或非有限值；五个 phase-0 wrapper 的复现误差均为零。

| 模型 | Observable gain 中位数 [95% CI] | Ranking Δρ [95% CI] | 正方向病例 |
|---|---:|---:|---:|
| HAT | .290 [.286,.296] | .031 [.016,.053] | 115/115 |
| SwinIR | .302 [.295,.307] | .035 [.019,.059] | 115/115 |
| I3Net | .252 [.244,.260] | .025 [.008,.053] | 115/115 |
| SAINT-style | .298 [.292,.305] | .032 [.017,.055] | 115/115 |
| CycleINR-style | .296 [.291,.300] | .134 [.058,.258] | 115/115 |

这组结果显著强化“局部 observable-error geometry 跨架构复现”的 claim，但不能被写成跨队列统一效应：fastMRI 汇总使用均值、IXI 使用中位数。排序后果也必须保留队列异质性——IXI 五个区间均为正，而 fastMRI 仅 CycleINR 明确为正。

### 2.2 Matched-geometry identity-swap

该对照固定最近锚点距离多重集 `{1,3}`，分别统计 residue 1/3 并等权。五模型 reflection-balanced gain 为 .251--.300，区间全部高于零；mirror difference 的五个区间全部跨零，冻结 orientation-warning 数为 0/5。数据表包含 2,875 个 residue-specific 行和 575 个 balanced model--case 行。

严格边界是“左右反射等价几何”，不是 signed geometry 完全相同。它降低了 residue 构成差异这一替代解释，但不能被描述为完全消除了所有几何混杂。

### 2.3 同模型 $\times4\!\rightarrow\!\times2$ 受益预测

冻结定义：在同一重建模型、同一病例和共同可比支持上，受益定义为 $\mathrm{MAE}_{\times4}-\mathrm{MAE}_{\times2}$。分析覆盖 598 个合格的 dataset--case--model 行、13 个模型，并采用 5,000 次病例/患者簇 bootstrap。

| 数据集 | 检查分数 | 正方向/合格模型 | 模型内 Spearman 中位数 |
|---|---:|---:|---:|
| fastMRI | Anchor-CV | 13/13 | 0.851 |
| fastMRI | Adjacent-anchor MAE | 13/13 | 0.802 |
| fastMRI | Candidate-bank disagreement | 11/11 | 0.835 |
| NingXia | Anchor-CV | 12/13 | 0.727 |
| NingXia | Adjacent-anchor MAE | 12/13 | 0.748 |
| NingXia | Candidate-bank disagreement | 10/11 | 0.710 |

严格解释：Anchor-CV 在大多数已评估模型中与回顾性加密受益正相关，但并非唯一或普遍最优分数。NingXia 上 adjacent-anchor MAE 的中位相关更高，因此稿件只主张“低成本、acquired-only 的候选检查信号”，不主张其普适优越性。

### 2.4 主动保留的不利边界

NingXia 的 degraded Res-SRDiff 是三个分数共同的非正方向例外：Anchor-CV $\rho=-.066$，adjacent MAE $\rho=-.051$，bank disagreement $\rho=-.242$；三个患者簇 bootstrap 区间均跨零。该例外已在图、正文、补充材料与限制中明确保留。

这样处理的好处不是“削弱贡献”，而是把贡献从脆弱的普适规律收缩为更可信的局部机制：物理证据依赖会掩盖共同误差；其可操作价值需要按模型、数据集和端点验证。

### 2.5 新图

新增/更新两张核心图：

- `fig_architecture_replication`：并列展示 fastMRI clean、IXI clean、IXI reflection-balanced 的 observable gain，以及两脑队列的 ranking consequence；
- 明确注记 fastMRI 均值与 IXI 中位数不做跨队列合并；
- `fig_same_model_consequence`：

- 面板 a：fastMRI 各模型的模型内 Spearman 点与中位数；
- 面板 b：NingXia 对应结果，红叉明确标出非正方向；
- 面板 c：10/20/30/50% 回顾性选择预算下的模型中位 oracle-normalized gain，阴影为模型 IQR 而非置信区间。

图中没有把某个方法标成 “ours”，也没有人为指定胜者。

## 3. CVPR 稿件的修改

### 3.1 Claim 重构

摘要、贡献、结果、讨论和结论统一为三层证据：

1. 三队列的 target-preserving shared/disjoint 对照支持物理依赖与共同误差盲区；
2. 五架构在 fastMRI 与 IXI 两个独立脑队列上均支持局部机制，但排序提升存在队列异质性；
3. 同模型 $\times4\!\rightarrow\!\times2$ 审计只支持回顾性优先级排序，不支持校准、自动重采集或临床安全。

所有 “preregistered” 改为 “prospectively frozen”，避免把本地事先冻结协议误写成公开注册研究。

### 3.2 版面与构建

- 主文：9 页总计，技术正文结束于第 8 页，参考文献位于第 9 页；
- 补充材料：6 页；
- 主文与补充材料最终日志均无 undefined reference、undefined citation、LaTeX error 或 overfull box；
- 第 7 页的双队列架构图与同模型后果图已渲染检查；
- 第 8 页完整包含 Discussion 与 Conclusion；由于 review 模板在参考文献前清栏，末页两栏密度不完全对称，但不存在裁切或正文超页。

CVPR 补充材料不含参考文献，因此其正确构建流程只需要 `pdflatex`；对 supplement 运行 BibTeX 所产生的无引用错误不属于最终构建错误。

## 4. TMI 稿件的修改

TMI 版本保留更完整的医学技术 QA 叙事，并把 IXI 五架构正式复现、reflection-balanced identity-swap 和同模型分析写入摘要、贡献、方法、结果、限制、可复现性边界、claim table 与结论。原先容易被批评为模型身份混杂的跨估计器后果，降级为历史敏感性证据。

构建结果：

- 主文 11 页总计；论文文字与 claim table 在第 10 页结束，参考文献续至第 11 页；
- 最终日志无 undefined reference、undefined citation、LaTeX error 或 overfull box；
- 仅有不影响输出的 underfull box 提示；
- 第 8 页双队列架构图、第 9 页 operating-regime 表与局限性、第 10 页 claim table/伦理占位符/结论均已视觉检查，无裁切或越界。

## 5. 作为严格审稿人仍会提出的拒稿风险

### 5.1 立即阻断提交的问题

1. **NingXia 伦理信息未完成。** TMI 仍含批准/豁免机构、决定编号、知情同意或豁免、允许用途的作者占位符。这个问题不解决，稿件不具备提交条件。
2. **两稿共享数据与核心机制。** 不能把它们作为两篇相互独立且同时在审的工作提交。必须先选择投稿顺序，并对扩展关系、文本/图表/实验重叠进行披露和量化。
3. **目标 venue 未锁定。** CVPR 分支仍以 2026 review style 作为排版基线；必须按真实目标年份 author kit 和政策重建。

### 5.2 主要科学风险

- 所有实验均为 T2 MRI，跨模态泛化没有证据；
- 全部稀疏采样来自致密体数据的回顾性模拟，无前瞻扫描；
- NingXia 只有 8 个独立患者簇，置信区间宽；
- IXI 尚无广泛的同模型 $\times2$ 矩阵；
- 无阅片者研究、病理分层、扫描时间/运动/成本模型和诊断终点；
- 五架构扩展中只有 SAINT 通过全部新的 influence-stability gate；
- I3Net/CycleINR 支持物理依赖现象，但不足以支持稳定有限响应 influence 的普遍 claim。

## 6. 接收率判断

本轮不提供虚假的“80%+”数值。严格评估应拆成可检查维度：

| 维度 | 当前判断 | 主要原因 |
|---|---|---|
| 机制清晰度 | 强 | 对照干预、代数分解和多架构证据形成闭环 |
| 实验透明度 | 强 | 有利与不利合格结果均保留，claim 与证据层级一致 |
| 外部有效性 | 中等偏弱 | 单模态、NingXia 小样本、缺少 IXI 同模型矩阵 |
| 临床有效性 | 弱 | 无前瞻采集、读者研究或诊断终点 |
| 可复现性 | 中等 | 有脚本、manifest、病例级表；内部数据和适配实现仍需清晰披露 |
| 投稿合规性 | 当前不合格 | 伦理占位符、双稿重叠策略、目标模板/政策未完成 |

因此，当前状态是“科学叙事明显增强、编译与表图合格，但不具备可辩护的 80% 接收保证，也尚未达到立即投稿状态”。

## 7. 下一轮最值得投入的工作

按对审稿风险的预期影响排序：

1. 补齐 NingXia 伦理与允许用途文本，并由作者核验真实性；
2. 选择单一近期投稿主线：优先提交 CVPR 机制稿，或合并为 TMI 完整稿；避免并行独立投稿；
3. 补齐 IXI 同模型 $\times4\!\rightarrow\!\times2$ 矩阵，使实用性证据覆盖第三数据集；
4. 若资源允许，在 NingXia 或另一膝关节队列复现五架构 clean 对照，补足跨解剖架构证据；
5. 增加前瞻性或模拟真实采集约束的成本敏感实验；
6. 对 2026 新文献、目标 venue author kit 和双重投稿政策做外部核验；
7. 投稿前运行一次独立的 claim--table--artifact 数值一致性检查和匿名化检查。

## 8. 关键产物

- CVPR 主文：`design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex`
- CVPR 主文 PDF：`design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf`
- CVPR 补充材料：`design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.tex`
- TMI 主文：`design/paper/TMI/TMI_ARCH_GENERALIZED/main.tex`
- TMI 主文 PDF：`design/paper/TMI/TMI_ARCH_GENERALIZED/main.pdf`
- 新图生成脚本：`design/paper/PLAN12_STRICT_REVIEW_ITERATION/scripts/build_same_model_consequence_figure.py`
- 新图：`design/paper/PLAN12_STRICT_REVIEW_ITERATION/fig_same_model_consequence.pdf`
- 双队列架构图脚本：`design/paper/PLAN12_STRICT_REVIEW_ITERATION/scripts/build_architecture_replication_figure.py`
- 双队列架构图：`design/paper/PLAN12_STRICT_REVIEW_ITERATION/fig_architecture_replication.pdf`
- IXI 正式运行状态与数值表：`design/paper/PLAN12_STRICT_REVIEW_ITERATION/P11_IXI_FULL_RUN_STATUS_ZH.md`
- 冻结同模型结果：`design/paper/PLAN11_CLAIM_STRENGTHENING/outputs/p11_same_model_benefit_*`
- 冻结 IXI 五架构/identity-swap 结果：`design/paper/PLAN11_CLAIM_STRENGTHENING/outputs/p11_ixi_clean_*_full.*` 与 `p11_identity_swap_*_full.*`

## 9. 可复核的最终判断

本轮已经实现的是：用第二个 115 例脑队列完成五架构独立复现，以反射平衡的 identity-swap 缩小几何替代解释，并结合同模型后果分析、负面边界和证据分层，提高两篇稿件的可信度与可审性。

本轮没有、也不能诚实实现的是：通过只挑有利结果来制造贡献，或保证某个接收概率。IXI 正式实验已完成；当前最有效的继续提升路径是先解除伦理与投稿重叠硬阻断，再补第三解剖部位的架构复现、IXI 同模型 $\times2$ 和更接近真实采集的验证。
