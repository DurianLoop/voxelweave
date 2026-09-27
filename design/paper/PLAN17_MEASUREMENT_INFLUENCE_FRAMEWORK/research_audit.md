# Research provenance audit — Plan 17

本审计先于本轮新实验及主稿修改完成。范围是当前 CVPR 的全部可发现历史证据，而不是声称已经重训全仓库模型。机器台账见 [research_ledger.json](research_ledger.json)，索引记录文件内容哈希、行号、规则、CSV schema、split、checkpoint 与训练配置。未记录的历史尝试和不可证实的先后顺序明确为未知，不补造记录。

## 证据范围和时间顺序

检索得到 1,623 个论文科学来源文件、832 个 CSV、7,714 条规则证据行；另收录工作区 64 个 split 文件、1,336 个 checkpoint 候选和 655 个训练配置。候选 checkpoint 不等于被论文使用：五架构 × 两脑队列的十个主要 checkpoint 另行逐一绑定源码、预测路径并计算 SHA-256。历史模型库和 111 配置的来源仍沿用 Plan 15 全量核验及本轮配置台账，不把无法唯一确定的训练快照冒充已确认使用的权重。

Git 中只有 2026-08-14 的一个 paper 历史快照，它同时包含 Plan 9 协议和结果；找不到能独立证明协议先于结果的提交序列。后续协议的日期文字、mtime 和运行 manifest 可定位记录，但日期可编辑，不能单独证成预注册。Plan 14 的协议版本哈希支持具体运行绑定，仍不是第三方注册。

历史可恢复的顺序为：Plans 2–8 对已知测试集探索 → Plan 9 架构扩展与 smoke 后控制修订 → Plan 10 模型库探索 → Plan 11/12 扩展 IXI 与受益审计 → Plan 13 多重比较／量纲／当前误差诊断 → Plan 14 TopCoW、事后亮区假设、CAS 迁移 → Plan 15 baseline 恢复 → Plan 16 图稿。完整事件和证据文件在台账中。

**当前重构本身也是事后科学整理。** Plan 9 原先将 ranking contrast 指定为 primary，后来主线转向更稳健的局部 observable gain。不能把这一结果层级调整描述成从一开始就预先指定的成功。

## 需要弱化或纠正的文字

| 旧表述／定义 | 审计决定 |
|---|---|
| prospectively frozen、prespecified、preregistered | 当前论文去掉对分析先后顺序的强断言；写 documented / retrospective / exploratory。frozen estimator 只指不再训练权重，可保留。 |
| rule-frozen | 改为 fixed-rule retrospective；不暗示规则从未参考既有结果。 |
| held-out | 只允许表示与重建模型训练／选择集的划分关系；明确这些数据已反复用于可靠性分析，不能称新分析的 untouched holdout。 |
| independent IXI replication | 改为 distinct-cohort replication；IXI 早已用于 HAT/SwinIR 和 24 例新架构影响分析，不是全新的分析确认集。 |
| neural influence = mean response cosine | **错误。** 实际为共享锚点响应内积之和除以双方全部锚点响应能量的几何均值。Plan 6 与 Plan 9 实现一致；新框架和理论按真实公式写。 |
| disjoint control fixes all geometry | 只能固定同目标及规定的几何属性；最近距离最多反射等价，完整上下文和相位归一化可变，不能宣称纯粹识别所有物理因素。 |

逐处文字清单见 `outputs/manuscript_provenance_phrases.json`；原稿保存在 `original_snapshot`。

## 信息访问、选择和统计

