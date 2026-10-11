# 两路径成本头与收益表示：公平比较及标签准备

已有 [17特征/真实标签合同](../OBSERVED_FEATURE_TO_ACTION_UTILITY_PREPARATION_2026-10-08.md)、[强适配准备](../TASK_ADAPTED_ACTION_UTILITY_NEXT_PREPARATION_2026-10-08.md)、[现有完整series适配器](../experiments/patient_complete_series_panel_2026_10_07.py)与 [新患者暴露审计](patient_registry_attempt03/receipt.json)。本准备不替换这些冻结文件，不重复原57,600合成配置，不制造MRI动作标签。

## 现有metadata可以确认什么

真实feature表19行/11患者与正式任务训练frozen_config的patient/UID完全一致；每患者全部series属于同head fold。11fold的heldout memberships合计19，training memberships190，重复membership不是新MRI样本。两个训练臂共享11患者训练暴露配置，所以11/11 head-heldout患者均被任务网拟合过；标签scope应为development_task_in_sample。训练最终checkpoint尚未读取，不能由配置审计推定最终模型已完成。

11项拒绝检查用真实metadata副本注入组边界/绑定错误，包含少一个series、重复series、错source SHA、heldout混入训练、ID充特征、nonfinite特征、错误task/pipeline患者外声明及绕过真实标签适配器；均实际被拒绝。独立程序另从冻结表和config重建所有分组/特征，全部exact；它核对原拒绝记录，没有冒称重新执行11个异常分支。零MRI/GT/权重数组，零head fits、神经/GPUforward、训练更新。

生产v1路径相对化失败、v2磁盘GB/GiB单位失败均保留；v3另目录真实exit0。新适配器只资格化metadata registry/folds与未就绪拒绝，**实际任务label bundle连接仍未资格化**。不可把本目录当成已经能训练MRI收益头的工具。

## 不把双头容量差当收益机制

预先选择连续患者端点Q（越大越好），定义C0=1−Q0、Ca=1−Qa、g=Qa−Q0=C0−Ca。已有cost-sensitive/defer已覆盖按条件预期成本选动作。若预测Ca/C0分别各配完整MLP、仅g配一个MLP，两者总容量不相等。

后续可审查的候选比较是所有臂共享同一隐藏trunk、两个**有真实监督**的scalar输出、相同参数/正则/优化预算：一臂直接表示(C0,Ca)，另一臂表示(m,g)，其中m=(C0+Ca)/2；两输出都参与loss，不放无监督dummy输出凑参数。以17维输入、8hidden units为容量说明，17→8→2含162个参数；当前17维是series特征，最终患者/action/state聚合与新增特征尚未冻定，这只是表示匹配示例，不是已训练或最终网络。

比较必须分成两个有不同含义的条件：

| 条件 | 目标 | 能解释的结果 |
|---|---|---|
| 等价损失控制 | 成本平方误差和 = 2(m−m*)² + (g−g*)²/2 | 只是同一预测函数的线性表示变换，不能算新算法 |
| 直接收益损失 | 明确冻结gain与nuisance权重，所有输出有监督 | 可能是有限样本的paired目标/正则差异，需MRI实测，不能称新Bayes决策 |
| 双错误率/既有defer | 同合法observed与任务状态、相同总head资源 | 排除宽泛“预测相对优势”已有方法解释 |
| baseline-only风险/observed误差 | 同信息与总预算 | 有用的较弱控制，不能代替上述强控制 |

两独立成本head与共享双输出head可以作为不同预先定义基线分别报告，但不能用不同信息或成本预算决定胜负。Gain>0概率与E[g]目标不同，保留旧目标审计；若安全harm约束另定义risk head、其训练/探测成本和输出参数也计入。

## 真实label bundle仍需补齐的字段

patient + 完整series集合；当前state与候选动作；合法observed/source SHA；各路径任务checkpoint SHA及其训练/调参/预训练患者role；完整FOV Q0/Qa、原端点定义、每series配对结果；完整共享/每series相位成本和墙时边界；失败/空预测/超预算/defer状态。患者utility先患者内series等权、患者间等权；cost合并series并只计一次shared费用，沿用旧complete_panel，不重实现另一个平均规则。

失败或缺任务分数不可填0、不可删行。所有成功/负/零/失败都在完整动作ledger；是否能形成用于拟合的完整label面板须另资格化。训练标准化、head、阈值/超参选择全部限train patients，患者全部series/action/state归同fold。开发内oracle动作评分只生成监督，不能冒充部署反馈。

## 患者外结论的两条合法路线

1. 用目前已充分适配的开发内任务网生成开发内配对label，诚实写task-in-sample；head-only患者留出用于开发选择。待方法/端点/action/budget/全部checkpoint最终冻结，八未见确认患者/12series验证整个pipeline；确认结果不反向调参。此路线不要求为普通经验论文另建formal calibration。
2. 若必须报告开发内整个pipeline患者外，另立fold-specific task训练及所有learned-component暴露合同。排除heldout不仅针对任务网，还包括有监督/无监督预训练、restorer、learned scaler与调参；只给task checkpoint贴未见ID不够。不得拿已训练所有11患者的warm start后少量finetune伪装排除。其训练/标签生成成本另实测，不能由当前26h估计自动授权或外推11倍成功。

本次registry把task未见但其他组件不明的scope保留null；已知task见过则pipeline患者外明确false。声明和ID审计只是必要条件，不能证明IID/无任何间接泄漏。4已见验证/9series、8确认/12series、lockedIXI与旧MIRA/MSValid84角色不回改。

## 待原训练结束后具体执行顺序

原两臂各19998真实terminal exit0/最后冻结→原56完整FOV/全部6能力gates/独立strict→同信息同容量dense/direct/common-projected充分适配→固定动作完整患者余量与实际全成本→必要时head及上述cost/defer/DC-based强控制→最终冻定未见确认。当前gate没有通过，任何label拟合入口都应继续拒绝。TACKLE/DCATS先例的加入不得回写原基线或从中间loss挑winner。
