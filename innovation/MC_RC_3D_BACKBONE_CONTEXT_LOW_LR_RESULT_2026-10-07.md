# 低学习率完整 context 对照：实测结果

两臂各1024次全骨干更新，共2048次CPU更新；原session89014已实际退出0，独立module/functional、完整history/GT流、四域计数及坐标重放亦实际退出0。没有重启该训练，GPU更新0。两臂均在评分前保存最后模型，阈值.5，原gate不改。

## 单开发series的同初始化/同流LR控制

| LR | 输入 | full Dice | recall | absRVE | 原foreground crop Dice | 原背景crop FP | 原拟合gate |
|---:|---|---:|---:|---:|---:|---:|---|
| 0.001 | native_reference | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0 | 失败 |
| 0.001 | raw_pchip | 0.973981 | 0.981207 | 0.014837 | 0.930993 | 278 | 通过 |
| 0.0001 | native_reference | 0.967647 | 0.976261 | 0.017804 | 0.938221 | 44 | 通过 |
| 0.0001 | raw_pchip | 0.963253 | 0.972305 | 0.018793 | 0.928290 | 0 | 通过 |

唯一训练配置变化为恒定LR .001 -> .0001；各臂自身初始checkpoint和128轮完整16tile流相同。从各自初始全tile head模型重启，非从崩塌后权重继续。各臂初始模型此前已用不同图像训练，所以两臂的最终差异不能视为MRI恢复收益；这是标准优化/能力对照，训练患者1、series1、独立科学确认0。旧高LR失败保留。

低LR主训练实测总墙钟 3484.30 秒；独立核验 23.82 秒。完整原始分母、空值、TP/FP/FN/TN 在下表及原JSON保留。

## 低LR四域原始计数

| 输入 | 域 | GT foreground | pred foreground | TP | FP | FN | TN | Dice | recall | absRVE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native_reference | full | 1011 | 1029 | 987 | 42 | 24 | 1965027 | 0.967647 | 0.976261 | 0.017804 |
| native_reference | anchors | 236 | 240 | 234 | 6 | 2 | 524046 | 0.983193 | 0.991525 | 0.016949 |
| native_reference | missing | 775 | 789 | 753 | 36 | 22 | 1375445 | 0.962916 | 0.971613 | 0.018065 |
| native_reference | tail | 0 | 0 | 0 | 0 | 0 | 65536 | undefined | undefined | undefined |
| raw_pchip | full | 1011 | 1030 | 983 | 47 | 28 | 1965022 | 0.963253 | 0.972305 | 0.018793 |
| raw_pchip | anchors | 236 | 236 | 231 | 5 | 5 | 524047 | 0.978814 | 0.978814 | 0.000000 |
| raw_pchip | missing | 775 | 794 | 752 | 42 | 23 | 1375439 | 0.958572 | 0.970323 | 0.024516 |
| raw_pchip | tail | 0 | 0 | 0 | 0 | 0 | 65536 | undefined | undefined | undefined |

## 原门槛与独立坐标状态

- native_reference 原gate: `{"foreground_patch_dice": true, "training_full_dice": true, "training_full_recall": true, "training_full_absRVE": true, "training_tp_positive": true}`。
- native_reference 生产module/functional重放概率最大差 0，二值差异 0；生产float32 vs NumPy: `{"max_probability_error": 1.1920928955078125e-06, "threshold_disagreements": 0, "original_strict_gate_passed": true}`；独立float64: `{"max_probability_error": 0.0, "threshold_disagreements": 0, "gate_passed": true}`。
- raw_pchip 原gate: `{"foreground_patch_dice": true, "training_full_dice": true, "training_full_recall": true, "training_full_absRVE": true, "training_tp_positive": true}`。
- raw_pchip 生产module/functional重放概率最大差 0，二值差异 0；生产float32 vs NumPy: `{"max_probability_error": 1.1324882507324219e-06, "threshold_disagreements": 0, "original_strict_gate_passed": true}`；独立float64: `{"max_probability_error": 7.105427357601002e-15, "threshold_disagreements": 0, "gate_passed": true}`。

19series资源资格启动条件：两臂原拟合gate全部通过=True；两臂生产float32严格坐标门槛全部通过=True；合并条件=True。没有用float64成功替代float32失败。

11开发患者/19series、4已见验证/9series、8保留确认/12series角色不变；本训练/重放没有加载新验证或确认效果，也不是正式19series充分适配。下一步资格/诊断按真实合并条件决定，不根据指标临时改变端点。

[完整主结果](experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/attempt01.json) · [独立重放](experiments/mc_rc_3d_backbone_context_low_lr_2026_10_07/independent_both1024_and_full_fov_attempt01.json) · [原协议](MC_RC_3D_BACKBONE_CONTEXT_LOW_LR_CONTROL_PROTOCOL_2026-10-07.md) · [创新收窄](INNOVATION_DECISION_AFTER_DEFER_READING_2026-10-07.md)。
