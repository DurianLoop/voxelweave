# 五人病灶约束动作空间：数值复核通过，方法尚未验证

[预写诊断合同](MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_PLAN_2026-10-02.md)明确本次是原raw失败后的事后开发探索。固定五人、240内部缺层、raw PCHIP→保存HAT、tile32、phase0，不再跑HAT。隐藏参考和人工病灶label参与优化，部署无法直接使用；原三人pipeline和五人raw无约束门槛失败继续保留。

支持域目标等权NMSE为凸二次目标，两约束分别要求病灶目标等权/像素加权NMSE不超过raw/HAT两端点较小值。两非负乘子、box内闭式alpha，单初值L-BFGS-B固定参数。完整系数、alpha、lambda、端点、求解状态、约束和dual均保存。

| 患者 | 缺层 | tile数 | 无约束支持域增益dB | 约束支持域增益dB | 数值认证/独立复核 |
| --- | ---: | ---: | ---: | ---: | --- |
| 001 | 21 | 1,344 | 0.167287485 | 0.165081296 | 通过 |
| 002 | 24 | 6,144 | 0.404077102 | 0.404077102 | 通过 |
| 004 | 39 | 4,116 | 0.819447069 | 0.819447069 | 通过 |
| 005 | 105 | 16,986 | 0.409169087 | 0.409169087 | 通过 |
| 006 | 51 | 6,282 | 0.659882842 | 0.659882842 | 通过 |

五人均达到既定0.1dB诊断条件。001只有目标等权约束起作用，lambda=(0.002610861222403467,0)，目标等权违例约8.48e-14 NMSE，像素加权余量约8.81e-5。这是固定数值精度容差内的近似边界，不能改称原严格守卫通过，更不是临床不劣界。其支持域代价约0.002206189dB；其余四人原无约束解已经满足约束，lambda均为0。

[执行结果](experiments/mc_rc_five_developer_constrained_oracle/attempt_01.json)、[合同](experiments/mc_rc_five_developer_constrained_oracle/run_contract.json)与[独立proof](experiments/mc_rc_five_developer_constrained_oracle/independent_pixel_and_dual_verification.json)均已落盘。独立程序重新解码原MR/标签，以SciPy PCHIP替代执行器Hermite，以逐tile dot替代向量block sum，再用实际像素重算三个区域端点，并独立求每tile二次式的端点/顶点最小值组成dual下界。240目标、34,872 tiles、五人errors=[]。核非负lambda、alpha box、约束违例≤1e-10、gap∈[-1e-10,1e-8]和stationarity≤1e-8；同时记录complementarity。未调用神经网络、未逐层再生成HAT，沿用已核hash及原两批15个采样前向proof。

独立复核首次有解析前SyntaxError，未开始任何数组处理；[失败记录](experiments/mc_rc_five_developer_constrained_oracle/independent_verifier_failed_attempt_01.json)保留，改为显式mask/count循环后全量复核通过。

## 共同系数对照进一步解释局部空间

看到上述结果后另写[常数诊断合同](MC_RC_CONSTRAINED_CONSTANT_DIAGNOSTIC_PLAN_2026-10-02.md)，求每患者共同alpha满足两约束的完整可行区间及最小支持域NMSE。它同样使用真值，不是部署基线。全部五人区间非空；逐tile math.fsum和固定1001点可行网格复核通过。[完整结果](experiments/mc_rc_constrained_constant_diagnostic/attempt_01.json)保存全部区间/alpha/端点。

| 患者 | 最优病灶可行共同alpha | 常数增益dB† | tile相对最优可行常数增益dB | 约束改变tile数 |
| --- | ---: | ---: | ---: | ---: |
| 001 | 0.142389530 | -0.489810376 | 0.654891672 | 10/1,344 |
| 002 | 0.669012615 | 0.206999971 | 0.197077132 | 0/6,144 |
| 004 | 0.491422296 | 0.562929950 | 0.256517120 | 0/4,116 |
| 005 | 0.193577446 | 0.162890927 | 0.246278160 | 0/16,986 |
| 006 | 0.417653341 | 0.453251669 | 0.206631172 | 0/6,282 |

†增益参照较低支持域NMSE的raw/HAT固定端点，该参照未必满足两病灶约束。001参照HAT本身病灶不可行，因此常数列的负值不表示较raw基底恶化。tile对可行共同系数的相对差是同约束比较。

001改变的10个tile全部属于病灶动作系数非零的10个tile，最大alpha改变约0.598567；其余四人不需改变。局部可行解超过全体积共享收缩，说明“统一减弱HAT”无法充分解释这一开发上限。这里用真值认出了局部冲突，尚未证明真实观测可以认出它。常数诊断首跑JSON序列化因NumPy bool失败，原脚本/合同与失败记录完整保留，再跑成功；无上游结果更改。

结论只到“固定五开发患者存在病灶约束下的局部动作增益空间”。尚无可部署方法、患者任务/Dice、真实厚层或未见患者确认，更无可发表claim。论文先例与下一步见[六篇复读](literature/2026-10-02_constrained_oracle_prior_art_recheck.md)和[新方向准备](MC_RC_JOINT_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)。
