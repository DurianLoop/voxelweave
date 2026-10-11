# 本项目创新候选与下一个医学实验

这是原文核读后的补充研究准备，不修改已经冻结的threshold、gates、split、budget或runner，也不以新paper目录替代医学实证。

最优先的候选仍是：在固定observed CISS、同容量且充分任务适配后，合法局部动作是否存在可重复的真实病灶恢复余量；若有，再学习部署可取得特征到真实action-value的映射，并用affected-window实测成本分配计算。发表表述必须绑定实际观测、patient分布、动作集合与全费用分母。MIRTO已覆盖泛评价协议、阈值转移、多宇宙和训练免费聚合；这些本身不再作为本项目主要创新。

已有 [匹配anchor结果](../MC_RC_MATCHED_ANCHOR_ORACLE_RESULT_2026-10-08.md) 显示GT oracle与部署定位不同：GT覆盖99.9649%前景/99.9229%边界、条件forward省57.6985%，但balanced QDA只省16.7439%，原几何gates0/19。已有 [费用场景](../MC_RC_MATCHED_ORACLE_BUDGET_RESULT_2026-10-08.md) A5患者等权比1.028456773，B5才.857047311，且并未补全全部生产费用。已有 [特征费用](../DEPLOYMENT_FEATURE_COST_RESULT_2026-10-08.md) 全19series cold child23.8487972秒。这里只读历史文本，不重载医学数组，不把oracle当部署定位。

| 待冻结的后续控制 | 要解决的问题 | 若出现此结果，候选如何降级 |
|---|---|---|
| 原强raw-pchip充分适配与native能力参考 | 是否只因原task模型训练不足而有修复收益 | 适配后收益消失，则不进入value head；native经验值不称Bayes上界 |
| 每策略validation-only阈值 + 强calibration-only baseline | 是否普通阈值校准就能带来同等收益 | 只赢弱阈值，则不能称病灶恢复或更优选择 |
| 同阈值动作差分与同实际FP诊断分别报告 | 如何分清map/action质量和operating point | fixedτ无增益、matched FP增益来自放宽，则记录转移来源 |
| 原完整FOV、患者内全部series合并、患者等权 | ROI、删小标签、pooled是否掩盖患者伤害 | 漏检/FP/FN/RVE任一原约束失败，则不能只报Dice胜出 |
| 相同动作/信息/preview曝光的强static、risk/error、cost-only、random、defer | value是否只是error proxy或额外监督机会 | matched强对照追平，则没有value选择创新证据 |
| baseline+定位+preview+action+生成/DC+transfer+任务/后处理完整实际wall | 面积/FLOPs/漏算共享准备是否冒充速度 | 只有条件forward便宜，完整患者超预算则不称加速 |

这些controls须在开发11患者/19series内用患者折来设计，选择频次、阈值及policy的变异要记录；4患者/9series已见验证不能重新贴“untouched”。8患者/12series确认只在动作、模型、阈值、预算、primary endpoint及比较family全冻结后一次打开。GT-informed matched FP、GT定位、oracle action gain仅分析/开发监督，不能偷偷进入部署selector。

同时记录ΔTP、ΔFP、ΔFN与真实病灶命中、患者伤害，支持诊断“哪里恢复了”；不增补本轮invented临床margin，不拿不显著p证明等价。小样本条件上界提示：最终8人即使0伤害也不能支持population risk≤10%的95%保证，因此候选claim优先限定效果/成本证据，风险普适保证需额外独立患者资源。

执行顺序已有：两臂各19998/合计39996/30h合同完成、两final和真实terminal exit0且来源历史冻结 → 56完整FOV两臂全部六能力gates及独立strict真实exit → 三observed臂真实19series费用 → 另冻结充分适配runner/budget → 合法action余量 → H1成立后才value政策和匹配强控制 → 全冻结后8人确认。待原训练结束后优先这条链，不重复合成资格、不断新增准备目录。当前raw仍live、新作业GPU余量不足8GB。

后续作者实现尝试：默认branch目前占位。未来正常公开release后，先核commit/README和实际计时分母、Holm输出，再决定是否复用；不要执行尚未核对源码、不要安装新环境或因API限流请求凭据。本轮已保存可运行CPU审计和失败记录，无法验证的MRI步骤保持明确前置依赖。
