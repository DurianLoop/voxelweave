# 完整post任务与相位控制之后的创新判断

研究目标仍active，尚无可发表且独立确认的新方法claim。45CISS及MC-RC已见8开发患者均不能再当后续方法完全未见确认；实现复核通过不等于科学确认。

## 这轮能成立的事实

1. 固定45人JSON full平均Dice raw=.74459750、pipeline=.65476150、post=.65284400。post−pipeline平均−.00191750，描述区间[−.00483038,−.00015858]；post−raw平均−.09175350。RTSTRUCT同方向，去1mm带顺序差区间跨0。换算子顺序没有消除缩放路径的大任务差距，但不能据单一冻结评估器说临床损害。
2. 855完整间隔的梯度能量诊断显示mixed_post比raw扩大anchors/inserted相位比，全45 ΔL正、平均+.93863810。同时处理anchors能降低该比，但这是纹理统计，且违反observed-preserving合同。
3. 三人固定归一化时，post anchors处理的full平均ΔDice仍为负，JSON−.00505496、RT−.00507443，逐人有反例。停止“带宽平衡恢复任务”的固定解释，不扩展失败配置到45人。
4. full结果包含anchors；不能仅凭full变化说missing预测变化。新增[实际输出分区审计](ANCHOR_PILOT_OUTPUT_DOMAIN_AUDIT_CPU_RESULT_2026-10-03.md)直接核对三人saved missing预测；已有12输入SHA证明fixed缺层网络输入不变。仅能定位给定任务链的响应。
5. 去1mm带正均值不是病灶核心恢复。[计数分解](ANCHOR_PILOT_BOUNDARY_DECOMPOSITION_CPU_RESULT_2026-10-03.md)发现JSON post_fixed−post带外平均FP减少72.67、TP减少14.33，带内FN增加119；两标签及全部反例保留。这是事后开发分析。

## 明确停止或不能宽称创新的分支

| 分支 | 实际证据 | 决策 |
| --- | --- | --- |
| HAT改善图像却使原主任务变差 | 原45完整主HAT−pipelinePCHIP平均+.036381704 | 原负向claim被反证，继续停止 |
| 残差相加保住原生细节 | 六开发项仅2/6过guard | 固定配置停止，不改名重启 |
| order_rms排序患者部署风险 | 最低15人JSON平均ΔDice−.11545667，双guard失败 | 固定排名方向/预算候选停止 |
| 平衡anchors带宽恢复post | 固定三人full负向且异质 | 当前恢复解释停止 |
| 频率约束、slice一致性、interleaved自监督 | dStripe/STRESS/SMORE直接先例 | 必需强对照，不能宽首创 |
| 原网格特征旁路/latent resampling | VINN/VINNA、Lazy Resampling | 不能简单组合模块命名创新 |
| 改归一化、分割条件生成、独立下游评价 | ISBI2019、SegRenorm、STRESS实际方案 | 不能把评估器选择或任务loss本身当贡献 |

## 现在值得准备的具体研究问题

优先问题是：在相同observations下，重建引起的输入信息变化与任务推理链对统计/上下文的响应能否分开，且在任务模型适配后仍存在可修正的缺层误差？这是一组待证问题，不是已成立方法。

第一项可测候选：任务输入的mean/std只由observed anchors计算并在全部重建输入之间固定，以阻断“生成missing→全volume统计→所有任务输入改变”的反馈。已有技术预检使该控制可行，但归一化和跨域训练已有先例。只能在新模型按相同规则训练、raw强基线、所有输入曝光预算相同后判断有无新效应；直接换官方checkpoint的归一化再挑最好的Dice不能证明方法。

第二项证据升级：训练曝光(raw-only/mixed/native)×归一化(full-volume/anchor-only)×相同输入(native/raw/pipeline/post/HAT)的完整矩阵。若差距随曝光收窄，支持任务模型适应为因素；若仍持续，继续测完整缺层病灶边界与体积。该矩阵是对原机制的区分实验，宽领域适配已有先例。

第三项方法入口只在第二项确认尚有缺层信息损失后开放：保持anchors/tail逐位不变，在原网格保留观测特征并生成missing，或者学习可部署的具体动作收益。现有旁路、频率约束、路由已有先例；需与相同容量、原网格PCHIP、固定频率修正、taskloss及同预算随机比较，旧岭/QDA/native能力失败必须保留。没有充分表征和新患者确认前，不训练新的收益头来覆盖旧失败。

后续设计与执行前资格见[更新准备](POST_TASK_AND_PHASE_NEXT_VALIDATION_PREPARATION_2026-10-03.md)和[矩阵规格](experiments/task_input_contract_matrix_preparation_2026-10-03.json)。GPU训练尚未执行，真实训练/确认来源尚未全部合格，不能给虚构可运行命令。FeTA的公开体积是SRR重建，不是原生薄层确认真值。

## 文献证据范围

新增8篇重点正文/415证据块/PDF0：前3篇Lazy Resampling、真实配对形态学、动态声道；后2篇dStripe/STRESS；追加3篇多中心归一化、SegRenorm、FeTA2024。[前3篇](literature/2026-10-03_bandwidth_consistency_fulltext_reading.md)、[中2篇](literature/2026-10-03_phase_direct_neighbour_fulltext_reading.md)、[追加3篇](literature/2026-10-03_task_normalization_context_fulltext_reading.md)均有原XML、正文、块索引及阅读登记。论文实验/图像/supplement未复现核读，题名数量不充当正文数量，未搜到同控制不证明首创。
