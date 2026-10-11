# 配对空间增强适配，保留完整医学门槛

前一goal轮属于progress：四篇原文核读和396步/36FOV真实结果改变了下一步决策；不是重复状态。其短强度增强仍未通过医学门槛，不证明充分适配或创新。

本轮拟实际验证空间增强与更长适配。四分支：native_reference/intensity、native_reference/spatial、raw_pchip/intensity、raw_pchip/spatial；每分支2992更新（11患者×272），总11968。每输入的两个分支从该输入原冻结last19998权重开始，AdamW均重置，lr/weight_decay均1e-4；输入间起始权重不同，不能称四分支共享state。使用原frozen_schedule前2992行，同crop/flip基本强度源batch_rng(19998+step)，同母GT、同patient/series曝光。不得与只99步的旧模型比较后归因空间增强；主要匹配控制是本实验同预算intensity分支，原parent与旧99step仅作描述。

两个分支均采用前轮固定gamma/bias/noise参数与独立seed。空间分支额外每sample以p=.3作物理3D rotation，三个欧拉角各[-15,15]度，isotropic scale[.85,1.15]；另设独立seed，不根据已见验证调参。图像trilinear，GTnearest，zero padding，align_corners=False。先空间后强度以保持噪声seed和分布相同。选中的forced foreground voxel在crop+flip后的坐标作为旋转/scale中心，普通随机crop使用patch几何中心；这是合法训练GT采样，不进入推断。所有坐标和预处理采样float64，模型输入转float32；不改变最终推断V4规则。物理轴/voxel轴/normalized轴变换分别明示并独立核对，不能在错误坐标上继续训练。

必须先通过完整patch synthetic图像/标签/物理坐标独立核验，以及所有19个开发series真实batch的配对母GT/crop/foreground保留检查；这些不初始化CUDA，不读9个验证影像/GT。训练只用11开发患者/19series，8未见确认患者/12series与lockedIXI关闭。

GPU授权有效；totals free>=8192MiB才尝试，FP32、无AMP/TF32、fraction .1、reserved<=2.5GB且运行free>=4GB。当前1394MiB故CPU4/interop1、below-normal。仅当前进程，不枚举/干预其他PID，不委派代理。磁盘/RAM各十进制8GB储备，整个新stage<=45MB，wall<=27000秒（7.5h）。启动前实测checkpoint payload与日志forecast，留临时原子写余量；不删历史或降低储备。

本阶段不保存optimizer以容纳公平四分支final state，不支持失败后默默续跑。逐步保存可无损重读gzip journal，最终四branch state全部完成并真正退出后冻结，不能按中间loss/checkpoint选择。不在训练期间评分验证患者。训练失败保留所有实际日志/退出/已完成分支，不宣布达到预算。

四分支全部真正完成后，另立固定最后state的全部9已见验证series完整FOV评价：两条独立实现、3e-6概率/3e-12坐标/零二值、无损reader、独立计数/患者先均值与原六门槛（fullDice>=.70，missingDice>=.65，recall>=.70，absRVE<=.50，四患者full/missing正Dice，无series零TP）。能力未达则继续补强基线，不进入收益头/动作claim。标准空间增强、额外训练、预训练、协议metadata本身不是新意；本轮不以小样本正结果宣布发表claim。
