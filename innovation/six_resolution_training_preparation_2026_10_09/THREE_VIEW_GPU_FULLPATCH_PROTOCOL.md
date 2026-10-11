# 三视图原尺寸GPU图/显存探测，人工目标，未作为医学资格

原模型CheckpointedTaskUNet3D、原全部深监督head/loss、FP32，原patch64×128×128，两sample三份固定GIN视图；人工input/target、本进程cold init，不读医学或parent模型。比较packed6一次forward与sequential2三次forward，各同一初始state、supervise第一视图+attached reverse-KL element mean×0.1；各一次完整backward/AdamW。数学/输入/参数共同绑定；GPU启用TF32off/deterministic。

分开记录prepared GIN CPU费用、transfer、实际forward/loss/backward/AdamW、gradient/parameter/moment capture，峰reserved/free。每branch结束仅释放本进程模型/graph并empty_cache本进程allocator。若packed因本进程2.4GB cap OOM，保存实际错误/峰值，再在独立函数scope跑sequential；不提高cap，不影响其他作业。job completed只是探测完成；两branch都成功后，概率/loss/全gradient/参数/moments分别按3e-6计算strict comparison gate，否则gate=false。

GPU启动aggregate free8192MiB、本进程allocator<=min(10%,2.4GB/total)/peak2.5GB/runtimefree4GB；CPU1/interop1/below-normal、RAM/disk8GB，preparation7MB/FOV20MB/other22.8MB完整余量，wall360秒。当前其他GPU研究进程同样受各自cap，不枚举或控制任何PID；只查询aggregateGPU。不操作用户原训练。8未见确认/lockedIXI关闭。

本轮人工原尺寸shape可以检验图/内存实现准备，不能替代真实19series/schedule/母GT/预处理/全费用或三视图医学训练，clinical_lambda_chosen=false。所有成功/失败留receipt；不保存人工checkpoint，不缩小科学family。作者仓库不执行。
