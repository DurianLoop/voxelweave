# 全tile特征覆盖诊断：最后权重全部结果

native/PCHIP各1024次17参数CPU更新，共2048；固定原骨干，使用同一开发001的全部16个推断tile。
原crop主head分支4096次及原全网络1024次更新分别保留，不合并成一次连续训练。全部原训练gate仍失败；没有验证/确认或新恢复方法确认。

| 输入 | 原foreground crop Dice | 全tile训练soft Dice | 完整FOV Dice | recall | precision | absRVE | TP/FP/FN | 原gate |
|---|---:|---:|---:|---:|---:|---:|---|---|
| native_reference | 0.919808 | 0.705941 | 0.678448 | 0.873393 | 0.554648 | 0.574679 | 883/709/128 | False |
| raw_pchip | 0.871483 | 0.632167 | 0.475659 | 0.758655 | 0.346432 | 1.189911 | 767/1447/244 | False |

每臂RAM特征矩阵1,073,741,824bytes；每更新16,777,216个重复tile体素，GT前景13,938，全部16tile保留。
重复体素是训练分母，不是独立patient/series；本项没有删除背景/空tile。native/PCHIP分别训练约151.65/141.81秒，总墙钟约350.65秒。
全tile覆盖后完整FOV Dice从局部head的0.590714/0.372671提高到0.678448/0.475659，但两臂仍未达到0.9，不能作为充分任务能力。
PCHIP原训练crop的Dice还从局部head0.907710降为0.871483。全部context上的共同线性head仍有残余误差；需进一步骨干适配/优化/context控制。
相较局部head，本项改变了训练空间/context覆盖与loss聚合域；不能称严格单因素采样因果实验。来自同一个已见开发series的比较不支持跨患者重建优劣结论。

## 所有域与完整分母

| 输入/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT | pred |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native_reference/full | 0.678448 | 0.873393 | 0.554648 | 0.574679 | 883 | 709 | 128 | 1964360 | 1011 | 1592 |
| native_reference/anchors | 0.643505 | 0.902542 | 0.500000 | 0.805085 | 213 | 213 | 23 | 523839 | 236 | 426 |
| native_reference/missing | 0.690366 | 0.864516 | 0.574614 | 0.504516 | 670 | 496 | 105 | 1374985 | 775 | 1166 |
| native_reference/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 |
| raw_pchip/full | 0.475659 | 0.758655 | 0.346432 | 1.189911 | 767 | 1447 | 244 | 1963622 | 1011 | 2214 |
| raw_pchip/anchors | 0.455013 | 0.750000 | 0.326568 | 1.296610 | 177 | 365 | 59 | 523687 | 236 | 542 |
| raw_pchip/missing | 0.482223 | 0.761290 | 0.352871 | 1.157419 | 590 | 1082 | 185 | 1374399 | 775 | 1672 |
| raw_pchip/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 |

## 独立实现核验

- native_reference：1024历史/LR、52项冻结骨干、1GiB特征和全部标签流SHA核对；16tile标签/预测/float64 NumPy loss一致，完整1966080native体素重放，最大概率误差7.74860382e-07，阈值预测差异0。
- raw_pchip：1024历史/LR、52项冻结骨干、1GiB特征和全部标签流SHA核对；16tile标签/预测/float64 NumPy loss一致，完整1966080native体素重放，最大概率误差8.94069672e-07，阈值预测差异0。

所有16tile的hard计数、empty/undefined及原crop计数见JSON。功能/模块网络比较仍只是实现核验，非第二独立训练网络。

[全部结果](experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/attempt01.json)、[特征/完整FOV核验](experiments/mc_rc_3d_all_tile_head_fit_2026_10_07/module_features_and_full_fov_verification_attempt01.json)、[冻结协议](MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md)。
