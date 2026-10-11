# 原尺寸三视图完整图 CPU 激活卸载透明性核验

冻结后执行新代码 qualify_three_view_offload_transparency_v1.py，不修改已执行的 GPU 探测或 VJP v1。只使用上轮相同 cold-init、固定三个 GIN 人工 view、人工椭球 target，shape (2,1,64,128,128)。不加载 MRI、真实 GT、parent、确认集或 locked IXI；不影响原训练进程。

比较内置 save_on_cpu(pin_memory=False) 与独立显式 saved_tensors_hooks：两分支各两步 AdamW，顺序三个 view 的完整 attached mean-target reverse KL 加第一 view 原深监督 loss，一次 backward 和一次 optimizer.step。保留同一 FP32 model/参数/损失/KL reduction，不 detach consensus、不改变累积顺序。lambda=0.1 仅人工图参数。每步全概率、loss、全梯度、参数和全部 AdamW state 比较，门槛 3e-6，step 逐位相同。记录初始/终止权重 SHA、全部优化器字段，不只检查最终 head。

显式 hook 将每个保存张量复制到 CPU，记录 shape/dtype/stride/原 device/字节数/内容 SHA。每次 unpack 将保存值复制回原 device，再复制回 CPU 独立核对 shape/dtype、torch.equal 和内容 SHA；并核对 CPU 保存值没有改变。记录所有 pack/unpack、重复恢复次数、保存后未恢复项（例如未参与 loss 的 view 深监督分支），不要求不参与反向的项必有 unpack。这证明保存值恢复的内容透明性；不声称底层总线硬件证明。每步 view/target SHA 不变。保存 journal 元数据，不持久保存大张量。

CPU1/interop1/below-normal，RAM/磁盘各保留十进制 8GB。GPU 只查询总体空闲/利用率，不枚举进程；启动 free≥8192MiB，allocator≤min(10%,2.4GB/total)，peak≤2.5GB，runtime free≥4GB；FP32、TF32off、deterministic。原 prep 7MB/FOV 20MB/other 22.8MB 的储存余量完整保留，wall≤360s。允许回收本作业对象/本 allocator cache。记全部合成输入准备、三个 forward、checkpoint block recomputation、loss/backward、传输/hash、梯度/optimizer/state capture及总 elapsed；诊断 hash 费用不得隐去。

人工成功不等于医学 GIN 资格、19series 医学训练或发表 claim。必须保留 packed/plain sequential OOM 和 two-pass VJP 参数门槛失败。后续医学资格需另冻完整 19series、母 GT、schedule、两步优化器、显存、独立 replay 和所有费用的具体协议；部署 full38 数值资格也仍独立 pending。
