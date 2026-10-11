# 独立v2修复：导入后的本进程可见设备

attempt01实际91ff4a exit1，CUDA未初始化、MRI/GT/model数组加载0、forward/backward/update均0。独立新进程证明当前MRI环境为torch2.11.0+cu128、CUDA12.8、available=True；原工具链在导入时设置CUDA_VISIBLE_DEVICES=-1，旧已存在授权adapter也明确在完成CPU imports之后恢复0。

v2在相同GPU准入后、调用is_available和_lazy_init之前，将本进程CUDA_VISIBLE_DEVICES恢复0并记录before/after与torch runtime；输出另写attempt02。冻结v1源码/失败与原protocol均不编辑。CPU算子仍在CPU；原6分支/12patch、fixed step2开发患者、显存/磁盘/时间限制、零optimizer更新和所有科学范围保持。该修复不是新的科研方法。
