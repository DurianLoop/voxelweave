# 冻结离线文本的第二次无损资源回收

只从已冻结 6997-file index chain 选择未压缩文本，路径、逻辑字节、SHA 全部保持。排除 tools、任何 MRI/GT/model 二进制、运行中的文件和不在冻结链中的文件。read-only inventory 先固定最多 1000 个、逻辑长度 >=4096 bytes 的目标和 Windows 文件属性；只有该清单完成后按独立 compress 模式执行 compact.exe /C /I /Q。

每文件压缩前后核原 SHA 和逻辑长度，并保存 GetCompressedFileSizeW 的变化；磁盘 snapshot 可能同时受其他进程写入影响，不替代物理 API 差值。失败保留，不删除或移动历史。CPU1/below-normal、wall 每模式 300 秒、目录 <=2MB、磁盘/RAM保留十进制8GB，另预留本目录2MB、数值资格2MB、文献2MB、原医学3MB和开发2.8MB。不操作其他 PID。资源够之后也必须先完整数值资格、训练入口/forward-backward/推理费资格才启动训练。
