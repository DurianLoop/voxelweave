# 失败开发series全部192tile的逐层设备数值定位

固定原FOV失败case2/native_reference、同19998 parent、同输入SHA；不读GT，不按效果/位置选择tile。原完整192tile按原两tile batch共96组全部覆盖。独立CPU functional interpreter按原算子/eps/激活/state进行FP32 forward，生产GPU CheckpointedTaskUNet3D注册48个叶模块的只读输出hook。卷积14、InstanceNorm14、LeakyReLU14、ConvTranspose3、head Conv3三层，另完整概率字段共49个。

每batch在CPU/GPU各自重放两次，核所有49字段逐位determinism。比较第一轮CPU/GPU的全部元素最大绝对差、绝对差均值、参考绝对值范围和相对差（分母abs(CPU)+1e-6，仅诊断）。记录最差batch/tile/层内位置，不宣称各层差是独立因果效应。捕获到CPU后不保留GPU中间张量；不训练/回传/改任何参数。hooks用于定位，不冒充生产部署计时。

第一轮概率重构完整FOV：CPU独立weight/axes/native mapping，GPU生产weight/axes/float64 native mapping，两者各自SHA必须复现原失败记录。保留原3e-6概率/3e-12坐标/二值零差gate；诊断完成即使exit0也不等于full38通过。两次forward产生384实际GPU tile evaluations和384 CPU tile evaluations，但唯一tile仍192，患者仍1/开发series仍1。

共享FOV stage20MB，其他22.8MB allowance不减，原历史atomic文件和所有失败保留；本attempt压缩journal<=3MB，wall3600秒。CPU1/interop1/below-normal、RAM/disk各8GB；GPU起始free>=8192MiB、allocator<=min(10%,2.4GB/total)、runtimefree4GB、peak<=2.5GB，FP32/TF32off/deterministic。只操作本进程，不枚举/修改其他PID，不动原终端训练。

本轮只做有来源的诊断；后续任何算术/后端干预另冻版本并先单病例再全38/独立审核，不能用本次逐层统计直接填训练资格。layerwise时间包括捕获/CPU重放/比较，是资格开销，不是纯GPU生产成本。全部新增只写innovation。
