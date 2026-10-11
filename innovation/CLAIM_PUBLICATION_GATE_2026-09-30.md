# MIRA 可发表主张的证据门槛

本文件追踪“形成可审稿的、有边界的机制 claim”，不以单个显著性结果代替论文可投稿性。状态基于当前工作区，随新结果更新；对未核实材料不推定 PASS。

**2026-10-01 最新门槛：** [Morshuis 2024](literature/2026-10-01_segmentation_guided_mri_fulltext_result.md)与[Fischer 2023](literature/2026-10-01_fischer_mri_uq_fulltext_result.md)的 MRI 重建/分割全文进一步排除“首次由多重重建量化分割不确定性或提示任务错误”的宽主张，但未找到相同的发布层同目标邻片切换。Kuestner 2024 仍缺方法全文，窄新意不判 PASS。[UPENN 两文件官方 Aspera 试验](UPENN_ASPERA_TWO_FILE_ACCESS_RESULT_2026-10-01.md)经精确路径核验后止于认证失败，零影像文件；同空间 NIfTI 标签/病灶终点未验证，原有 DICOM 结果不能回填 atlas 标签。以下表格的门槛结论因此不变。

| 门槛 | 当前证据 | 判定 / 下一动作 |
|---|---|---|
| 明确新意且避开直接先例 | [原稿 Related Work](../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex)、[Hu 2021](literature/2026-09-30_hu_mira_overlap.md)、[不确定性近邻](literature/2026-09-30_mira_uncertainty_neighbours.md)、[新增两篇全文核读](literature/2026-10-01_shared_context_neighbours_fulltext.md)及[Savant 2026 问题定义原文](literature/2026-10-01_savant_formulation_fulltext_result.md)：直接误差预测、conformal 区间、内在歧义分解、已测子空间审计、输入扰动评分和邻层距离的重要性均已有；同目标发布层邻片上下文切换与成对误差可观测性是当前窄差异。 | **部分满足。** 不能主张首次 MRI 测量/邻层上下文审计或响应式风险评分；定向查询不是系统综述，Kuestner 2024 全文仍缺，需按目标场合查新。 |
| 多架构、跨开发队列的机制证据 | 现有稿件 fastMRI/IXI 各 20 有序配对；acquired-only mask 与 residue 敏感性，部分影响稳定性和固定锚数反例均有记录。[IXI 权重的 MSValid 次级复制](MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md)同队列 84 人/479 目标为 +24.19 个百分点。 | **有边界通过。** 旧队列反复参与研究；IXI 权重次级复制不增加独立患者来源数，也不消除选择史。 |
| 新患者来源的事前固定确认 | [MSValid 旧主结果](MSVALID_EXTERNAL_CONFIRMATION_2026-09-30.md)：84 人/479 目标，旧 fastMRI 权重对 `ΔO=+19.76` 点；[同队列 IXI 权重跟进](MSVALID_IXI_WEIGHTS_SECONDARY_RESULT_2026-10-01.md)为 +24.1856 点。[ReMIND 冻结新来源](REMIND_NATIVE_T2_CONFIRMATION_RESULT_2026-10-01.md)：同一 IXI 权重对 62/63 人、248 目标，+26.3999 点。[UPENN 处理后来源冻结检查](UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md)：374/374 人、1,496 目标，+28.1156 点，95% 患者 CI +27.9006 至 +28.3309 点，零失败且两种独立复核通过。 | **三来源发布层单配对证据通过，外部新意/机制门槛未全过。** ReMIND 有 `MPR`，UPENN 已选 374 套全部 `DERIVED/SECONDARY/OTHER`；第三来源在前两来源阳性后设计，不能当盲发现队列，也不能证明原始采集身份。 |
| 相位/伙伴质量/归一化反解释 | 旧 fastMRI 权重对的[MSValid 反向/线性](MSVALID_POSTHOC_CONTROL_RESULT_2026-09-30.md)为 +19.50/+14.62 点。**公开来源稿使用的同一 IXI 权重对**另有 [MSValid 共同缩放/反向](MSVALID_IXI_WEIGHT_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) +24.0358/+24.0681 点（84/84 人均正）及 [ReMIND 共同缩放/反向](REMIND_POSTRESULT_CONTROLS_RESULT_2026-10-01.md) +26.3236/+26.3049 点（62/62 人均正）；[ReMIND 代数分解](REMIND_ERROR_ALIGNMENT_DECOMPOSITION_RESULT_2026-10-01.md)的质量失衡项 +0.0779 点、对齐项 +26.3220 点。[同 HAT 参考的两来源线性伙伴](PUBLIC_LINEAR_PARTNER_CONTROL_RESULT_2026-10-01.md)仍为 +20.5445/+22.9386 点。[MSValid 同几何后合成噪声控制](MSVALID_MATCHED_GEOMETRY_NOISE_CONTROL_RESULT_2026-10-01.md)两档仅 -0.000339/+0.002529 点。 | **两来源结果后控制完成，因果仍未隔离。** 独立 min/max 与所选参考相位不是唯一解释；分解非独立证据。线性伙伴大效应否定双网络特有性；同几何合成噪声未重现大效应，但不能模拟原始独立采集。邻层内容、signed geometry 和 MPR 发布处理仍共变。 |
| 指标分母稳健性 | [两来源原结果固定共享分母复算](FIXED_DENOMINATOR_TWO_SOURCE_RESULT_2026-10-01.md)：MSValid +24.2152 点（84/84 人、479/479 目标正），ReMIND +26.4918 点（62/62 人、248/248 目标正）；独立逐目标/患者/区间复核通过。 | **分母变化非唯一解释。** 仍为结果后同预测的代数敏感性；不增加样本来源，也不识别纯采集身份。 |
| 外部队列上的响应影响超锚数证据 | 内部 acquired-only HAT/SwinIR 四层在目标+精确上下文调整后仍有 +0.24 至 +0.34 的探索性偏 rank 相关，[六项结果后同时错配对照](RESPONSE_PLACEBO_SIX_FAMILY_RESULT_2026-10-01.md)均正，最弱下界 +0.0009；SAINT 错配混合。[MSValid 阶段 1](MSVALID_INFLUENCE_STAGE1_RESULT_2026-09-30.md)的简化几何调整为 +0.5681，精确上下文仅 +0.0386。P13–P24 线性几何留出虽正，精确类别基线后为负；[P25–P84 冻结 60 人留出](MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md)在完整性/源影像哈希通过后，误差余弦 MAE 差为 **-0.000168**，23/60 人受益、排序不变。 | **内部条件性响应线索保留；外部增量预测/可行动评分分支停止。** 完整 84 人的两中位目标响应不能替代原 479 目标合同；错配响应不是物理采集随机化。正向弱基线或内部结果不能覆盖严格外部负结果。 |
| 可部署风险识别 | 原 acquired-only guard 对照的同时 AP 区间跨零。[两来源目标误差排序检查](TWO_SOURCE_TARGET_ERROR_RANKING_RESULT_2026-10-01.md)发现 MSValid SwinIR 共享/不相交一致率 0.661/0.802，但 ReMIND 0.613/0.677 的改善区间跨零；不相交分数还需要原 x4 输入所无的 phase-2 层。 | **仍失败。** 平均误差可观测比例上升不能替代跨来源确认的目标风险排序或校准。论文只主张回顾性审计，不提供可部署正确性分数。 |
| 原始独立采集来源 | MSValid 缺原始 DICOM 链，ReMIND 含 `MPR`。[本地 fastMRI 7 例重复 T2 非像素头筛查](FASTMRI_REPEAT_T2_HEADER_GATE_RESULT_2026-10-01.md)在四对双 T2 系列中没有一对通过完整时间/几何/协议门槛；两对仅有缺时间证明的同几何线索，且该本地资料精确 release/使用权未核。 | **未通过。** 不运行原始采集身份目标像素实验，不主张纯身份因果；如能取得授权与采集记录，另定事前方案。 |
| 数据使用、伦理与图像刊登依据 | [既有数据/伦理台账](../design/paper/FINAL_SUBMISSION_PREPARATION/DATA_ETHICS_CITATION_AUDIT.md)：IXI 来源/许可已核；[MSValid Zenodo 正式引文与 CC BY 4.0](literature/msvalid_zenodo_citation_audit_2026-10-01.md)及[ReMIND 官方 TCIA 来源、CC BY 4.0 与 MPR 限制](REMIND_NATIVE_T2_SOURCE_AUDIT_2026-10-01.md)已核。[公开来源构稿路线](PUBLIC_ONLY_MIRA_MANUSCRIPT_ROUTE_2026-10-01.md)排除了 fastMRI/NingXia 图、表和患者像素；当前量化图不含患者影像。IXI 权重发布/share-alike 义务及正式署名仍待专项核对。 | **公开来源内稿可审阅，外发仍待核。** 旧稿若保留 fastMRI/NingXia，则其 release/刊图、伦理与同意仍是阻断项；不能用公开来源稿替旧稿洗清来源。 |
| 正式引用与可分发产物 | [逐来源发布审计](PUBLIC_SOURCE_RELEASE_CITATION_AUDIT_2026-10-01.md)确认 MSValid 的六位 Zenodo 创建者、日期、DOI 和许可；[TCIA/Datacite 直接核查](literature/remind_official_citation_audit_2026-10-01.md)取得 ReMIND 强制 18 位作者、Version 1 数据引文并写入内稿；IXI 衍生权重的具体再分发义务未作法律/机构确认。 | **部分满足。** ReMIND 数据引文缺口已关闭；正式投稿/公开权重前仍须核实 IXI 权重与代码/数据发布条件、目标场合格式并由真实作者确认。 |
| 稿件与可复现包同步 | [原 CVPR 主文](../design/paper/CVPR/CVPR_ARCH_GENERALIZED/PAPER/main.tex)仍是旧证据版本；[独立 11 页审阅稿](manuscript_review_2026-10-01/README.md)混有旧来源。[公开来源英文草稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)另有已逐页核对的 5 页 [PDF](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.pdf)、[量化图](figures/PUBLIC_TWO_SOURCE_FIGURE_NOTE_2026-10-01.md)及[复现补充材料内稿](PUBLIC_ONLY_REPRODUCIBILITY_SUPPLEMENT_2026-10-01.md)。两组结果后控制和线性负对照均已写入。 | **科学草稿与内部复现索引完成，投稿包未完成。** 当前 `environment.yml` 与实测 NumPy 不一致且缺 pydicom；仍须目标场合格式、正式引文、可分发的环境锁/代码、IXI 衍生权重许可、作者与对外发布确认。 |

