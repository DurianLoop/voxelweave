# 开发标签网格往返对照

全tile输出层诊断仍失败，因此在新结果打开前定义一个零训练控制：仅原11开发/19系列，将真实native hard GT按当前0.5mm网格nearest-exact变为physical hard GT，再按实际推断的trilinear/align_corners=False概率回映native，并在固定0.5阈值评分full/anchors/missing/tail。不读取MR、不开四验证或八确认，不产生部署方法。

逐例用独立NumPy pixel-center重采样和PyTorch核对最大概率误差<=3e-6，二值预测差异0；先记录两种数值与计数再断言。报告全部19series、全部患者、空/undefined和原Dice/recall/absRVE阈值，患者内先平均series再患者均值，不删除失败系列。

这是当前hard-label sampling和概率映射链的诊断参照，不是可学习连续概率的数学性能上界。即使hard-GT往返低于0.9，也不能证明任意模型不可能达到0.9；即使通过，也不能证明网格无信息损失、训练网络可拟合或SR好坏。

不调网格/阈值，不修改标签或既有checkpoint；单线程自身below-normal、RAM/磁盘各8GB、不初始化CUDA，<=180秒、新结果只JSON<=3MB。全部新增结果/源SHA独立留存。部署不会使用真实标签，本控制仅为已见开发数据的测量诊断。
