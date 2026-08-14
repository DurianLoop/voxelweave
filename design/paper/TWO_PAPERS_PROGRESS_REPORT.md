# MRI 层间插值两篇论文进展报告

更新日期：2026-08-13  
项目目录：`D:\MRI\design\paper`

## 1. 总体状态

当前形成两条相互隔离的论文线：

| 论文线 | 目标 | 当前状态 | 证据边界 | 已编译稿件 |
|---|---|---|---|---|
| TMI | IEEE Transactions on Medical Imaging Regular Paper | 完整研究稿已生成并审计；等待人工元数据和伦理信息 | 严格冻结为 Plan 1--4，未加入后续 CVPR 实验 | `TMI/TMI_MANUSCRIPT/main.pdf`，6 页，323,766 bytes |
| CVPR | CVPR 会议论文 | 科研门槛已达到，匿名审稿稿和补充材料已生成并审计 | Plan 5 及后续独立探索，包括新增 IXI、Anchor-CV 和共享影响机制 | `CVPR/CVPR_UPGRADE/PAPER/main.pdf`，6 页，307,306 bytes |

两篇论文均已完成 LaTeX 编译、日志检查和逐页视觉审阅。最终版本无 overfull box、未定义引用、致命 LaTeX 错误或图表剪裁。目前均为研究产物，尚未执行任何投稿。

---

## 2. TMI 论文进展

### 2.1 论文信息

暂定标题：

> Measurement Overlap Governs Disagreement-Based Reliability in Deterministic MRI Slice Interpolation

核心定位是确定性 MRI 层间插值中的“共识盲区”：两个重建结果即使高度一致，也可能因为复用了相同的误差来源而同时出错。论文重点不是提出新的重建主干网络，而是研究测量重叠如何影响分歧信号的可靠性。

主文件：

- `TMI/TMI_MANUSCRIPT/main.tex`
- `TMI/TMI_MANUSCRIPT/main.pdf`
- `TMI/TMI_MANUSCRIPT/TMI_COMPLIANCE_CHECK.md`
- `TMI/TMI_MANUSCRIPT/CLAIM_TRACEABILITY.md`

### 2.2 冻结证据范围

TMI 仅使用 Plan 1--4 已冻结证据：

- fastMRI brain T2：24 个独立测试病例；
- NingXia knee T2：8 个患者、22 个序列，统计推断按患者聚类；
- HAT 和 SwinIR 两类冻结插值器；
- 线性和三次插值作为非神经模型族检查；
- IXI 115 例只用于冻结的辅助难度分析，不进入核心 overlap 干预；
- 密集切片只用于回顾性相位网格模拟和误差评估，不进入部署时可靠性分数。

后续 Plan 5+ 的 IXI overlap、clean flip、五级 ladder、Anchor-CV 和共享影响实验均未写入 TMI。这一边界用于避免事后强化期刊主张和两条论文线之间的证据污染。

### 2.3 核心研究结果

1. 分歧只观察两个误差的差值，不能观察二者共有的共模误差。论文给出误差均值项与误差差分项的精确能量分解。
2. 在同一物理目标上，零锚点重叠的相位网格比最大共享锚点的反序控制更能排序真实重建误差：
   - fastMRI：Spearman 差值 `0.355`，病例聚类 95% CI `[0.225, 0.557]`；
   - NingXia：差值 `0.193`，患者聚类 95% CI `[0.113, 0.336]`。
3. HAT、SwinIR、线性插值和三次插值均给出方向一致的模型族证据。
4. 解耦上下文的分歧能够回顾性预测从 x4 加密到 x2 的重建收益：总体关联约 `rho=0.811`。
5. 在预设 25% 加密预算下，分数排序选择优于随机选择并接近 oracle，但该结果仅属于回顾性方法学验证。
6. 负结果被保留：NingXia 校正后没有充分证据支持 PC 一定优于 TTA；曲率难度不能稳定跨队列迁移；低分歧不能作为正确性证明。

