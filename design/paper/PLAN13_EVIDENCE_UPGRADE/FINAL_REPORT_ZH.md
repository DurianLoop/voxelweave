# Plan 13：双论文证据审计、补充实验与重建报告

分析与外部核验：2026-09-08；最终交付：2026-09-09。工作范围：`D:\MRI\design\paper`。本轮没有投稿、发送邮件、推送仓库或改动其他正在运行的训练任务。

## 1. 结论与交付

本轮完成了两篇现有稿件的实质修订、四类补充分析、图表重制、参考文献纠错和 LaTeX 重建。最重要的收获不是增加有利数字，而是区分仍稳健的局部误差几何现象与较弱的排序、受益和部署主张。

- **机制核心保留**：在既有 fastMRI/IXI 五架构正式结果上，40 个“队列×模型×汇总口径”局部增益的五模型同时区间全部为正。
- **排序主张收缩**：历史逐模型区间不能解释为五模型联合保证。按既有病例内中位数排名口径，同时区间支持 IXI 的 HAT、SwinIR、SAINT-style；I3Net/CycleINR-style 不再排除零；fastMRI 为 0/5。
- **受益主张收缩**：控制当前 ×4 误差后，fastMRI/NingXia 的 26 个 Anchor-CV 条件关联区间全部跨零。强原始相关不能单独证明其包含超出当前难度的加密价值信息。
- **新增第三队列实验**：恢复并重新评价 IXI I3Net 的 115 对 ×2/×4 输出，使用 7,334 个共同缺失平面，而非直接相减不兼容旧摘要。原始尺度分数与受益相关为正；仅使用已采集锚点的归一化也会使原始尺度受益排名反转，负结果已写入两稿。
- **纠正证据语义**：披露目标掩膜的信息访问、不同倍率的不同权重、MAE/RMSE 定义错误、代数耦合以及 IXI wrapper 只检查一例/模型的真实范围。
- **版面修复**：TMI 从 11 页改为含参考文献 10 页；CVPR 主文 9 页且技术正文不超过 8 页。补充材料为 8 页。未通过压缩正文行距或缩小正文达到页数。

当前版本仍是**可审查的研究候选稿，尚不具备直接投稿条件**。伦理和作者信息、最终投稿顺序、目标年份完整 author kit、方法新颖性与真实采集验证仍需解决。本轮没有估计“接收概率”。

### 文件入口

| 产物 | 路径 |
|---|---|
| CVPR 主文 | [PDF](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.pdf) / [LaTeX](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex) |
| CVPR 补充材料 | [PDF](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/supplement.pdf) / [新增分析源码](../CVPR/CVPR_ARCH_GENERALIZED/PAPER/p13_additional_analysis.tex) |
| TMI 主文 | [PDF](../TMI/TMI_ARCH_GENERALIZED/main.pdf) / [LaTeX](../TMI/TMI_ARCH_GENERALIZED/main.tex) |
| 原始文件保护记录 | [135 文件 manifest](original_manifest.json) / `original_snapshot/` |
| 分析协议 | [PROTOCOL.md](PROTOCOL.md) |
| 原始与结果哈希 | [主分析 manifest](outputs/run_manifest.json) / [IXI 实验 manifest](outputs/ixi_i3net_run_manifest.json) |
| 数值验证 | [verification.json](outputs/verification.json) |
| PDF 构建验证 | [build_audit.json](build_logs/build_audit.json) / `page_renders/` |
| 完整证据路径表 | [CLAIM_EVIDENCE_MAP.md](CLAIM_EVIDENCE_MAP.md) |
| 复现指令 | [RUN_COMMANDS_ZH.md](RUN_COMMANDS_ZH.md) |
| 可审查修改 | [源码差异](outputs/manuscript_changes.diff) / [修改文件哈希](outputs/changed_original_files.json) |
| 本地草稿源码包 | [CVPR](delivery/CVPR_Plan13_DRAFT_sources.zip) / [TMI](delivery/TMI_Plan13_DRAFT_sources.zip)，含依赖图表及当前 PDF，不含原始 MRI 数据 |
| 最终产物清单 | [FINAL_ARTIFACT_MANIFEST.json](FINAL_ARTIFACT_MANIFEST.json)，记录代码、结果、报告、构建日志及源码包哈希 |

