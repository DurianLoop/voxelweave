# 单012固定切面、完整tile覆盖的最小拟合结果

仅已见开发患者012、第38原生plane，按前景z唯一排序取中位数；随机初始化原981,602参数架构、固定1000updates、无augmentation、全部16tile循环，每tile曝光125次。最后checkpoint按原完整FOV推断/概率回原生/.5，不给推断GT定位。

| 2D native plane端点 | 结果 |
|---|---:|
| Dice | 0.984110500 |
| recall | 0.969312602 |
| precision | 0.999367222 |
| absolute relative area error | 0.030073650 |
| TP / FP / FN | 4738 / 3 / 150 |
| 预写fit gate | True |

预写gate为plane Dice/recall≥.95、绝对相对面积误差≤.05，逐项：{"native_plane_dice": true, "native_plane_recall": true, "absolute_relative_area_error": true}。独立原生label轴、bincount与另套完整plane重放通过；面积ratio不是完整3D体积/缺层能力。

最小固定切面可拟合，说明此架构/几何/优化链条能在这张训练例上达到预写门槛。多切面单病例和多患者失败仍有效；改变了z曝光、augmentation与tile覆盖，不能据此定位一个失败因子。下一步可单独控制采样覆盖/augmentation、充分曝光和whole-FOV训练。

生产global/local调用1001/1004；独立完整plane重放1/4。GPUfalse、确认/验证/隐藏MR未开。单切面训练结果不作独立科学确认，goal active。

[协议](MC_RC_GLOBAL_LOCAL_FIXED_PLANE_FIT_CPU_PROTOCOL_2026-10-03.md)、[原始生产](experiments/mc_rc_global_local_fixed_plane_fit_cpu/attempt_01.json)、[独立核验](experiments/mc_rc_global_local_fixed_plane_fit_cpu/independent_metrics_and_plane_attempt_01.json)。
