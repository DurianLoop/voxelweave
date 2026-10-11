# 减少反向重算同时驻留张量

原reference-lifetime fullpatch v2实际6bf525 exit1/no session：step0 GPU/CPU各1人工更新，全部54param/162state、概率binary比较通过，parameter3.725290298461914e-9；step1三路GPUforward完成，反向OOM256MiB，step1 CPU未跑。两步资格未通过；不能把step0成功当完整通过。

v3保持所有数学算子、参数/初始state、输入target、loss与AdamW，仅将每个6层卷积块的checkpoint分为两段(conv/norm/leakyrelu)，去除原外层整块checkpoint。保留独立compact norm解析VJP、disjointpool、消费后释放skip以及临时传输input。CPU保存hooks与逐位审计保留；参考图仍显式FP64 norm/nativeCPU pool，不拆段。

先16³三view完整两步对独立CPU，原54/162/allprob/binary3e-6/0门槛；通过后原64x128x128两步完整检查，wall10800，原GPUallocator2.4GB/peak2.5GB/free4GB/admission8192MiB、strictdeterministic/TF32off、CPU1/interop1/below-normal、RAM/disk8GB、stagecaps不变。失败保留，不改原源码。不读取医学/GT/parent，不动原进程。