第三架构 SAINT 的[精确上下文关联](SAINT_EXACT_CONTEXT_AUDIT_2026-09-30.md)仍为正，但其原始响应错配中有一种与正确锚点配对几乎相当；不能把“三架构物理身份特异性复制”列为已通过门槛。P25–P84 五批的[冻结留出结果](MSVALID_INFLUENCE_P25_P84_RESULT_2026-10-01.md)已全量报告为负，不再以连续影响量申请部署评分主张。

当前可以写出的最强科学句子：在固定 IXI HAT→SwinIR 对上，MSValid、ReMIND 和后续 UPENN 处理后 T2 分层中，切换到不相交**发布层**邻片均提高同目标成对误差可观测比例；UPENN 374/374 人及 1,496/1,496 目标同向。这个回顾性量依赖目标真值和额外 phase-2 观测，ReMIND 的 `MPR`、UPENN 的派生/次级标志、相位/解剖共变及研究选择史限制因果解释。UPENN 成对 MSE 未改善；可行动评分、真实薄层解剖恢复与临床安全均未获证明。**这是有三来源实证支撑的窄候选 claim；新意、许可和投稿门槛仍未全部通过。**

2026-10-01 扩展来源核查：上表的本地 fastMRI 七例仅是子集。[全部多 T2 清单病例的非像素头结果](FASTMRI_ALL_T2_HEADER_GATE_RESULT_2026-10-01.md)覆盖 61 例、2,944 个头，14 对双 DICOM T2 标签中四对技术匹配、零对有可用独立采集时间证据；清单 138 条 T2 行与头内 71 个 T2 系列的映射仍待解释。**原始独立采集来源门槛仍未通过**，不读取目标像素，不将这批本地资料加入公开来源稿。

