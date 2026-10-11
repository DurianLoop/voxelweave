# 本进程 CUDA 可见性修复

V2 actual5f1edd exit1/no session，receipt 给出 GPU aggregate free24035MiB、CUDA_initialized=false、CPU/GPU optimizer updates0；失败在 torch.cuda.is_available。已有 CPU utilities 在 import 时设置 CUDA_VISIBLE_DEVICES=-1，旧 smoke v2 已记录相同过程内问题。不能据此声称 GPU 被占满或驱动不可用。

V3 保存 CPU import 后的可见性，启动前在本进程恢复 CUDA_VISIBLE_DEVICES=0，再恢复原 initializer、查询实际 CUDA 版本与资源。保留 V1/V2，使用新目录 attempt03；其余模型、输入、两步 gate、receipt 保存方法与所有资源限制不变。不修改系统环境或用户原进程。
