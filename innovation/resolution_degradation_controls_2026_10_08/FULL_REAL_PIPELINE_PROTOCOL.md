# 完整真实 MRI 分布与独立强度管线：执行前固定

前提已实际观察：228真实字段session5725/868f3b exit0；228同生产强度组合session31866/ee6557 exit0；独立强度40合成字段696add exit0，完整5984 primitive参数元数据合法。各前提receipt/source SHA再次核验；仅新检查入口和输出，旧冻结来源不改。

范围是原2992步×每步2patch=5984母几何，不是“5984个不同患者”。native-reference、raw-PCHIP两种输入分别重放，每种对throughplane/inplane/allaxes全部三模式检查，总35,904字段。保留11开发患者/19series；每患者每输入272步/544patch，每模式原enabled1785事件/每输入。GT仅用于合法训练sample_batch原crop与母label重放；分辨率和强度算子API均不接GT，不能用于部署时GT定位。已完成的原sampler独立审计继续作为来源，当前不冒充另一独立sampler实现。

完整真实MRI重建cache SHA和label SHA对旧资格，逐步原sample_batch的geometry/label/primitive对冻结5984 journal；所有母label保留。三模式固定factor、整数coarse尺寸、align_corners和原母域支持语义不变。每个完整target检查：生产Torch vs独立SciPy分辨率；两结果经过相同生产强度后的误差传播；生产输入上的独立强度isolated误差；Torch+生产强度 vs SciPy+独立强度的最终误差。上述强度误差均≤3e-6、support≤3e-6、coordinate≤3e-12、支持mask二值差0。独立强度共享NumPy PCG64正态抽样规范，不独立重写RNG。分辨率阶段padding逐位保留；gamma后padding与identity逐位相等不作要求或宣称，支持mask不等于InstanceNorm安全证书。

不挑患者/series/patch/轴，不因GT选择增强；失败字段参数、各误差及真实terminal保留。所有比较是软件资格，没有模型/forward/backward/新训练，没有医学效果。4已见验证/9series不参与选择；8未见确认/12series和lockedIXI继续关闭。

本次首次完整MRI重放预算单独固定：CPU1/本进程低优先级，墙钟32,400秒；磁盘和RAM各8,000,000,000bytes储备、本目录总5,000,000bytes不降。35,904项日志使用压缩JSON列数组，日志上限1,500,000bytes，开跑为最终journal+receipt预留1,800,000bytes；存各数值gate，不保存影像数组或每字段随机digest。来源cache、冻结schedule、geometry journal、算子版本SHA足以确定性重建；将成本按cache读取、sample_batch、分辨率生产/独立、强度生产/独立、日志与其他开销分开汇总，stage实际wall不冒充训练/部署费用。超预算也保留失败，不删旧证据。

35,904字段完整且真实exit0后才独立audit终端日志计数/完整患者分母、原母label与所有数值门槛；随后另实测matched训练所需forward/backward总费用及磁盘储备。此处training_ready仍false，不能把metadata和228stress外推成完整资格、不能立即拿普通分辨率增强称创新。GPU授权继续有效，原8192MiB起跑储备不变，原CPU四臂不迁移/重启，不枚举其他PID。

科研主线仍是：先充分任务能力和具体动作真实病灶损害改善余量；再证明合法采集可见性对动作损害差/全费用的患者折外预测，比较强QC/error-cost/defer/static/random/去采集特征。全11GT的19998parent不能冒充独立折外初始化；未见确认必须等完整选择协议冻结后一次打开。当前发表claim未确认，goal active。
