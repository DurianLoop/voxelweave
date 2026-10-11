# Pareto Testing：风险约束下成本优化的直接强对照

实际官方来源 https://arxiv.org/abs/2210.07913 ，题名 Efficiently Controlling Multiple Risks with Pareto Testing。作者 Bracha Laufer-Goldshtein、Adam Fisch、Regina Barzilay、Tommi Jaakkola。[本地原文](source_cache/pareto_testing_verified_primary_2026-10-07/pareto_testing.pdf) 23 页，侧栏 arXiv:2210.07913v1，2022-10-14；不将未确认的会议路径当正式引用。

最初候选 PMLR206/laufer-goldshtein23a 404，arXiv2210.07998 实为 Lambda-DARTS；attempt01真实exit1且没有错论文PDF。PMLR206索引未含目标题名，attempt02真实exit1。官方arXiv题名搜索attempt03真实exit0找到正确ID，逐一citation_title核对后actual download/extraction真实exit0。三个失败/恢复目录完整保留，下载reading=false不改。

完整文字选读页1–9、13–14，共11/23页；页13大部参考文献及附录入口，不冒称额外方法页。render/view页5、6、7、8、14，共5页。只核已读的A.1–A.3，不称全部附录/完整复现。

页4 formulation：多个期望risk高概率同时满足，另外一个或多个free objective尽量优化；calibration为i.i.d.、模型已在训练数据学习。页5先将calibration拆Dopt/Dtesting，在Dopt构造多risk+cost的Pareto front，再用Dopt联合max-p-value从小到大排序；页6Algorithm1在fresh Dtesting执行固定序列检验，遇首个不拒绝停止，认证集内按free objective选择。直接在同calibration上做经验约束优化或不作FWER校正均不保证其高概率性质。

页6 Proposition5.1/页14 A.2 的保证来自独立split、valid p-values和first true null。认证安全策略集合以后可取一个，也可按独立固定随机权重time sharing。页14 A.3 的证明用 Q_i(mixture)=sum_j Delta_j Q_i(config_j)。它不涵盖基于当前X选择不同配置的路由器；最终router必须作为一个完整候选单独评分和校准，也不能混合预测概率再称等同随机配置选择。

页7计算改动为Transformer token pruning、early exiting、head pruning，三维作用可能互相影响。相对cost公式考虑token长度平方和head数，并另报FLOPs；这是代理cost，原文称定义会随硬件/应用改变，没有证明MRI实际端到端耗时。相对准确率下降D在[-1,1]，其正部D+在[0,1]作为更保守loss是明确已有方法。“正部退化风险”本身不能称本项目新理论。

页7 worst-class多风险及selective abstention也已考虑；不能只看接受区域忽略完整队列。页8–9实际实验是五个NLP文本任务IMDB/AGNews/QNLI/QQP/MNLI、BERT-base12层/12head，不是MRI。相同18x20x18=6480配置grid进行公平对照，包括3D-SGT、SplitFST和不保证风险的经验优化。50–100次拆分不是独立数据人数累加；原文报告成本改善不能替代本项目实测。

实现移植时要记原文细节：页5正文Pareto非支配通常描述为所有维度不差且至少一维严格好，Eq5却写所有维度严格小；需在本项目协议明确采用哪一规则并报告tie，不默称完全逐字复现。页6Figure2图注说high-to-low risk，而Algorithm1和图中走向是low-to-high p-value；以算法定义实施并保留该歧义。页8图注alpha序列出现0.5与最大0.2不一致，实际图刻度.025,.05,...,.2；不凭图注拼造精确实验配置。

新意判断：多风险/多维自适应计算、独立数据学习Pareto候选、认证集合内cost优化和随机策略time-sharing均已有直接先例。应新增Pareto Testing和SplitFST作为成本/安全选择强对照；当前MRI尚无已确认新claim。

[完整策略后续准备](../RISK_COST_FULL_POLICY_FOLLOWUP_2026-10-07.md) 与 [LTT核读](2026-10-07_learn_then_test_primary_reading.md) 对接。真正待验证的是充分适配dense/direct/SR的修正余量、合法observed特征预测的患者收益、联合非加性超出分式Dice/重叠及既有策略能解释的部分，以及计入所有探索成本后是否保留改善。