后续[清单 UID 交叉核查](FASTMRI_MANIFEST_LINKED_PAIR_RESULT_2026-10-01.md)把 138 条标 T2 的清单行解析为 122 个不同 UID，其中 55 个头内描述不含字面 `T2`。扩展比较 64 对清单关联 UID，技术匹配仍是同四对，64 对均无可用时间证据；这解除字面标签漏筛的疑问，但不改变来源门槛的失败状态。

正式数据引文更新：[TCIA 当前集合页与 DataCite 原始响应](literature/remind_official_citation_audit_2026-10-01.md)已核得 ReMIND 强制数据引文的 18 位作者、2023、Version 1 和 DOI，并同步至[公开来源内稿](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)。上表“ReMIND 首选引文未捕获”为历史状态，现已关闭；IXI 衍生权重、可分发代码/环境、作者和目标场合审查仍未关闭。

本次续作补充：[位置通道六人小试](POSITION_CHANNEL_ONLY_PILOT_RESULT_2026-10-01.md)只证明输入编码敏感性，不能隔离原始采集身份；[已知 profile 训练内 12 条件试验](KNOWN_PROFILE_HOLDOUT_PILOT_RESULT_2026-10-01.md)发现留出观测选核对缺层误差无正向收益，不能升级为新方法 claim。[重复采集来源筛查](REPEAT_ACQUISITION_SOURCE_SCREEN_2026-10-01.md)的两条线索分别受限制性 EULA 与 NIH controlled access 约束；都没有进入患者试验。[实测运行时审计](PUBLIC_ONLY_RUNTIME_PROVENANCE_2026-10-01.md)通过，但不是经全新安装验证的环境锁；[OpenAlex 有界筛查](literature/2026-10-01_context_overlap_openalex_result.md)低召回，不能关闭目标场合查新。以上不改变表内“科学候选有证据、投稿门槛未全过”的判定。