### 2.4 已完成的文章丰富工作

在不改变任何冻结数值的前提下，文章增加或强化了：

- 共模误差与反向误差两个理论极限；
- diversity、observability 和 calibration 三个概念的区别；
- NingXia 患者层级重采样的统计解释；
- MRI 物理切片锚点与普通数据增强之间的区别；
- 回顾性加密结果的实际含义和前瞻性限制；
- IXI 仅为辅助证据、不是核心干预复现的明确说明。

### 2.5 稿件与格式状态

- 6 页，IEEEtran 10 pt、双栏、US Letter；
- 摘要约 220 词，符合当前审计标准；
- 5 张图、2 张表；
- 字体已嵌入；
- 所有 6 页均已视觉检查；
- 参考文献位于第 6 页；
- 未使用补充材料规避正文限制。

### 2.6 TMI 尚未解决事项

- 作者姓名、单位、通讯作者和 ORCID；
- 基金与致谢；
- NingXia 伦理审批或豁免机构、编号、知情同意或豁免措辞；
- fastMRI、IXI 的最终伦理及数据使用措辞；
- 匿名代码或最终代码仓库 URL；
- 内部数据的共享限制；
- IEEE 要求下适用的生成式 AI 使用披露。

因此，TMI 当前是“研究稿完整、机械合规通过，但尚不可直接上传投稿”的状态。

---

## 3. CVPR 论文进展

### 3.1 论文信息

暂定标题：

> From Measurement Overlap to Shared Influence: Reliable Context Design for MRI Slice Interpolation

CVPR 论文从 TMI 的共识盲区观察出发，但将研究推进到“机制变量和部署方法”层面。核心新增内容是：用精确 ladder 否定简单 overlap-count 定律，再以 estimator coefficient 的共享影响解释误差对齐，最后导出不需要 x8 模型和额外采集的 acquired-anchor cross-validation 方法。

主文件：

- `CVPR/CVPR_UPGRADE/PAPER/main.tex`
- `CVPR/CVPR_UPGRADE/PAPER/main.pdf`
- `CVPR/CVPR_UPGRADE/PAPER/supplement.tex`
- `CVPR/CVPR_UPGRADE/PAPER/supplement.pdf`
- `CVPR/CVPR_UPGRADE/PAPER/CVPR_COMPLIANCE_CHECK.md`
- `CVPR/CVPR_UPGRADE/PAPER/CLAIM_TRACEABILITY.md`

### 3.2 CVPR 科研门槛

最终审计评分：

| 维度 | 评分 |
|---|---:|
| 新颖性 | 4/5 |
| 重要性 | 4/5 |
| 机制深度 | 5/5 |
| 实验严谨性 | 4/5 |
| 审稿韧性 | 4/5 |

总门槛由早期的 `4/4/4/4/3` 提升为 `4/4/5/4/4`，已经满足生成 CVPR 完整论文的内部标准。

### 3.3 新增队列与实验

CVPR 分支新增 IXI brain T2 115 个独立检查，并完成 C5-E011--E014：

#### C5-E011：Acquired-Anchor Cross-Validation（Anchor-CV）

对每个内部 x4 已采集锚点执行留一法：用相邻两个已采集锚点线性重建被留出的锚点，再以真实已采集切片计算残差。该方法：

- 不使用密集目标作为分数输入；
- 不需要额外 phase grid；
- 不需要训练新模型；
- 不调用 x4 模型执行 stride-8 域外推理；
- 适合作为 examination-level triage，而不是像素或切片级不确定性图。

Anchor-CV 与 x4 重建误差的 Spearman 相关性：

| 队列 | 独立单位 | rho | 95% CI |
|---|---:|---:|---:|
| fastMRI | 24 examinations | 0.937 | [0.816, 0.975] |
| IXI | 115 examinations | 0.955 | [0.926, 0.972] |
| NingXia | 8 patients / 22 series | 0.955 | [0.747, 0.980] |

