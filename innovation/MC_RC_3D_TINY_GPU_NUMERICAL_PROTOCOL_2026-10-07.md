# 独立小型3D GPU数值预检

用户GPU授权已存在。本预检只用合成batch2×1×16×32×32，0患者/0MRI/0标签来源，和原64×128×128/512更新GPU拟合完全分开，不放宽或替代其8GB启动、4GB运行及3600秒原合同。

新小任务启动要求GPU totals至少1,300,000,000字节空闲；CUDA初始化和每个操作后global free至少500,000,000字节、自身reserved峰值<=160,000,000字节。allocator最多GPU总量1%；只查GPU totals、不枚举/控制用户进程。不等待或抢占资源，任何失败记录并结束自身进程。总体<=120秒，新增证据<=1MB；CPU单线程、自身below-normal、RAM/磁盘原8GB保留。

与当前3D候选同架构，seed20261007，同合成数据/初始weights；CPU float32三head与GPU float32前向比较最大概率绝对误差，门槛3e-4；TF32关闭、cudnn benchmark关闭、deterministic开启。BF16-autocast误差和0.5二值差异仅作描述，不声称与float32等效。分别执行float32/BF16一个SGD1e-3更新，所有参数梯度有限，encoder/decoder/up/head分支各有非零梯度，保留峰值/时间/损失，0checkpoint落盘。

两次合成更新不是实际病灶训练，不是原GPUpilot或充分任务能力。不据小shape推算完整batch显存/速度，不与两臂CPU固定拟合相混。