新的[官方 QIN 前列腺重复 T2 全量头部筛查](QIN_REPEAT_T2_ALL_HEADER_RESULT_2026-10-01.md)覆盖 15 人、30 套原始/主要 2D 系列，且经独立哈希和几何复核；**0/15** 对满足事前固定的同方向和同位置规则。该结果将 QIN 从“可能的同几何独立采集来源”降为不合格来源线索，不改变当前公开来源脑 T2 稿件的窄 claim，也不关闭原始采集身份来源门槛。

[两来源同可用观测预算控制](TWO_SOURCE_EQUAL_INFORMATION_CONTROLS_RESULT_2026-10-01.md)进一步区分了回顾性可观测性和实际重建收益：不相交伙伴的等权平均相对共享平均在 727/727 目标降低 MSE；但额外 phase-2 观测被公平提供给原生线性和两种三次插值后，ReMIND 相对 PCHIP 仅 +0.91% 患者平均增益，95% 结果后区间跨零。按事前计算停止规则，**集成作为跨来源稳健新重建方法仍未通过**；MIRA 发布层上下文审计结论不因此变成部署或临床 claim。

[Hu 2021 引用链与近期文献有界筛查](literature/2026-10-01_mira_citation_neighbour_result.md)共阅 157 个去重标题，并核读 Radmanesh 等 2022 年全文的欠采样数据 Monte Carlo 误差估计；另查到 Kuestner 等 2024 年五架构深度集成不确定性论文的正式摘要，但无法取得全文。两者进一步否定“MRI 中首次无真值误差估计/跨架构不确定性”的宽泛措辞。当前精确发布层上下文对照未在已读范围内找到直接重合，但查询截断且 2024 全文缺失，**新意门槛仍只部分满足**。

