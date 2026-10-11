# 固定完整45人：整volume统计反馈审计

90个既有raw/post数组逐位重放通过。此次新增神经前向0，GPU使用0。单线程低优先级CPU，每人均通过15GB磁盘/8GB可用内存门槛。另一个不导入torch的标量复核通过45患者、270采集域矩单元、90相同图像域RMS、90 Fraction Dice差、12手工关联和45行CSV。

此方案在原任务结果已知之后制定，是事后开发审计。所有45人均保留；统计从候选图像计算，没有用missing真值或labels选择患者/阈值。科学独立确认患者仍为0。

raw与post的anchors/tail图像值相同，但各自整volume归一化后有实数关系 `Ypost=a*Yraw+b`，`a=std_raw/std_post`、`b=(mean_raw-mean_post)/std_post`。float32实际数组与解析关系仅在浮点容差内一致，不声称逐位相同。

| 输入统计指标 | 45人均值 | 最小 | 最大 |
| --- | ---: | ---: |
| a_minus_one | +0.025524691944 | +0.020721551399 | +0.037041277433 |
| b | -0.000063936733 | -0.000272333719 | +0.000043349652 |
| observed_normalized_rms | +0.026642186808 | +0.021494614383 | +0.039288092644 |
| std_relative_change | -0.024882179853 | -0.035718228617 | -0.020300885555 |

所有45人的post std都减少，平均−2.4882%；于是相同anchors归一化后的scale平均增加2.5525%。归一化anchors RMS平均.026642，不是图像物理误差或病灶损失。均值offset较小也不能推出网络对它不敏感。三人pilot的scale/RMS落在全45范围内，但这不保证任务响应代表性。

| 原post−raw full Dice | JSON均值 | RT均值 |
| --- | ---: | ---: |
| full45，n=45 | -0.091753499951 | -0.091588209385 |
| fixed_pilot3，n=3 | +0.033359793753 | +0.035143371676 |
| remaining42，n=42 | -0.100690163787 | -0.100640465176 |

固定pilot三人原post−raw为正、其余42人及全45为负。不能把三人微小统计互换效果外推到全45，也不把排除三人的42人称为新确认集。这里仅分组说明已知技术预检的限制。

| 预列输入指标 | JSON Pearson / Spearman | RT Pearson / Spearman |
| --- | ---: | ---: |
| a_minus_one | -0.303941 / -0.002503 | -0.308222 / -0.004084 |
| b | +0.446200 / +0.258235 | +0.448480 / +0.241634 |
| observed_normalized_rms | -0.303476 / -0.007642 | -0.307918 / -0.009223 |

scale/RMS的Pearson约−.30，但Spearman接近0，不能支持稳定单调的部署风险排序；offset的关联也只是同一事后队列关联。原图像、病灶、模型曝光与其他因素共同变化，没有因果识别。没有bootstrap、p值、风险挑人、政策阈值或归因比例。所有12关联保留，不因最大值选择新动作。

当前可成立的是：observed-preserving图像合同不自动等于observed网络输入保持，生成缺层可经整volume统计反馈改变anchors输入。宽机制在[Region Normalization及Partial Convolution](literature/2026-10-03_masked_normalization_primary_reading.md)已有明确先例。这是本管线中的可复核实例，尚不构成首次机制发现或有效新方法。

[45行统计和全部原任务差](experiments/full45_normalization_drift_cpu/all45_statistics_and_saved_dice.csv)、[12完整关联](experiments/full45_normalization_drift_cpu/all12_descriptive_associations.csv)、[全部患者矩及输入hash](experiments/full45_normalization_drift_cpu/attempt_01.json)、[独立标量复核](experiments/full45_normalization_drift_cpu/independent_scalar_csv_and_correlations.json)。

后续保留anchor-only统计作为训练/推理一致的控制。现有证据不足以扩大三人统计互换到45人或重新调anchors模糊。先明确任务训练来源/曝光、共享患者身份和未见确认角色，再用完整模型×输入矩阵检验输入域适应后是否仍有缺层任务损失。GPU训练尚未执行。
