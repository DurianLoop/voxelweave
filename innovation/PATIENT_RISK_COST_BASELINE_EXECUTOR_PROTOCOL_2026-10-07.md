# 患者层 LTT / SplitFST / Pareto 对照执行器：事前协议

上一阶段已完成实质progress：2篇原文27选读页/10view、合成workflow独立核验、exact排序反例、140新stage/1386累计证据。原训练session99542仍live/native8811，不操作用户终端训练。新文件仅innovation，旧证据不改。

本轮实现真正可调用的CPU数值/选择执行器，不只写后续计划。输入为已求得的**完整部署策略×患者**损失及free objective面板，不加载MRI、GT、权重或torch。支持binary exact binomial及continuous[0,1] Hoeffding-Bentkus p-value，按策略取各risk的max，比较同候选的Bonferroni、开发顺序的SplitFST、Dopt Pareto筛选+顺序的Pareto Testing。选定策略的效用估计仍需未见确认。此执行器实现已有强对照，不宣称新理论。

输入边界：每面板最多256患者、128完整策略、8risk/8objective；患者/策略ID唯一。optimization/testing患者集合必须不相交；testing不能出现在事前declared forbidden cohort中。每个候选覆盖同样完整患者，缺失值、非有限值、错误形状、非binary的binary loss和[0,1]越界均拒绝，不能silently删失败病例。风险限alpha与delta在(0,1)，bounded成本不是默认risk；cost为free objective时须非负并含已冻结全部费用。

Pareto规则明确用标准weak dominance：所有维度<=、至少一维<（论文页5Eq5写all-strict的歧义保留）；另提供all-strict复核变体，不称默认完全逐字复现。面板列顺序冻结，策略ID作p值/效用平手确定排序。FST按Pareto Algorithm1使用p<delta，p==delta停止；Bonferroni按LTT使用p<=delta/N。first non-rejection之后不能继续认证。

数值采用80位Decimal，binary CDF先用Fraction精确计算；bounded HB的KL项和e*BinCDF(ceil(sum loss))独立计算后取min，额外上加1e-60保守数值余量。n<=256，alpha/delta限有限十进制有效精度<=30；最终决策用Decimal，不用float显示值或近似相等放宽。此是数值实现，理论保证条件来自原文i.i.d./有效p-value/FWER，不由fixture单独证明。

资格先使用固定synthetic面板：64 optimization/64 testing、4策略、两个风险（二元harm、连续loss）和total_cost。BASE/MID/CHEAP/DOMINATED固定，预期BASE/MID可认证、CHEAP不通过、weak Pareto剔除DOMINATED，最终选MID。另固定halt/empty/max-risk/tie/角色交叉/缺失/越界验证；不是调参搜索MRI有利结果。独立verifier不得import本执行器，用Fraction/不同Decimal公式复算原始面板的p值、frontier、顺序与选择。

真实使用还需原正式train/56FOV/6能力gate/strict/actual exits通过、充分适配dense/direct/SR和完整候选结果、额外独立calibration与规则冻结证明。当前4已见validation不是fresh testing，8确认及locked IXI关闭；此轮不生成MRI risk certificate、不调用真实队列，不把synthetic面板IDs当患者人数。
