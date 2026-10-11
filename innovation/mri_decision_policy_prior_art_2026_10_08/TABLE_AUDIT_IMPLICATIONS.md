# 已执行的论文数值复核

对视觉核过的 Diagnostic p11 Supplementary Table2 及 L2SR p18 Table3 建立 [逐项转录](PAPER_TABLE_TRANSCRIPTION.json)，[CPU程序](audit_reported_tables.py) 实际 bb50d8=0。复核只读取论文数值和来源，没有读取MRI、预测、GT或权重数组，没有forward／训练。本轮没有将数值复核说成MRI方法收益，也没有独立复现实验。

| Diagnostic报告设置：Policy Classifier 减对照 | 正／负／零，18个设置 |
|---|---|
| 对Policy Reconstruction，AUC | 1／17／0 |
| 对Policy Reconstruction，Recall | 1／17／0 |
| 对Policy Reconstruction，Specificity | 17／1／0 |
| 对Undersampled，AUC | 9／7／2 |
| 对Undersampled，Recall | 8／6／4 |
| 对Undersampled，Specificity | 11／5／2 |

18=3 center fractions×6采样率。这些设置共用数据、模型与嵌套样本，不可当独立患者或做18次胜负的二项显著性检验。比较仅是已发表三位小数；tie是报告值tie，不保证未舍入相等。没有患者级预测／CI／threshold曲线，本轮不能断言风险非劣、总体显著优劣或合理阈值可弥补。Fig3只展示其中条件，不能以其曲线概括全部配置。

例如 center fraction0、7%时PC AUC=.777／Recall=.699／Specificity=.854；PR=.806／.850／.763。PC并未在这组AUC／召回胜出，却有较高specificity。论文p6文字“约.780 AUC”可视为约数，而非本轮强制修改表格。完整采样Oracle AUC=.819是单个已训练full-input classifier；PR可以超过它，不能称它是所有算法／同信息配置的数学上界。

L2SR 表3中，相比PG-MRI，报告的四种knee horizon加速比为3.524–4.378；但L2S/L2SR耗时仍为Random/LOUPE的3.15–8.125倍。x4 Base=.0201s／.0843s／.0040s。这说明减少中间恢复已有费用收益，且静态控制的低费用必须计入本项目。这里只计算报告均值的比例，未运行这些模型；不外推brain／3D CISS／别的GPU、完整患者或实际scanner scan time。

数据计数CPU核对32035+5249+1841=39125，只确认slice合计一致，没有验证患者互斥。L2SR的3–5倍训练时长来自文字范围，不转换为精确秒数。

后续评价沿用已冻结主要端点，不由本文所见端点权衡事后改success定义。在开发阶段同时保存既定full Dice、完整病灶／漏检统计和患者完整cost；如果某策略只有单端点变化，应报告真实权衡，而不是选一个最漂亮指标宣称全面改善。