## 2. 接管与原始材料审计

完整阅读了仓库根 README、paper README、Plan 12 严格审稿报告、CVPR 主文及补充源码、TMI 主文、现有 bibliography、两稿 claim traceability、CVPR evidence selection，以及 Plan 9/10 总结和 Plan 11 冻结协议。进一步追踪了正式统计表、对应统计和推理脚本，以及用于新实验的 NIfTI/运行 manifest。

Plan 9–12 的 93 个 CSV 均已整表解析并记录路径、SHA-256、行列数和技术试运行标记，见 [historical_csv_inventory.csv](outputs/historical_csv_inventory.csv)。该清单是完整性和来源审计，不意味着每个历史实验都重新运行了模型。对进入本轮主张的结果进行了逐键、逐病例和独立公式复算；对未重跑的历史统计保留其来源和原有局限，不声称已完成全仓库训练复现。

### 2.1 文件保护

修改前复制了两个当前候选包及入口文件，共 135 个原始文件，包括原稿 PDF、LaTeX、图表、样式和审计文本。逐文件 SHA-256 验证通过。当前稿仍在既有 `CVPR_ARCH_GENERALIZED`、`TMI_ARCH_GENERALIZED` 中维护；所有新增代码、分析结果、快照、日志、预览和报告都位于 paper 目录内。

旧 Plan 的正式 CSV 和模型输出没有覆盖；`smoke`、`debug`、`failure_probe` 没有进入本轮正式结论。GPU 已被其他训练进程占用，本轮使用 CPU 完成再分析和已有输出的重评价，没有终止该进程或抢占其训练显存。

### 2.2 发现并修复的证据问题

| 问题 | 原状态及风险 | 本轮处理 |
|---|---|---|
| Plan 路径失效 | 实际 Plan 9–12 已在 `ARCHIVE/PLANS/`，入口说明仍指向顶层 | 更新现行入口与证据映射；历史报告保留当时状态 |
| 旧脚本根目录推算失效 | 归档后 `parents[]` 推算使 ROOT 不再指向 `D:\MRI` | 新实验使用独立、已验证路径；不直接重跑会覆写旧 full 输出的脚本 |
| TMI 11 页 | 官方初投稿上限为含参考文献 10 页 | 去除重复解释/重复 claim 表，重排重建语境表，保留科学负结果 |
| MAE/RMSE 写错 | TMI 文本称以 disagreement RMSE 归一化；代码实际为 disagreement MAE / sqrt(成对 MSE) | 改正文定义并推导带残差形状因子的正确关系 |
| 代数相关被当作机制支持 | 共享比例与归一化分歧共享定义 | 降为描述性分解，独立证据落在控制干预导致的误差几何变化 |
| “不访问目标”过强 | Plan 9/11 和 bank 分数使用 GT 1% mask | 两稿显式披露 privileged support；不把整体流程称为完全 target-free |
| 同模型等于同权重 | ×2/×4 同标签可能来自不同训练 checkpoint | 改为模型身份/同架构配对，明确非固定权重、非纯采集干预 |
| wrapper 范围夸大 | IXI 验证表只有 IXI012 的五行 | 写清 fastMRI 每模型 24 例；IXI 每模型一例 gate |
| 作者/期刊错误 | PMID 42192056 被写成 van der Velde、European Radiology Experimental | 按记录改成 van Lohuizen 等、MAGMA，并补 DOI |

另一个重要限制仍然存在：shared/disjoint 不仅改变物理身份，还可能改变方向、可用上下文及上下文内归一化。reflection-balanced 对照限制了特定几何替代解释，并没有产生“所有混杂都消失”的识别。本轮不将局部关联升级为因果中介。

## 3. E01：架构结果的汇总、多重比较与病例影响

