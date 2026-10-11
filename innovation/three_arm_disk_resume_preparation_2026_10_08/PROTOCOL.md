# 三臂磁盘恢复执行准备，2026-10-08

本阶段补三臂执行的磁盘持久恢复缺口。不是新算法，也不以人工数据资格代替 MRI 能力、真实资源或方法收益。原训练 session 99542 只观察，不修改。所有新增文件仅在本目录；此前已绑定的来源不修改。

执行前冻结本协议及资格源码。人工源复用已核验的两个 synthetic ObservedMRI；无真实 MRI、旧模型权重、验证或确认像素读取。三臂仍为 legacy_dense / direct / common_projected_dense；共同初始化 1,401,795 参数，float32，PATCH 64×128×128，batch 2，AdamW lr/wd=.0001。复用既有 arm_view、draw_training_batch、update、snapshot，不重复已通过的内存恢复或 FOV 测试。

两次独立 Python 进程：连续进程每臂执行三个共享 draw，保存第 1 步和第 3 步的不可覆盖磁盘 checkpoint、绑定 journal 前缀和元数据；恢复进程加载每臂第 1 步，在同一 draw 序列上执行第 2、3 步，另存终点。计划总计 15 次人工更新 / 15 次人工神经 forward；无 FOV forward。真实计数以 worker 结果与实际退出为准。第 1 步持久化后不重启用户训练，而是在新的资格进程里恢复。独立 verifier 只加载本阶段 9 个人工 checkpoint，对连续/恢复终点的完整 model、optimizer、CPU RNG、step 和配置逐项精确比较；不再神经 forward。

Checkpoint 绑定不可变 journal 前缀 SHA、行数、每行 arm/step/uid/patient、配置 SHA 和源码 SHA。恢复先在标准库入口核文件、哈希和计数，再 import 神经模块。日志可能先于 checkpoint 提交，故进程中断后的未绑定尾部不允许默默回退或自动接纳；正式运行若有此状态，必须先独立审计。本阶段用六类实际磁盘 fault fixture 验证提前拒绝：缺失行、多余行、截断行、checkpoint SHA 错、元数据步数错、arm 错；另外核正确元数据可接受。错误证据保留，不篡改正确 checkpoint 或前缀。

CPU 4 / interop 1 / BLAS 1，CUDA 不可见、不得初始化，自己的进程 below-normal，不枚举或控制其他 PID。整段资格限 600 秒（各 child 限 240 秒），本目录累计输出上限 200,000,000 bytes。RAM / 磁盘可用始终各至少 8,000,000,000 bytes；保存单个 checkpoint 前另预留 25,000,000 bytes。启动先核本目录预期最大 200 MB 写入后仍有 8 GB 磁盘。禁止删历史证据腾空间。源代码不写 pyc。

正式医学入口是准备与延期检查入口，不分配三臂正式长训练步数，不宣称充分适配已冻结或已训练。依赖顺序保持：原两臂真实 final exit 0 / 冻结 → 全 56 完整 FOV → 全六能力 gates → 独立 strict / 实际退出 → 三臂真实 19-series 资源 / 实际退出 → 基于资源另冻充分适配预算和正式入口 → 真实动作余量与完整费用 → 强静态/充分适配/费用控制 → 未见 8 患者确认。GPU 已授权；新的医学 GPU 作业仍需启动 8,000,000,000 bytes 空闲，不触碰别的训练。

本阶段只资格化可复用的三臂训练循环和磁盘提交/恢复原语。没有正式医学 stream、budget、长程 wall/storage 配置，所以不能称正式长训练入口完整资格化，更不能从本阶段确认可发表 claim。
