# 支持 mask 不能直接成为任务输出安全证书：合成资格

当前 TaskUNet3D 的 ConvBlock 使用 Conv3d→InstanceNorm3d，未设置 track_running_stats=True。InstanceNorm在推理时也依赖当前样本整张feature的均值/方差。输入某位置支持充分，并不保证该位置任务输出只依赖有支持的输入；卷积还会跨mask边界传播信息。

只在8³、1通道、float64合成数组中验证此机制：中心4³输入保持相同，外部改成0；3³均值卷积后，中心2³的卷积结果必须相同，但InstanceNorm结果可能变化。生产Torch卷积/InstanceNorm与独立SciPy correlate+NumPy population variance核对，数值误差≤3e-6。此独立核验检验一个可证伪的非局部影响机制，不加载模型checkpoint、不跑患者forward、不改训练，不作为医学损害或论文创新结论。

CPU1/低优先级、wall30秒、stage5MB、8GB磁盘/RAM储备，零其他PID干预。后续mask-loss仍可作普通训练control，但不能称其隔离了全部padding影响；若需要这种主张，须显式处理卷积感受野和归一化依赖并实测完整任务模型。