- fastMRI 原始 split 为 112/24/24 序列、111/24/24 患者；一患者跨 train/val，test 与二者 ID 无交集。IXI 为 404/58/115，三个集合 ID 无交集。NingXia 八个患者 fold 逐一核对；病例／患者对应限于本地标识，不额外推断跨数据集身份。
- Plan 9/11 使用目标 1% 掩膜。HAT/SwinIR 与新架构影响探针使用完整致密检查的 min/max，含目标信息。因此它们是回顾性机制测量，不能整体称 target-free。新输入分数必须重新限定掩膜和尺度来源。
- Plan 14 已证明模型库 `target_0.01` 是目标模型预测掩膜，不能再次误写成 GT mask。原生全平面 baseline 与共同支撑 QA 不混算。
- Plan 9 stable-wrong 的 error Q75 / disagreement Q25 来自被报告的 shared 测试平面；Plan 8 则使用 zero-overlap 阈值。这是不同的描述性患病率定义，不能合并或冒充外部验证的检测阈值。
- 反转控制 smoke 是在观察一例 I3Net/SAINT 的不利响应之后修改。其构念理由合理，但仍是 outcome-informed 协议修订；原输出必须保留。
- I3Net/CycleINR 的幅度稳定性失败、NingXia fixed-count 失败、context selection／jackknife／residualization 三类方法失败、Res-SRDiff 退化、CAS 一般误差排名损失均保留；更换章节位置不等于排除实验。
- 所有排序和局部效应以 examination/patient 为独立单位；slice/context 重复测量完整随簇重采样。历史逐项区间按 pointwise 标明；Plan 13 五架构 simultaneous interval 不追认整个历史研究的多重检验控制。
- 历史阈值、幅度、模型和上下文是否曾进行未记录的额外搜索无法排除。台账提供可发现尝试全清单；不能据此宣称不存在选择偏倚。

## 新实验资格与停止边界

GPU 正被其他训练占用，本轮用 CPU 与既有预测。OAI-prepared 是 label-like 数据，MRNet 缺少可靠 patient linkage；TopCoW、CAS、fastMRI、IXI 和 NingXia 的既有结果均已看过。本轮可做按训练部分估计阈值的有限开发／转移审计，但**没有可认证的全新未触及队列**。Q4 的“真正 held-out 可行动优越性”若无法证明，则保持开放，不靠持续调分数获得阳性。

不做牵强的非 MRI 实验。局部线性随机扰动数值检查只验证新命题计算，不记成自然图像跨域实证。

## 文献边界核对

共同偏差不被输出变异反映已有先例：[Hu, Pezzotti, Welling, MICCAI 2021](https://miccai2021.org/openaccess/paperlinks/2021/09/01/280-Paper1009.html)。因此新增命题不宣称发明误差分解，而是将物理共享协方差和局部敏感性接到可执行审计。

[Deep Ensembles, NeurIPS 2017](https://papers.nips.cc/paper_files/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html) 研究的是训练集成预测不确定性；本轮二模型方差和确定性 TTA 对照不能冒充对该完整方法或全部 Bayesian uncertainty 的反证。

结论：现有证据允许重构一个有边界的机制／审计框架；不允许升级为预注册、无泄漏的普适可靠性方法。此审计完成后才开展本轮限定实验。

## 最终源码复核补记（事后完整性检查）

上文“以 examination/patient 为独立单位”指重采样单位，不能将所有历史点估计改称病例级排序。原始 clean control 的点相关混合 plane/model 观测并对固定 phase-0 误差排序；其区间按 examination/patient 簇重采样。五架构分析先在检查内聚合，二者估计对象不同。主表与正文现已明确区分。

历史宽上下文汇总另含 966 行 reference-versus-itself，必然具有 count=2、influence=1、error cosine=1。保留原表，新增剔除这些行的 7,728 行敏感性分析。六个队列/模型分层的 influence-minus-count 相关优势为 0.0614、0.0855、0.1279、0.1177、0.0701、0.0603，六项同时 95% 区间全部为正。主图 3 和主表 2 使用此结果，fixed-one 历史失败照常显示。这项补查是发现问题后启动的事后分析，不追认成初始预设端点；见 `INTEGRITY_ADDENDUM.md` 和 `outputs/nonself_influence_manifest.json`。

最终台账还将 16 个 NingXia HAT/SwinIR fold 权重绑定至哈希，连同十个主要五架构权重，共核对 26 个已使用权重。1,336 个可用候选权重仅表示可发现资产，不等于它们全部进入论文或已经逐个重跑。
