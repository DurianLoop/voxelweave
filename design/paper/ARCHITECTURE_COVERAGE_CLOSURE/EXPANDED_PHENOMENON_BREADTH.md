# 非核心基线的相位覆盖敏感性

本表不是新增的跨模型主检验。shared 是同一冻结输出的确定性重复，故 O=0 是构造结果；正 ΔO 说明相位变化使预测改变，不能单独证明共享误差机制、TTA 鲁棒性或独立错误。该限制同样适用于所有八个模型，不挑选支持区域。

| 队列 | 模型 | 支持 | ΔO [同时95%CI] pp |
|---|---|---|---|
| fastmri | linear | acquired_union | 30.107 [29.236,30.979] |
| fastmri | cubic | acquired_union | 38.528 [37.419,39.637] |
| fastmri | acvtt | acquired_union | 12.191 [10.828,13.555] |
| fastmri | ressrdiff | acquired_union | 21.993 [20.443,23.543] |
| fastmri | arssr | acquired_union | 24.158 [23.275,25.041] |
| fastmri | resunet | acquired_union | 19.924 [18.513,21.335] |
| fastmri | gan_2p5d | acquired_union | 29.441 [28.213,30.669] |
| fastmri | smamba_unet | acquired_union | 26.143 [24.761,27.526] |
| fastmri | linear | full_common_valid | 30.162 [29.284,31.039] |
| fastmri | cubic | full_common_valid | 38.623 [37.506,39.741] |
| fastmri | acvtt | full_common_valid | 12.190 [10.825,13.554] |
| fastmri | ressrdiff | full_common_valid | 21.987 [20.437,23.538] |
| fastmri | arssr | full_common_valid | 24.183 [23.295,25.071] |
| fastmri | resunet | full_common_valid | 19.918 [18.509,21.327] |
| fastmri | gan_2p5d | full_common_valid | 29.427 [28.200,30.654] |
| fastmri | smamba_unet | full_common_valid | 26.135 [24.753,27.516] |
| fastmri | linear | target_1pct | 30.365 [29.442,31.289] |
| fastmri | cubic | target_1pct | 38.638 [37.474,39.801] |
| fastmri | acvtt | target_1pct | 12.457 [11.111,13.802] |
| fastmri | ressrdiff | target_1pct | 22.112 [20.542,23.682] |
| fastmri | arssr | target_1pct | 24.309 [23.400,25.217] |
| fastmri | resunet | target_1pct | 20.101 [18.694,21.508] |
| fastmri | gan_2p5d | target_1pct | 29.572 [28.341,30.803] |
| fastmri | smamba_unet | target_1pct | 26.335 [24.955,27.715] |
| ixi | linear | acquired_union | 28.775 [28.196,29.353] |
| ixi | cubic | acquired_union | 41.671 [40.634,42.707] |
| ixi | acvtt | acquired_union | 28.000 [27.340,28.660] |
| ixi | ressrdiff | acquired_union | 32.216 [31.370,33.062] |
| ixi | arssr | acquired_union | 31.396 [30.721,32.071] |
| ixi | resunet | acquired_union | 30.809 [30.107,31.511] |
| ixi | gan_2p5d | acquired_union | 24.272 [23.727,24.816] |
| ixi | smamba_unet | acquired_union | 29.767 [28.959,30.575] |
| ixi | linear | full_common_valid | 28.757 [28.181,29.333] |
| ixi | cubic | full_common_valid | 41.627 [40.598,42.656] |
| ixi | acvtt | full_common_valid | 27.957 [27.301,28.614] |
| ixi | ressrdiff | full_common_valid | 32.136 [31.300,32.972] |
| ixi | arssr | full_common_valid | 31.348 [30.679,32.018] |
| ixi | resunet | full_common_valid | 30.783 [30.087,31.479] |
| ixi | gan_2p5d | full_common_valid | 24.208 [23.665,24.750] |
| ixi | smamba_unet | full_common_valid | 29.700 [28.901,30.500] |
| ixi | linear | target_1pct | 28.969 [28.387,29.550] |
| ixi | cubic | target_1pct | 41.801 [40.770,42.832] |
| ixi | acvtt | target_1pct | 28.135 [27.477,28.792] |
| ixi | ressrdiff | target_1pct | 32.295 [31.457,33.133] |
| ixi | arssr | target_1pct | 31.517 [30.845,32.188] |
| ixi | resunet | target_1pct | 30.956 [30.258,31.655] |
| ixi | gan_2p5d | target_1pct | 24.394 [23.853,24.934] |
| ixi | smamba_unet | target_1pct | 29.860 [29.057,30.663] |

原五架构 20 有向对/队列的主矩阵、目标、权重和同时区间全部不变。新增矩阵使用同一五个目标；每目标共同有限支持、每检查内均值、检查等权；5000次共同检查bootstrap，按队列/支持在八个非核心模型之间同时校正。
Res-SRDiff：固定外生 RNG seed20260914，保存完整原采样顺序，包括未用于统计的输出切片；这是条件于固定随机性的相位实验，不是重跑旧 PSNR 表。其随机扩散噪声不能借此被宣称通过 acquired-only 有限响应合同。
ArSSR：完整体积编码保留，仅省略未使用的输出坐标；与原 wrapper 的逐值一致性单列。其他目标选算也在各队列第一个注册病例和全 wrapper 比对后才能使用。IXI 保留输入 NIfTI staging；新预测以浮点 NPZ 保存，不冒称重现旧输出 NIfTI 的序列化量化。
目标支持、acquired-union、全共同有效支持均报告；没有按结果挑选 mask、模型或病例。