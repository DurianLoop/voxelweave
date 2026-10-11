# 强静态与联合适配控制：待真实效应阶段

本轮是准备补充，不是已资格化的医学实验入口、正式新增endpoint或训练协议。已有 [三臂入口](../three_arm_resource_bridge_2026_10_08/run_three_arm_real_resource.py) 和 [标签／费用准备](../paired_task_label_adapter_2026_10_08/POSTFIT_EXECUTION_BRIDGE.md) 的依赖继续适用。新增文献说明下列对照必须解释清楚，但对照思想本身已有先例。

1. 在原两臂final／能力／strict以及三臂真实资源资格后，正式强task适配前固定legacy dense、direct、common-projected三种路径，共同observed、容量、initialization、draw、监督和训练预算；真实资源测试不是充分训练。native只做能力参照，不作为部署动作／增益标签。
2. 对合法修正／动态选择，分清“同一个冻结充分适配task模型上的不同动作”与“各路径自己充分适配task模型的最终pipeline”。两种问题可以有不同收益，但不能静默跨checkpoint配对；task、action、observed、label、cost各SHA与病人角色明确绑定。MASC的joint-vs-posthoc不能替代这一控制。
3. 比较固定最佳合法动作、开发上学得的固定序列、cost/defer条件成本、DC-based，以及候选状态选择。固定序列若需多个动作，必须在真实组合后的task输出上评分并实测union/cache费用；不能把单动作ΔQ相加／单动作秒数相减。具体动作库和fixed-sequence预算仍须在正式新版本协议预先冻结，本轮不造假动作库或新收益。
4. 如果某候选以更多task适配训练优于静态，给静态相同适配预算和监督，区分额外task训练、状态可用信息及选择器自身的作用。可以规划同候选joint task模型上的fixed/defer选择及静态适配模型上的候选选择，但每项应先冻结暴露和费用，不能在8未见确认上尝试矩阵。
5. 每轮候选用同一完整病例panel／患者权重，保留负／零／undefined／失败和全FOV。sLBCS明确指出候选间更换病例subset会偏向易病例；我们也不能为每个action挑各自子集。开发head-only LOPO仍不是整个pipeline患者外。
6. 沿用固定主要端点、预算单位和汇总方向。若另外规划quality-vs-实测wall-time预算曲线，必须预先定坐标／范围／重叠成本边界／初始probe付费和插值规则，不把acquisition rate AUC叫部署cost AUC，不用看到结果后的曲线积分取代主要full Dice。Thesis已展示汇总变化反转排名。

上述阶段当前无完整合法action标签、无完整部署cost；fit_ready=false。准备比较不是拟合许可。旧9pair已见弱checkpoint不做正式fit，原strongcapacity尚待。开发11患者19series／已见4/9不冒称独立确认；方法、全部checkpoint、端点、action和budget冻结后才一次8未见12series确认；lockedIXI及旧MIRA/MSValid84保留。

科研训练／label生成成本与部署完整患者成本分别记；部署含启动、IO、定位、feature/selector、动作生成、transfer、task推断、组合、后处理/失败及父级wall-time，selector/probe不免费。若fixed static pipeline在强适配和完整cost下同样好或更好，保留负结果，不改主要端点或挑预算坐标挽救动态方法。当前最有可能发表的结果形式取决于这些真实比较，不能提前许诺方法收益。
