# 观测投影信息诊断：执行前源码核对后的 v2

保留最初 [v1 协议](OBSERVED_PROJECTION_INFORMATION_PROTOCOL_2026-10-08.md)，未执行其中任何合成数组或效果评分。核原 `mc_rc_observed_only_training_input.reconstruct` 源码后发现，本项目raw_pchip只有内部间隔使用四anchor的PCHIP，首尾间隔走linear fallback；不能将全局PCHIP见证称项目预处理的见证。因此在新实验之前用本v2明确绑定实际fallback并替换固定合成数组，不是根据已测效果调例子。两协议均保留，v2是唯一执行合同。

全19系列metadata秩、独立modular rank、角色关闭、资源预算和原训练约束保持v1。使用已冻结两通道资格/独立核验的native_shape/observed_indices/grid，仅读JSON/源码，不读MRI/GT/NPZ/checkpoint。生产Fraction精确消元；独立两个预定素数1000003/1000033达到matrix维数上界才出有理数秩证书，否则记录未资格。归一化统计固定、availability仅由mask决定，padding不影响秩。理想实数秩不保证float32可逆/条件数，不描述实际MRI信号或PCHIP总信息量。

唯一固定合成见证：native r=4,c=1,z=16，observed z=[0,4,8,12]，physical r=2,c=1,z=12。

- A：[[0,0,3,3],[0,2,1,3],[0,1,2,3],[0,1,2,3]]。
- C：[[0,0,1,3],[0,2,3,3],[0,1,2,3],[0,1,2,3]]。

两者observed mean=3/2、variance=3/2、std=sqrt(3/2)，元素16；统计由observed实际复算，两者相同不只假设固定外部常数。比较：(1)现有模块native sparse normalized numerator/availability→physical trilinear；(2)现有模块native raw_pchip（首尾linear fallback，内部四anchor SciPy PCHIP，tail复制）→同observed归一化→physical；(3)先将observed anchors面内投影到相同physical平面，再同一local_pchip/fallback→归一化→z physical map。记录所有数组与SHA和float32结果。

生产调用现有 `native_fields/physical_fields`，直接验证真实实现，不写另一个冒充原模块的算法。合成observed数据实例没有真实MRI文件/UID/标签。路径(3)只在本合成诊断实现，不改正式模块或已资格baseline；它是后续控制准备，非已训练新方法。

独立以有理数Fritsch-Butland斜率及Hermite核内部区间、显式linear边界及tail、原像素中心trilinear，最后sqrt(3/2)归一化；与生产float32比较atol/rtol各1e-5。不跑神经网，不把差异当PCHIP更优、任务收益或临床效果。同raw观察的流程比较仍有意义，但输入变换差异不能被隐藏或宣称严格信息等价。

自身CUDA不可见，CPU1/interop1、BLAS1、below-normal，每生产/独立<=600s，RAM/disk各8GB余量，新stage<=20MB。新医学数组、神经/GPUforward、训练更新0，不操作/枚举其他PID，不新委派。原训练99542继续原合同；真实final退出后才56FOV/6gates/strict，确认/验证/lockedIXI关闭。失败留原version/attempt，新修复另存。
