# 标准增强同容量配对续训 pilot

本实验诊断泛化失败，不是收益头、缺层动作或确认试验。只使用现有 11 名开发患者/19 series，禁止读取 8 名未见确认患者、locked IXI。4 名已见验证患者本阶段也不加载。

四个分支：native_reference/basic、native_reference/strong、raw_pchip/basic、raw_pchip/strong。每种输入的两个分支从该输入已冻结的 last19998 权重开始；输入间权重不同，不能声称四臂共享相同起始 state。两条原训练共同随机初始化的祖先来源保留。各分支重置相同 AdamW（lr=1e-4，weight_decay=1e-4），99 更新。相同父 schedule 前 99 个 patient-balanced draws；crop/flip/basic intensity 使用 batch_rng(19998+step)。同一输入两分支共享标签与几何；native/raw 对应 step 使用同参数/噪声种子。唯一变化是在 basic 输入上施加标准强度增强，非论文方法复现，非新意。

strong：每样本 gamma p=.3，指数均匀 [.7,1.5]，以该训练输入 patch 自身 min/max 归一映射后恢复原 mean/std；平滑乘性 bias p=.3，三个轴线性 log-field 系数各 [-.3,.3]；Gaussian noise p=.3，标准差 [0,.08]。顺序 gamma→bias→noise。噪声不声称真实 MRI Rician 模型。无额外通道、空间插值或标签修改。参数在任何新医学评分之前冻结，无按困难病例调参。

先进行 full-size synthetic 变换核验，包含 identity、重复确定性、配对参数、标签不变与独立数值公式。核验不作网络 forward。启动前 source SHA 和起始 state 校验，不改已执行源码。

GPU 用户授权有效；仅 totals query，不枚举其他 PID。至少 8192 MiB free 才尝试 GPU，CUDA fraction .1、FP32、无 TF32/AMP、reserved≤2.5GB、运行 free≥4GB。不够时用 CPU4/interop1/below-normal，沿用磁盘/RAM各十进制 8GB 储备；V4 session70619 真正结束之后才能启动，避免并行占用 CPU。当前 pilot wall≤3600 秒，全目录保存≤40MB；保存四个最终 state 与逐步 journal，不保存 optimizer，不支持失败后默默续跑。

四臂全部完成才另立完整 FOV 评价入口。禁止按中间 loss/checkpoint 挑最好模型；记录全部最终结果。短续训不能证明充分适配、augmentation普遍有效、SR收益或可发表 claim。完整后续训练预算须根据 pilot 实际费用明确冻结，旧六门槛不能降低。最终评价的严格概率与坐标门槛不沿用旧 float32 缺陷；需使用已核验 V4 映射。
