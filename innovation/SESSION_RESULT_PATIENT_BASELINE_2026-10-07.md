# 可复用患者风险/成本强对照：本轮结果

本轮有实质progress：将已读LTT/Pareto方法落实为可调用的强对照，完成三个合成资格及两个独立核验；**尚无已确认可发表的新MRI claim**。未新增论文原文阅读，不把之前两篇重复计为新论文。

Bonferroni、SplitFST、Pareto支持binary exact binomial、continuous bounded HB及多risk max-p-value；相同固定患者/策略面板，正确处理first non-rejection、空认证集、阈值边界、多free objective和weak/all-strict Pareto差异。独立Fraction/120位Decimal以不同公式重算9个选择场景、104个risk值、全部frontier/排序/认证/效用选择一致。生产12项非法输入检查通过；独立verifier对拒绝分支只核记录，不冒称重新执行异常分支。

完整series适配器要求所有(patient,UID,policy)覆盖；风险患者内series等权、患者间等权；总cost求和所有series再加一次shared cost，并要求9项费用显式存在。固定不等series数例子MID患者Dice .575，而错误series平均 .633333...；BASE对应 .5/.6。三分之一rounding资格确认连续loss上舍入、binary harm/RVE事件在精确Fraction上判定。独立重放3个面板/8患者策略行，全部原始metric、loss、成本及rounding通过。另一组12项缺失/重复/GT入推理/费用漏项等拒绝通过。

数值限制与真实使用边界已记录：[实际舍入补充](PATIENT_RISK_COST_BASELINE_NUMERICAL_AMENDMENT_2026-10-07.md)、[完整series协议](PATIENT_COMPLETE_SERIES_PANEL_PROTOCOL_2026-10-07.md)、[真实输入模板](PATIENT_RISK_COST_REAL_INPUT_TEMPLATE_2026-10-07.json)。模板没有真实MRI结果或通过的先验，不可直接使用为证据。

新独立calibration是正式风险保证的条件，不是所有经验MRI效益claim的必需条件；该执行器不自行发MRI certificate。完整策略冻结后8未见确认仍可验证经验效益，只能报告已被实际证据支持的范围。通用方法正确、合成资格和输入计数本身不是创新或MRI收益。

最新实际poll ea302f，同session99542仍live，native9306、invocation02新增9207、累计20496.50812969997秒；两臂last19998/总39996尚未完成；PCHIP99为历史。GPU实际21:28:37.609仍1394MiB空闲。既有正式训练单独持续，本轮新增MRI/GT读、model/GPUforward、训练更新均0。11开发/19series、4已见validation/9series、8未见确认/12series与locked IXI角色保持；旧MIRA/MSValid84确认存在。

下一步仍先原train/56FOV/6能力gates/strict/实际exits，再真实资源资格及充分适配dense/direct/SR。有真实余量才验证observed-only特征、联合策略、计全成本强cost/defer/union-greedy/random/LTT/Pareto，最后冻结确认。全文执行与claim边界见 [后续路线](RISK_COST_BASELINE_AND_CLAIM_SCOPE_FOLLOWUP_2026-10-07.md)；[公开对话](SESSION_VISIBLE_DIALOGUE_PATIENT_BASELINE_2026-10-07.md) 已保存。
