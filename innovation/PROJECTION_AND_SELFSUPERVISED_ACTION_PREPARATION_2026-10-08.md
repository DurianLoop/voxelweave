# 下一步：区分输入变换、观测一致性与患者动作收益

新rank/合成见证和Noise2Self/SSDU核读改变的是下项受控比较的解释与准备；没有当前MRI任务收益，goal仍active。PCHIP、noncommuting resampling、mask、自监督risk、SSDU和成本路由不是单独创新。

1. 继续同live session99542，不重启/迁移或控制用户终端训练。两臂各19998/总39996、共同初始化/样本/监督、CPU4/interop1、float32、AdamW lr/wd=.0001、30h/8GB储备/250MB合同不变。真实final退出且两臂最终冻结后，原56FOV/全部6gates/strict先完成；本轮没有读取任何中间任务效果。
2. 原两通道direct/dense资格保持；后续workflow比较仍使用同raw观测源，有实际意义。若要归因PCHIP恢复先验、direct利用效率或MR修正收益，额外准备**从共同投影observed anchors开始的两路径控制**，保留原native-PCHIP先生成和旧one-channel参照。先明确统计来源、两臂同availability、边界fallback/tail/physical坐标及预算，再实现独立模块/版本，不能覆盖旧qualifier或原观察保持合同。
3. 本轮共同投影路径只在合成例子运行。若继续到MRI，另冻全19开发observed-only协议，核所有实际observed包/索引/输入hash、fractional mask及完整FOV成本，不读取隐藏MR/GT构造输入。该控制改变预处理顺序和有效输入范围，应作为因果解释的附加对照，不重新命名主方法或用更弱来源制造SR优势。
4. 如将观测留出误差作为动作收益特征，先冻结heldout层/点、实际层距与fold；mask在一切会混合目标值的插值、特征和统计操作之前确定，训练/部署信息范围分别记录。J-invariant理论需另外核全部函数依赖、条件噪声独立与无偏；未满足不发理论证书。普通经验特征比较无需为了经验任务论文额外索取这些理论条件。
5. heldout信号误差不是任务benefit。实际配对端点为同一充分适配baseline下的完整患者Q(动作后)-Q(基线)，收益/损害/零收益均保留；整患者cross-fitting，成本先合并全部series，再患者等权。控制同信息/容量误差/风险头、固定最佳合法动作、cost/defer、预算随机与union-aware greedy；初始化、定位、动作生成、探索、transfer、infer、后处理全部实测。
6. 联合/连续动作从当前状态做差分，不能将单动作增益相加或按静态N+m*k外推；最终checkpoint的full/cached及任何新布局重新核输出/硬预测/完整FOV。面积gate不代替总预算，费用流程A/B按真实实现事先规定。
7. 强适配后若无稳定可修正余量，或优势由输入投影/已知baseline解释，记录受控负结果，不包装新的方法首创。若开发内仍有配对净收益，再冻结方法/端点/预算/threshold/checkpoint，才8确认/12series与第二任务网；4已见验证不更名新确认、lockedIXI关闭、旧MIRA/MSValid84证据保留。freshcalibration仅约束正式风险保证。

待验证claim仍为：在合法raw观测预算和完整实测总成本相同的条件下，动作可获益性预测优于强已知控制，改善预定完整患者病灶端点并在冻结确认复现。当前效应量、区间、确认均未得；本轮精确rank是输入诊断，不把它替代MRI效益发表目标。