新增[UPENN-GBM 官方元数据与冻结首例头部结果](UPENN_GBM_T2_SOURCE_AND_HEADER_RESULT_2026-10-01.md)：候选轴位 T2 描述虽然涵盖 402 套/374 人且标 CC BY 4.0，首例 64/64 DICOM 头均为 `DERIVED/SECONDARY/OTHER`；独立复核通过。依事前规则停止将这个已选分层用作原始 2D 采集层确认，且不对其余 401 套作未验证断言。此结果不增加主稿患者证据，也不改变“发布层审计有实证支撑、原始身份和投稿门槛未通过”的判定。

[TCGA-GBM 官方元数据可用性筛查](TCGA_GBM_T2_SOURCE_SCREEN_RESULT_2026-10-01.md)的 NBIA 系列响应为空，且集合枚举不含该精确标识；现阶段无法据此定义新患者 T2 队列或文件级权利。不能将技术性空响应当成阴性队列。两条新增来源线索都没有为主稿增加独立患者结果，[创新点决策备忘录](INNOVATION_DECISION_MEMO_2026-10-01.md)保留候选主张和停止规则。

新增[NPB-REC 2022 原文核读](literature/2026-10-01_npb_rec_fulltext_result.md)：相同欠采样 k-space 输入上的九组权重样本标准差与 MSE 相关，已是 MRI 多预测分歧/误差估计先例；它未做同一发布目标上切换物理层上下文的试验。[Kuestner 2024 全文访问复核](literature/2026-10-01_kuestner_fulltext_access_audit.md)仍只取得正式摘要/索引，无法排除其方法细节直接碰撞。故宽泛新意继续否定，窄新意仍只部分满足。

[Edupuganti 等 TMI 2021 全文核读](literature/2026-10-01_edupuganti_fulltext_result.md)进一步显示，在 MRI 重建中方差可能漏掉主导偏差，且 SURE 可在明确噪声假设下估计无真值风险；因此“首次发现模型分歧漏检共同错误/首次无真值 MRI 风险审计”也不能成为本稿贡献。其固定单线圈 k-space 观测的膝 MRI 任务不同于当前发布层上下文对照，但这不等于证明全球无直接先例。

**2026-10-01 全量 UPENN 更新（覆盖上方首例阶段的“未增加患者证据”历史状态）：** [374 人/1,496 目标的独立复核结果](UPENN_GBM_PROCESSED_T2_CONTEXT_RESULT_2026-10-01.md)满足事前成功标准，患者等权 `Delta O=+28.1156` 点（95% CI +27.9006 至 +28.3309），374/374 人正；处理后来源审计得到第三个阳性分层。全部 374 套头均为派生/次级，不关闭原始采集身份门槛。结果后分解、固定分母敏感性仍仅是同一预测的代数描述。正式 [UPENN 数据引文](literature/upenn_gbm_official_citation_audit_2026-10-01.md)已归档；公开来源草稿 PDF 仍是两来源快照，不能当最新三来源稿件。

