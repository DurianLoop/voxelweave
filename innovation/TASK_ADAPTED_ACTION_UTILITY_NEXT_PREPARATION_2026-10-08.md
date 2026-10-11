# 补读后的行动准备：适配、完整费用和确认不混淆

接续[旧17特征／真实标签连接合同](OBSERVED_FEATURE_TO_ACTION_UTILITY_PREPARATION_2026-10-08.md)，新增依据为[Prakash正文与Noise2SameSupplemental](literature/2026-10-08_downstream_segmentation_and_proof_reading.md)及[一次真实特征路径费用](DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md)。旧方案／冻结结果不回改；本文件不产生新MRI收益或风险认证。

1. **适配是强对照。** 对legacy dense、direct和common projected dense采用旧同raw／同通道／同初始化／同监督／增强／预算因素合同。Prakash先denoise再分别适配seg已存在；仅恢复后送固定作者模型不够证明解剖损害或创新收益。若候选输入包含不同修正状态，应事前明确baseline和候选各自适配范围及训练样本／动作状态覆盖，防止让某一路见过修正、另一路只见过旧分布。
2. **训练与部署预算分别报。** unsupervised预训练、action标签生成、探索和head训练不是免费；部署端用合法observed定位／特征及动作，完整测量启动、数据IO、定位、特征、动作生成、transfer、神经推理、组合、后处理／失败。当前23.8488s只是一次CPU19series特征资格生产路径含开销，不能线性换算GPU或完整患者task费用；19.3780s只是明确计时相位子集。患者成本先合并全部series，共享cold startup／审计／写出仍单列，不把仅1.7616s患者均值称full deployment成本。
3. **同样可见信息与已有相对决策。** 本轮17特征由合法observed两fold构成；ROI和task-state来自部署合法来源，不能GT定位。若error／risk／cost头也可取得这些特征，强对照必须给它们同信息、总head容量、相同整患者cross-fitting及总预算。新增必须保留的强对照是**两路径条件成本／错误率头**及已有cost-sensitive／learning-to-defer gate，不只与baseline-only风险头比。Madras physical3 Eq(3)和Mozannar physical2 Eq(1)已在旧原文中直接复读：比较两方损失、预测动作相对优势已有。patient／UID只用连接与分组。观测误差预测容易，但标签必须是真实完整患者ΔQ，不用MSE或training loss代替；连续期望ΔQ回归与gain>0分类不同，看到结果前选定。
4. **实测可修正余量。** 原两臂final exit0／最终冻结后，先原56FOV／6能力gates／strict，再同容量强适配。固定动作原集合及patient端点，保留所有负／零／失败；若无余量，归档负结果。联合动作在当前状态算ΔQ和incremental union成本，不假设additivity。理论风险保证另需其条件，普通经验病灶收益研究不额外强加freshcalibration要求。
5. **确认只用未见资料。** 方法、端点、阈值、checkpoint、动作及预算冻定后才8确认／12series和第二任务网；已见4／9不称fresh确认，lockedIXI关闭，旧MIRA／MSValid84保留。候选是否可发表仍需配对净收益、强控制、完整成本及直接MRI查新，当前未满足。

收益标签还须标明task checkpoint曾拟合哪些患者：若task网训练用过完整11开发患者，head-only的leave-patient-out并不使整个pipeline对heldout患者未见，其标签应叫开发内标签。要声称开发内整个pipeline患者外，需fold-specific任务训练与真实成本；目前未执行。最终冻结8确认可验证整个未见patient pipeline，但不能事后把开发内标签改名。无需为普通经验结论额外引入formal calibration合同。

已复读SafeRestore source TXT 347–401及1265–1277行：其六个可用特征已有entropy、回投影MSE、raw/action detector-map差异、图像residual等；生成全部候选和detector outputs后选择，明确无latency／energy优势。后续六特征及动作特定双风险排名应作为实质对照，全部探索费用计入。MoEDiff本阶段只复核已有笔记／部分摘录，合并输出截断，不声称新完整原文核读。来源与实际阅读范围见[本阶段补充碰撞记录](literature/2026-10-08_relative_utility_collision_recheck.md)。Noise2Same的generic conditionalvariance推断例子只作适用性审计，不另立理论claim绕开病灶目标。
