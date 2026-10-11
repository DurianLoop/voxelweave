# 全38开发FOV GPU/CPU功能实现与磁盘原子捕获资格

未来入口；仅在19series两步coverage actualexit0且独立终态audit后运行，不与本会话其他GPU工作同时启动。完整35904仍可独立CPU运行，本资格不代替其terminal。19开发series×native_reference/raw_pchip两parent=38完整FOV，11开发患者全部保留。使用原parent19998 weights，不训练、不读GT、不评分医学效果。native_reference只能力诊断，非部署输入；raw_pchip来自合法observed原流程。

生产CheckpointedTaskUNet3D GPU FP32、TF32off/deterministic，原V4完整滑窗/权重融合/native float64坐标映射。独立CPUfunctional_fov逐volume重算神经网络、独立tile/weight/native插值；完整概率最大绝对误差<=3e-6，固定threshold.5二值0差，独立float64 native坐标概率差<=3e-12及二值0差。所有volume都保存hash、最大误差、分歧数和覆盖/费用metadata，不能以均值或crop代全FOV。

同一个GPU parent state转CPU，torch.save用新临时文件xb写入、flush/fsync、原子rename到新终态.pt，weights_only重载，完整state hash逐位同。两输入各一个文件；不删除历史，不覆盖已有路径；只认证本次文件系统操作和重载，不证明断电恢复或optimizer resume。保存新的资格用parent复制文件不当新trained checkpoint。

GPU起始free8192MiB/进程cap10%/peak2.5GB/runtime free4GB，CPU1/interop1/below-normal、RAM/disk reserve各8GB。stage20MB（含两个约5.6MB终态权重及一个atomic临时峰值、metadata/audit），其他既有stage allowance22.8MB保留（原20.8MB加已执行checkpoint-storage stage2MB），wall10800秒。不减少既有完整family budget；新stage另计，不把以前1MB cost allowance改成足够。

实际GPU完整forward与CPUfunctional单独计时；MRI加载、全FOV融合/映射、源/概率/二值hash、比较、atomic保存/reload计总费用。terminal后独立枚举38identity/全部numgate及源SHA。资格全通过也不等于强泛化、正式六臂训练或发表claim。4已见验证像素、8未见确认12series、lockedIXI继续关闭。
