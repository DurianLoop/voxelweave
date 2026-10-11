# v3：保留完整batch与loss的activation checkpointing诊断

v2实际2262bb exit1，已初始化GPU并读取1开发GT、1输入和1parent；第一个完整batch forward在本进程10% allocator上限内OOM（2.39GiB allowed），没有完成forward/backward或optimizer更新。这是本配置费用负结果，不是显卡整体没有空闲显存；失败原样保存。

新v3对每个encoder/decoder ConvBlock用torch non-reentrant activation checkpointing，up/head/order、完整batch2、3深监督loss、FP32和参数命名保持；backward重算费用全部记录。独立先在固定非医学2×1×16×24×32 synthetic上比较原TaskUNet与checkpointed实现所有输出、总loss与所有参数gradient，要求逐位相同；不初始化CUDA、不加载医学数据/模型。实际GPU仍12完整million-voxel patch，不减少batch或crop，不提高显存上限。

v3独立attempt03，原v1/v2所有SHA保持。新CPU资格及adapter都绑定。v3成功仅说明checkpointed graph在此病例有限梯度和费用可行；它不认证原未checkpointed trainer的内存，不包括AdamW optimizer状态，不完成2992训练/完整推理资格，不等同独立医学增益。protocol其余18百秒/1MB/CPU1/8GB reserves和科学门槛照旧。
