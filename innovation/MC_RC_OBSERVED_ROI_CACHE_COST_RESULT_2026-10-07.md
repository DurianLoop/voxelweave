# 观测预测 ROI 与当前 3D 缓存成本：结果

完成全部16series/8开发患者的4既有方法，不改变冻结旧ROI的训练、阈值、患者剔除或2mm规则。011/012/013三个现开发series没有旧预测，记录not_available；19系列标签oracle背景与这里的16系列预测ROI不构成同支持/同队列受控比较。

生产v2实际exit0，20.7864秒；独立实现实际exit0，62.2358秒。各加载64个冻结预测数组，模型/分类/GPU forward、训练更新、新MRI和新GT数组均0。显式物理disk+binary_dilation代替EDT，Fraction Boolean中心支持代替torch，独立tile/batch/Fraction汇总核对16系列、64支持、3456缺层记录全部一致。

| 固定方法 | 总完整N | 重算k | 空ROI系列 | 非空且有条件省forward | 非空ROI的5动作含初始化严格省 | 患者等权条件forward节省 | 来源旧前景覆盖（患者等权） | 来源旧ROI gates通过 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| joint_QDA 主 | 521 | 209 | 1 | 15/15 | 13/15 | 55.1371% | 5.3781% | 0/16 |
| appearance_QDA | 521 | 43 | 14 | 0/2 | 0/2 | 87.5% | 0.4198% | 0/16 |
| coordinates_QDA | 521 | 0 | 16 | 0/0，未定义非空率 | 0/0，未定义非空率 | 100%，全为无编辑 | 0% | 0/16 |
| joint_LDA | 521 | 156 | 0 | 16/16 | 15/16 | 58.6392% | 0% | 0/16 |

55.1371%是患者内系列等权、再8患者等权；不是(521−209)/521的总计数比例，更不是速度或MRI任务收益。五个“同支持替代动作”是计数摊销条件，尚无五种实测有效修正。all-series统计仍含空ROI，表中特别单列非空结果，空ROI可作为defer而非有效加速。appearance非空两系列全部触及其原batch，对它们没有forward省算。

旧ROI低覆盖和gates失败在旧实验里已知；本轮新增事实是同一冻结ROI映射当前3D窗口后的重算成本及它与已知覆盖的交集。所有方法“原前景≥.99、边界≥.99且有forward省算”的交集均0，不能称新证明所有observed表示都不可能。没有新GT评分或临床确认。

首生产v1实际exit1（0.2239672秒），在加载预测数组前失败于grid对象直接等于JSON对象的断言。核16系列发现只有padding tuple/list表示不同；JSON规范化后全部数值和tile顺序精确一致。v1原源码/失败JSON保留，新v2采用JSON规范化精确比较。另发现v1以basename保存source snapshot使两个attempt_01.json相互覆盖；v2改唯一索引前缀，9份snapshot逐SHA检查一致。修正均未调科学配置。

直接后续：[真实输入探针协议](MC_RC_OBSERVED_ROI_REAL_INPUT_PROBE_PROTOCOL_2026-10-07.md)，[生产结果](experiments/mc_rc_observed_roi_real_input_probe_2026_10_07/attempt01.json)。模型能力、完整输出等价、真实总耗时和净收益仍需后续实验。

原始证据：[失败v1](experiments/mc_rc_observed_roi_cache_cost_2026_10_07/attempt01.json)、[成功v2](experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/attempt01.json)、[独立disk/rational](experiments/mc_rc_observed_roi_cache_cost_v2_2026_10_07/independent_disk_rational_attempt01.json)。
