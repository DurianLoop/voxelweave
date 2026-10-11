# 强对照实现后的真实claim路线

本轮实现并运行了 [患者风险/成本执行器](experiments/patient_risk_cost_baseline_executor_2026_10_07.py) 和 [完整series患者面板适配器](experiments/patient_complete_series_panel_2026_10_07.py)，合成测试不是MRI结果，也不是可发表新机制。它们推进可审核的后续比较，避免只写LTT/Pareto名字而不准备实际执行。

方法合同：同固定策略、完整患者输出、同cost预算，Bonferroni/SplitFST/Pareto都有可调用函数，支持binary风险和continuous bounded loss、多个free objective。默认weak Pareto按标准语义，all-strict变体可比较；FST严格p<delta，Bonferroni p<=delta/N。数值精度和舍入由 [实际补充](PATIENT_RISK_COST_BASELINE_NUMERICAL_AMENDMENT_2026-10-07.md) 固定，已执行源码/snapshots保留。

验证范围：9个独立重放的选择场景、104个risk p值；患者面板包含不等series数量、所有费用、精确harm/RVE事件与30位保守舍入。缺失/重复/GT入推理/费用漏项均在合成资格中拒绝；独立verifier重算完整结果，但对异常分支只核原拒绝记录。声明FOV或cost字段不证明原MRI实际执行，真实数据还须绑定最终评价/成本记录。

重要范围：额外fresh calibration缺失只阻止**正式高概率风险保证**。用户目标是一个真实、可发表的MRI claim，并未要求必须证明这种统计保证；不能自行把fresh calibration增加成任何经验效益论文的硬前提。仍可用已知LTT/Pareto的结构作为开发期强选择控制，冻结完整策略后在8未见确认上比较经验MRI效益；若没有独立calibration，须明确没有正式RCP保证，不能称已认证。理论条件未满足时不会由本执行器发出MRI certificate。

执行顺序保留原合同：99542真实exit0/两臂last19998；原56FOV/4验证患者6能力门槛/独立strict/actual receipts；真实资源资格；充分适配dense/direct/SR；合法observed特征与完整patient联合策略；总成本与cost/defer/union-greedy/random/LTT结构/Pareto结构比较；冻结后8确认。旧理想坐标门槛失败不覆盖，locked IXI关闭；旧MIRA/MSValid84确认单独存在。

可发表claim的候选仍是：在明确的MRI任务/退化与扫描范围内，合法observed信息选择联合修正，在相同真实总成本下，对充分适配基线有超过上述强控制的完整患者收益，并在规则冻结后的未见确认复现。需要区别Dice分式、overlap、weak baseline和选择偏差解释；没有该剩余收益就保存负结果，不把库资格、数值正确或通用反例改写成创新成果。

[真实输入模板](PATIENT_RISK_COST_REAL_INPUT_TEMPLATE_2026-10-07.json) 留空真实证据字段；模板不能通过生产输入验证，后续仅创建新填充文件，不覆盖冻结模板/来源证据。
