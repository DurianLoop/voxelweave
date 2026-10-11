# 全2992步病灶采样点—部署窗口位置诊断

预先固定：全部11开发患者/19series，原四臂全部2992步；以冻结intensity训练日志每步第一patch的forced-foreground点为探针。其GT归属来自已完成5984行独立母标签审计。本阶段不加载MRI/GT/model数组；不读取开发评估partial指标。对四臂每步的patient/uid/geometry/mother label核对完全一致。

用原lattice和tile_plan，枚举包含每个探针的部署tile，按实际Gaussian融合权重归一化。独立标量公式核全部探针权重，并核原production blending_weight逐点值（误差<=3e-6）。每点报告训练patch及部署贡献的最近边界距离、距任一边界<8及<16体素的比例、归一化中心偏移，以及下采样相位相同的贡献比例。几何以增强前母图坐标为准；flip不改变中心偏移绝对值与边界距离，空间分支的实际最终label不在本诊断中重新分析。

所有探针保留，包括padding邻近与重复点；系列内点均值，再series→patient→全11患者。它仅描述被前景采样加权的一组真实训练点，不能代替全病灶体素、正常背景、验证患者或总体解剖分布，不估计Dice/recall或因果。

若训练和部署加权边界暴露近似，不再把简单边缘位置失配当首要未经检验解释；若明显不同，仅准备完整FOV匹配采样的常规控制，仍需同预算训练与患者端点。IN内容统计、局部上下文及池化相位等混杂仍不能由几何结果排除。普通sampling/overlap/加权融合已有原始先例，不能声称新方法。

CPU1/interop1/below-normal、wall120秒，无CUDA；结果加gzip日志总<=300kB，新阶段总<=1.2MB，磁盘8GB及原live输出预留不减。源文件只读，attempt01仅新建；失败保留实况，不降低门槛。
