# 现有部署动作上界、直接先例与训练准备

前一goal turn为实质progress：完整542新参考actual exit0/独立audit、GPU checkpointed六分支actual exit0/独立audit、7180冻结链。当前完整35904 session44317经工具重新确认live；不重启，不修改任何用户原终端训练或其他PID。

本轮先做一个有明确边界的反事实上界诊断：使用既有已结束JSON整数TP/FP/FN/TN（不读MRI/GT/概率/model数组），只比较raw_pchip_intensity与raw_pchip_spatial两个2992同预算、同parent、合法observed输入的完整FOV task流程。9series均保留，4已见验证患者先均值；另11开发患者/19series只作训练病例描述。native_reference因用了missing原始像素而排除部署动作。

按整数计数构造Fraction Dice/recall/absRVE，比较固定策略、16个患者一致策略与512个逐series策略。逐series最大fullDice的患者先均值为这**两个现有动作**任意whole-series选择器的乐观上界；它不给新SR/TTA、局部融合或新task模型作上界。完整原六gate联合枚举，包括全患者full/missingDice正、无series零TP；费用暂置0只为乐观资格上界，不能称净收益或费用匹配实验。真实gain/risk/controller全费用仍须后续实际运行。

文献检索5组bounded EuropePMC TITLE_ABS查询，pageSize8、每响应400KB、TLS验证、只发送公开研究关键词、不上传病例；索引/摘要不计主文阅读。选择与本项目直接相关的新主文后冻结DOI/PMCID与范围，再获取XML/文本并保存。主文完整阅读、定向阅读、表/公式/图像和补充材料区分计数。已有论文不再计新。

同时准备checkpointed六臂2992训练与optimizer/terminal capture/full-inference费用资格，保留原schedule/几何/母GT/两输入三模式、优化器reset与六医学gate。只有完整35904实际exit0+独立v2 audit、完整GPU费用资格及fresh整轮资源准入后才启动正式训练。19998parent仅开发能力诊断，不用于严格LOPO外折。确认8患者12series/lockedIXI关闭。

CPU1/below-normal、RAM/disk8GB、stage2MB、其他既有allowance16.8MB保留，oracle wall120秒、检索wall300秒。新目录只写innovation，不安装、不委派、不删历史、不更改绑定源码。没有可发表且独立确认的claim，目标active。
