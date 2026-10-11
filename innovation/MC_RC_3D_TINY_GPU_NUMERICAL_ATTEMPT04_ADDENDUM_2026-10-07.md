# attempt04：同shape清理仅供前向核对的缓存

attempt03实际exit1，1次合成float32更新后peak_reserved=192,937,984 bytes>原160,000,000门槛；同时nvidia-smi free691,011,584、CUDA接口free23,164,092,416。不同接口的差异已在同一次guard分别保存，不把CUDA接口数字当物理共享可用容量。原完整GPU资格未运行，患者更新0。

新attempt04保持attempt03的16³合成shape及全部160MB/500MB/1.3GB门槛；在数值比较结束后，释放仅供核对的GPU前向输出并empty_cache自身空闲allocator缓存，再做更新。此改变只减少自身缓存占用，不改数据、权重、SGD、模型或精度规则。先保存前向误差数值，失败也保留；若仍不满足，不再扩大本轮门槛。四次attempt源码/结果全部保留。
