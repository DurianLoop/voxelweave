# anchors-only对照必须控制全volume归一化

固定VS-SEG-202/203/204，raw及mixed_post两基线，共6个真实体积对照。修正版session90226实际exit0、CUDA未初始化、0神经前向。共享模块间接导入torch，未加载checkpoint；MONAI NormalizeIntensity类从已认证wheel/vendored文件隔离执行，Transform基类替换为object，未导入完整MONAI环境。该技术预检没有独立第二实现/科学患者复核，不等同于任务成功。

| 患者/基线 | 原缺层像素不变 | ownstats归一化后缺层变化像素 | 最大绝对差 | RMS | 固定stats缺层变化像素 |
| --- | --- | ---: | ---: | ---: | ---: |
| VS-SEG-202/raw | 是 | 11440128/11440128 | 0.16101456 | 0.01284055 | 0 |
| VS-SEG-202/mixed_post | 是 | 11440128/11440128 | 0.15453243 | 0.01342209 | 0 |
| VS-SEG-203/raw | 是 | 11440128/11440128 | 0.12815380 | 0.01122568 | 0 |
| VS-SEG-203/mixed_post | 是 | 11440128/11440128 | 0.12835598 | 0.01167346 | 0 |
| VS-SEG-204/raw | 是 | 11440128/11440128 | 0.20043087 | 0.01295783 | 0 |
| VS-SEG-204/mixed_post | 是 | 11440128/11440128 | 0.18060684 | 0.01354872 | 0 |

六对均保持原缺层数组完全相同；更换anchors后使用各自mean/std，全部缺层像素的网络前归一化数值改变。固定对应基线的mean/std后，六对missing与tail逐位一致。这是输入层面的直接反例：重建数组中的missing不变，并不保证任务网络接收的missing不变。最大差单位为归一化强度，不是原MRI值、解剖误差或Dice。

首session51036实际exit1，最后的torch未导入断言错误；先前六组数组断言已经通过。首计划/脚本/contract/failed attempt均完整保留，追加[修正说明](ANCHOR_NORMALIZATION_CONTROL_CPU_REPAIR_2026-10-03.md)与attempt02，只修过程标记、不改变患者/条件/计算。首结果静态torch_imported=false不是实际状态证据。

后续任务应比较2×2输入条件×own/fixed normalization，而非只比较改anchors前后。固定stats技术控制可用原解析baseline由anchors构造，但改变observed anchors的图像条件仍不符合原SR合同。未执行此任务矩阵，0新Dice结论。

证据：[初方案](ANCHOR_NORMALIZATION_CONTROL_CPU_PLAN_2026-10-03.md)、[首失败](experiments/anchor_normalization_control_cpu/attempt_01.json)、[实际修正版结果](experiments/anchor_normalization_control_cpu_attempt_02/attempt_01.json)。
