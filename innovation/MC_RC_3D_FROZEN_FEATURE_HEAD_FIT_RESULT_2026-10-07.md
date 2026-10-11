# 固定骨干、主head拟合：全部结果

4分支各1024次CPU参数更新（bias-only 1参数/full-head 17参数），共4096次；原全网络1024更新另计。
仅001开发系列，骨干及aux heads未更新、阈值0.5不变，四验证/八确认未开。所有分支仍失败原完整拟合gate。

| 输入/分支 | 原foreground crop Dice | 主head soft Dice | 完整FOV Dice | recall | precision | absRVE | TP/FP/FN | 原gate |
|---|---:|---:|---:|---:|---:|---:|---|---|
| native_reference/bias_only | 0.499774 | 0.388206 | 0.240725 | 0.144411 | 0.722772 | 0.800198 | 146/56/865 | False |
| native_reference/full_head | 0.943708 | 0.933369 | 0.590714 | 0.818002 | 0.462269 | 0.769535 | 827/962/184 | False |
| raw_pchip/bias_only | 0.449627 | 0.314415 | 0.407837 | 0.277943 | 0.765668 | 0.636993 | 281/86/730 | False |
| raw_pchip/full_head | 0.907710 | 0.897301 | 0.372671 | 0.860534 | 0.237835 | 2.618200 | 870/2788/141 | False |

17参数分支将同一foreground训练crop Dice提高到native0.943708/PCHIP0.907710，而完整FOV仅0.590714/0.372671。
这表明原最后特征对该crop具有可利用的分离能力，不支持“当前架构无法学习”的断言；完整体积门槛仍失败，需要覆盖实际推断contexts的训练/骨干适配。
bias-only降低背景概率同时明显牺牲recall；不能只看某个Dice改善选择阈值/偏置策略。输出层分支也改变了优化隔离及LR，不能单因果归结为偏置初始化或深监督冲突。

## 全部域和分母

| 输入/分支/域 | Dice | recall | precision | absRVE | TP | FP | FN | TN | GT | pred |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| native_reference/bias_only/full | 0.240725 | 0.144411 | 0.722772 | 0.800198 | 146 | 56 | 865 | 1965013 | 1011 | 202 |
| native_reference/bias_only/anchors | 0.335664 | 0.203390 | 0.960000 | 0.788136 | 48 | 2 | 188 | 524050 | 236 | 50 |
| native_reference/bias_only/missing | 0.211435 | 0.126452 | 0.644737 | 0.803871 | 98 | 54 | 677 | 1375427 | 775 | 152 |
| native_reference/bias_only/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 |
| native_reference/full_head/full | 0.590714 | 0.818002 | 0.462269 | 0.769535 | 827 | 962 | 184 | 1964107 | 1011 | 1789 |
| native_reference/full_head/anchors | 0.542135 | 0.817797 | 0.405462 | 1.016949 | 193 | 283 | 43 | 523769 | 236 | 476 |
| native_reference/full_head/missing | 0.607280 | 0.818065 | 0.482864 | 0.694194 | 634 | 679 | 141 | 1374802 | 775 | 1313 |
| native_reference/full_head/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 |
| raw_pchip/bias_only/full | 0.407837 | 0.277943 | 0.765668 | 0.636993 | 281 | 86 | 730 | 1964983 | 1011 | 367 |
| raw_pchip/bias_only/anchors | 0.402367 | 0.288136 | 0.666667 | 0.567797 | 68 | 34 | 168 | 524018 | 236 | 102 |
| raw_pchip/bias_only/missing | 0.409615 | 0.274839 | 0.803774 | 0.658065 | 213 | 52 | 562 | 1375429 | 775 | 265 |
| raw_pchip/bias_only/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 |
| raw_pchip/full_head/full | 0.372671 | 0.860534 | 0.237835 | 2.618200 | 870 | 2788 | 141 | 1962281 | 1011 | 3658 |
| raw_pchip/full_head/anchors | 0.371025 | 0.889831 | 0.234375 | 2.796610 | 210 | 686 | 26 | 523366 | 236 | 896 |
| raw_pchip/full_head/missing | 0.373198 | 0.851613 | 0.238957 | 2.563871 | 660 | 2102 | 115 | 1373379 | 775 | 2762 |
| raw_pchip/full_head/tail | undefined | undefined | undefined | undefined | 0 | 0 | 0 | 65536 | 0 | 0 |

## 独立实现核验

- native_reference/bias_only：1024条历史、冻结参数及SHA核对；模块网络重放全部1966080体素/16tiles，最大概率误差2.08616257e-07，二值差异0，四域和原gate全部一致。
- native_reference/full_head：1024条历史、冻结参数及SHA核对；模块网络重放全部1966080体素/16tiles，最大概率误差9.53674316e-07，二值差异0，四域和原gate全部一致。
- raw_pchip/bias_only：1024条历史、冻结参数及SHA核对；模块网络重放全部1966080体素/16tiles，最大概率误差2.98023224e-07，二值差异0，四域和原gate全部一致。
- raw_pchip/full_head：1024条历史、冻结参数及SHA核对；模块网络重放全部1966080体素/16tiles，最大概率误差1.07288361e-06，二值差异0，四域和原gate全部一致。

功能网络与模块网络的比较是实现核验，不是第二独立训练任务网络。
下一项按新协议在全部16个推断tile特征上拟合同样17参数，检查覆盖的影响；不将重复tile/voxel当独立患者，不更改门槛。

[运行结果](experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/attempt01.json)、[模块网络核验](experiments/mc_rc_3d_frozen_feature_head_fit_2026_10_07/module_full_fov_verification_attempt01.json)、[新覆盖协议](MC_RC_3D_ALL_TILE_HEAD_FIT_PROTOCOL_2026-10-07.md)。
