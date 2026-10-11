# 两名MC-RC开发患者复核：原raw分支未过门槛

按[预写执行合同](MC_RC_001_002_RAW_ACTION_EXECUTION_PLAN_2026-10-02.md)，首次解码MC-RC-001/002各最早合格时间点，使用首批全部IPP认证affine与对应整数标签变换。两个病例均已用于来源/方法开发，不是新确认患者，也不是VS-SEG-001/002。CPU固定HAT、phase0、x4模拟抽层、tile32；无训练、无GPU。

| 患者 | 原生数组 | 内部缺层 | raw支持域oracle增益dB | 两病灶守卫 | raw开发门槛 |
| --- | --- | ---: | ---: | --- | --- |
| VS-MC-RC-001 | 256×256×30 | 21 | 0.167287485 | 均失败 | 失败 |
| VS-MC-RC-002 | 512×512×36 | 24 | 0.404077102 | 均通过 | 通过 |

001的病灶目标等权NMSE从raw基底0.014458403上升至0.016607810，约恶化14.9%；像素加权从0.012389281上升至0.013496814，约恶化8.94%。002的pipeline诊断也未通过两守卫。故三人pipeline原主方向失败、五人raw无约束门槛失败，不能开始原收益头训练。

[完整结果](experiments/mc_rc_001_002_raw_action_oracle/attempt_01.json)和[冻结输入](experiments/mc_rc_001_002_raw_action_oracle/run_contract.json)保存UID、来源、归一化、观测和全部端点。[独立复核](experiments/mc_rc_001_002_raw_action_oracle/independent_numerical_and_forward_verification.json)检查45目标、14,976 tiles及全部保存端点；6个首/中/末HAT直接前向逐位一致，errors=[]。复核器仅五项来源/范围替换的[适配记录](experiments/mc_rc_001_002_raw_action_oracle/independent_verifier_source_adaptation.json)保留，旧三人冻结源码未修改。未逐层重新生成全部HAT，也未做Dice/任务验证。

后续[病灶约束诊断](MC_RC_FIVE_DEVELOPER_CONSTRAINED_ORACLE_RESULT_2026-10-02.md)是看到失败后的新问题，不改本结果及预写门槛。
