# 人工 GPU 与独立 CPU 的两步检查

前置：high_precision_model_cpu_attempt01 真正完成两步且原数值/二值门槛全部通过。使用同初始权重与原 16³ 三人工 view/target，新 high_precision 模块图在 GPU 对独立 functional 图在 CPU，两步 AdamW，各两次更新。

比较 loss、三个 head/三个 view 的概率及 threshold=.5、54 参数梯度和更新、162 optimizer state 字段。数值 3e-6、binary0，不调 eps/lr，不加载 MRI/GT/parent，未通过立即停止并保留失败。

只查询 GPU aggregate，不枚举或修改 PID，不改变用户原终端进程。GPU 启动 free>=8192 MiB；本进程 allocator<=min(10%,2.4GB/total)，peak_reserved<=2.5GB，runtime free>=4GB；FP32 参数和 FP64 运算，TF32 off，deterministic，CPU1/interop1/below-normal，RAM/disk decimal8GB reserve。wall360s，无权重落盘。

这不是原 FP32 模型、正式六臂、真实全分辨率或 19series 的资格。新的成本不能继承原 FP32 预测；只推进人工数值关系。