输入是 Plan 9 两份 fastMRI 正式 per-plane 表和 Plan 11 IXI `full` 表。分别有 1,200 行和 5,750 行；每队列均为五模型、每例五目标、两条件。无重复 `(case,model,target_z,condition)` 键，相关数值全部有限，shared+observable 闭合通过。

设每病例每模型效应为 `O_disjoint − O_shared`。保留历史估计：fastMRI 局部效应使用病例内均值、病例间均值；IXI 使用中位数。额外计算四种均值/中位数组合，不跨队列合并。

10,000 次 bootstrap 使用同一病例抽样携带全部五模型；每个队列、端点和汇总口径分别以五模型最大绝对标准化偏差建立近似同时区间。它是 bootstrap 同时区间，不能解释成小样本下的精确覆盖保证；40 个敏感性结果也不是 40 个独立重复试验。

| 队列 | 病例内 / 病例间 | 五模型局部效应范围 | 同时区间全正 |
|---|---|---:|---:|
| fastMRI | mean / mean | .080–.226 | 5/5 |
| fastMRI | mean / median | .078–.224 | 5/5 |
| fastMRI | median / mean | .085–.226 | 5/5 |
| fastMRI | median / median | .089–.227 | 5/5 |
| IXI | mean / mean | .249–.297 | 5/5 |
| IXI | mean / median | .252–.301 | 5/5 |
| IXI | median / mean | .249–.295 | 5/5 |
| IXI | median / median | .252–.302 | 5/5 |

每种口径下每个病例的局部方向也保持正向；逐病例删除结果全部存入 CSV，避免只报告总均值。

### 排序后果没有同等稳健性

下表为历史病例内中位数排名口径对应的同时区间。它与历史 5,000 次逐模型百分位区间有不同推断目标，后者没有删除，也不以本轮替代后掩盖历史结果。

| 队列 | 模型 | 排名 Δρ | 五模型同时 95% 区间 |
|---|---|---:|---:|
| fastMRI | HAT | .057 | [−.103, .216] |
| fastMRI | SwinIR | .062 | [−.145, .269] |
| fastMRI | I3Net | .018 | [−.103, .140] |
| fastMRI | SAINT-style | −.010 | [−.193, .174] |
| fastMRI | CycleINR-style | .342 | [−.115, .798] |
| IXI | HAT | .031 | [.004, .057] |
| IXI | SwinIR | .035 | [.007, .064] |
| IXI | I3Net | .025 | [−.007, .058] |
| IXI | SAINT-style | .032 | [.004, .059] |
| IXI | CycleINR-style | .134 | [−.014, .283] |

用两条件成对误差均值构成共同排序端点，仍得到 IXI 三模型、fastMRI 零模型区间明确为正。该共同端点依然包含干预后的误差，不是固定 phase-0 误差，更不是独立临床终点。此敏感性只说明结果不完全由条件各自误差端点驱动。

完整结果：[architecture_sensitivity.csv](outputs/architecture_sensitivity.csv)、[architecture_leave_one_out.csv](outputs/architecture_leave_one_out.csv)。新图使用长细线表示同时区间、粗线表示历史逐模型区间，避免把两种置信解释混为一谈。

## 4. E02：受益与当前误差的耦合

Plan 11 全部 598 行均保留。复核 `benefit=MAE_x4−MAE_x2`、病例/折/模型/支持集配对和有限值。bank disagreement 对解析插值器的缺失是注册表结构性缺失，未补零，也未扩大分母。74 个原始相关点值全部复现，最大差异为 `2.22×10^-16`。

新问题是：因为 benefit 已包含 `MAE_x4`，一个很会排序当前困难病例的分数能否自然产生强 benefit 相关？本轮对 score、benefit 分别在 `MAE_x4` 的秩上做线性残差化，再求 Pearson，即 partial Spearman；每次 bootstrap 重新排名。用独立最小二乘实现验证了全部 74 个条件相关。

