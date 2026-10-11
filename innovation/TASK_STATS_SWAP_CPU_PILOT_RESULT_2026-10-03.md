# 固定三人raw/post统计互换：CPU结果

全部6次交叉CPU前向已完成；两条原对角条件复用既有核验预测。最终独立复核通过6交叉输入重放、6对角输入SHA、72采集域confusion单元、30配对端点及6保存预测核验。没有GPU调用、新训练或科学独立确认。

这三人是原固定技术预检名单202/203/204。其原post−raw JSON full均值为+.033359793753，与全45人的−.09175350相反；RT同样三人+.035143371676而全45为负。不能用三人结果解释全45损失、声称恢复或计算唯一归因百分比。

| 原JSON full比较 | 三人平均ΔDice |
| --- | ---: |
| post_rawstats-post_poststats | +0.001410324010 |
| raw_poststats-raw_rawstats | +0.000937623111 |
| post_rawstats-raw_rawstats | +0.034770117763 |
| post_poststats-raw_poststats | +0.032422170642 |
| normalization_image_interaction | -0.002347947121 |

主比较post_rawstats−post_poststats逐人JSON full：202 −.000768344059、203 +.002298443881、204 +.002700872208；RT平均+.001523343559。效应小且包含反例。固定图片换统计仍改变网络的整个输入，不能据ΔDice把它叫解剖恢复。

所有两标签×full/slab/去1mm带×5比较均保存，无筛选、bootstrap或显著性声明。full与slab在这三人可能相同，不得据此省略采集域。以下采集域由原始z索引建立后映射至RAS，区别于包含anchors的slab；unsupported tail保留undefined，不填0。

| 采集域，主比较post_rawstats−post_poststats | JSON三人均值（定义n） | RT三人均值（定义n） |
| --- | ---: | ---: |
| observed_anchors | +0.002543319792 (3) | +0.003040982433 (3) |
| supported_missing | +0.001080172947 (3) | +0.001075879441 (3) |
| unsupported_tail | undefined (0) | undefined (0) |

[全部30端点](experiments/task_stats_swap_cpu_pilot/all30_endpoints.csv)、[90逐人配对差](experiments/task_stats_swap_cpu_pilot/all90_patient_differences.csv)、[72采集域计数](experiments/task_stats_swap_cpu_pilot/all72_acquisition_domain_counts.csv)、[90采集域配对差](experiments/task_stats_swap_cpu_pilot/all90_acquisition_domain_differences.csv)、[输入与端点独立复核](experiments/task_stats_swap_cpu_pilot/independent_inputs_domains_and_all30_estimates.json)。

解析的difference-in-differences是预列交互项；两条统计/图像路径不同意味着不能提出自然唯一的归因比例。网络、患者与标签均来自已见开发条件，复核独立性限于NumPy输入重放与Fraction计数运算，不能替代新模型/患者科学确认。结合[三篇直接先例](literature/2026-10-03_masked_normalization_primary_reading.md)，anchor-only统计保留为控制，当前不作为独立创新或扩大原失败恢复干预的证据。
