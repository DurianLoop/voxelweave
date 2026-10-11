# 完整推断 context 的骨干接续拟合：新阶段协议

这是既有单开发系列拟合失败后的开发诊断，不是新的 SR 方法，也不是 19 系列训练或独立患者确认。旧文件、失败、gate、分配均保留；本阶段只写入 innovation。

## 先进行 CPU 资源资格

仅使用 VS-MC-RC-001 / 1.3.6.1.4.1.14519.5.2.1.10875952303942319530925289292568369177，读取已经认证的 native input、hard label 和全 tile 主 head 最后 checkpoint。比较 1 和 4 个 PyTorch intra-op 线程；interop 仍 1，自身进程 below-normal，不枚举或修改其他 PID。每种线程数从完全相同权重与 AdamW 新优化器开始，2 次 warmup + 4 次计时更新，固定两个推断 tiles，float32，无 CUDA。此为 12 次资源测试参数更新，丢弃结果，不计正式模型的训练累计。

先比较无更新预测最大概率差 <= 3e-6，再比较 4 线程是否至少快 20%。不能通过后使用 4 线程；失败保留并按 1 线程估时。CPU 总资格墙钟 <= 300 秒；RAM/磁盘各保留 8 GB，资格新输出 <= 1 MB。采样与数据加载在 RAM，没有新患者缓存。

## 接续骨干拟合

资格后在新补充文件冻结具体线程数及更新数，方可运行两臂。预定从各自最后全 tile head checkpoint 接续所有骨干和三个 head。native_reference/raw_pchip 两臂相同完整 16 tile plan、batch2、无增广、相同确定性 tile 顺序、相同更新预算和 AdamW lr=0.001，weight_decay=0.0001；保持原三尺度 BCE+Dice、float32、threshold=.5、最后 checkpoint。每 8 次更新覆盖全部 16 推断 tiles，每轮按独立固定 seed 的 permutation；不删空 tile，不挑有利病例，不依据效果改 LR 或选 checkpoint。与旧实验相比，这同时改变了优化的参数集合、输入 context 和采样域；只能称接续拟合诊断。

预定最多每臂 1024 次更新；依据资源计时缩小尚未执行的预算时，必须在训练前写新补充文件，不以效果选预算。两臂总资源墙钟 <= 5400 秒（含评估）；超过预算保存失败。两个最终 checkpoint 全部冻结后，评分原训练 crop 和完整 FOV 的 full/anchors/missing/tail，保留 empty 和 undefined。原 gate 保持：foreground crop Dice>=.9、full Dice>=.9、recall>=.9、absRVE<=.25、TP>0。训练与独立推断实现都核验。预测的网格往返数值问题单独保留。

新输出 <= 120 MB；不打开四验证或八确认患者。单病例通过也不构成 SR 损害或恢复收益的证据。后续仍须完整 11 开发患者/19 系列充分适配、原四验证能力 gate、公平部署信息矩阵和真正独立确认。

GPU 使用已授权，但仍遵守原 fresh nvidia-smi totals >=8,000,000,000 bytes 的启动门槛、4 GB runtime 余量及 2.5 GB peak。没有资源时只记录 totals，不初始化 CUDA、不占用显存等待。
