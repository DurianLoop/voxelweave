# 三名开发患者的动作上限：主pipeline方向未过病灶门槛

三名MC-RC开发患者的CPU试验已完整结束，并完成独立数值/直接前向复查。**预写主动作pipeline PCHIP→HAT未达到开发门槛：整体支持域均有增益，但004的病灶目标等权守卫、006的病灶像素加权守卫失败。按合同停止这个固定主动作/32像素分支的收益头训练投入。** 不将raw次要结果改称原主比较通过。

[执行前方案](MC_RC_THREE_DEVELOPMENT_ACTION_ORACLE_PLAN_2026-10-02.md)、[冻结输入/源码/权重合同](experiments/mc_rc_three_development_action_oracle/run_contract.json)、[完整结果](experiments/mc_rc_three_development_action_oracle/attempt_01.json)。004/005/006每人取最早一个头+label-grid合格时间点，未按效果选时间点；分别56/144/72层、39/105/51个内部缺层，共195目标。原45+1队列动态效果量未读。

## 预写动作与实际效果

phase0 stride4模拟抽层，观测min/max、256resize/clip/HAT管线固定，观测层逐位保留、尾端复制末观测。支持域由两相邻观测1%阈值并集确定；人工标签仅用于病灶评价。tile32的alpha来自隐藏参考，属于不可部署oracle，二次收益公式不是新理论。

“病灶守卫”是该指标不高于base/HAT两个固定输出中该端点的较小值；目标等权与像素加权各自检查。表中dB比较对象是两固定输出较佳者，不是已学得的新方法。

| 患者 | 主pipeline支持域gain dB | 病灶目标等权守卫 | 病灶像素加权守卫 | 主开发门槛 | 次要raw支持域gain dB | raw两守卫 |
| --- | ---: | --- | --- | --- | ---: | --- |
| 004 | 0.147614 | 失败 | 通过 | 失败 | 0.819447 | 均通过 |
| 005 | 0.177642 | 通过 | 通过 | 通过 | 0.409169 | 均通过 |
| 006 | 0.240365 | 通过 | 失败 | 失败 | 0.659883 | 均通过 |

主合同要求三人全部达到≥0.1dB且两病灶守卫均通过，实际仅1/3满足。004主oracle的病灶目标等权NMSE相对较佳固定输出上升约0.6515%；006病灶像素加权NMSE上升约0.3022%。这些小幅差异按已定严格门槛为失败，不能事后容差化；也不能把它们当临床显著损害，未计算Dice、患者CI或临床重要差异。

失败针对当前优化支持域MSE的固定tile oracle及开发门槛；尚未验证病灶约束oracle、观测可见守卫或收益预测器，不能据此推断所有同处理动作策略均无可用空间。

次要raw在三人都通过图像误差守卫，值得另立后续开发问题，但不抵消主失败。它同时改变解析base的resize/clip，与pipeline动作不可混称同处理方法增益；raw自身支持域误差在005/006优于HAT，不能只突出HAT有用tiles。

## 常数混合已经吃掉一部分空间

结果后追加描述：从预先算过的α=0,.25,.5,.75,1中，为每患者/动作选支持域误差较小值，再与tile oracle比较。这个逐患者“最佳常数”也看参考，不是部署策略；没有据此修改主门槛或方法。算术与来源hash见 [对照记录](experiments/mc_rc_three_development_action_oracle/fixed_mixture_comparison.json)。

| 患者 | pipeline oracle超过该患者最佳预写常数 dB | raw oracle超过该患者最佳预写常数 dB |
| --- | ---: | ---: |
| 004 | 0.145453 | 0.256700 |
| 005 | 0.158746 | 0.260357 |
| 006 | 0.144012 | 0.225164 |

raw相对端点的0.409–0.819dB不能直接当新收益预测器可取得的增量；超过较强常数参照仅0.225–0.260dB，而且仍借真值。后续必须比较无需真值的固定混合、同容量误差头、分歧/动作幅度/观测留出及任务表现，不能用oracle标题替代可预测性证据。

## 独立复查范围与限制

[独立脚本](experiments/verify_mc_rc_three_development_action_oracle.py)不调用主decode/analyses或PchipInterpolator：原ZIP重新解码MR、用NIfTI方向工具核整数标签变换；以Hermite形式核PCHIP、向量化块线段投影核alpha和全部层策略SSE；每患者首/中/末缺层直接调用HAT网络，绕过predict/_predict_residual。实际exit0/errors=[]，195目标、54,768 tiles、九个直接前向均逐位一致，见 [proof](experiments/mc_rc_three_development_action_oracle/independent_numerical_and_forward_verification.json)。

HAT所有输出hash已核，**仅九层直接重跑，未逐层再生成全部HAT体积**；不要称全部HAT输出独立再生成。数值独立复核不等于新方法未见患者确认，三人角色仍development；科学独立确认人数0。只评模拟抽层图像/病灶误差，未跑分割任务，不保证物理厚层恢复、3D连续性或临床安全。

后续方向见 [明确保留主失败的准备](MC_RC_RAW_ACTION_FOLLOWUP_PREPARATION_2026-10-02.md)。本轮成果是可失败设计的真实结果、停止一个不满足门槛的训练分支，并找到需要进一步开发验证的次要候选；尚无可发表claim。