| 队列 | 分数 | 原始模型中位 ρ | 控制 ×4 后中位 partial ρ | 条件区间明确为正 / 模型 |
|---|---|---:|---:|---:|
| fastMRI | Anchor-CV | .851 | .203 | 0/13 |
| fastMRI | Adjacent MAE | .802 | −.068 | 0/13 |
| fastMRI | Bank disagreement | .835 | .056 | 1/11 |
| NingXia | Anchor-CV | .727 | .291 | 0/13 |
| NingXia | Adjacent MAE | .748 | .426 | 1/13 |
| NingXia | Bank disagreement | .710 | .389 | 0/11 |

这些区间跨零并不证明“没有作用”；它说明现有证据不足以支持普遍的额外受益信息。控制量使用真实误差，因此这是回顾性诊断，不能成为新的部署分数，也不是因果效应估计。小样本和接近完美的相关会导致部分 bootstrap 残差退化；有效重复数逐行公开，没有填零制造精度。

### 患者影响与等权敏感性

NingXia 按八患者重采样并完整携带 22 序列。12 个原本正向的 Anchor-CV 模型，在八次 leave-one-patient-out 中仍全部为正。Res-SRDiff 原始 ρ=−.066，逐患者删除范围为 −.274 到 .426，方向不稳定；没有据此删除它。

患者内先取序列中位数、再对八患者等权相关，Anchor-CV 模型中位 ρ=.786；Res-SRDiff 为 −.214。该分析改变了 estimand，因此作为独立敏感性列出，不替换原来序列层点估计/患者簇区间。

完整结果：[benefit_coupling.csv](outputs/benefit_coupling.csv)、[leave-one-cluster-out](outputs/benefit_leave_one_cluster_out.csv)、[patient-equal](outputs/benefit_patient_equal.csv)。

## 5. E03：代数和信息可用性审计

### 5.1 正确关系包含形状因子

令 `T` 为两预测误差平方均值，`q` 为 shared fraction。在同一支持上：

`RMSE(a−b)/sqrt(T) = 2 sqrt(1−q)`。

实际历史脚本使用 MAE，所以正确式子为：

`MAE(a−b)/sqrt(T) = 2 κ sqrt(1−q)`，其中 `κ=MAE(a−b)/RMSE(a−b)`，`0≤κ≤1`。

对 29,296 个历史行复核，带 κ 的分解最大残差为 `1.19×10^-15`；κ 范围 .247–.831。故不能把 MAE 情形错写为无条件的精确 RMSE 等式，也不能把共享比例—归一化分歧相关当成独立机制发现。正文与图注已降为描述性证据；真正需要实验支持的是改变物理上下文后误差几何如何变化。

### 5.2 可用信息应逐项区分

| 量 | 输入值 | 掩膜/尺度来源 | 可以支持的解释 |
|---|---|---|---|
| 原始 Anchor-CV | ×4 已采集锚点，包括被暂时留出的已采集锚点 | 已采集锚点 mask | acquired-only 输入检查 |
| Adjacent MAE | 相邻已采集锚点 | 两锚点 mask 的并集 | acquired-only 输入检查 |
| 旧 scale-normalized Anchor-CV | 输入检查分数 | 旧代码 robust range 来自完整 dense volume | 不能自动称全流程 acquired-only |
| 新 IXI normalized 分数 | 同上 | 只用已采集锚点 1%–99% 范围 | acquired-only 分数，但原尺度受益排名会反转 |
| Plan 9/11 disagreement | 两预测 | GT 1% mask | 目标辅助支持上的回顾性机制评价 |
| Candidate-bank disagreement | 预测库 | `target_0.01` 支持 | 不能未经重评价声称目标完全不可见部署 |
| 旧 clean flip | phase-0、flip 预测 | phase-0 prediction mask | 与上述目标掩膜协议不同，不可统一抹平 |
| shared/observable fraction | 预测及真值误差 | 对应实验支持 | 必须依赖真值的回顾性诊断 |

下一步最有价值的新增推理是：对完整五架构 shared/disjoint 输出使用预先冻结的 acquisition-only mask 重算，报告与 GT mask 的配对差异。现有 Plan 11 没有保存全部 alternate-context 体预测，本轮不能仅凭 per-plane 摘要重算这个实验；需要重新推理或恢复那些体输出。

