# 原MRI项目结构与本轮创新边界

本轮只读核对D:\MRI\README.md前80行和design\design1_pastnet\README.md前75行，未修改根文件、未读原训练checkpoint或操作其进程；不是新模型/病例评估。文档是历史项目陈述，不替代当前训练terminal、原预测或统计复核。既有IXI资料中的历史描述不作为本轮模型选择或新的lockedIXI评价；lockedIXI像素/GT继续关闭。

原项目是病例级T2 through-plane interpolation，有Linear/Cubic及I3Net、HAT、SMamba等基线。PAST-Net G086已含四sparse anchors、phase/validity/difference/curvature条件、query-specific coarse image、共享encoder/phase soft fusion、宽MA3、空间context、interval内三q的多尺度latent交互、spatial/FFT双域expert及learned gate、bounded correction和coarse skip。故宽泛“多锚点+phase+gate+空间/频域”不能作为新创新。开发集小幅PSNR提升也不能升级成独立泛化。

原文档明确fastMRI test24已被多轮开发查看，只能当本地开发；最后若干小收益不足以支持继续无止境续训。另有跨数据集不一致的历史报告，本轮没有重新打开任何测试数据、没有复核这些汇总数字或据此选择新模型。新claim必须用预先冻结的患者协议独立确认。

现有辅助task实验native_reference和合法raw_pchip的已见验证分数都较低，且两个既有raw whole-series选择器GT乐观上界.5546达不到原.70gate。因此先检验普通任务泛化/真实动作余量，再训练选择器。当前19series optimizer/后续38FOV资格只为让这些医学实验可执行，不称算法贡献。

保留的窄假设：在强普通训练、实际SR/TTA动作及同信息action-risk差/QC/defer控制之后，合法采集信息或由observed MRI计算的采集响应特征，能否改善患者级病灶净收益决策。它必须同时超过原PAST-Net已有conditioning/gate、去额外采集特征、metadata-only、同容量风险差、strong static/always/none和费用匹配random。不能移除定义任务位置必需的query/geometry后把不公平退化称“采集信息增量”。

所有controller、teacher/localizer、feature/阈值/成本校准使用开发内折；含11GT的19998 task parent不可用于严格外折warm-start。需要对实际部署组合成对执行完整FOV，不从单动作效应相加造联合收益。动作失败、fallback、defer按原患者分母保留；人类成本未实测只能明确成本假设及敏感性。当前没有独立确认的发表claim。
