# 下一阶段：同输入逐算子设备误差，尚未执行

保留原失败case2/native_reference、19998 parent、输入SHA、完整192tile/96batch、49叶字段顺序。CPU独立functional在每一层保留该层输入与输出；对Conv3d、ConvTranspose3d、InstanceNorm、LeakyReLU及sigmoid，各用**同一个CPU参考输入**执行原GPU算子，再比较CPU原输出。不从GT选tile，不通过筛选输入或成功层缩小分母。

这样得到相同输入下的本地数值差异，可与已结束的真实GPU流水线传播误差对照。卷积/转置卷积仍原权重、padding、stride；IN仍原eps/affine/native实现，F32/TF32off/deterministic。GPU参照必须绑定原model算子形状/配置，不能用数学不同的简化卷积代替。记录每layer/max/mean/范围/最差位置，不把local error相加预测完整FOV，不用这一诊断判断临床效果。

每device参考与same-input operator各重复一次核determinism；全部96×49身份完整保留。CPU原概率重建必须重现原FOV SHA，原完整GPU概率SHA已有此次全tile成功诊断记录；如果重跑真实GPU流水线，则也记录完整SHA和全部费用。审核需明确哪些字段只是metadata复核、哪些确有独立像素重算。

启动前另冻执行代码和具体上限：共享FOV20MB/other22.8MB不减，journal<=3MB、wall3600s；CPU1/interop1/below-normal、RAM/disk8GB；GPU起始free8192MiB、allocator<=min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB。逐算子转移不能同时将全部CPU中间张量常驻GPU。保持参数SHA、不训练、GT0、不触及未见确认/lockedIXI或原训练/其他PID。

本文件只准备后续诊断，不给尚未执行的输入/参数转移、费用或结果补成功标志。全38概率资格仍false；无发布claim。