与 x4→x2 回顾性加密收益的相关性为 fastMRI `0.799`、NingXia `0.615`。IXI 没有冻结的 x2 输出，因此该终点为 `NOT RUN`。

#### C5-E012/C5-E013：精确五级 overlap ladder

四锚点分析固定目标、锚点数量、绝对距离集合、估计器、掩膜和预处理，仅改变物理锚点共享关系。wide ladder 使用距离 `{2,4,6,8}`，compact ladder 使用 `{1,2,3,4}`。

主要发现：

- overlap 总体趋势在三个队列中方向一致；
- 但 compact ladder 的 `0→1` 级在三个队列中均违反严格单调性；
- IXI wide ladder 也复现该例外；
- 因此“共享锚点越多，可靠性一定逐级下降”的整数计数定律被否定。

#### C5-E014：Shared Influence Mechanism

将两个局部估计器写成物理锚点联合位置上的系数向量，并计算 coefficient cosine、signed dot product 和 common absolute coefficient mass。

common absolute mass 与 error cosine 的相关性为：

- fastMRI：`0.815`，而 overlap count 为 `0.503`；
- IXI：`0.789`，而 overlap count 为 `0.466`；
- NingXia：`0.855`，而 overlap count 为 `0.630`。

在全部四个机制终点和三个队列上，coefficient cosine 相对 overlap count 的绝对相关优势，其聚类 95% CI 均大于零，优势范围约 `0.189–0.283`。因此更准确的结论是“减少共享测量影响”，而不是机械地最小化共享锚点数量。

### 3.4 加密预算结果

完整评估了 10%、20%、30%、50% 四个预算点，并保留 random、oracle、PC、TTA、committee、adjacent-anchor difficulty、analytical bipartition 和 extra-grid phase score 等比较方法。

Anchor-CV 占 oracle-over-random 可实现增益的比例：

| 队列 | 10% | 20% | 30% | 50% |
|---|---:|---:|---:|---:|
| fastMRI | 0.998 | 1.000 | 0.876 | 0.933 |
| NingXia | 0.566* | 0.801 | 0.831 | 0.711 |

`*` NingXia 10% 预算的聚类增益区间跨越零。论文没有宣称该策略在所有队列和预算下都优于全部基线。

### 3.5 明确保留的负结果与边界

- fastMRI 的 Anchor-CV 层内局部定位中位 rho 为 `-0.264`，所以方法只定位为 examination-level triage；
- wide ladder 因体积深度不足不能覆盖 fastMRI，compact ladder 是按覆盖条件注册的复现实验；
- NingXia 只有 8 个独立患者，区间仍较宽；
- NingXia 10% 预算不显著；
- IXI 没有 x2 benefit 终点；
- 四锚点 shared-influence 是分析型、估计器相关的机制，尚不能证明深度非线性网络具有完全相同的显式系数；
- 没有前瞻性扫描、临床安全、校准不确定性或自动重采集决策证据。

### 3.6 稿件与格式状态

- 使用当前可获得的官方 CVPR 2026 author kit；
- 匿名 review 模式，paper ID 为占位符；
- 6 页总长，正文在第 5 页结束，参考文献分布于第 5--6 页；
- 5 张图、3 张表；
- 另有独立可编译的 1 页补充材料；
- 主稿和补充材料均编译成功；
- 所有 6 页均已视觉检查，无图表剪裁或栏布局错误。

### 3.7 CVPR 尚未解决事项

- 确定实际投稿年份，并在官方目标年份模板发布后刷新 style；
- 填写 paper ID；
- 完成作者 OpenReview profile；
- 确定匿名代码仓库策略；
- 核实 NingXia 伦理/同意和 fastMRI/IXI 数据使用措辞；
- 完成适用的 AI 使用披露；
- 根据实际投稿年份重新核查双投稿、预印本和先前发表规则。

