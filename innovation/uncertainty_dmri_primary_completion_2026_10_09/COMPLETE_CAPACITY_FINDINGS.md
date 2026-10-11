# 完整76开发与36已见验证：能力诊断的决策改变

真实8042cc整体exit0、无session_id，全部四last2992/76 production+76 independent functional FOV完成，elapsed4169.07s。原capture真实288edd exit0独立核全部19series/11患者、来源及概率3e-6/float64坐标3e-12/二值零差。冻结准备入口随后真实7e4c67 exit0，Fraction重新计算全四臂76开发+36已见验证、四region/五指标，所有undefined传播null并保留分母。

| 分支 | 开发full Dice | 已见验证full Dice | 开发recall | 已见验证recall |
| --- | ---: | ---: | ---: | ---: |
| native/intensity | 0.862924 | 0.468329 | 0.889303 | 0.559930 |
| native/spatial | 0.866582 | 0.521877 | 0.843003 | 0.453378 |
| raw PCHIP/intensity | 0.880839 | 0.518307 | 0.863256 | 0.512911 |
| raw PCHIP/spatial | 0.860915 | 0.463237 | 0.846439 | 0.446741 |

四分支开发患者先均值均通过原四能力参照（fullDice.70/missingDice.65/recall.70/absRVE.50），因此优先级转向泛化/普通增强控制。不能把它表述为每个开发患者都达到全部条件：例如native/intensity的011 fullDice.648501、missingDice.616541，raw/spatial的011 recall.687117；这些失败保留。它说明现网络不是在全部训练患者完整FOV上普遍弱，不能排除个别患者容量/训练或处理问题。

全部四分支原六验证医学门槛仍未通过，native spatial均值改善此前只由1/4患者为正、四人recall均下降；开发spatial的native recall也比同预算intensity低。完整数据不支持把空间增强均值改善直接称稳定病灶净收益，也不支持宣布SR动作claim。两组不同患者/采集/病灶构成，组均值差不是单因素因果证明，更不是独立未见确认。

下一具体步骤：先用冻结28series的合法采集metadata及已有GT体积计数作全队列描述，核异常/分布差异，不加载验证影像或GT数组；不能据4已见验证选择阈值、checkpoint或增强参数。普通resolution/support/reliability六臂入口继续保留；必须等35904强度资格真实终态审计，并容纳六final33.73MB及输出余量后才启动。GPU授权有效但当前free1394MiB仍低于原8192门槛，磁盘储备之外约14.7MB；不动用户训练或删历史。

随后在严格患者fold内训练task/gain/QC/UQ；全11GT parent不能作为外折初始化。创新只考察充分普通task后采集信息对真实paired动作净收益是否有增量，保留全部控制与全费用。8确认12series及lockedIXI关闭，goal active。

[全量比较数据](../conditional_uq_and_task_capacity_followup_2026_10_09/complete_comparison_attempt01/receipt.json)、[开发独立审计](../development_capacity_after_matched_2026_10_09/ACTUAL_DEVELOPMENT_EVALUATION_EXIT.json)与实际工具记录均保存。本文件为6823归档后的新增事实，旧README中的live进度是当时快照，不回写；下一增量归档纳入真正完成的开发输出。
