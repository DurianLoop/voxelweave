# 完整患者策略：风险、成本与效益验证准备

本文件补充已有 [后续实验顺序](CALIBRATION_AND_ACTION_GAIN_FOLLOWUP_2026-10-07.md)。新的可发表claim未确认；LTT/Pareto是强已知控制，不是本项目创新理论。真实资源入口实现与合成资格均不能证明MRI效益。

| 候选说法 | 已有直接机制 | 本项目下一项可区分验证 |
| --- | --- | --- |
| 非单调、多risk安全策略选择 | LTT Theorem1/Proposition6 | 同固定候选/损失/数据预算与LTT比较 |
| risk约束下优化cost，多维参数联合选择 | Pareto Testing Algorithm1 | 同observed信息、完整患者FOV与实测总cost |
| learning test path/Pareto front | SplitFST/Pareto Dopt | 候选/排序只在开发或独立opt split学习 |
| 独立随机混合安全配置 | Pareto Corollary5.2 | 与完整observed特征router比较，router另作候选 |
| 正部退化风险 | Pareto Eq7的D+ | 本项目明确Dice正部/病灶召回/体积风险定义 |
| MRI联合修正具有额外净收益 | 当前尚未验证 | 充分适配dense/direct/SR、强cost/defer/union-greedy/random后仍改善 |

执行依赖：session99542真实结束且native/PCHIP各last19998冻结，先记terminal exit，再原56FOV评价、4已见validation的全部6能力门槛、独立strict与actual receipts。任何缺失都不启真实两通道资源资格；任何能力失败先诊断能力，不能新资格覆盖原失败。旧direct理想绝对误差门槛仍失败，其float解释器通过不能抹去失败。

资源资格CPU或GPU通过后，dense与direct用共同canonical初始化/1,401,795参数、同PATCH/batch2/监督draw/增强/损失/AdamW LR/WD .0001，另立正式充分适配预算；资源测试68更新权重全部丢弃。SR需明确相同observed信息和充分适配；不拿当前弱的临时资源权重做效益比较。

患者是评估与统计单位。先每series完整FOV求原.5阈值指标，再患者内series等权，最后患者等权；不得用tiles/多series增加独立n。GT只用于开发监督与冻结规则评价，不进入候选生成/推理。对joint策略须跑empty/single/pair/union真实系统，扣Dice分式与重叠影响后再判增益，记录部署可得feature能否预测该增益。

风险定义候选准备（尚未在MRI数据上校准）：L_Dice=1-患者平均Dice∈[0,1]；L_drop=max(0,患者Dice_base-患者Dice_policy)∈[0,1]；L_harm=1{患者下降超过事前eps}可用binary检验。未截断absRVE和无上界total wall cost不能直接用同一bounded/binary检验；可预定义tail事件1{absRVE>tau}/1{cost>B}，但保证的是超标概率，不是原数值均值。裁剪loss必须将对应保证清楚标为裁剪指标。

每一个被检验候选是**完整部署策略**，含候选生成、feature、gate、SR/direct/fallback组合、融合、.5阈值、完整patient输出；不是单个安全arm。一个解析提醒：三个observed亚群概率(.08,.08,.84)，A仅在第一群harm、B仅在第二群harm，则两arm各risk .08；独立随机任一混合仍 .08，但按X分别选择A/B会到 .16。此为手算已知选择反例，未运行MRI，也不声称新定理。需要单独评价和认证该router。

强对照统一固定候选/信息/监督/容量与总成本：always baseline、always action（预算单列）、两risk两cost cost-sensitive/defer、union-greedy、同预算random、LTT Bonferroni/SplitFST、Pareto Testing。LTT/Pareto移植要保留独立opt/testing数据或事前顺序；同calibration排序并作未校正FST已被本轮精确反例排除。认证集合内效用选择的risk保证允许复用testing数据，但所选效用仍需未见确认，不能当无偏泛化结果。

费用至少包含observed加载/归一化、SR、candidate探索/预跑、feature scoring、gate、FOV warmup、cache、host/device搬运、最终infer；开发时探索cost与部署cost分别记录、全部公开，不能仅计被选tile。当前并发负载下resource timings不称稳定benchmark。

数据缺口：11开发/19series、4已见validation/9series属于开发证据；8确认/12series继续关闭，预留规则冻结后的终检，不另充calibration再称未见确认；locked IXI test关闭。若需要正式risk guarantee，须新独立calibration来源及患者人数规划。即使假设n4新独立且零错误、binary alpha=.3，p=.2401仍不能过delta=.1；实际4人更无fresh资格。无足够独立数据时只报告经验效益及范围，不伪称认证。旧MIRA已有MSValid84患者确认仍单独成立。

否决条件：充分适配后无真实余量；feature预测不能超随机；效益被cost/defer、union-greedy、LTT或Pareto解释；成本计全后优势消失；8冻结确认未复现。相应负结果保留。存在MRI特有剩余差异后，再准备第二任务模型/数据源与真实独立确认，不能以原理反例代替。
