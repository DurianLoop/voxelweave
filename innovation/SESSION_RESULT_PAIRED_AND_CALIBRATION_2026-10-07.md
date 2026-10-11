# 本轮结果：公平执行器归档与风险/收益强对照

本轮补齐上次配对采样/FOV资格的归档，并新增核读3篇方法原文和两项CPU精确反例。研究有实质推进，**新可发表claim尚未确认**。现有正式训练未结束，因此没有新MRI病灶效益评价。

- 配对sampler与two-channel完整FOV的合成资格已真实exit0：24组draw、6次合成更新、checkpoint恢复tree exact、每臂8tile/生产与独立解释器physical逐位一致。direct理想坐标绝对误差3.21865e-6仍不满足旧<=3e-6；float32解释器和float64诊断通过均不覆盖旧失败。
- 新取得Guo2017、SelectiveNet2019、CRC2025v4三份原文，38PDF页，完整选读23页，7页实际render/view。CRC第五作者误写已更正为Tal Schuster；其肿瘤例子实际肠道息肉，非脑MRI。校准、selection head、两路径cost/gain、非单调loss包络都属已知机制。
- CPU反例及独立整数/Fraction复核真实exit0：4组/400合成样本条件risk精确校准，最高risk修正增加5个错误，等调用预算两路径risk差减少40个。必须有强cost-sensitive/defer对照；这不是MRI收益或新理论。
- 校准位置CPU检查真实exit0：各tile argmax不变，先tile温度缩放再概率融合仍可改变最终.5预测（.528496->.441312）；融合后的正温度缩放保持最终.5预测。独立Decimal80位重放最大差2.22045e-16，原生产代码不改。未来配方必须固定施加位置。
- readiness旧attempt01 tool exit1、attempt02真实exit3均保留。原训练/56FOV/独立receipt缺失时不打开MRI新资源资格，不把完成JSON当terminal exit。

最近实际训练poll chunk05cd6a：同session99542仍live，native7326、新增7227、累计15863.582562200027秒；PCHIP99仅旧快照。GPU已授权，最近实际20:05:32.904 free1394MiB/total24455MiB/util90%，未达到既定新GPU8GB启动门槛。当前4已见validation/19开发series不被重新称独立calibration，8确认及locked IXI test关闭。旧MIRA的MSValid84人确认单独存在，不能把全项目确认抹成0。

当前新意应检验：充分适配的dense/direct/SR是否保留真实可修正余量；合法observed特征能否预测完整患者系统收益；联合策略在计入真实总成本、扣Dice分式影响之后是否超过双路径cost/defer、union-greedy和同预算random。没有余量或被已知控制解释时保存负结果。

[配对资格结果](MC_RC_3D_PAIRED_SAMPLING_FOV_RESULT_2026-10-07.md) · [新原文阅读](literature/2026-10-07_calibration_selection_primary_reading.md) · [风险/收益CPU结果](CALIBRATED_RISK_VS_ACTION_GAIN_CPU_RESULT_2026-10-07.md) · [校准位置结果](experiments/calibration_position_cpu_2026_10_07/attempt01.json) · [后续真实实验准备](CALIBRATION_AND_ACTION_GAIN_FOLLOWUP_2026-10-07.md)。

[用户与接续范围](SESSION_USER_HANDOFF_PAIRED_AND_CALIBRATION_2026-10-07.md) · [用户摘要逐字原文](SESSION_IMPORTED_SUMMARY_PAIRED_AND_CALIBRATION_VERBATIM_2026-10-07.md) · [公开对话](SESSION_VISIBLE_DIALOGUE_PAIRED_AND_CALIBRATION_2026-10-07.md)。实验、真实退出、阅读范围和失败由本阶段执行台账保存；归档另核验前1130冻结SHA，live invocation02/history/resume不纳入冻结。

