# 冻结训练内完整FOV诊断：运行前协议

落实已有下一诊断准备，不修改冻结20,000步模型或任何此前文件。仅11开发患者全部19合格系列、训练匹配raw PCHIP/observed_shared、原生完整FOV/全部z、固定.5；无新训练、无早停/阈值选择、无GT定位/裁剪/后处理。四验证已看过仍为验证，八确认关闭；隐藏MR不解码。

绑定最后checkpoint、初/终权重、训练protocol/support/input SHA、19开发输入生产与354观测层/76输入/19标签轴证明、已完成验证/复核回执。先推断固定清单第一个完整开发输入并估每plane耗时，再按所有19原生plane数估完整时长；固定运行预算上限3600秒估值，仅资源可行性守卫，不按效果决定保留哪个系列。第一个输入仍纳入完整19，不另算新复制。

完整预测生成后再读标签评分。全保留full/anchors/supported missing/tail、TP/FP/FN、Dice/precision/recall、signed/absolute RVE与物理ASSD/HD95、empty/undefined。先每患者内等权系列，再11患者等权，不使用训练patch或仅可见肿瘤切面作能力结论。

独立label轴、逐层bincount、cKDTree距离与固定首/中/末57完整plane重放全部执行，复用已证明的独立算法和同architecture重放，来源SHA记录。它不是第二独立训练模型。指标/重放全部核验之后再解释训练内表现；本次不设新的发表/泛化门槛，结果只决定下一能力开发方向。训练内低则优先可拟合性/优化；训练内高、验证低则查覆盖/泛化；两者都不能否证重建。

CPU单线程、自身below-normal，磁盘≥15GB/可用内存≥8GB；新增预测/报告<100MB，逐系列RAM处理。输出新mc_rc_frozen_global_local_development_diagnosis_cpu目录，exist_ok=False；失败保留、不覆盖、不因观察超时重启。GPU/用户终端训练/locked IXI test不操作。所有新增只在innovation，科学确认0，goal active。
