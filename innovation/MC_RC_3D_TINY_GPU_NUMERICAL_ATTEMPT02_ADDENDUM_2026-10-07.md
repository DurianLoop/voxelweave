# 小型GPU预检attempt02：仅修复自身CUDA可见性

首轮入口实际exit1，CUDA初始化前RuntimeError: No CUDA GPUs are available，合成GPU/患者更新均0。原因由源码读取确认：继承的`mc_rc_observed_only_training_input.py`在import时将本进程CUDA_VISIBLE_DEVICES设为-1。原完整GPUpilot已在其8GB守卫之后恢复0；本次小入口遗漏了这一步。

保留首轮源码、协议、结果和traceback，不修改旧文件。新attempt02在自己的进程通过GPU totals启动门槛且CUDA尚未初始化后，记录原可见性并将其恢复0，核对is_available再执行同一小任务。只改自身进程环境，不更改用户终端环境/运行进程。其余shape、数据、初始seed、两个1步更新、数值/资源门槛及原完整GPU合同均保持。
