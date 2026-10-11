# 全 FOV 的 FP32 InstanceNorm 算术诊断

必须等全部192tile逐层定位真实exit0、独立96batch×49field身份/分母/最大值审核完成后才执行。本次固定原失败case2/native_reference和19998 parent；读取全部192tile，GT0，不按病例效果或病灶选tile。CPU独立functional完整参考SHA必须重现原失败。GPU native原始输出也必须重现原失败SHA。

两个预先固定的算术干预仅替换14处推理 InstanceNorm.forward，输入/输出/参数/统计全FP32，eps1e-5及原affine参数保留，不训练：

1. `fp32_centered`：torch.var_mean(correction=0)的方差/均值；((x-mean)*rsqrt(var+eps))*weight+bias。
2. `fp32_affine_addcmul`：同一var_mean；scale=rsqrt(var+eps)*weight，shift=bias-mean*scale，torch.addcmul(shift,x,scale)。

这两个代数等价的形式因浮点舍入未必逐位相同；它们是诊断候选，不自动当部署算子。两候选都独立做两次完整FOV推理，逐位重放SHA；各与冻结CPU原参考比较概率max<=3e-6、二值零差。不会改变CPU参考、eps、阈值、平滑、概率精度或医学六gate；两者成功/失败均记录。原始GPU native只运行一次作为已有重复检查后的复现锚。不同候选从同一state重载，权重SHA必须始终一致。

完整FOV融合/float64 native mapping继续用原生产实现；CPU独立坐标gate<=3e-12/二值零差。单病例通过也仍full38=false；正式部署须另外冻结实现、完整38及两个原子捕获、全费用、真实终态和独立审核。本诊断计时是干预资格费用，不直接覆盖原完整训练费用合同。

共享FOV stage20MB，other22.8MB allowance及历史atomic文件不减；CPU1/interop1/below-normal、RAM/disk各8GB，wall1800秒。GPU起始free8192MiB、allocator<=min(10%,2.4GB/total)、peak2.5GB/runtimefree4GB；FP32/TF32off/deterministic。只操作本进程，不动其他PID或用户原终端训练。八未见确认/lockedIXI关闭。所有新增只写innovation，原已执行/冻结源不编辑。
