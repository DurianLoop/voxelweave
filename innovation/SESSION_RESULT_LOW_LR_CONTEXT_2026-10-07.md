# 低学习率接续阶段结果

本阶段新增3篇原文、3篇重点摘要，完成两臂共2048次单001低LR全骨干更新、66次全部丢弃的多患者资源更新，以及两臂全19series各1139tile的完整FOV计时。科学确认患者0，可发表claim尚未确认，长期goal active。正式19series训练尚未启动。

native最后模型full Dice .967647、recall .976261、absRVE .017804；PCHIP .963253/.972305/.018793；两臂均过原单系列拟合gate。全部history、模型/预测SHA、三head functional/module、四域端点、生产和NumPy坐标及float64独立核验通过。旧native空预测未在低LR下复现；两臂不同初始权重，这不是公平SR效益或唯一病因证明。旧高LR失败保留。

HCC原文中AUC上升伴accuracy/sensitivity下降、主要DeLong差异不显著；Madras2018和Mozannar2020已经覆盖按两路径预期损失选择gate。因此单独gain head不支持方法首创。下一待检验问题是充分适配后是否仍有稳定、可预测且可独立确认的病灶修正余量；加入双路径成本头、已知defer、强PCHIP、直接任务、普通风险/误差和同预算随机等强对照。57,600配置合成gain目标检查及独立复算通过，仅为已知理论实现核验，无MRI效果。

资源资格两臂各33步、全19series覆盖、各患者3步、GT/增强一致、梯度有限；最终更新后权重丢弃。完整FOV计时无GT/任务评分，其独立核验只针对metadata/时间。正式多患者CPU预算现在可以依据完整实测准备，仍需共同随机初始化的正式入口及资格。GPU授权保持，最新物理GPU观测单独保存；不操作用户终端训练。

角色仍11开发/19series、4已见验证/9series、8保留确认/12series，当前四验证效果未在本阶段打开，八确认和locked IXI test关闭。没有改根环境或.gitignore。可见请求、公开进度、用户接续摘要、论文来源/版本/失败、脚本和结果均保存到innovation；未展示的历史原话不伪造。修复图v2已在本次直接view_image核看，原false快照/遮挡v1保留。

[拟合与独立结果](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_RESULT_2026-10-07.md) · [资源成本](MC_RC_3D_19SERIES_CPU_RESOURCE_AND_FOV_RESULT_2026-10-07.md) · [创新判断](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md) · [defer原文阅读](literature/2026-10-07_learning_to_defer_primary_collision_reading.md) · [HCC阅读](literature/2026-10-07_hcc_sr_task_primary_reading.md) · [gain目标审计](TASK_GAIN_TARGET_CPU_AUDIT_RESULT_2026-10-07.md) · [真实退出ledger](SESSION_EXECUTION_LEDGER_LOW_LR_CONTEXT_2026-10-07.json) · [可见对话](SESSION_VISIBLE_DIALOGUE_LOW_LR_CONTINUATION_2026-10-07.md)。
