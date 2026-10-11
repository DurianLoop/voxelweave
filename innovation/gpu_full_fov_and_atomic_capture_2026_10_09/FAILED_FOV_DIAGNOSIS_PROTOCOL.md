# 第三开发series的FP32完整视野数值诊断

原38FOV attempt01实际exit1：前2通过，第3为native_reference、最大概率差5.334615707397461e-6、二值零差。失败结果、原源码和一份已写atomic parent权重保留，不当38完整资格；不降低3e-6/3e-12/二值零差门槛。

只选原失败identity，source/model/hash沿原19998 native parent。重新计算相同独立CPU FP32完整FOV一次，对照GPU原contiguous与channels_last_3d内存布局。模型参数值、算子、FP32/TF32off/deterministic、滑窗/权重/native映射及threshold均不变；布局不是新方法创新。没有GT、医学分数、新训练、验证或确认输入。

新诊断不保存MRI/概率数组或额外模型文件，metadata纳入原20MB stage，不减少22.8MB其他allowance；CPU1/interop1/below-normal、RAM/disk reserve8GB、wall1800秒。起始GPUfree8192MiB，allocator上限取min(10%,2.4GB/total)，runtimefree4GB且peak<=2.5GB；取更紧allocator仅保护原最大显存合同，不增加费用或放宽任何科学gate。每个模型forward前后核resources。只操作本进程。

单失败病例诊断即使通过也不能认证完整38。若新布局有改善，另生成新38 runner，重复全部identity/原概率门槛/atomic资格并独立审核；之前失败不删除。布局若无改善，记录实测负结果，进一步定位InstanceNorm/卷积各层误差，不将二值一致当概率资格通过。
