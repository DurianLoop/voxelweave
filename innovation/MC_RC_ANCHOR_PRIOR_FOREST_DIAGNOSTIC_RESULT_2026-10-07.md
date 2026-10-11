# 19系列合法观测定位诊断：先验、覆盖和窗口费用

生产 v4 工具 c31426 实际 exit0，独立工具779eda实际 exit0。全部19开发系列/11患者、57候选支持、3015缺层记录通过独立复核。诊断未建立可发表的MRI净任务收益claim。

| 固定方法 | 患者/系列等权前景覆盖 | boundary覆盖 | ROI面积占比 | 条件forward省算 | 原全部gates |
|---|---:|---:|---:|---:|---:|
| 19队列 empirical QDA | 0.8820% | 1.2061% | 0.3035% | 60.8898% | 0/19 |
| **19队列 balanced QDA（主）** | **98.9361%** | **98.2023%** | **12.9525%** | **16.7439%** | **0/19** |
| balanced ExtraTrees（解释性） | 92.2123% | 93.8427% | 9.0258% | 17.5864% | 0/19 |

这些为缺层完整GT评分后的开发诊断，覆盖是ROI几何端点，并非最终病灶分割准确率或SR任务增益。observed anchor Dice三者患者等权均值分别0.0000096162、0.0518242、0.0508971；作为分类器仍有大量FP。新19队列 empirical不等于旧16模型，不能跨队列将差异全部归为先验。

当前两QDA类条件参数/患者训练剔除相同，只变priors，所以能隔离先验对决策支持的影响。主方法提高覆盖时，19/19都失败于原ROI≤5%和tile32≤10%门槛；foreground≥.99为12/19，boundary≥.99为12/19，tileforeground≥.995为18/19。不能用均值约99%宣称每病例99%，也不能追调阈值/半径覆盖本次失败。主方法“foreground与boundary都≥.99且有条件省算”的交集12/19。

ExtraTrees foreground/boundary门槛分别15/19，原面积门槛仅1/19、tile面积2/19；该面积通过病例并未使全部gates通过。完整覆盖和省算交集也12/19，不能因其个别病例改善改成新主方法。012的前景覆盖仅29.2250%，说明非线性/平衡样本并不消除当前范围内漏检；与QDA还存在抽样/权重/容量差别，不能纯归因非线性优劣。

三者全量N相同572，条件重算k分别175/447/417。empirical有1空ROI，省算不是有用修复；全batch失效分别1/2/3series。ROI面积比例与window比例不同，精确物理格点/window/batch2费用已核，不由面积推断时延。

**加入初始化后的费用仍不充分。**元数据精确分析工具fe2e70 exit0，假设5次同一支持修正、冷cache：cached calls下界N+5k，dense为5N。主balancedQDA全队列pooled比2807/2860=0.98147，但完整患者workload先累加其series后、患者等权平均是1.02846；原患者/系列两层等权是1.03256。ExtraTrees相应pooled0.92902、完整患者1.01989、两层等权1.02414。不能只报告较有利pooled数字掩盖患者平均成本。

重复支持的严格省算条件为m*(N-k)>N，k=N无有限盈亏平衡m。即使满足forward下界，定位、生成、候选探索、transfer/cache和后处理仍未入账，因此不是真实端到端加速结论。若baseline已经计算，费用分母需要另明确；不能同时去掉cold费用又采用dense冷比较。实际动作/累计编辑可能改变支持，此分析不替代真实输入或最终模型输出资格。

执行范围完整保留：v1准备19observed MRI+19observed标签后，joblib Windows管道失败（8a9599 exit1）；v2编码断言失败（1585da exit1）；v3新加源码路径未列审计允许集合，0医学读取时被阻止（202730 exit1）。v4仅修执行核验，复用v1冻结矩/样本，重新19observed预测，**全部19预测冻结后**才完整GT评分。没有hidden nativeMRI特征/GT框/自己held患者监督，没有阈值/半径搜索或排除病例。

独立复核重新解码observed标签坐标、重建抽样index/features和centered矩、重推22个QDA参数/Cholesky决策、复拟合11forest并精确核704trees的分裂/value/样本数组，以独立leaf累加重放全部硬预测；显式physical disk、另一GT transpose/flip与boundary、Fraction坐标支持/窗口费用及全部汇总计数通过。共享旧feature_plane/normalization/SciPy过滤以及sklearn训练/tree.apply已明示，不称独立库或确认研究。

本阶段含失败准备和独立重放实际observedMRI包数组读取76、observed标签数组读取38、完整开发GT数组读取38。新nativeMRI数组/神经forward/GPUforward/神经训练均0，确认/已见验证未读。外部原训练session99542仍live，不能将其更新计为本诊断工作。

- [固定诊断协议](MC_RC_ANCHOR_PRIOR_FOREST_DIAGNOSTIC_PROTOCOL_2026-10-07.md)、[串行修订](MC_RC_ANCHOR_PRIOR_FOREST_SERIAL_EXECUTION_ADDENDUM_2026-10-07.md)、[编码/审计修订](MC_RC_ANCHOR_PRIOR_FOREST_ENCODING_ADDENDUM_2026-10-07.md)。
- [生产结果](experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/attempt01.json)、[独立复核](experiments/mc_rc_anchor_prior_forest_diagnostic_v4_2026_10_07/independent_label_models_roi_attempt01.json)、[初始化分析](experiments/mc_rc_anchor_prior_forest_amortization_2026_10_07/attempt01.json)。
- [两篇原文笔记](literature/2026-10-07_prior_balance_primary_reading.md)、[后续claim准备](ANCHOR_PRIOR_DIAGNOSTIC_TO_NET_BENEFIT_PREPARATION_2026-10-07.md)。
