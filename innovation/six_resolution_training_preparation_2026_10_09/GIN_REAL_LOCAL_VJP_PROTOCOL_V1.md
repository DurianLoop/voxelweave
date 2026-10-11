# 首个真实病例的局部卷积 VJP 归因，v1

冻结 scope：复用 gin19_real_graph_attempt02 的 case0/native_reference/step0、原母 GT、三个序列化 GIN 参数及 cold-init seed20261009。只定位最差参数 decoders.2.layers.3.weight flat1658；不挑新患者，不打开 parent/确认/lockedIXI，不修改原 runner、原终端或其他 PID。

CPU 独立 functional 图只增加观测回调，GPU production 图只增加观测 hook。保留 non-reentrant checkpoint、原 CPU 独立 loss 和 GPU production loss；观测首次前向的该 Conv3d 输入/输出及完整图反向传入的 cotangent，重算时不重复登记。完整图每设备三次 forward、一次 backward、optimizer update0。先比较原 journal 最差坐标的梯度，任何不复现均保留失败。

局部隔离矩阵：固定该卷积权重，对 CPU/GPU 记录的输入各两种、上游 cotangent 各两种，在 CPU/GPU 两个 backend 上各做三视图局部 VJP，总24次局部 convolution backward。记录完整 weight-gradient 最大差、最差原坐标、逐视图值与求和。另用 float64 NumPy einsum 从真实输入和 cotangent 独立计算 flat1658 的交叉相关导数（四种输入/上游组合），不重新训练或修改 optimizer。输入来源、cotangent 来源、backend 是三个独立因素；本诊断区分局部 backward 算术与传入该层的差异，不能将下游 cotangent 差异直接定位为某一个 IN/激活算子，不能据此宣称临床伤害或发表 claim。

CPU1/interop1/below-normal，RAM/disk各十进制8GB。保持 prep7MB、FOV20MB、other22.8MB，加录用稿6MB完整cap；reserve 用 free 减各目录尚可增长字节，当前已占用字节不重复扣除。GPU启动free8192MiB，allocator min(10%,2.4GB/total)，peak2.5GB、runtimefree4GB；FP32/TF32off/deterministic。wall600秒、receipt150KB，只存 SHA/统计和坐标；中间大tensor只保留内存。既有3e-6/3e-12/二值0和六医学gate不变，本归因不是19series或full38资格。
