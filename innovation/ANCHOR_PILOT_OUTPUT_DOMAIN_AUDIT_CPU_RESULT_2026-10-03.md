# 三人已保存预测：观测层、缺层和tail的实际响应

这是完整pilot后的事后开发审计，没有新前向或MRI像素解码，torch未导入。18保存预测与三标签文件SHA核对；54个配对分区XOR计数以逆方向映射逐原生层复算，full混淆计数等于三个分区之和。两标签和原六比较全部保留。

| 患者 | fixed post 缺层网络输入 | supported missing 预测变化体素 | 缺层域总量 |
| --- | --- | ---: | ---: |
| VS-SEG-202 | 逐位相同（已有输入证明） | 288 | 11440128 |
| VS-SEG-203 | 逐位相同（已有输入证明） | 593 | 11440128 |
| VS-SEG-204 | 逐位相同（已有输入证明） | 186 | 11440128 |

完整体积Dice包含anchors，因此full差本身不足以定位缺层输出。上表直接核对实际missing预测，任何变化只能解释为当前完整任务推理链对仅anchors干预的响应；3D上下文、内部统计和滑窗等效应在这里未进一步拆开。未证明真实MRI解剖改变，也不支持已失败的带宽恢复主张。

[54个XOR分区计数](experiments/anchor_pilot_output_domain_audit_cpu/all54_prediction_xor_domains.csv)、[108个两标签分区任务差](experiments/anchor_pilot_output_domain_audit_cpu/all108_label_domain_task_differences.csv)、[完整来源与身份记录](experiments/anchor_pilot_output_domain_audit_cpu/attempt_01.json)。supported missing与observed anchors指标不替代原full主结果；科学独立确认仍为0。
