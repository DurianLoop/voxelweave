# attempt03：减少合成shape并保留资源断言前的数值

attempt02实际exit1，float32前向误差门槛已通过且一个SGD更新已执行，随后资源断言失败；没有完整arm记录，也未保存触发时free/peak数值。因此不假称知道精确失败峰值，不当成功资格。该attempt没有病灶更新、MRI读取或checkpoint保存。

重要观察：初始化前nvidia-smi totals free=1,461,714,944 bytes，CUDA初始化后mem_get_info free=23,768,072,192 bytes；不是严格同一时点，不能据此证明具体驱动机制，但CUDA接口的数字不足以单独认证共享物理显存。原完整GPUpilot尚无患者更新；后续完整GPU运行需要新版本在原4GB运行门槛下同时查询totals，不改变原门槛。

attempt03把合成shape减为batch2×1×16×16×16，其余初始化seed/1步SGD两精度和160MB reserved上限保持。更新前后均同时记录totals和CUDA内存数字，资源观测先保存再断言；totals及CUDA各自free均须>=500MB。较小shape仅认证该shape，不证明原完整batch峰值/速度。只有通过原1.3GB小任务启动门槛才初始化CUDA；失败保留并结束，不继续调整本次门槛。
