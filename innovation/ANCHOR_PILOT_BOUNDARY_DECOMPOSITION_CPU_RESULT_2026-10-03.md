# 三人边界反向结果：事后计数分解

固定两标签/六比较，读取18个已复核条件记录。无新MRI解码或神经前向、未导入torch。full−去1mm带混淆计数非负，三个分区reference体素跨条件相同；完整36个汇总和108个逐人比较已保存。

本分析写于全部pilot端点已见之后，是开发性事后解释。分区Dice分母不同，不能相加或互相替代；“outside”还含远离reference的背景，并非纯病灶核心。

| 标签 | post_fixed−post 域 | 平均ΔTP | 平均ΔFP | 平均ΔFN | 平均ΔDice |
| --- | --- | ---: | ---: | ---: | ---: |
| original_json | full | -133.33 | -83.67 | +133.33 | -0.00505496 |
| original_json | outside_1mm_band | -14.33 | -72.67 | +14.33 | +0.02011658 |
| original_json | excluded_1mm_band | -119.00 | -11.00 | +119.00 | -0.02972866 |
| rtstruct | full | -138.33 | -78.67 | +138.33 | -0.00507443 |
| rtstruct | outside_1mm_band | -14.00 | -61.00 | +14.00 | +0.01731318 |
| rtstruct | excluded_1mm_band | -124.33 | -17.67 | +124.33 | -0.02974891 |

完整逐人计数见[108配对值](experiments/anchor_pilot_boundary_decomposition_cpu/all108_paired_partition_differences.csv)，包括反例；[36汇总](experiments/anchor_pilot_boundary_decomposition_cpu/all36_partition_summaries.csv)及[108条件分区](experiments/anchor_pilot_boundary_decomposition_cpu/all108_condition_partitions.csv)保留全部条件。

这些变化仅定位保存预测在参考标注附近的错误。它们不证明MRI解剖改变、标注错误、临床损害或某个因果机制，也不恢复已失败的post带宽主张。两标签及三人开发诊断不是科学独立确认。
