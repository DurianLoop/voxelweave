# V1 记录写入失败的独立修复

V1 actual113bd3 exit1，其末尾 FileExistsError 暴露 dump 的独占创建行为与周期性 receipt 保存不相容。V1 receipt 只保存了初始状态，不能把其中的零更新计数当作实际运行完成后的计数；内存里的原异常和精确更新计数未持久化，记录为不可恢复，不补造。

V2 使用新目录 high_precision_model_gpu_attempt02 与独立脚本：receipt 以同目录临时文件 write_text 后 replace 更新，保留 V1 源码、initial receipt、actual failure。除此以外模型、输入、两步验证、数值/二值 gate、资源限制、其他进程和医学数据边界不变。V2 的实际 GPU aggregate 与计数以其终态记录为准。
