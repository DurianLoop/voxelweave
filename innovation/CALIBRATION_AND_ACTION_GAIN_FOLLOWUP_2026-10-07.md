# 风险校准与动作收益的后续冻结准备

本轮阅读和合成反例改变了强对照/保证条件，尚未放行真实MRI新任务。现有session99542必须先真实结束，两臂last19998冻结，再执行原56FOV和6项能力gates/独立strict核验；不按中间loss调预算。8确认和locked IXI test关闭。

## 候选与可失败命题

| 候选 | 必要已知对照 | 可失败条件 | 当前状态 |
|---|---|---|---|
| 单例/局部修正收益的合法特征预测 | 完整双路径risk/cost-sensitive、同容量defer、risk排序、matched random、强dense/direct/SR充分适配 | real oracle无正余量；或收益预测不赢两路径成本 | 前置MRI能力未结束；本轮仅合成反例 |
| 实际联合修正与共享计算的预算策略 | 真union-greedy、实际组合FOV评分、随机同预算、原始counts/Dice解析分解 | 优势由Dice分式、支持冲突或并集成本解释；或总预算计入后消失 | 既有action-composition工具已备，未获真实病灶正收益 |
| 修正伤害的统计控制 | CRC原monotone设置、已知单调包络，必要时读Learn-then-Test等finite-policy先例 | 不满足patient exchangeability/独立calibration/终点loss；或保证只来自全部拒绝 | 不承诺当前4/8患者安全保证，后续方法级查新待补 |
| 强稀疏基线消除SR收益的受控负结果 | 同信息/容量/训练流、既有mask/NConv/partialconv、统一geometry | 弱baseline/不充分训练/后验挑子集解释结果 | 公平配对实现已过合成资格，真实资源资格尚未实现/运行 |

## 真实任务执行顺序

1. 保持原正式训练和原56FOV评价；原gates失败时先诊断能力，不制造SR胜弱baseline。采用[只读readiness协议](MC_RC_3D_PAIRED_RESOURCE_READINESS_PROTOCOL_2026-10-07.md)核真实exit与SHA，不能以JSON complete猜进程结束。
2. 能力通过后实施真实19series/fullPATCH/batch2资源资格，记录全部缓存/搬运/forward/backward/checkpoint恢复成本。CPU或已授权GPU按真实资源固定；不得迁移正在运行的recipe。当前GPU总量查询空闲仅1394MiB，新GPU启动门槛8GB未满足。
3. 冻结独立dense/direct/SR充分适配配方，复用本轮已验证paired draws/two-channel FOV。选定校准施加位置；最终FOV后温度缩放与tile前缩放不是同一操作。保留旧one-channel，分清padding增强改变、mask输入改变和SR信息表达改变。
4. 有稳定真实修正余量后，固定GT-free候选集合/特征/成本，开发GT仅作监督和诊断；部署infer不得接GT/ROI。训练risk0、risk1和gain控制时保持同feature/capacity/supervision/patient split，允许“不修正”。收益差头与两成本头本身都是已知cost-sensitive实例。
5. 每患者完整FOV记baseline、policy、fallback全部结果；单独记接受比例和接受域结果但不能替代完整队列。标明always-action不同预算。费用含observed加载、SR、FOV warmup、缓存、候选探索、评分、policy、搬运，不只计执行被选tile；patient-first等权多series，保持原.5门槛。
6. 有联合策略时记录empty/single/pair/union实际系统loss及cost，扣Dice分式效应和threshold/support影响。若考虑CRC，先冻结patient loss函数、保证类型、loss上界B、monotonicity/right-continuity/可交换假设与合法lambda_max；原文已有包络处理须作为对照。**FNR控制不等同Dice/体积/每病例安全。**
7. 完成开发选择后一次冻结8确认/12series规则，不能把确认8重新用作阈值训练/calibration，再称未见确认。当前4已见validation只提供开发证据。需要额外独立calibration/更多确认来源时记录缺口，不因series数多就虚增患者量。

若充分适配没有余量、收益不可预测、或已知cost/defer/union-greedy解释全部增益，保存负结果，停止相应正向claim。可发表性仍需真实确认、强对照、精确范围与第二任务模型验证；合成资格和通用反例不替代这些。

