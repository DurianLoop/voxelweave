# 精确校准仍可能选中有害修正：实际CPU结果

事前固定4组/400合成样本，不读MRI或模型、不训练、无CUDA。主脚本chunk3d4d86和独立脚本chunk7afe05均真实exit0；独立逐整数/Fraction核4组、13策略行、18有限样本算术行。它是已知决策条件的有限反例，不是新理论或MRI病灶效果。

| 同100次action预算的规则 | 所选group | 全400样本错误 | 相对baseline少错 |
|---|---|---:|---:|
| 不调用，0次预算 | 无 | 200 | 0 |
| baseline最高risk | A | 205 | -5 |
| 已知两路径risk差 | B | 160 | 40 |
| 每group等概率随机，100次预算 | 随机 | 181.25，期望 | 18.75，期望 |
| 总是调用，400次预算 | ABCD | 125 | 75 |

baseline risk0和action risk1在每group均与精确错误率一致，即risk已正确校准。高risk指出容易错，不能单独指出修正有效。两路径gain最大与相对cost最小的24排列选择一致；已知cost-sensitive/defer即必要控制。

高risk嵌套调用A、AB、ABC、ABCD时错误200->205->165->135->125，加入动作可增错。单调调用支持并不使实际系统loss单调；不把这个反例误报为CRC已经实测失效。

CRC finite-n算术另有18行，B=1的修正不等式下限n4=.20/n8=.1111/n11=.08333/n19=.05；只证明该不等式的可行范围，不否定满足终点条件的fallback保证。原真实项目没有认证的低loss终点和独立calibration。4已见validation、8保留确认、11开发患者、19series均按实际用途标明，不被重新宣称可用校准样本。

[事前协议](CALIBRATED_RISK_VS_ACTION_GAIN_CPU_PROTOCOL_2026-10-07.md) · [主结果](experiments/calibrated_risk_vs_action_gain_2026_10_07/attempt01.json) · [独立整数复核](experiments/calibrated_risk_vs_action_gain_2026_10_07/independent_attempt01.json) · [实际原文阅读](literature/2026-10-07_calibration_selection_primary_reading.md)。

