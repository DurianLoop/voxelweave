# 引文跟进：SBNet事前选择

SACT页5已经提出tile共享门控、halo重叠和kernel-call开销；DynConv页2–3直接引用SBNet作为实际分块稀疏推断前例。为核对比逐pixel门控更接近当前MRI窗口执行的先例，追加唯一第三篇：Ren、Pokrovsky、Yang、Urtasun，SBNet: Sparse Blocks Network for Fast Inference，CVPR2018（目标CVF正式会议稿）。这是前两篇阅读触发的后续选择，不伪称原两篇固定方案中的第三篇。

取得后核题名、作者、会议信息；主要关注block gather/scatter、halo、mask生成费用、密集baseline backend及3D对象检测与3D MRI卷积的区别。仅公开GET，单响应32MB/25秒，独立输出目录。沿用已有公开获取函数，其源码hash单独绑定，不修改已执行函数或既有取得结果。若404保留，不把路径猜测当论文身份确认。
