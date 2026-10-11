# 深监督标签预检：限定19开发系列

目的：在完整任务适配前，检查很小的真实病灶经过physical grid与deep-supervision resize后是否还有前景。仅标签/既有metadata，读取原11开发/19series；不读取MR source像素，不打开验证/确认效果、不产生模型预测、不训练神经网络。当前两臂CPU512拟合协议/代码/输入都冻结，本诊断不改变它们。

每series使用SEED20261007及该series原v2物理二值target，32次batch primitive；与生产的forced-foreground-first/uniform-voxel-center-second、clamp边界、三轴flip、强度随机数消耗一致。每次记录centers/starts/flips/scale/shift和两个patch的真前景数。三输出GT按64×128×128、32×64×64、16×32×32，用当前生产nearest-exact取得；独立oracle分别原patch、1::2、2::4，与每个GT逐值比较。标签权重仍4/7、2/7、1/7。

记录任何forced-FG patch的半/四分之一GT归零及whole batch归零，保留所有series、samples、counts、前景比例及随机stream hash。32draw不是患者独立样本，不能把608 draws当608患者或据其显著性声称泛化。

统计是监督路径诊断，不声称zero coarse GT自动造成漏检；主head仍可能有全部病灶，Dice对empty GT的平滑项/BCE背景监督仍存在。若出现问题，后续新配置才评估pooling/soft targets/scale weights等已知对照，当前运行不改。所有额外训练尝试有自己的协议/预算，不将修复当新贡献。

沿新有限存储资源合同：单线程，自身below-normal，磁盘>=8GB/RAM>=8GB，新保存<=20MB，无CUDA。最多在内存中保留一个series target和一个batch；不落盘复制患者体积。
