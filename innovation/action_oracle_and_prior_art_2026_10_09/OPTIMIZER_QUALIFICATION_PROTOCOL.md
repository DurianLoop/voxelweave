# 开发病例 GPU AdamW / 内存捕获资格

只在已使用的 VS-MC-RC-009、原 schedule step2 做两输入×三分辨率模式各一次更新。完整 batch 为 2×1×64×128×128，原母 GT、crop、resolution/intensity 合同保持。每臂重新加载各自 19998 parent，并重置 AdamW；不保存训练 checkpoint，不计算医学端点。

AdamW lr=1e-4、weight_decay=1e-4、betas=(.9,.999)、eps=1e-8，foreach=False/fused=False；FP32、TF32 off、deterministic、non-reentrant activation checkpointing。从实际 GPU 梯度用独立 NumPy float64 首步闭式式子核对全部参数、m/v 状态，绝对误差 gate 3e-6；step counter 必须为1。另把完整 state_dict 用 torch.save 写入 BytesIO、weights_only 重载，逐位 state hash 必须相同。此捕获只认证内存序列化，不认证磁盘原子保存、训练断点恢复或完整 FOV 推理。

GPU 起始 free>=8192MiB，本进程 allocator 10%，执行时 free>=4GB、peak reserved<=2.5GB；CPU1/interop1/below-normal，RAM/disk reserve 各8GB。本目录总 stage 2MB，其他既有 allowance 16.8MB保持，wall1800秒。只查询GPU汇总，不枚举或修改其他PID，不触碰原终端训练。对照完整35904仍独立运行；本短资格不代替它。

必须保存真实工具终态并做独立枚举审核。成功仅说明该病例的首步 AdamW / 内存捕获可行；仍不允许称六臂2992训练就绪、通用optimizer内存上界、患者泛化或可发表claim。确认患者与lockedIXI继续关闭。
