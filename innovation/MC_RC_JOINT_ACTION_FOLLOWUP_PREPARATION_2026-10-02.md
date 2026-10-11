# 新联合目标的后续准备：原收益头分支继续停止

本页是五人约束/常数事后诊断后的新研究准备，状态prepared_not_executed，不恢复原失败分支，不自动开始训练。依据[数值结果](MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md)和[六篇先例](literature/2026-10-02_constrained_oracle_prior_art_recheck.md)，优先检验可见信息是否同时辨认支持域收益和局部病灶代价。

| 需回答的问题 | 下一项具体工作/对照 | 当前状态与停止条件 |
| --- | --- | --- |
| 可见特征是否有信号 | 为固定五开发患者另写预测诊断合同，按患者leave-one-out；特征仅真实观测、phase/spacing/可用采集头、raw/HAT及delta。先低容量回归，特征标准化/阈值仅fit患者；隐藏参考/人工mask只造监督和评估 | 尚未提特征/训练；五人LOPO仍是开发，不是独立确认。若超不过同容量误差预测、phase/spacing、动作幅度和共同系数，则停止预测分支 |
| 局部代价是否能从合法区域信息预测 | 比较无任务特征与冻结分割模型产生的预测区域/边界特征；人工mask方法仅oracle。加入SafeRestore式候选entropy、任务输出差、残差幅度等可见风险路由对照 | 尚未在MC-RC运行任务模型。仅001有活跃约束，不能据其10块训练一个声称可泛化的病灶守卫；需更多来源合格开发患者和真实失败分母 |
| 联合目标是否超出增加模型容量 | 相同可见输入/容量/步数/预算：支持域动作收益、普通base绝对误差、双区域动作代价；常数混合、连续共同系数训练基线、随机匹配接受率、简单规则必须保留 | 未选最终网络/调参，不采用真值constraint alpha作部署特征。若只有更大容量有增益，不能归因联合目标 |
| NMSE保护是否兑现任务收益 | 完整缺层、原生网格、全部固定患者的冻结任务模型Dice、HD95/物理表面、病灶体积；空标签按原空值规则，按患者汇总；同时保存支持域和两病灶NMSE | 尚未做MC-RC任务。NMSE守卫不能替代Dice/病灶检出；若影像收益但预定任务守卫失败，记录失败 |
| 是否能独立确认 | 先审核MC-RC其余候选的原生头/标签与身份，患者所有时间点整体分组，排除全部58名与VS-SEG共享者；划分开发/验证/校准/确认前冻结名单与hash | 71候选/159 T2只是标签目录范围；未全部原生审核，不能称71合格确认患者。已有五开发患者与已用于设计的VS-SEG不可当未见确认 |
| 若需要风险certificate | 定义患者级事件率、两端点分母/界值、覆盖、政策族错误预算；独立调阈值和认证，完整病例固定政策一次评估 | 暂无临床界值/足够认证来源；不拿1e-10数值精度当临床不劣，不把tile数当独立样本。不照搬SafeRestore图像i.i.d.到同一患者相关缺层 |

可直接复核本阶段的命令（均CPU，成功产物不覆盖）：

```powershell
D:\conda\envs\MRI\python.exe -B innovation\experiments\verify_mc_rc_five_developer_constrained_oracle.py
D:\conda\envs\MRI\python.exe -B innovation\literature\verify_mc_rc_constrained_stage_archive.py
```

尚不能执行的训练/校准不提供伪可运行命令。先把患者角色、目标、损失、允许输入、共享特征、固定对照、资源预算、停止条件写入新的独立合同，再做CPU低容量诊断；GPU训练等待真正需要时安排，当前不占GPU。无真值SURE/ENSURE/重复监督仍需真实观测/噪声来源，真实厚层恢复仍需PSF/采集合同，保留未验证状态。

原session83910固定45 CISS+1 TSE队列继续推断及自动再生成/输出核验/主分析。完整结束后按原合同运行vs_seg_selection_sensitivity.py，不能提前利用动态子集决定当前设计。原HAT−pipeline PCHIP两主要方向和001/202 Dice反证保持。科学goal active，尚无独立验证claim。