## 6. E04：IXI I3Net 共同支持新实验

发现 `full_test115_x2_fast` 和 `full_test115_stable` 各有完整 115 个模型输出，前者 ×2、后者 ×4。`full_test115_x2` 没有预测文件；没有把它当成另一个可挑选结果。两个 checkpoint 的 SHA-256 不同：

- ×2：`8c87ac897ebfd7c166cb99f4a7b8922bfc4552be79c242abb39194c3da21c3b8`
- ×4：`48927b521c834f5f6bc26c0b28886d873aae41c0beee5cdbe01c7dec704977f9`

故这是**同架构、不同倍率专用权重**的恢复输出实验；不能宣称模型权重固定，更不能把效应归因全部给额外测量。

对 115 例原始 T2、×2 与 ×4 预测逐一验证 affine 和平面形状，并在共同深度内保留全部奇数 z：这些平面对两倍率都是未采集位置，共 7,334 个。两模型误差使用同一原始目标、同一 1% mask；先平均每例平面 MAE，再按检查 bootstrap。保存 345 个输入文件哈希。旧基准表的 39.26 等数值是另一个支持口径，未被混入本实验或用新数值覆盖。

| 同一共同支持 | ×4 MAE | ×2 MAE | 平均受益 |
|---|---:|---:|---:|
| I3Net | 33.6466 | 25.6206 | 8.0260 |
| Linear | 57.3583 | 39.2054 | 18.1529 |

I3Net 的 115/115 病例受益为正；Linear 的表格仅是同支持解析参照，不把其更大的“改善量”解释为重建模型更好。

| 分数 | 原始尺度受益相关 [95% CI] | 控制当前误差后的相关 [95% CI] |
|---|---:|---:|
| Anchor-CV | .843 [.768,.894] | .216 [.007,.430] |
| Adjacent MAE | .845 [.771,.896] | .227 [.020,.437] |
| Anchor-CV / acquired range | −.238 [−.404,−.058] | .321 [.129,.475] |
| Adjacent MAE / acquired range | −.236 [−.397,−.060] | .319 [.135,.465] |

这里是 10,000 次检查 bootstrap 的逐分数探索性区间；没有做“归一化更差”的因果判断或宣称四分数同时显著。调整前后的差别也反映当前误差、尺度与受益的共同变化。

### 冻结预算的负结果

| 选择预算 | 原始 Anchor-CV oracle-normalized gain | 归一化 Anchor-CV oracle-normalized gain |
|---|---:|---:|
| 10% | .814 | .147 |
| 20% | .713 | −.067 |
| 30% | .835 | −.090 |
| 50% | .824 | −.266 |

50% 预算下，归一化 Anchor-CV 相对随机平均收益为 −.920 MAE 单位，区间 [−1.635,−.149]；归一化 adjacent MAE 为 −.812，[−1.542,−.070]。原始两个分数在全部预算下均高于随机，但没有普遍的 Anchor-CV 最优性。

归一化只改变分数，而终点仍按 raw intensity 定义，是预先声明的尺度敏感性分析。因此它说明原始尺度的预算政策不能随意搬到归一化评分上，不证明同时归一化评分与终点的所有方案都会失败。

完整来源：[IXI per-plane](outputs/ixi_i3net_benefit_per_plane.csv)、[per-case](outputs/ixi_i3net_benefit_per_case.csv)、[geometry](outputs/ixi_i3net_geometry.csv)、[correlations](outputs/ixi_i3net_benefit_correlations.csv)、[budgets](outputs/ixi_i3net_benefit_budgets.csv)。

## 7. 论文与图表具体修改

### CVPR

保留物理依赖、可证伪机制、count-ladder 反例、influence 稳定性失败和 NingXia fixed-count null/mixed 的叙事。增加同时区间和条件 benefit 的边界，将同模型固定改为模型身份配对。新增 IXI 单架构共同支持结果，同时披露目标掩膜。机制总图改为受边界约束的实验链，去掉把独立性写成充分/必要程度规律的标题。

