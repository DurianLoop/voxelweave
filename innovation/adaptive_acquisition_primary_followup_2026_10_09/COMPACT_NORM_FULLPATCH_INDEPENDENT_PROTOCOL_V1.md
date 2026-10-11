# 原尺寸三view两步GPU与独立CPU完整检查

前置compact_norm_fullpatch_cost_attempt01完整三路forward/loss/backward/一次人工更新真实通过；数学v2、原小图CPU/GPU、offload小图两步均通过。新检查必须保留原尺寸(2,1,64,128,128)，不是缩patch结论。

GPU采用compact norm model与已逐位核验的CPU保存hooks；独立CPU采用high_precision_cpu_reference_v1 functional图（FP64显式中心化方差、nativepool），三人工view同seed991/GIN801-803、同椭球target、初始seed20261009同54FP32parameters、原AdamW与loss。完整两步、每步全部loss/三head三view概率binary、54gradient/parameter、162optimizer字段，原3e-6/binary0gate。每步确认inputs/targetSHA不变，已完成prefix不算两步资格。

CPU1/interop1/below-normal、RAM/diskreserve十进制8GB，GPU启动8192MiB、allocator min(.1,2.4GB/total)、peak2.5GB/runtimefree4GB，TF32off与strictdeterministic。全流程wall10800s，按每分支与每view记录进度与真实计数；不启动医学数据/parent/确认患者，无训练权重落盘，不动用户原进程。成功仅认证本人工配置两步关系，19series/fullFOV/full35904仍是独立依赖。
