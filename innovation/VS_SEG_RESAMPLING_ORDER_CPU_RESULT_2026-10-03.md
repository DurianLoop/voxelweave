# 全45处理顺序对照：裁剪未激活，PCHIP顺序效应小于整体处理效应

固定45已见CISS、2,565内部缺层、两原参考，producer和独立verifier均实际exit0。180既有解析体积逐位重放一致，90新post体积由另一表达式重新构造且SHA一致；36完整端点/逐患者/逐层ROI与标量bootstrap全部复核通过，errors=[]。新增神经forward为0，科学独立确认患者0。后续新任务队列是另一合同，尚未将其结果混入本报告。

本实验只能诊断处理因素，不能复活原HAT负向主张。新post先在原网格插值，再同observed min/max归一化、缩256及恢复；pipeline先缩observed layers再插值。anchors和不可插值tail逐位保留。全45不换病例，TSE不并入。

## 1. 显式裁剪实际改变了多少

linear/PCHIP、before/post四组合全部0像素、0层、0越界。因此这些解析条件间的差异不能归因于显式clip[0,1]。这不评价HAT残差后的clip；也不排除skimage内部clip、空间滤波/抗混叠/量化等其他因素。

## 2. 插值顺序是否改变输出

| 核 | 全图最大归一化差的患者min / median / max | 超过预写1e-6 |
| --- | --- | --- |
| linear | 6.24880023e-08 / 1.34143201e-07 / 1.7991203e-07 | 0/45 |
| pchip | 0.00912657211 / 0.0138783954 / 0.0197610862 | 45/45 |

线性对照符合预写解释容差。PCHIP的局部差可达观测范围约0.91%–1.98%，但“超过浮点容差”不等于有任务意义。独立Hermite/linear另一公式最大归一化误差≤预写5e-7，实际全队列最大4.59948427e-08；这些顺序差异不是PCHIP重算程序错误的证据。

## 3. 图像误差效应有多大

以下为患者等权、患者内缺层等权NMSE。负值表示左条件误差更小；45患者共享5000draw、seed20261031。所有区间均描述性、未familywise校正。

| 核/区域 | 比较 | 平均差 | 描述性95% CI | 负/零/正患者 |
| --- | --- | --- | --- | --- |
| linear/support | post_resize-raw | -0.000111230868 | [-0.000121152017, -0.000101619763] | 45/0/0 |
| linear/support | pipeline-post_resize | 3.05426233e-14 | [-1.67495879e-13, 2.19674195e-13] | 20/0/25 |
| linear/support | pipeline-raw | -0.000111230868 | [-0.000121152017, -0.000101619763] | 45/0/0 |
| linear/original_json_lesion | post_resize-raw | -0.000368877117 | [-0.00046381616, -0.000286373514] | 42/0/3 |
| linear/original_json_lesion | pipeline-post_resize | 1.12867862e-11 | [-2.72388066e-11, 4.70902168e-11] | 22/0/23 |
| linear/original_json_lesion | pipeline-raw | -0.000368877106 | [-0.000463816134, -0.000286373519] | 42/0/3 |
| linear/rtstruct_lesion | post_resize-raw | -0.000389318001 | [-0.000467184625, -0.00032236877] | 45/0/0 |
| linear/rtstruct_lesion | pipeline-post_resize | 1.26581973e-11 | [-2.42072981e-11, 4.81278068e-11] | 21/0/24 |
| linear/rtstruct_lesion | pipeline-raw | -0.000389317988 | [-0.00046718459, -0.000322368718] | 45/0/0 |
| pchip/support | post_resize-raw | -0.000142890502 | [-0.000155498255, -0.000130704226] | 45/0/0 |
| pchip/support | pipeline-post_resize | -1.21248932e-06 | [-1.35359973e-06, -1.08947167e-06] | 45/0/0 |
| pchip/support | pipeline-raw | -0.000144102991 | [-0.000156824808, -0.000131818667] | 45/0/0 |
| pchip/original_json_lesion | post_resize-raw | -0.000452672743 | [-0.000568603921, -0.000352865203] | 43/0/2 |
| pchip/original_json_lesion | pipeline-post_resize | -8.17468857e-08 | [-3.1913492e-06, 3.08342906e-06] | 23/0/22 |
| pchip/original_json_lesion | pipeline-raw | -0.00045275449 | [-0.000569706032, -0.000353052961] | 42/0/3 |
| pchip/rtstruct_lesion | post_resize-raw | -0.000475666957 | [-0.000571107181, -0.000394781132] | 45/0/0 |
| pchip/rtstruct_lesion | pipeline-post_resize | 9.24537176e-07 | [-2.30763309e-06, 4.0340007e-06] | 21/0/24 |
| pchip/rtstruct_lesion | pipeline-raw | -0.00047474242 | [-0.000570467417, -0.000394153765] | 45/0/0 |

PCHIP支持域整体pipeline−raw为-0.000144102991；顺序pipeline−post为-1.21248932e-06，两均值比0.8414%。这是已固定路径的描述性分解，不是“0.84%因果中介”或新理论。双病灶平均顺序差的两个加权版本CI均跨0，不能声称病灶平均收益，也不能声称等效。

## 4. NMSE降低不能等同结构保护

| 条件 | support mean NMSE | JSON lesion mean NMSE | RT lesion mean NMSE |
| --- | --- | --- | --- |
| raw_linear | 0.00155821488 | 0.00456564288 | 0.0044383553 |
| pipeline_linear | 0.00144698401 | 0.00419676578 | 0.00404903731 |
| post_resize_linear | 0.00144698401 | 0.00419676577 | 0.00404903729 |
| raw_pchip | 0.00159072017 | 0.00501516739 | 0.00483657855 |
| pipeline_pchip | 0.00144661718 | 0.0045624129 | 0.00436183613 |
| post_resize_pchip | 0.00144782967 | 0.00456249465 | 0.00436091159 |

这里的roundtrip反而让support NMSE全部45人降低；两个病灶域也多数降低。旧已完成分割记录中raw PCHIP Dice .74459750、pipeline PCHIP .65476150，因此图像误差均值不能单独解释任务变化。不能预先把roundtrip称“恶化图像”；它可能平滑误差，但任务因果仍需直接控制。新post的Dice尚待[独立CPU任务合同](VS_SEG_POST_RESIZE_TASK_CPU_PLAN_2026-10-03.md)，不在本报告推断。

## 5. 可复核范围和下一步

NMSE沿用旧float32差后float64归一化；pipeline/post输出差另用float64，二者不可混称。独立复核共享native decoder、observed min/max/skimage和RNG；采用另一Hermite公式、另一post构造、fresh ROI dot-product、math.fsum、标量bootstrap和手写分位，不是全软件栈独立，更不是新患者验证。

PCHIP顺序在本项目确有数值效应，但当前图像均值证据不支持将其作为主要创新或解释全部Dice差。继续直接测post条件的冻结任务输出，随后准备跨输入训练矩阵和另一个任务评估器；未来新方法必须使用未参与选择的患者。原网格旁路/特征重采样等宽创新已被[本批三篇正文](literature/2026-10-03_resampling_order_fulltext_reading.md)排除。

[全部36端点CSV](experiments/vs_seg_resampling_order_cpu/all36_descriptive_endpoints.csv)；[全部患者与逐层结果](experiments/vs_seg_resampling_order_cpu/attempt_01.json)；[独立复核](experiments/vs_seg_resampling_order_cpu/independent_replay_attempt_01.json)；[计划](VS_SEG_RESAMPLING_ORDER_CPU_PLAN_2026-10-03.md)。