补充材料增加完整 Plan 13 方法和负结果，将不可读的三队列巨型表拆为每队列完整四指标表。旧的 negative-method experiments 仍保留，包括最低 influence 选择器、jackknife IQR、residualization 的失败。

### TMI

重写摘要，纠正 MAE/RMSE 与代数解释。用较易读的全模型 MAE 矩阵替代 5.8 磅大表；完整四指标数据仍存在。缩短重复的讨论、重复的临床建议和重复 claim 表，原始文本均在快照。保留每一类实质负结果，并加入本轮条件关联失败和归一化预算低于随机的结果。正文不把代码/数据归档冒充期刊允许的额外文本补充。

按当前 TMI 规则加入真实的 Codex 使用披露草案，注明需要作者核验，不虚构“作者已审核完毕”。引用中作者超过六位的条目按 TMI 约定显示首位作者等。

### 视觉与构建

新图使用矢量 PDF 和可编辑 Python 源；PNG 只作审查预览。检查并修复图例与数据线重叠。逐页渲染了全部 27 页并检查联系表，重点查看 CVPR 第 7–8 页、补充材料最后的边界图表、TMI 第 6–10 页。未见裁切、文字覆盖、图例遮挡；TMI 最后一页部分空白属于参考文献收尾。

三份最终日志无 undefined reference/citation、LaTeX error 或 overfull box。仍有非致命的 underfull/字体替换等模板信息，未把这些提示写成编译失败。MiKTeX 在沙箱内无法访问现有用户配置；通过工具的自动授权审查使用已安装配置后完成编译和 PDF 渲染，没有重新安装或升级 TeX。

## 8. 外部文献与投稿规则核验

以下为 2026-09-08 实际读取的公开记录，并非沿用 Plan 12 的时间状态。

