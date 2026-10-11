# 原患者 metadata 作业失败保留

真实 tool `39d1ea` exit1。11 患者/19 series 分组与拒绝检查已经走过，但在写最终 receipt 前，root_file_hashes 调用了仅接受 innovation 子路径的 entry()，对 D:\MRI\.gitignore 执行 relative_to(innovation) 而 ValueError。此处不是 MRI 或训练失败，也不将未写 receipt 的内部检查称为通过作业。

保留原已执行源码、原 patient_registry_attempt01 目录及两个 source_snapshot，不补写成功 receipt。另存 v2 只修 root metadata 路径表示、使用新 attempt02 目录，并将 v2 源码本身纳入绑定；不改变分组、特征、患者角色或暴露判断。
