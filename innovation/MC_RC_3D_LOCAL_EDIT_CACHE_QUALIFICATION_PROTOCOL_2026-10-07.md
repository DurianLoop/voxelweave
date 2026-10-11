# 单开发 MRI 的局部修改缓存资格协议

目的：验证在已冻结的滑窗推断函数上，局部缺层输入修改能否复用未受影响窗口的最终概率，减少后续动作对照计算。已知增量缓存先例为 DeltaCNN 与 SIGE；本实验不检验新方法、MRI 恢复效果或最终 19-series 模型能力。

只读取开发 VS-MC-RC-001、UID 末尾 369177 的 observed-only 包及其 PCHIP 构造。模型固定为已完成并独立核验的单001低学习率 raw_pchip_last1024.pt；不读取正在训练的中间模型。两模型公平性不在本实验范围。

ROI 只用 native_shape 选择：r/c 中心各7像素，在区间内非锚点层中选择离 z 中点最近者（并列选较小索引）。对已按 observed statistics 归一化的输入加 float32 0.25。锚点层和 observed package 完全不修改；原统计量不重估。无 GT 用于选 ROI，不读 label 或完整 native-reference MRI。

采用原 physical_mr trilinear center map。逐元素精确找出实际改变的 physical 输入；逐窗口检查是否含改变元素，再提升到原 batch pair（原位置和顺序不变）。受影响 batch 中全部窗口重算，不在窗口内裁小 patch，不冻结或替换 InstanceNorm 统计。

先完整计算基线16窗口并缓存概率，再完整计算修改后16窗口作为参考；最后只重算受影响的原 batch pair，复用其余基线概率。三次计算使用同权重、float32、CPU4 intra-op / 1 inter-op。Gaussian 权重、float64 累计、padding 裁剪和 native float32 回映与原函数相同。

门槛在读取 MRI 前固定：缓存路径与完整修改路径所有 tile 概率、physical 拼接概率及 native 概率的 array SHA 完全一致；native 阈值0.5差异0；未受影响窗口输入和概率完全相等；缓存路径至少少一次 forward；原生产 infer_full_fov 对完整修改路径也必须概率 SHA/coverage SHA 一致。保留所有失败，不放宽为容差门槛。

额外只记录基线与修改输入之间的 probability/threshold 变化，按 full/anchors/missing/tail 划分。它们无 GT、不是 Dice 或病灶收益。若锚点任务预测发生变化，仅说明保留输入锚点不保证任务输出锚点不变；不能把变化唯一归因为 IN，卷积和重采样同样存在。检查 physical 输出改变是否位于实际受影响窗口并集。

资源：仅本进程 below-normal；8GB RAM/磁盘余量、900秒墙钟，stage保存最多10MB。概率缓存仅驻留 RAM，不保存 MRI/GT/预测体积。本次不是正式GPU实验（GPU授权保持，空闲显存不足）；不控制其他PID或用户终端训练。

时钟仅是同时有训练负载时的单次观察，不作为加速benchmark。明确记录缓存初始化成本、跳过数、实际 forward数和所需概率缓存字节；即使缓存结果通过，也不能推出收益标签已有效、候选动作有价值或可发表claim成立。