**2026-10-01 文献与临床任务门槛补充：** [四种子正向引用链筛查](literature/2026-10-01_four_seed_forward_citation_result.md)覆盖 62 条索引记录、61 个不同 work ID，并核读两篇 arXiv HTML 全文。它们未执行已读范围内相同的发布层邻片切换合同，却已在固定欠采样 k-space 下研究病灶检出或结构分割误差；仅有 `Delta O` 不足以主张临床保护。Kuestner 2024 等相关工作仍为摘要级，**新意门槛未关闭**。[MSValid 官方 ZIP 的标注来源门槛](CLINICAL_TASK_LABEL_SOURCE_GATE_2026-10-01.md)查得 398 个 T1/T2/FLAIR NIfTI 和六个 `.DS_Store`，无标签成员；只排除该 ZIP 内的直接配对标签，不能排除另行发布标注。未取得同目标物理层、同系列、可信标签前，不运行病灶/分割指标；获得标签后须先冻结映射、病例、主要任务终点与负结果规则。三来源经验审计保持阳性，临床、原始采集机制及正式投稿门槛仍未通过。

**UPENN 标签空间与三来源内稿更新：** [官方提交者说明核读](UPENN_GBM_LABEL_ALIGNMENT_GATE_RESULT_2026-10-01.md)确认专家修订肿瘤标签与配准 NIfTI 对齐，并明说 NIfTI 与 DICOM 按设计不对齐。因此不能把这些标签直接叠加到已冻结的 374 套 DICOM/1,496 目标上；随后 [NBIA 全系列及 SEG 路由原始响应](literature/source_cache/upenn_gbm_label_routes_2026-10-01/index.json)证明当前官方 DICOM 清单 3,680 套全是 MR、UID 集合与冻结 MR 清单相同，SEG 查询返回空正文。这仅限该接口/时间点，不否定单独发布的 NIfTI 标签。新的 [三来源英文内部文本](PUBLIC_ONLY_MIRA_MANUSCRIPT_DRAFT_2026-10-01.md)和[匿名逐患者图](figures/PUBLIC_THREE_SOURCE_FIGURE_NOTE_2026-10-01.md)已纳入 UPENN 及任务级先例，**旧五页 PDF 仍是两来源快照**。图文更新不关闭临床任务、原始采集、先例全文、权重许可、环境复现或作者投稿门槛；当前 claim 保持窄的发布层回顾性审计。

[UPENN 官方逐扫描可用性表](UPENN_GBM_NIFTI_LABEL_FEASIBILITY_RESULT_2026-10-01.md)进一步筛出 232 条基线记录标注人工修订肿瘤分割可用，其中 114 个受试者前缀与已选 DICOM 人群重叠。这只是新 atlas NIfTI 任务的来源线索；尚无 NIfTI 文件目录、确切 T2/标签同仿射、目标面标签阳性率或临床终点结果。69 GB Aspera 包未下载。发表门槛因而仍未通过；只有完成新协议的空间与任务级检验，才能讨论病灶相关后果。

[0.9 mm 薄层系列单例非像素门槛](UPENN_GBM_THIN_T2_HEADER_PILOT_RESULT_2026-10-01.md)从 86 条修订标签薄层元数据记录对应的 83 套处理后 T2 SAG SPACE 系列中事前选首例。官方 ZIP 的 192/192 头均为 3D、物理层距约 0.9 mm，同时全部为 DERIVED/SECONDARY/OTHER，且无来源影像链；独立只读复核通过。它确认一个发布层薄网格，却不关闭原始采集薄层真值或同空间标签门槛，也不能外推到其余 82 套。

**2026-10-01 官方 NIfTI 文件清单更新：** [Faspex 公开链接文件级审计](UPENN_NIFTI_OFFICIAL_PACKAGE_INVENTORY_RESULT_2026-10-01.md)通过网页正式公开授权流程列出 671 个结构像扫描目录，以及 147 个候选修订分割链接。官方 CSV 虽标记 232 个基线扫描可用修订分割，但当前包的 `images_segm` 目录缺少其中 85 个；147 个链接中仅 60 个有约 0.9 mm T2 厚度元数据。预选首例有同扫描 ID 的 T2/分割文件名，尚未转移 NIfTI 或核查 shape/affine。正式任务实验必须先以可取得且同网格的文件重新冻结分母，不能将 CSV 的 232 当成有效标签病例，更不能将 atlas 标签叠到现有 DICOM。无 HTTP 网关且本机缺 Aspera Connect，当前同空间头部与病灶终点门槛未通过。[Verschuur 2022 T2 插值分割全文](literature/2026-10-01_verschuur_neonatal_t2_fulltext_result.md)又否定了宽泛的“首次用 T2 切片插值改善分割”新意；固定参考成对误差可见性的窄主张尚需 Kuestner 方法级排重。

