# 两臂512更新CPU拟合：完整实际结果

两臂各512更新已完成，共1024更新；独立checkpoint/完整FOV重放与四变体patch诊断均已执行。
只训练同一个开发系列001，不能作为19series充分训练、四验证能力或重建创新确认。GPU更新0，八确认未开，科学确认0。

| 输入 | foreground训练patch Dice | 完整训练FOV Dice | recall | absRVE | TP | 拟合gate | 更新耗时(秒) |
|---|---:|---:|---:|---:|---:|---|---:|
| native_reference | 0.834883 | 0.351453 | 0.975272 | 3.549951 | 986 | False | 1867.580407 |
| raw_pchip | 0.814870 | 0.256330 | 0.976261 | 5.617211 | 987 | False | 1855.260587 |

## 所有域及空/undefined

| 输入/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT前景 | 预测前景 | GT空 | 预测空 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| native_reference/full | 0.351453 | 0.975272 | 0.214348 | 3.549951 | 986 | 3614 | 25 | 1961455 | 1011 | 4600 | False | False |
| native_reference/anchors | 0.333574 | 0.978814 | 0.201044 | 3.868644 | 231 | 918 | 5 | 523134 | 236 | 1149 | False | False |
| native_reference/missing | 0.357312 | 0.974194 | 0.218777 | 3.452903 | 755 | 2696 | 20 | 1372785 | 775 | 3451 | False | False |
| native_reference/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 | True | True |
| raw_pchip/full | 0.256330 | 0.976261 | 0.147534 | 5.617211 | 987 | 5703 | 24 | 1959366 | 1011 | 6690 | False | False |
| raw_pchip/anchors | 0.233924 | 0.978814 | 0.132835 | 6.368644 | 231 | 1508 | 5 | 522544 | 236 | 1739 | False | False |
| raw_pchip/missing | 0.264059 | 0.975484 | 0.152696 | 5.388387 | 756 | 4195 | 19 | 1371286 | 775 | 4951 | False | False |
| raw_pchip/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 | True | True |

## 预定的四个crop变体（不是四种完整体积效果）

| 输入/变体 | foreground crop主head hard-Dice | 主head batch soft-Dice | 主head前景平均概率 | 主head背景平均概率 | 三head加权loss |
|---|---:|---:|---:|---:|---:|
| native_reference/training_augmented | 0.834883 | 0.011610 | 0.965567 | 0.130403 | 0.921665 |
| native_reference/flips_only | 0.834673 | 0.011609 | 0.965610 | 0.130422 | 0.921677 |
| native_reference/intensity_only | 0.834883 | 0.010742 | 0.965567 | 0.141066 | 0.947387 |
| native_reference/identity | 0.834673 | 0.010740 | 0.965610 | 0.141102 | 0.947087 |
| raw_pchip/training_augmented | 0.814870 | 0.011515 | 0.953220 | 0.129802 | 0.920600 |
| raw_pchip/flips_only | 0.815070 | 0.011515 | 0.953205 | 0.129799 | 0.920596 |
| raw_pchip/intensity_only | 0.814870 | 0.011405 | 0.953220 | 0.131069 | 0.932653 |
| raw_pchip/identity | 0.815070 | 0.011405 | 0.953205 | 0.131063 | 0.932640 |

完整逐head数量、概率及梯度核对见诊断JSON。4变体均报告，没有挑最优变体或改变阈值。
logit梯度是当前输出上的局部描述，不是模型参数梯度冲突、优化因果证明或新的训练方法。

## 独立实现核验

- native_reference：512条更新/LR记录及checkpoint来源已核；1966080完整native voxel重放，概率最大绝对误差5.96046448e-07，阈值预测差异0；16tiles、全部四域计数和拟合gate核对。
- raw_pchip：512条更新/LR记录及checkpoint来源已核；1966080完整native voxel重放，概率最大绝对误差6.55651093e-07，阈值预测差异0；16tiles、全部四域计数和拟合gate核对。

功能重放器是独立实现核验，不是第二独立训练任务网络。CPU结果不自动通过GPU显存/数值/速度资格。
门槛失败保留，不减少分母、不改阈值/最后权重、不把弱任务能力改写成SR损害病灶。

[训练记录](experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/attempt_01.json)、[独立重放](experiments/mc_rc_3d_cpu_fixed_fit_2026_10_07/independent_both512_and_full_fov_2026_10_07.json)、[四变体诊断](experiments/mc_rc_3d_final_patch_diagnostic_2026_10_07/attempt01.json)。
