# 冻结模型的观测层预测区域：0/15通过，完整重放已复核

原session77501已exit0，15系列完整执行、errors=[]；独立复核session29338已exit0，errors=[]。固定主要ROI「预测在真实观测层的mask两侧并集+2mm」**0/15系列通过事前覆盖与面积门槛**，8患者都至少有失败系列。停止这个固定checkpoint/primary-region配置，不调半径、阈值、crop或改用dense次要ROI替代主失败。

[合同](MC_RC_FROZEN_PREDICTED_REGION_CPU_PLAN_2026-10-03.md)、[全部计数和task诊断](experiments/mc_rc_frozen_predicted_region_cpu/attempt_01.json)、[来源哈希](experiments/mc_rc_frozen_predicted_region_cpu/run_contract.json)、[独立输入/前向/区域复核](experiments/mc_rc_frozen_predicted_region_cpu/independent_observed_input_roi_and_model_replay.json)。

| 开发患者 / 系列 | 主ROI前景覆盖 | 主ROI边界覆盖 | sparse全体积Dice |
| --- | ---: | ---: | ---: |
| 001 / TSE时间点1 | 0 | 0 | 0 |
| 001 / TSE时间点2 | 0 | 0 | 0 |
| 002 / Ax3D FIESTA旧时间点 | 0 | 0 | 0 |
| 004 / SPC tra iso | 0 | 0 | 0 |
| 005 / 3D FIESTA HIGH RESOLUTION | 0 | 0 | 0 |
| 005 / Ax3D FIESTA | .441122 | .353693 | .410439 |
| 006 / FIESTA-C | .249013 | .122657 | .134223 |
| 006 / SPC rst tra p2 iso | 0 | 0 | 0 |
| 006 / SPC tra iso 384 | .982213 | .942915 | .867673 |
| 007 / FIESTA-C | 0 | 0 | 0 |
| 009 / FIESTA-C | 0 | 0 | 0 |
| 009 / TRIGEMINAL ci3d | 0 | 0 | 0 |
| 010 / 3D FIESTA Hi Res | .492393 | .375845 | .436919 |
| 010 / FIESTA-C | 0 | 0 | 0 |
| 010 / DRIVE AX | 0 | 0 | 0 |

不是所有series都完全不会分割：006 SPC的task Dice较高，但边界覆盖仍不足.99。11系列全volume真阳性为0，其中8个prediction为空，另外3个有误定位预测；这些结果不能用整体均值遮蔽。评价均对官方label，未使用truth选crop或输入模型。Sparse只解码phase0 genuine MR，不读取隐藏MR像素。

独立验证重新读1069个原DICOM头并排序、解码268个真实观测array；独立Hermite公式与实际PCHIP输入在预写浮点容差内一致，实际输入hash精确相同；全部15次冻结CPU前向和显式整数native回转逐位复现；重新读官方label、physical disk膨胀、显式六邻居boundary、759×6策略计数/主区域packed masks、全部task指标与患者内时间点平均复核通过。作者inferer、Pydicom、PCG64库仍复用，不称全算法独立重写。独立实现复核不增加科学独立患者。

结果只约束这个冻结模型及输入/区域配置。不能尚未测native就称domain shift导致、抽层导致、或者所有可见表征都失败。理想真实观测mask的15/15几何成功表明信息表达仍有探索空间，但它不是部署结果。接着执行[16系列完整native能力对照](MC_RC_NATIVE_COMPETENCE_CPU_PLAN_2026-10-03.md)，区分既有定位不足和sparse造成的额外下降。

此15是历史冻结子集，不是目前三批全部合格来源；[16系列范围更正](MC_RC_SOURCE_DENOMINATOR_CORRECTION_RESULT_2026-10-03.md)保留遗漏和后续补充方案。独立确认患者0，可发表claim未确认。旧岭失败、收益/误差等价、原HAT−pipelinePCHIP主比较与001/202改善反证均保留。
