# GPU 六分支图与费用诊断（执行前冻结）

用途：在一个固定开发病例上检查两种输入×三种分辨率控制的真实 GPU forward/backward、有限梯度、母 GT 不变和实际费用。它不是2992步训练资格，不更新 optimizer、不保存权重，也不进行完整FOV医学评价或发表确认。

病例与crop从既有5984 geometry journal按step排序，选择最早两个patch都启用resolution primitive的step；选择只读开发schedule/geometry元数据，先写frozen_config，之后才读取该病例MRI/GT和19998 parent。6分支共12个64×128×128 patch，使用原sample_batch和seed、对应parent及三深监督loss。两输入共享母GT/geometry；每个新分辨率patch同时用独立separable oracle比较（图像逐位零差、支持二值零差、强度3e-6；原门槛不降低），再施加既有float64-stats强度增强。原padding逐位保持在强度增强之前检查。

GPU准入：设备0 aggregate free至少8192MiB，不查询其他PID；本进程allocator上限为GPU总显存10%，峰值reserved不得超过2.5GB，执行中free至少4GB。FP32、TF32关闭、deterministic cuDNN；CPU1线程/below-normal；RAM/disk至少十进制8GB，并留完整CPU资格及原stage allowance15.8MB和本stage余量1MB。wall1800秒、目录总保存不超过1MB。不操作原终端训练或任何其他进程，不安装依赖。

按分支记录source/cache/checkpoint/input/label SHA、primitive、valid/padding/fallback统计、loss、各模块非零有限梯度、load/transform/transfer/forward/loss/backward/verification/sync/完整墙钟和显存。前后完整state_hash相等并最终核源SHA。不得以这6个paired crop的loss推断任务增益，GPU费用单病例不外推普遍速度，不代完整六臂optimizer/capture/inference资格。19998 parent含全部11开发GT，严禁严格LOPO外折初始化；确认8患者12series和lockedIXI保持关闭。

实际整体exit0且独立终态审核后才称此项图诊断通过。失败保留attempt与绑定源码，另版本修复。full35904仍另行从头执行，不因本诊断通过自动宣布训练就绪。
