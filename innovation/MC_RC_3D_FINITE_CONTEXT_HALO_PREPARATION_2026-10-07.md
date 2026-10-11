# 当前3D骨干的有限依赖halo推算（无MRI准备）

这是下一阶段准备，不改变正在运行的低LR训练。当前14个InstanceNorm仍用整tile空间统计，因而下述有限依赖推算**不适用于当前实际IN网络的严格整图等价**。仅在这14处改为固定统计/逐位置算子/已知有限局部统计且保持卷积窗口依赖不增加时成立；没有训练替代网络、没有MRI收益结论。

按实际网络：4级，每级2个padding1的3×3×3 conv；3个kernel2/stride2 max-pool；3个kernel2/stride2/padding0 transpose conv；每个decoder2个3×3×3 conv，skip concat；head1×1×1。忽略IN的非局部依赖时，潜在空间输入依赖可在每条轴上独立枚举。不能只用近似RF标量或把单层3³统计核当整网halo。

事前两种独立核验：逆向整数区间递推（conv扩张、transpose向下取整、pool展开），以及正向布尔依赖矩阵（实际每层邻域union与skip union）。256长度的全部interior位置按模8相位核对集合、左右半径与周期；128tile、offset64对照同全轴位置；offset65作为非对齐对照；64tile对照是否有完全不触及外部依赖的interior。报告原64×128×128 patch的core尺寸，不改变实际训练patch。

只加载网络结构/源码，不读MRI或GT，不前向任务像素、不更新参数；CPU1线程、自身below-normal、CUDA未初始化，输出<1MB、墙钟<=120秒、RAM/磁盘各留8GB。结构潜在依赖不等于某一固定输入下所有位置梯度都非零；也不证明当前MRI性能受该依赖影响。
