# 开发标签与合法支持的重叠资格（运行前）

全38独特patch、39845888目标体素两级支持mask核验已经真正f75c96 exit0，30patch部分真实FOV支持不足、8完全充分。不能据保守box全部超界就禁用全部增强；也不能据背景角点缺失推定病灶监督被破坏。

本次只加载11开发患者19series的原reference label，按旧认证physical_label/lattice映射，以旧全target SHA、crop start/flips和母batch SHA匹配38patch。仅读label/metadata，不加载MR或model，不运行患者分割性能。所有series/患者保留，不按GT筛病例；4已见验证/8未见确认/lockedIXI关闭。

重新计算已通过全体素独立SciPy核验的生产几何support mask，严格采用相同参数/threshold1−1e-9；哈希匹配已保存mask。分别计数foreground和background在crop-only/真实fullFOV支持不足的位置、失去的权重均值；用于判断mask-loss/common interior会否丢失病灶训练监督。标签完全不变，GT不参与几何mask/策略/阈值的计算。

这是开发入口与监督重叠诊断，不是标签质量审计、患者效益或病灶医学伤害结论，更不证明augmentation失效原因。未核验完整2992训练分布，未来仍须matched训练和完整FOV评价，六医学门槛不降。

CPU1、低优先级、wall300秒、stage5MB与磁盘/RAM8GB储备，不操作任何其他PID。原训练保持源/配方/设备不变。
