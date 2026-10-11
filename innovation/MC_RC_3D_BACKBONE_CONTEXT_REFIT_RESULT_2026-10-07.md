# 完整context骨干接续拟合：最后模型结果

本阶段仅开发VS-MC-RC-001的一个已见series；两臂各1024次更新所有参数，共2048。主训练与独立核验的工具退出码均实际观察为0。两臂最后checkpoint均冻结后才评分；未选择中途/最佳模型。

4 intra-op/1 interop、自身below-normal、AdamW恒定lr=.001、weight_decay=.0001、原三尺度BCE+Dice、同一冻结16tile流的128轮、含空tile、无增强。训练及主评价总墙钟3314.34秒；独立核验22.63秒。GPU训练0、CUDA未初始化。

## 原门槛逐项结果

| 输入 | 原foreground crop Dice | full Dice | full recall | full absRVE | TP | 全部原gate |
|---|---:|---:|---:|---:|---:|---|
| native_reference | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 0 | 失败 |
| raw_pchip | 0.930993 | 0.973981 | 0.981207 | 0.014837 | 992 | 通过 |

固定gate：foreground crop Dice≥.9；full Dice≥.9、recall≥.9、absRVE≤.25、TP>0。任一失败保持失败，不以其他域或数值实现的有利结果替换。

## 全部域与分母

| 输入 | 域 | GT前景 | 预测前景 | TP | FP | FN | Dice | recall | precision | absRVE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native_reference | full | 1011 | 0 | 0 | 0 | 1011 | 0.000000 | 0.000000 | undefined | 1.000000 |
| native_reference | anchors | 236 | 0 | 0 | 0 | 236 | 0.000000 | 0.000000 | undefined | 1.000000 |
| native_reference | missing | 775 | 0 | 0 | 0 | 775 | 0.000000 | 0.000000 | undefined | 1.000000 |
| native_reference | tail | 0 | 0 | 0 | 0 | 0 | undefined | undefined | undefined | undefined |
| raw_pchip | full | 1011 | 1026 | 992 | 34 | 19 | 0.973981 | 0.981207 | 0.966862 | 0.014837 |
| raw_pchip | anchors | 236 | 235 | 230 | 5 | 6 | 0.976645 | 0.974576 | 0.978723 | 0.004237 |
| raw_pchip | missing | 775 | 791 | 762 | 29 | 13 | 0.973180 | 0.983226 | 0.963338 | 0.020645 |
| raw_pchip | tail | 0 | 0 | 0 | 0 | 0 | undefined | undefined | undefined | undefined |

anchors为真实每4层观测；missing仅最后anchor之前未观测层；tail为最后anchor之后。空GT/空预测与undefined保留，未删除或视为Dice=1。

## 原两个增强crop（包括背景crop）

| 输入 | crop编号 | GT前景 | 预测前景 | TP | FP | FN | Dice | recall | absRVE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| native_reference | 0 | 1662 | 0 | 0 | 0 | 1662 | 0.000000 | 0.000000 | 1.000000 |
| native_reference | 1 | 0 | 0 | 0 | 0 | 0 | undefined | undefined | undefined |
| raw_pchip | 0 | 1662 | 1642 | 1538 | 104 | 124 | 0.930993 | 0.925391 | 0.012034 |
| raw_pchip | 1 | 0 | 278 | 0 | 278 | 0 | 0.000000 | undefined | undefined |

PCHIP原背景增强crop存在278个FP；其通过预定foreground/full-FOV拟合gate不等于所有输入context均无FP。

## 独立实现与坐标精度

| 输入 | 生产坐标重放概率最大差 | 阈值不一致 | float32/NumPy坐标最大差 | 阈值不一致 | 原严格坐标gate | float64/NumPy坐标最大差 | 阈值不一致 |
|---|---:|---:|---:|---:|---|---:|---:|
| native_reference | 0 | 0 | 9.59232693e-14 | 0 | 通过 | 2.22044605e-16 | 0 |
| raw_pchip | 0 | 0 | 1.13248825e-06 | 0 | 通过 | 2.22044605e-16 | 0 |

两臂完整1024行history、同一随机tile stream、每batch真实GT计数、所有16tile每轮覆盖、checkpoint/预测SHA和参数变更已核。module与functional逐tile所有三个head核验通过；四域contingency table及原crop gate独立重算一致。生产坐标与float64坐标结果分开；float64通过不改判float32失败。原端点以生产float32坐标、threshold=.5为准。

## 与旧诊断的联系及限制

旧两个固定crop全网络512更新、冻结骨干两个crop head1024更新、全16tile head1024更新的失败均保留。本次接续同时改变可训练参数集合、输入context与采样域；它是已见series拟合诊断，不能单独归因于某个机制。历史head模型没有被替换或重命名。

两臂全部原gate是否通过：False。即使通过也只证明此已见series和这些训练条件；不能称完整11患者/19series能力、四验证能力、SR损害或收益、第二独立任务网络、患者外科学确认。

原始记录：[训练](experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/attempt01.json)、[独立核验](experiments/mc_rc_3d_backbone_context_refit_v2_2026_10_07/independent_both1024_and_full_fov_attempt01.json)、[论文核读](literature/2026-10-07_exact_tiling_TIN_KIN_primary_reading.md)、[KernelNorm补读与数值准备](literature/2026-10-07_kernel_norm_primary_reading_and_numerical_preparation.md)。
