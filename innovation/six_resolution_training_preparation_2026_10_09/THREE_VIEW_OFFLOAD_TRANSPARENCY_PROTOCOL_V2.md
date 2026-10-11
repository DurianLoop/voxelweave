# CPU 卸载透明性核验 v2

完整继承 THREE_VIEW_OFFLOAD_TRANSPARENCY_PROTOCOL_V1.md 的人工数据、完整三图、两步 AdamW、所有门槛与资源/费用记录。

v1 实际 exit1，CUDA 初始化前 is_available 检查失败，MRI/GT/parent/optimizer updates 均0。原因定位于导入既存 CPU 参考模块时把 CUDA_VISIBLE_DEVICES 重设为 -1；原 v1 文件和失败 receipt 保持。v2 在导入完成后的 main 与初始化前显式恢复已授权的设备 0，沿用旧 GPU 脚本相同做法，不改变任何其他进程环境。输出另目录 attempt02；绑定 v1 的真实失败。其余实现不变。两版本运行结果不得混为一次成功。
