# 基于既有工作保留的创新假设及否证路径

当前没有可发表且独立确认的claim。更合理的优先问题是：先把普通3D病灶task在患者间泛化做充分，再问合法采集信息是否在同预算、同信息、同容量控制之上，改善具体SR动作的病灶净收益选择。以下是研究准备，不是预注册的最终确认协议。

## 现有项目证据指向泛化不足

以下数值复核自既有完整FOV终态receipt，只读其JSON，不重新打开病例数组。训练19998 parent加2992 matched续训。开发患者11/19series的分数来自训练过的患者；已见验证患者4/9series不作为新独立确认。

| 分支 | 开发 full Dice | 已见验证 full Dice | 验证 missing Dice | 验证 recall | 验证 absRVE |
|---|---:|---:|---:|---:|---:|
| native_reference + intensity | .8629 | .4683 | .4704 | .5599 | 1.1123 |
| native_reference + spatial | .8666 | .5219 | .5213 | .4534 | .4837 |
| raw_pchip + intensity | .8808 | .5183 | .5194 | .5129 | .5120 |
| raw_pchip + spatial | .8609 | .4632 | .4628 | .4467 | .9321 |

来源：[开发终态](../development_capacity_after_matched_2026_10_09/evaluation_attempt01/receipt.json)、[已见验证终态](../spatial_adaptation_matched_2026_10_08/evaluation_attempt01/receipt.json)。验证36生产+独立实现数值gate通过，但四分支都未达原六医学gate。空间增强的native Dice上升同时recall下降；部署raw的空间增强Dice下降。这些事实不能推导“所有空间增强无效”，也不能靠新模块开发集loss低来证明突破。

原六gate：[原协议](../spatial_adaptation_matched_2026_10_08/EVALUATION_PROTOCOL.md)要求患者先均值fullDice>=.70、missingDice>=.65、fullrecall>=.70、fullabsRVE<=.50，四患者full/missingDice均正，无series零TP。保留原分母与端点，不降低。

## 宽泛组合已经有先例

[三篇新主文与作者源码记录](PRIMARY_FINDINGS_AND_NEXT.md)已排除把physics-conditioning、MC variance gate、domain unlearning、普通GIN/SSC或TTA单独当创新。DG-TTA强增强后自适应收益可小或负；UAF-AIMM自适应相对前一模块增量仅.47；PEIL已有按solver下游效用学习物理conditioning的思想。各自数据/监督/端点与本项目不同，不能直接移植其医学效果。

## H1：采集信息改善动作净收益决策

部署输入只含真实observed MRI、合法geometry/spacing/采集信息、mask及由这些输入计算的特征。native missing pixels、GT病灶ROI和验证GT不能进入部署controller。native_reference仅能力诊断上界。

候选动作a应是预先冻结的可实际执行流程（例如原输入直接任务、固定SR后任务、明确预算的自适应流程及defer），不是把三种分辨率训练增强直接叫临床SR动作。每一动作都需分别生成完整FOV预测，再与相同母GT配对；联合动作要真实重跑，不能相加单动作收益。动作失败/fallback/defer均计入患者分母。

在开发内折定义患者级损失L_p(a)和费用C_p(a)，比较G_p(a)=L_p(a0)-L_p(a)-lambda[C_p(a)-C_p(a0)]。lambda、FN/FP权重、费用单位、医学安全约束和主比较family须在开发内折冻结；本文件没有选择最终值，也不在已见验证或8未见患者上搜索。

若risk模型r(x,a)估计同一个L_p(a)，则r(x,a0)-r(x,a)就是收益估计，gain-head换名不构成创新。H1需超过同信息/容量的action-risk差、QC加defer、去采集与metadata-only，以及static/always-none/always-action/费用匹配random；与最强普通训练增强及明确固定步TTA的增量分开报告。SSC12通道要raw复制/同容量与descriptor全费用控制。

先在严格患者内/外fold中判断真实动作余量：包括task训练、teacher、localization、feature变换、gain/QC/UQ/cost校准、阈值/停止全部不得见外折任何series。含11开发GT的parent不可作LOPO外折warm-start。先做余量诊断仍可能只支持“当前强基线下无有效动作”，这也是保留的负结果。

## 继续顺序与停止条件

1. 完整35904分辨率/强度合同从头检查真实exit0与独立audit；GPU graph成功不替代该合同。
2. 六臂部署/参考输入×三种普通分辨率增强的完整optimizer、capture、推理与费用资格，以及fresh资源预算；随后同parent/预算对照可用于开发能力诊断。
3. 强GIN/SSC与适应对照各自独立资格及患者fold cold-init。若泛化改善、真实paired动作余量存在，再冻结H1 controller及强风险控制。
4. 冻结统计family、原医学gate、主患者端点与全费用后，才一次打开8未见确认患者12series；lockedIXI继续关闭。独立第二任务实现仍必要。

无动作余量、普通增强消去采集信息增量、同信息risk/QC控制消去增量、费用匹配后失败，或未见患者不复现，都记录负结果并收窄或放弃对应claim。当前读到的来源与这轮GPU小诊断不证明“首创”或可发表性。