---

## 4. 两篇论文的关系与差异

| 比较项 | TMI | CVPR |
|---|---|---|
| 核心问题 | 为什么确定性重建之间的一致性会漏掉错误 | 如何从 overlap 观察推进到更准确的共享影响机制和可部署分数 |
| 主证据 | Plan 1--4 冻结的零/最大 overlap、模型族、回顾性加密 | clean control、IXI、五级 ladder、shared influence、Anchor-CV、全预算曲线 |
| 方法贡献 | 可靠性设计原则与 phase-grid disjoint score | 无 x8 推理、无额外采集的 Anchor-CV examination score |
| 机制深度 | 共模误差和可观察误差能量分解 | overlap-count 定律的否定及 estimator coefficient influence 精炼 |
| IXI 作用 | 仅冻结的辅助难度分析 | 115 例核心机制和方法外部队列 |
| 当前篇幅 | 6 页 TMI 双栏 | 6 页 CVPR review 双栏，加 1 页 supplement |

CVPR 已经形成比初始分支更明确的独立贡献，但仍与 TMI 共享“测量重叠导致共识盲区”的发现和部分实验逻辑，不能据此自动认定两篇论文可以同时投稿。

---

## 5. 投稿风险与策略

当前标记：`SUBMISSION_CONFLICT_RISK`。

两篇稿件不应在未经规则核查和作者决策的情况下同时送审。投稿前需要：

1. 明确两篇稿件是否已有预印本、投稿、拒稿或在审状态；
2. 选择投稿顺序和优先目标；
3. 按目标年份政策量化文字、图表、实验和贡献重叠；
4. 若 TMI 先行，确认 CVPR 是否构成充分扩展，并按规则披露和引用前作；
5. 若重叠仍不符合规则，合并稿件或推迟其中一篇；
6. 在实际提交日重新检查 IEEE TMI 与 CVPR 的双投稿、先前发表和预印本政策。

该风险属于投稿治理问题，不影响当前两条研究线已经形成可编译完整稿件的事实。

---

## 6. 建议的下一步优先级

### P0：投稿前必须完成

- 补全 NingXia 伦理审批、知情同意/豁免和内部数据使用信息；
- 补全作者、单位、基金、ORCID 和通讯作者信息；
- 决定 TMI/CVPR 投稿顺序并完成正式重叠审计；
- 准备匿名及最终代码仓库；
- 核查两目标期刊/会议的 AI 使用披露要求。

### P1：提升审稿韧性

- 为 CVPR 增加非线性网络的 influence approximation 或可解释 Jacobian/attribution 验证；
- 获取独立的 IXI x2 或其他真实加密收益终点；
- 在新患者队列上锁定 Anchor-CV 阈值和预算策略；
- 如条件允许，设计前瞻性 acquisition/cost pilot。

### P2：文稿完善

- 根据作者选择，将 TMI 扩展至更完整的期刊篇幅或保持当前紧凑稿；
- 在目标年份 CVPR author kit 发布后重新编译和逐页审计；
- 完成匿名补充材料中的完整配置表、聚类区间和运行清单；
- 统一术语：measurement overlap、shared influence、observable error、Anchor-CV 和 examination triage。

---

## 7. 结论

TMI 论文已经形成一个证据冻结、边界清晰的期刊研究稿，系统论证确定性 MRI 插值中的共识盲区及 measurement-overlap 设计原则。CVPR 论文则完成了从现象到机制再到方法的推进：严格计数定律被实验否定，共享系数影响成为更准确的解释变量，Anchor-CV 解决了此前 stride-8 域外推理和额外采集的部署问题。

当前两篇论文的科研内容、LaTeX 稿件、图表、追溯记录和格式审计均已完成到可供作者内部定稿的程度。剩余关键工作主要是人工伦理/作者元数据、代码发布安排和两篇文章的投稿顺序与重叠政策决策。
