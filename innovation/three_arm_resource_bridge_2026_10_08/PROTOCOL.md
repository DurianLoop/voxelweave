# 三条同观测任务路径的资源执行桥接

本阶段实现此前因素矩阵中缺少的第三条路径执行：legacy dense、direct、common projected dense。现有两臂worker和资格、共同投影19series生产/独立v2、原训练session99542均不改。新的执行桥接不是新算法或MRI收益；没有充分任务能力/真实资源/正式预算时不训练医学任务模型。

三臂共享同一个observed源和统计、availability/valid/target对象、patient-first stream、一次物化的crop/foreground/random/flips/scale/shift。旧dense和新common dense使用`s*x+t*valid`；direct使用`s*numerator+t*availability`。各臂同canonical two-channel初始SHA、1,401,795参数、AdamW lr/wd=.0001、float32/PATCH64×128×128/batch2。新common路径用dense语义，不能落入旧worker的else=numerator。保留所有路径名字和选中数组SHA；任意unknown arm拒绝。

复用旧draw/apply/update/snapshot/FOV函数，不重写原标签几何、Gaussian blend、pixel-center返回映射或数值门槛。每臂资源stream更新后丢弃权重；checkpoint仅内存，第二步连续/恢复树精确比较。全FOV只对固定最大tile数代表两次，不评分病灶；资格不能替代完整19series实测。

新增synthetic资格走实际输入构造：两个固定synthetic ObservedMRI(33×35、native17、stride4)→旧physical_fields与共同投影shared_source/projected_pair_fields→三个输入。native pixel没有真实MRI来源，二值人工target独立定义。core65×129×133/padding至68×132×136；3draw/臂+恢复第二步额外1，共12资源更新，3臂×2pass×8tile/batch2=24FOVforward，共36神经forward。CPU4/interop1/BLAS1、below-normal、CUDA不可见；<=600s，阶段输出<=10MB，RAM/disk均8,000,000,000bytes储备。审计拒绝任何医学数据/磁盘权重，updated weights不落盘。

独立verifier不导入新worker，用另写NumPy crop/scale/support/flip重建每个新臂的batch与target SHA，核共有mask/label、容量初值、更新数及FOV原元数据/coverage/repeat；不重新跑网络或重演恢复，因此只独立核输出record，而不能冒称独立完整神经forward。旧独立FOV资格继续保留，无需重复已通过的全网络functional检查。

医学资源入口仍须在import神经/医学模块之前，运行旧readiness并核原两臂final exit/冻结、56FOV/六gates/独立strict。新合成结果、独立verifier及实际退出receipt均绑定后才可读开发19 observed+GT。真实loader一次读observed，同时构造三路，核旧19字段SHA/new共同投影19SHA/同GT；开发19/11角色不变，4已见验证/8确认像素都不读。六field总5,729,136,000bytes只是数组量，不是进程峰值。

真实资源每臂33draw+1恢复更新，共102；资源权重丢弃，仍未授权成正式训练。新资源入口沿旧CPU/GPU精度与telemetry合同：GPU先8GB空闲，自身allocator .1、reserved<=2.5GB/运行free>=4GB、禁TF32、deterministic，不能控制别的PID；每attempt<=1200s/5MB。返回后根据真实资源才另冻正式三臂预算；不变原终端训练。

若当前依赖未就绪，入口返回3、prerequisite_deferred、neural imports/MRI reads/CUDA/updates0。这次只资格新增三臂dispatch，不重复57,600gain合成、旧registry或旧19输入数组资格。原direct ideal绝对门槛失败仍保留。0新论文、0新MRI收益、长期goal active；所有新增仅本目录且已执行文件不覆盖。