- [CVPR 2027 官方 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) 已公开，列出注册 2026-11-10、正文 11-16、补充 11-23（AoE）。本轮不能继续写“2027 未公布”。但完整 Author Guidelines 链接未成功取得可用页面；当前 CVPR 2026 style 仅作布局基线，不能声称已经完成 2027 author-kit 合规验证。
- [TMI 官方作者说明](https://ieeetmi.org/authors-instructions/)规定初投稿含参考文献不超过 10 页，且不允许用扩展正文式的补充文档绕过篇幅；会议扩展稿需披露并说明实质扩展。该页面也要求披露 AI 生成内容。本轮处理了页数和披露草案，但作者和伦理依赖仍未解决。
- [van Lohuizen 等，PMID 42192056](https://pubmed.ncbi.nlm.nih.gov/42192056/)纠正了旧作者与期刊错误；真实 DOI 为 `10.1007/s10334-026-01369-0`。其 acquisition perturbation 和方差—误差界限与当前讨论相关。
- [Giannakopoulos 等，2026](https://onlinelibrary.wiley.com/doi/full/10.1002/mrm.70526)及其[作者预印本](https://arxiv.org/abs/2601.13236)已补入两稿，说明校准误差区间方法与本文确定性误差可观测机制的区别，不能把所有不确定性方法笼统描述为只靠分歧。
- [Savant 2026](https://arxiv.org/abs/2605.16476)的现有引用可核验，但属于预印本；它改变 interpolation formulation，本工作固定目标研究物理上下文对误差几何的影响。
- 核对了 [I3Net](https://pubmed.ncbi.nlm.nih.gov/38669167/)、[深集成 MRI](https://pubmed.ncbi.nlm.nih.gov/38282254/)、[Bayesian variational MRI](https://pubmed.ncbi.nlm.nih.gov/34506279/)和 [Hu 等系统误差工作](https://miccai2021.org/openaccess/paperlinks/2021/09/01/280-Paper1009.html)的关键元数据。没有发现这些已核对条目需要同类作者纠错。

这是一轮有目标的一手文献核验，不是系统综述，也不能证明不存在全部相关先行工作。[2026 MRx 工作](https://www.nature.com/articles/s41586-026-10475-x)的 hallucination/uncertainty 附图也是下一轮新颖性边界需要继续细读的邻近工作；本轮没有用它的实验数字扩展自己的证据。

## 9. 尚未解决的投稿风险

### A. 提交前必须由真实资料解除

1. **NingXia 伦理与数据治理**：批准/豁免机构、决定编号、知情同意或豁免、允许用途仍缺失。TMI 的占位符保留，不能从其他论文借伦理编号。CVPR 同样使用内部人类数据，相关说明也需完成。
2. **作者、单位与最终核验**：两稿仍为匿名候选；TMI 最终作者/单位、责任作者、资金及数据可用性承诺需真实填写。AI 披露只是草案，作者应核验产生的文字、代码和图表。
3. **双稿科学重合**：共享三个队列、核心代数、物理对照和架构实验，本轮新统计也共同进入两稿。降低文本相似度不能消除科学重合。仍需合并或先后投稿，并明确哪部分是扩展；不能作为互不相关的研究同时提交。
4. **最终 venue 与模板**：CVPR 2027 CFP 已知，完整 author kit 尚未在本轮取得。当前 PDF 带 2026 review 页眉，仅是可审稿布局候选。投稿前要重建最终年份模板和验证匿名化、补充材料及当届政策。

### B. 主要科学风险

5. **TMI 方法创新门槛**：本工作主要是机制与技术 QA，而非新重建或校准方法。TMI 是否认为其方法论创新足够仍是实质风险，增加相关表不能自动解决。
6. **GT 支持与尺度信息**：多个输出分数的支持掩膜来自目标；旧归一化分数还可能访问 dense range。需要 acquisition-only mask 的完整配对重评价。
7. **物理独立性不等于统计独立性**：相邻脑结构、模型先验、上下文归一化和方向仍共享信息。不能把 disjoint anchors 直接称独立误差。
8. **同架构受益仍含 checkpoint 差异**：新增 IXI 只补了一个架构；13 模型同标签比较也不自动固定权重。尚未识别“仅增加测量”的因果收益。
9. **当前误差耦合及尺度依赖**：26 个 Anchor-CV 条件区间跨零；归一化分数在 IXI raw-benefit 预算中低于随机。任何普遍收益预测/最佳分数主张都应撤回。
10. **样本独立性与试验历史**：NingXia 仅八患者；IXI 虽是独立于 fastMRI 的队列，却已多轮参与研究，不能把本轮再分析称为未接触的独立确认集。
11. **多重比较与 bootstrap 近似**：同时区间按端点/队列构建，不覆盖整个多年所有实验的家庭错误率。模型家族不是额外独立样本；宽区间和退化重采样须保留。
12. **跨解剖和跨模态范围**：五架构 clean 仅覆盖脑 T2；没有膝关节五架构复现，也没有其他模态。既有 NingXia 固定 count null/mixed 仍然有效。
13. **临床与真实采集缺口**：无前瞻扫描、真实 slice profile、运动/时间成本、阅片者实验、病灶或任务标签。MAE/SSIM 不能替代诊断终点，更不能作安全证书。
14. **实现谱系与完整复现**：SAINT/CycleINR 是适配/内部风格实现；IXI wrapper gate 只测一例/模型。本轮没有重训全部基线或重新验证所有训练 split 元数据。历史 manifest 中 train/val counts 缺省也需单独补齐。

## 10. 下一轮建议顺序

先解决伦理和单一投稿主线；接着恢复或重跑五架构 alternate-context 预测，冻结 acquisition-only mask/scale 比较。若只投入一个新科学实验，优先用真实采集约束或明确读者任务检验分歧的技术价值，而不是再增加一种事后融合分数。若资源仅允许离线计算，则补齐 IXI 多架构 ×2 配对及固定权重/固定 checkpoint 的可比实验，同时保留 current-error adjustment 与尺度反例。

本轮已经把可以靠本地证据、工程实现和编辑解决的问题具体完成；缺少的伦理、作者元数据和临床材料没有代填。重建成功不等于投稿风险解除。
