# 原人工整网协议验证新compact norm分支

前置compact_double_norm_cpu_attempt02所有8case输出/VJP、12个60位Decimal最小步长有限差分通过，失败v1保留。新model仅替换旧high_precision_task_model_v2的14个norm；保持54FP32参数/同初始state、FP64graph、disjoint deterministic pool、3view人工16³input/target与原AdamW/loss。

先CPU两步，对独立functionalCPU reference（显式方差、nativeCPU pooling），每步54param/162state、所有概率、binary，原3e-6/binary0。通过后GPU两步对同独立CPUreference；GPUaggregate8192MiB/allocator min(.1,2.4GB/total)/peak2.5GB/free4GB、strictdeterministic/TF32off，CPU1/interop1/below-normal、RAM/disk8GB、wall360s及原cap不变。

模型一阶VJP限制明确，原checkpoint/offload关系仍需分层验证；人工小图不认证原fullpatch、19series或医学claim。无MRI/GT/parent数组读取、无权重落盘、不动原终端进程。
