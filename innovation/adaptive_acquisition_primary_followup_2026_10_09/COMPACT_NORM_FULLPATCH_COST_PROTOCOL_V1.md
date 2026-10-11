# 新compact norm与已核验CPU保存的原patch成本

前置compact norm数学v2、CPU/GPU小图以及audited offload small两步通过。原shape(2,1,64,128,128)、seed991/GIN801-803/人工椭球target、初始54FP32参数、FP64graph、同loss及AdamW，顺序三view完整forward/loss/backward/最多1optimizer update。

全forward/loss/backward应用已单独核验的CPU保存hooks；记录pack/unpack与bitwise内容/SHA/shape/dtype/device、CPU逻辑peak、仅本进程GPUpeak/free。出错也保存实际journal和phase/forward开始完成数、更新数。独立CPU全patch模型尚未运行，成功只说明人工图成本可行。

严格deterministic/TF32off、GPUaggregate8192MiB、allocator min(.1,2.4GB/total)、peak2.5GB/runtimefree4GB，CPU1/interop1/below-normal、8GB RAM/diskreserve、wall360s及原stagecap不变。不能通过缩小patch/通道或提高显存budget冒充解决原配置；不读取MRI/GT/parent、不枚举修改PID、不动原训练。