**2026-10-01 MSD 独立标注区域试验更新：** [事前冻结的官方 MSD BrainTumour 完整结果](MSD_TASK01_TUMOR_ROI_CONTEXT_RESULT_2026-10-01.md)为 484 次尝试、483 个完整病例、1,932 个目标层、1 例预先记录的标签传输失败；独立公式和完整分母复核通过。病灶内 `Delta O` 为 +11.6537 点（95% 患者区间 +11.2256 至 +12.0681），病灶减同层等面积局部阴性对照为 +0.5819 点（+0.2302 至 +0.9337），按联合事前规则通过一个**处理后发布层的标注区域测量门槛**。区域差异幅度小，仅 267/483 病例为正。用同样四个真实偶数层的 PCHIP 对照，病灶平均 MSE 为 236.57，远低于 HAT0/SwinIR2 平均的 1,208.05，且 482/483 病例更优。故“新增临床/诊断获益”或“更好的同预算重建方法”门槛**未通过**，不能借统计显著的 `O` 差异宣称达标。BRaTS 标签来自多模态配准发布数据，不证明 T2 单模态诊断或原始采集因果；与 TCIA 其他匿名病例的完全去重未核实。Kuestner 2024 全文、IXI 衍生权重权利、干净环境复现、正式署名与场合审查仍未闭环，**可发表/可投稿状态仍是部分满足**。

**结果后解析反证更新：** [同 483 例 PCHIP0/线性 phase 切换结果](MSD_TASK01_ANALYTIC_CONTEXT_CONTROL_RESULT_2026-10-01.md)给出病灶减邻近阴性区 `Delta O=+0.9428` 点（探索性患者区间 +0.5503 至 +1.3381）；神经模型减该解析控制的配对差值为 -0.3609 点（区间 -0.7910 至 +0.0761）。纯解析估计器也产生正向区域差异，故任何“深架构特有的病灶机制”或因此获得的方法新意门槛**未通过**。该控制在看到神经结果后设计，不能作为独立阳性复制；原始冻结统计判据保持通过，但科学解释与投稿新意应进一步收窄。

**Kirby21 重复 T2w 来源门槛：** [全文、Table 1、官方目录与许可核读](KIRBY21_REPEAT_T2_SOURCE_GATE_RESULT_2026-10-01.md)确认两种协议均包含 T2 加权 DTI 几何参考，21 人两次重新摆位、官方有 42 个 Session 入口；但该序列是名义 2 mm 的 3D Fourier 采集，1 mm 重叠切片不能视作独立 2D acquired slices。匿名 Session 的同人配对、每包 T2w 原始文件和几何仍未核，未下载影像或接受许可。此来源**不关闭原始 2D 层采集身份门槛**，也不改变现有稿件的窄发布层审计定位。

**ON-Harmony 2025 来源交集复核：** [全文与官方非影像 CSV 审计](ON_HARMONY_REPEAT_T2_SOURCE_GATE_RESULT_2026-10-01.md)确证九人同机重复，但唯一 2D T2w FLAIR 扫描仪 GE MR750 不在九人的重复扫描仪中（0/9）；不能以跨扫描仪 2D/3D 对照替代原始同机 2D 身份实验。补充 [145 条检索索引筛查](literature/2026-10-01_native_2d_t2_targeted_search_result.md)尚无可直接放行来源。未下载影像；原始机制与发表门槛保持未通过。

