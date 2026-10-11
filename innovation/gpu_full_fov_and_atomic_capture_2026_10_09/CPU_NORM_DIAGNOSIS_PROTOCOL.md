# 单失败FOV的归一化设备干预诊断

实际layout v2 exit0只是诊断完成：contiguous/channels_last_3d给出相同概率SHA、同5.3346e-6最大差，均未过原3e-6 gate，且后者更慢；不生成38资格。v1诊断CPU replay成功，但继承CPU输入模块把CUDA_VISIBLE_DEVICES改成-1，GPU可用性断言失败；v2在imports之后恢复0，失败保留。

下一单病例诊断只改变InstanceNorm3d的执行设备：所有卷积/反卷积/激活仍GPU FP32，InstanceNorm使用同权重值/同F.instance_norm/同eps在CPU FP32计算，然后返回GPU。CPU reference始终原独立functional_fov，不改。所有state值/hash、FP32/TF32off/deterministic、FOV/坐标/threshold及3e-6/3e-12/二值零差保留。不训练、不读GT、不评分患者效益；这只是定位CPU/GPU数值差，不能解释为新的MRI模型或纯GPU部署路径。

沿FAILED_FOV_DIAGNOSIS_PROTOCOL.md的20MB共享stage/22.8MB其他allowance、CPU1/interop1/below-normal、RAM/disk8GB、wall1800s、起始GPU8GiB/allocator<=10%且<=2.4GB/peak2.5GB/runtimefree4GB。记录完整混合推理实际时间，包含CPU规范化和全部传输，不以GPU kernel时间冒充费用。即使单病例通过，也须新完整38及实际终态/独立审核后才考虑部署资格。
