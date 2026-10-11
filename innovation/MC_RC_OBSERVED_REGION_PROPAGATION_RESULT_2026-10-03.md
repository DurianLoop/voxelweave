# 理想观测区域传播结果：几何可行，不能称可部署优势

冻结的15系列/8开发患者、phase0、759内部缺层全部执行完成；9个策略/对照保留。唯一主要区域为两侧**真实观测标签**并集+2mm。15/15通过事前几何门槛。

| 主区域指标 | 15系列范围 |
| --- | ---: |
| 缺层前景覆盖 | 0.9955604883–1 |
| 缺层边界覆盖 | 0.9921875–1 |
| ROI / 全缺层平面面积 | 0.0003473618–0.0276431129 |
| tile32 / 全缺层平面面积 | 0.0022977941–0.0500992063 |
| tile前景覆盖 | 全部1 |

[执行合同](MC_RC_OBSERVED_REGION_PROPAGATION_PLAN_2026-10-03.md)、[全部结果](experiments/mc_rc_observed_region_propagation/attempt_01.json)、[输入哈希](experiments/mc_rc_observed_region_propagation/run_contract.json)、[独立复核](experiments/mc_rc_observed_region_propagation/independent_raw_label_roi_verification.json)。执行session55551与独立复核91233均exit0（继承摘要及已存在proof）。独立实现从原label slab重建787,030前景体素、physical-offset disk dilation对照EDT、显式六邻居边界、全部759×9策略及3×759 packed masks、随机预算和患者汇总，errors=[]。

这只说明理想观测病灶区域对缺层有足够几何覆盖空间，没有证明MRI上能预测区域，更没有新SR重建收益或独立临床保护。不能因其通过就把人工真值mask放入部署流程。后续[真实稀疏MRI导出预测](MC_RC_FROZEN_PREDICTED_REGION_CPU_RESULT_2026-10-03.md)已检验实际瓶颈。

范围更正：此实验对应原冻结15系列子集；[当前来源名单审计](MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md)确认三批目前16系列合格，旧名单漏002第二时点。保留旧结果和原合同；遗漏系列另按新合同补充，不追溯修改15/15或称它覆盖全部当前合格来源。独立科学确认患者仍0。