**2015 年 57 人多模态复扫全文核读：** [论文协议](CONNECTIVITY_TEST_RETEST_T2_SOURCE_GATE_RESULT_2026-10-01.md)只在第一次 session 列 T2w，第二次未列；每次共同的 S-MRI 为 T1w 3D MP-RAGE。该来源不能构成重复 T2w，未核其公开压缩包。两条补充来源均未关闭原始采集机制门槛。

**两来源解析反证：** [同目标、同支撑的 PCHIP0/线性 phase 切换](TWO_SOURCE_ANALYTIC_CONTEXT_FALSIFICATION_RESULT_2026-10-01.md)在 MSValid 84/84 人、ReMIND 62/62 人上分别得到 +29.2470/+30.9585 点，均大于原神经配对的 +24.1856/+26.3999 点；727 目标、146 患者、四个区间及两例原像素重放复核通过。该结果后负对照不能识别数值差的网络贡献，但直接否定“大 `Delta O` 必须依赖深架构”。现有发布层审计可以作为描述性事实；若要称可发表的新方法或机制，当前证据不足，必须将这项反证和同观测 PCHIP 负结果纳入正式稿件判断。

**同邻片重建基线与预处理反解释：** [483 例同两邻片线性对照](MSD_EQUAL_NEIGHBOR_LINEAR_AUDIT_RESULT_2026-10-01.md)给出病灶 raw linear/HAT/SwinIR MSE 805.23/1,597.15/1,403.28；[完整 CPU 像素重放](MSD_PIPELINE_LINEAR_CONTROL_RESULT_2026-10-01.md)显示仅模型同款 min/max、resize 与裁剪就把线性基线升至 1,068.26，但 HAT/SwinIR 相对该基线仍多 +528.89/+335.02。两个分析均为结果后探索，后者还在单例预检后冻结；它们使“更优重建”门槛更加明确地**未通过**，也不能证明肿瘤特异先验损害或域移因果。独立同空间病理来源、IXI validation-only 同合同对照和真实任务终点未完成；宽泛病灶安全/选择性恢复新意已有先例，正式可发表性仍未通过。

**全前景反证与更窄的区域结论：** [MSValid/ReMIND 旧档案同邻片联结](TWO_SOURCE_EQUAL_NEIGHBOR_PERFORMANCE_CHECK_RESULT_2026-10-01.md)在各自全前景中，两模型均优于 raw linear，患者符号 84/84 和 62/62 一致；[MSD 同病例全前景像素重放](MSD_FULL_SUPPORT_EQUAL_NEIGHBOR_POSTRESULT_RESULT_2026-10-01.md)给 HAT 相对 raw linear -20.12 MSE（区间跨零），SwinIR -221.40（区间全负，但患者符号近乎平衡）。因此上一段的“更优重建未通过”只能指 **MSD 标注肿瘤 ROI 的方法优势主张**，不能推广为 MSD 整图模型崩溃或三个来源均输给线性。195/197 个 MSD 病人分别呈 HAT/SwinIR 病灶更差而全前景更好的符号反转；此为结果后描述。全局指标掩盖局部异常损失已有 MRI 先例，需新来源与实际任务终点才可能支撑独立新意。

**IXI validation-only 原域诊断：** [58 人/232 层同合同 CPU 结果](IXI_VALIDATION_EQUAL_NEIGHBOR_DIAGNOSTIC_RESULT_2026-10-01.md)的 HAT/SwinIR 全前景 MSE 相对 raw linear 分别 -1,923.06/-1,853.99，均为 57/58 人更低；原生 256-square 图像的 raw/pipeline linear 近乎相同。这排除“模型代码路径本来总输线性”这一简单反解释，却**不关闭**训练分布/病理的因果隔离门槛，因为该 validation 曾用于 checkpoint 选择、没有肿瘤 ROI 且与 MSD 发布处理不同。仍需独立同空间病理来源与任务终点；发表状态不变。
