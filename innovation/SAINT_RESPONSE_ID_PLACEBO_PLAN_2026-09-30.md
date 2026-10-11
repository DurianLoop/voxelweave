# SAINT acquired-only 锚点响应错配负对照

本方案在已见 SAINT 精确上下文关联及 HAT/SwinIR 错配结果后制定，属于**结果后探索**。待 MSValid P25–P36 CPU 批次结束后只读 `ARCHITECTURE_COVERAGE_CLOSURE/outputs/acquired_responses` 中全部 SAINT NPZ，以及已保存的 `saint_acquired_observations.csv`；不调用模型/GPU。对 fastMRI/IXI 全部 24/115 检查对象、每对象三个目标、每目标四个一共享上下文，在主幅度 `.01` 计算正确物理锚点响应配对及与前述实验完全相同的 A/B 错配。三者共享完整响应能量分母。逐文件 SHA-256 核原 CSV `source_hash`，原影响分数复算误差须不超过 `1e-7`。

全局 rank 后同时调整目标和精确上下文类别，主比较为正确配对偏相关减两错配偏相关均值；检查对象整体 1,000 次 bootstrap，fastMRI 种子 20261024、IXI 种子 20261025，仅给探索性区间。报告所有层与阴性结果，不因已知 SAINT 正关联修改负对照定义。即使正值，也只是第三架构的内部响应标签特异性，不等于真实物理采集随机化、外部队列复制或实用评分。
