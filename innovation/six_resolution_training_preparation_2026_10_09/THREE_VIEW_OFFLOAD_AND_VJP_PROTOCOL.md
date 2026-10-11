# 原尺寸三视图attached目标：CPU保存激活与两pass VJP的全图核验

依据上次真实packed6/sequential2 OOM，固定同一人工64×128×128 patch、同GIN三视图/人工target/初始state SHA、原CheckpointedTaskUNet3D与全部深监督head。两新实现另版本，不编辑旧源/失败，不改变lambda0.1（仅人工验证）、batch2/三视图/母loss/FP32/TF32off/optimizer/cap。

reference为sequential3 forward，torch.autograd.graph.save_on_cpu(pin_memory=False)保存autograd必要张量到CPU，随后一次完整supervised第一view+attached mean-target reverse-KL backward。保存激活不改变数学loss。实际RAM与转移费用全计，不把CPU offload当免费。

candidate为two-pass attached VJP：先以同权重/no_grad取得完整三视图logits；用独立GPU leaf logits计算**attached** mean-target KL及其对三视图logits的完整梯度（包含均值依赖，不是detach-target）。将完整上游gradient移到CPU。按view2→1→0逐view重算原模型，先核完整final logits与第一pass逐位同；各自即刻backward注入该view上游gradient，view0同时原三head监督，累积同θ的grad，最后一次AdamW。权重不能在view间更新，不重新抽GIN随机数。两pass增加3次原完整forward与CPU/GPU传输，实际费用单列。

在完整原尺寸对比全部三head/三view概率、真实loss、全部对应参数grad、一次AdamW后的参数及step/exp_avg/exp_avg_sq，门槛3e-6；同input/target/state SHA不变。reference一次完整attached图作为独立图结构对照，VJP图本身不detach均值语义。理论链式法则不替代实际全参数/optimizer结果。

两模式各保存原始成功/失败，job exit0仅在两者均完整且所有gate/memory通过；GT/MRI/parent0，无医学评分，complete19series_GPU_three_view_qualified=false。原六医学gate、CPU/GPU FOV资格和完整family预算不受此人工准备影响。

GPU启动free8192MiB、allocator<=min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB，CPU1/interop1/below-normal、RAM/disk8GB；preparation7MB/FOV20MB/other22.8MB完整余量；wall360秒。不改其他PID/原训练，不开启确认/lockedIXI，不安装或保存人工checkpoint。
