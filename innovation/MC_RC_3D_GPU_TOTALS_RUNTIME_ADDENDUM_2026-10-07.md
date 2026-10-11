# 完整GPU拟合的共享显存观测修复（尚未执行）

小型GPU预检有3次合成float32更新（attempt02/03/04各1次），均因资源守卫未完整通过；BF16未执行，患者GPU训练0。attempt04小shape三个head的CPU/GPU概率最大误差8.9407e-7、1.0133e-6、1.7583e-6，阈值预测差异全0。这个局部数值事实不能替代完整batch显存/速度或512拟合资格。

attempt03/04均记录reserved峰值192,937,984 bytes，超过其160MB门槛；清理自身空闲前向缓存没有降低这一峰值。保留全部失败，不继续扩大本轮小任务门槛。

同次guard中nvidia-smi free691,011,584、CUDA mem_get_info free约23.1GB，二者不一致。原因未通过驱动/进程审计查明（禁止枚举用户进程）；因此新完整GPU入口在原4GB运行门槛下，要求**两个接口各自的free均>=4GB**，记录两个读数和reserved峰值，资源断言前也保存最后读数。不以CUDA接口单独决定共享GPU足够空闲。

新入口`experiments/run_mc_rc_3d_gpu_fit_pilot_totals_v2_2026_10_07.py --attempt 02`保留原8GB totals启动/4GB运行、2.5GB peak、10%allocator、3600秒投影、250MB保存、float32/TF32关闭、每臂512步、初始权重/数据/统计/监督/最后checkpoint/阈值和拟合gate。输入/科学配方完全沿原协议；只增加资源观测和日志。输出独立`mc_rc_3d_gpu_fit_pilot_totals_v2_2026_10_07_attempt02`，原attempt01和CPU实验都不变。

此文件是必要实现准备，不是已运行的GPU资格。新入口只在新totals>=8GB后启动，目前约1.4GB时不再执行已知会延期的完整入口。
